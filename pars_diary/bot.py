"""Main module to start telegram-bot."""

from aiogram import Bot, Dispatcher
from loguru import logger

from .handlers import routers
from .utils.config import TOKEN, parser
from .utils.db import check_db


# Starting bot
async def main() -> None:
    """Основная функция запуска бота."""
    # Connecting log file
    logger.add("log.log")

    # Checking for the existence database
    await check_db()

    # Initializing parser
    await parser.init()

    # Initializating dp and bot
    dp = Dispatcher()
    bot = Bot(token=TOKEN)

    # Connect hendlers
    for r in routers:
        logger.debug("Include router: {} ...", r.name)
        dp.include_router(r)

    # Clean the webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # Starting
    logger.info("Bot start polling...")
    await dp.start_polling(bot)
