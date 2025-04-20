"""Main module to start telegram-bot."""

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from loguru import logger

from .config import config, default, parser
from .handlers import routers
from .utils.db import check_db
from .utils.messages import error

dp = Dispatcher()


@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    message = None

    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message

    if message:
        await message.answer(
            await error(event.exception, message.from_user.language_code),
        )


async def main() -> None:
    """Основная функция запуска бота."""
    # Connecting log file
    logger.add("log.log")

    # Checking for the existence database
    await check_db()

    # Initializing parser
    await parser.init()

    # Initializating bot
    bot = Bot(token=config.token_tg, default=default)

    # Connect hendlers
    for r in routers:
        logger.debug("Include router: {} ...", r.name)
        dp.include_router(r)

    # Clean the webhook
    await bot.delete_webhook(drop_pending_updates=True)

    # Starting
    logger.info("Bot start polling...")
    await dp.start_polling(bot)
