"""
handlers — Telegram bot message handlers (age gate + AI conversation).
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from bot.ai_agent import chat, clear_history

router = Router()

# In-memory set of verified (adult) users
_verified_users: set[int] = set()

# Simple reply keyboard for age confirmation
_age_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Sì, ho 18+ anni"),
               KeyboardButton(text="❌ No")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — ask the user to confirm their age."""
    # Reset any previous verification and conversation context
    _verified_users.discard(message.from_user.id)
    clear_history(message.from_user.id)

    await message.answer(
        "👋 Benvenuto! Prima di continuare, confermi di avere almeno 18 anni?",
        reply_markup=_age_keyboard,
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    """Handle /reset — clear conversation context and re-ask age."""
    _verified_users.discard(message.from_user.id)
    clear_history(message.from_user.id)

    await message.answer(
        "🔄 Conversazione resettata. Confermi di avere almeno 18 anni?",
        reply_markup=_age_keyboard,
    )


@router.message(F.text == "✅ Sì, ho 18+ anni")
async def age_confirmed(message: Message) -> None:
    """User confirmed they are 18+. Start bookmaker conversation via AI."""
    user_id = message.from_user.id
    _verified_users.add(user_id)

    # Remove the age keyboard
    await message.answer(
        "✅ Perfetto, grazie per la conferma!",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Send typing indicator while AI generates the first question
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Kick off the bookmaker conversation by telling the AI the user is verified
    first_reply = await chat(
        user_id,
        "L'utente ha confermato di essere maggiorenne. "
        "Chiedigli con quali bookmaker è già registrato.",
    )
    await message.answer(first_reply)


@router.message(F.text == "❌ No")
async def age_denied(message: Message) -> None:
    """User is not 18+. Politely refuse the service."""
    _verified_users.discard(message.from_user.id)
    clear_history(message.from_user.id)

    await message.answer(
        "😔 Mi dispiace, questo servizio è riservato ai maggiorenni. "
        "Torna quando avrai compiuto 18 anni!",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message()
async def handle_message(message: Message) -> None:
    """Handle any text message — forward to AI agent if user is verified."""
    user_id = message.from_user.id

    # If the user has not passed the age check, ask again
    if user_id not in _verified_users:
        await message.answer(
            "⚠️ Per favore, conferma prima la tua età.",
            reply_markup=_age_keyboard,
        )
        return

    # Ignore non-text messages
    if not message.text:
        await message.answer("Per ora posso gestire solo messaggi di testo.")
        return

    # Send "typing" action while waiting for the AI response
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Get AI response
    reply = await chat(user_id, message.text)
    await message.answer(reply)

