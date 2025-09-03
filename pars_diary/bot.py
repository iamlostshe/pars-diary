"""Main module to start telegram-bot."""

from aiogram import Dispatcher
from loguru import logger

from .auth import AuthMiddleware
from .config import bot, cait_parser
from .handlers import routers


async def main() -> None:
    """Основная функция запуска бота."""
    logger.add("log.log")

    await cait_parser.init()

    dp = Dispatcher()
    dp.message.middleware(AuthMiddleware())

    for r in routers:
        logger.debug("Include router: {} ...", r.name)
        dp.include_router(r)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot start polling...")
    await dp.start_polling(bot)
