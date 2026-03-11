"""
postgres — PostgreSQL helpers for the bot project.
Provides both sync (startup checks) and async (runtime queries) access.
"""

import logging
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from config import DATABASE_URL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sync helpers (used at startup before the event loop is running)
# ---------------------------------------------------------------------------

def get_connection() -> psycopg.Connection[Any]:
    """Create a synchronous PostgreSQL connection."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def check_bookmakers_table() -> int:
    """Return the number of rows currently stored in the Bookmakers table."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL('SELECT COUNT(*) AS total FROM "Bookmakers"'))
            row = cursor.fetchone()
            total = int(row["total"])

    logger.info("Tabella Bookmakers disponibile con %d righe.", total)
    return total


# ---------------------------------------------------------------------------
# Async helpers (used at runtime inside the event loop)
# ---------------------------------------------------------------------------

async def get_all_active_bookmaker_names() -> list[str]:
    """Return a list of distinct names of active bookmakers, ordered by priority."""
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL, row_factory=dict_row
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql.SQL(
                    'SELECT DISTINCT name FROM "Bookmakers" '
                    "WHERE active = TRUE "
                    "ORDER BY name"
                )
            )
            rows = await cur.fetchall()
    return [r["name"] for r in rows]


async def get_available_bookmakers(user_bookmaker_names: list[str]) -> list[dict]:
    """
    Return active bookmakers whose name does NOT appear in *user_bookmaker_names*.
    Comparison is case-insensitive.  Results are ordered by priority (ascending = highest first).
    """
    # Normalise user input to upper-case for comparison
    excluded = [n.upper() for n in user_bookmaker_names]

    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL, row_factory=dict_row
    ) as conn:
        async with conn.cursor() as cur:
            if excluded:
                await cur.execute(
                    sql.SQL(
                        'SELECT DISTINCT name, link, min_dep FROM "Bookmakers" '
                        "WHERE active = TRUE AND UPPER(name) != ALL(%s) "
                        "ORDER BY name"
                    ),
                    (excluded,),
                )
            else:
                await cur.execute(
                    sql.SQL(
                        'SELECT DISTINCT name, link, min_dep FROM "Bookmakers" '
                        "WHERE active = TRUE "
                        "ORDER BY name"
                    )
                )
            rows = await cur.fetchall()

    logger.info(
        "Bookmakers disponibili dopo esclusione di %s: %d",
        excluded, len(rows),
    )
    return [dict(r) for r in rows]


