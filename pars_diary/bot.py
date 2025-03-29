"""Main module to start telegram-bot."""

from aiogram import Bot, Dispatcher
from loguru import logger

from pars_diary.handlers import ROUTERS
from pars_diary.utils.db import check_db
from pars_diary.utils.load_env import TOKEN


# Starting bot
async def main() -> None:
    """Основная функция запуска бота."""
    logger.add("log.log")

    # Checking for the existence database
    check_db()

    # Init dp and bot
    dp = Dispatcher()
    bot = Bot(token=TOKEN)

    # Connect handlers
    for router in ROUTERS:
        logger.debug("Include router: {} ...", router.name)
        dp.include_router(router)

    # Starting
    logger.info("Bot start polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
