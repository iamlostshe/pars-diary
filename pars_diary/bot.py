"""Main module to start telegram-bot."""

from aiogram import Dispatcher
from loguru import logger

from .config import bot
from .handlers import routers


async def main() -> None:
    """Основная функция запуска бота."""
    # Подключаем файл для сбора логов
    logger.add("log.log")

    dp = Dispatcher()

    for r in routers:
        logger.debug("Include router: {} ...", r.name)
        dp.include_router(r)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot start polling...")
    await dp.start_polling(bot)
