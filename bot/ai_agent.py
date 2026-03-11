"""
ai_agent — Wrapper around the OpenAI Responses API with function-calling support.
Keeps per-user conversation context via previous_response_id.
The agent's sole purpose is to gather bookmaker registrations from the user
and propose available ones by querying the database through a tool call.
"""

import json
import logging
from typing import Optional

import openai
from openai import AsyncOpenAI

from config import (
    OPENAI_API_KEY,
    AI_MODEL,
    AI_INSTRUCTIONS,
    AI_MAX_TOKENS,
    AI_REASONING,
    AI_TIMEOUT,
    AI_MAX_RETRIES,
)
from db.postgres import get_available_bookmakers

logger = logging.getLogger(__name__)

# Async OpenAI client with timeout and retry policy from settings.yaml
_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    timeout=AI_TIMEOUT,
    max_retries=AI_MAX_RETRIES,
)

# In-memory store: user_id -> last response id (context chaining)
_previous_response_ids: dict[int, Optional[str]] = {}

# ----- OpenAI function tool definition -----
# The model will call this tool when it has collected the user's bookmaker list.
_tools = [
    {
        "type": "function",
        "name": "get_available_bookmakers",
        "description": (
            "Riceve la lista dei nomi dei bookmaker con cui l'utente è già registrato "
            "e restituisce i bookmaker attivi non ancora utilizzati dall'utente."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_bookmaker_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Nomi dei bookmaker con cui l'utente è già registrato.",
                }
            },
            "required": ["user_bookmaker_names"],
        },
    }
]


def clear_history(user_id: int) -> None:
    """Reset conversation context for a user."""
    _previous_response_ids.pop(user_id, None)


async def chat(user_id: int, user_message: str) -> str:
    """
    Send a user message to GPT via the Responses API and return the assistant's reply.
    If the model invokes the get_available_bookmakers tool, execute the DB query,
    feed the result back, and return the final response.
    """
    reasoning = {"effort": "medium"} if AI_REASONING else None

    try:
        # --- First call: send user message ---
        response = await _client.responses.create(
            model=AI_MODEL,
            instructions=AI_INSTRUCTIONS,
            input=user_message,
            tools=_tools,
            previous_response_id=_previous_response_ids.get(user_id),
            max_output_tokens=AI_MAX_TOKENS,
            reasoning=reasoning,
        )

        # Store response id for context continuity
        _previous_response_ids[user_id] = response.id
        logger.info("Response %s received for user %d", response.id, user_id)

        # --- Check if the model wants to call a tool ---
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if tool_calls:
            # Process each tool call (we only have one tool, but loop for safety)
            for tool_call in tool_calls:
                if tool_call.name == "get_available_bookmakers":
                    args = json.loads(tool_call.arguments)
                    user_names = args.get("user_bookmaker_names", [])

                    logger.info(
                        "Tool call get_available_bookmakers for user %d with names: %s",
                        user_id, user_names,
                    )

                    # Query the database for available bookmakers
                    available = await get_available_bookmakers(user_names)

                    # --- Second call: feed tool result back to the model ---
                    follow_up = await _client.responses.create(
                        model=AI_MODEL,
                        instructions=AI_INSTRUCTIONS,
                        previous_response_id=response.id,
                        input=[
                            {
                                "type": "function_call_output",
                                "call_id": tool_call.call_id,
                                "output": json.dumps(available, ensure_ascii=False),
                            }
                        ],
                        tools=_tools,
                        max_output_tokens=AI_MAX_TOKENS,
                        reasoning=reasoning,
                    )

                    _previous_response_ids[user_id] = follow_up.id
                    logger.info("Follow-up response %s for user %d", follow_up.id, user_id)
                    return follow_up.output_text

        # No tool call — return the model's direct text reply
        return response.output_text

    except openai.AuthenticationError:
        logger.critical("Chiave API OpenAI non valida o scaduta.")
        return "⚠️ Errore di configurazione del servizio. Contatta l'amministratore."

    except openai.PermissionDeniedError as exc:
        logger.error("Permesso negato dall'API OpenAI: %s", exc.message)
        return "⚠️ Non ho i permessi per completare la richiesta."

    except openai.RateLimitError:
        logger.warning("Rate limit superato per utente %d dopo %d tentativi.", user_id, AI_MAX_RETRIES)
        return "⏳ Il servizio è momentaneamente sovraccarico. Riprova tra qualche secondo."

    except openai.BadRequestError as exc:
        logger.warning("Richiesta non valida per utente %d: %s", user_id, exc.message)
        return "⚠️ La richiesta non è valida. Prova a riformulare il messaggio."

    except openai.NotFoundError as exc:
        logger.error("Risorsa non trovata (modello?): %s", exc.message)
        return "⚠️ Errore di configurazione del servizio. Contatta l'amministratore."

    except openai.UnprocessableEntityError as exc:
        logger.error("Entità non elaborabile: %s", exc.message)
        return "⚠️ Non riesco a elaborare la richiesta. Prova a riformulare."

    except openai.APITimeoutError:
        logger.warning("Timeout per utente %d dopo %ds.", user_id, AI_TIMEOUT)
        return "⏳ La risposta ha impiegato troppo tempo. Riprova."

    except openai.APIConnectionError as exc:
        logger.error("Connessione all'API fallita: %s", exc)
        return "⚠️ Impossibile contattare il servizio AI. Riprova più tardi."

    except openai.InternalServerError:
        logger.error("Errore interno OpenAI per utente %d.", user_id)
        return "⚠️ Il servizio AI ha riscontrato un errore interno. Riprova più tardi."

    except openai.APIStatusError as exc:
        logger.error("Errore API OpenAI non gestito (status %d): %s", exc.status_code, exc.message)
        return "⚠️ Si è verificato un errore imprevisto. Riprova più tardi."

