"""Main module to start telegram-bot."""

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from loguru import logger

from pars_diary.handlers import ROUTERS
from pars_diary.utils.db import check_db
from pars_diary.utils.load_env import TOKEN
from pars_diary.utils.messages import error

# Константы
# =========

dp = Dispatcher()

# Корневые обработчики
# ====================


@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message
    else:
        message = None

    if message is not None:
        await message.answer(
            error(event.exception, message.from_user.language_code), "HTML"
        )


# Главная функция
# ===============


async def main() -> None:
    """Основная функция запуска бота."""
    logger.add("log.log")

    # Checking for the existence database
    check_db()

    bot = Bot(token=TOKEN)
    # Connect handlers
    for router in ROUTERS:
        logger.debug("Include router: {} ...", router.name)
        dp.include_router(router)

    # Starting
    logger.info("Bot start polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
