"""
main — Entry point for the Telegram AI Agent bot.
Initializes the bot, registers handlers, and starts polling.
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from bot.handlers import router
from config import TELEGRAM_BOT_TOKEN
from db.postgres import check_bookmakers_table

# Configure logging — set LOG_LEVEL=DEBUG in .env for verbose output
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Create bot and dispatcher, verify DB, register routes, start polling."""
    total_bookmakers = check_bookmakers_table()
    logger.info("Database RicashDB pronta. Bookmakers caricate: %d", total_bookmakers)

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Register the handlers router
    dp.include_router(router)

    logger.info("Bot avviato — in attesa di messaggi…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
