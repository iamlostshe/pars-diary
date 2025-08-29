"""Main module to start telegram-bot."""

from aiogram import Dispatcher
from loguru import logger

from .config import bot, parser
from .handlers import routers
from .utils.db import check_db


async def main() -> None:
    """Основная функция запуска бота."""
    # Подключаем файл для сбора логов
    logger.add("log.log")

    # Проверка наличия файлов бд
    # TODO(): Перейти на postgreSQL
    await check_db()

    # Инициализация парсера
    # TODO(): Перейти на bars-api
    await parser.init()

    dp = Dispatcher()

    for r in routers:
        logger.debug("Include router: {} ...", r.name)
        dp.include_router(r)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot start polling...")
    await dp.start_polling(bot)
