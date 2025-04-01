"""Main module to start telegram-bot."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, ErrorEvent, Message, Update
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from loguru import logger

from pars_diary.config import config, default, metrics, users_db
from pars_diary.handlers import ROUTERS
from pars_diary.messages import error_message

# Константы
# =========

dp = Dispatcher(db=users_db)

# Корневые обработчики
# ====================


@dp.message.middleware()
@dp.callback_query.middleware()
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Callable[[Update, dict[str, Any]], Awaitable[Any]]:
    """Логирование для сообщений и подсчёт использованных команд."""
    if isinstance(event, CallbackQuery):
        logger.info("[c] {}", event.callback_query.data)
    elif isinstance(event, Message):
        logger.debug("[m] {}", event.message.text)
        metrics.use_command(
            event.message.from_user.id, event.message.text.split()[0][1:]
        )
    else:
        logger.warning("Unprocessed event {}", type(event))

    return await handler(event, data)


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
        await message.answer(error_message(event.exception))


# Главная функция
# ===============


async def main() -> None:
    """Основная функция запуска бота."""
    logger.add("log.log")

    logger.info("Setup I18n context")
    i18n = I18n(path="locales", default_locale="ru", domain="messages")
    dp.message.middleware(SimpleI18nMiddleware(i18n))

    bot = Bot(token=config.telegram_token, default=default)
    # Connect handlers
    for router in ROUTERS:
        logger.debug("Include router: {} ...", router.name)
        dp.include_router(router)

    # Starting
    logger.info("Bot start polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
