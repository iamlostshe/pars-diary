"""Main module to start telegram-bot."""

# Integrated python modules
import asyncio

# Aiogram
from aiogram import Bot, Dispatcher

# Modules need to be installed
from loguru import logger

# Writed by me modules
from handlers import routers
from utils.db import check_db
from utils.load_env import TOKEN


# Starting bot
async def main() -> None:
    """Основная функция запуска бота."""
    # Connecting log file
    logger.add("log.log")

    # Checking for the existence database
    check_db()

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


if __name__ == "__main__":
    asyncio.run(main())
