"""Main module to start telegram-bot."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, ErrorEvent, Message, Update
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from loguru import logger

from pars_diary.config import config, default, metrics, parser, users_db
from pars_diary.handlers import ROUTERS
from pars_diary.messages import error_message

# Константы
# =========

dp = Dispatcher(db=users_db, parser=parser)

# Корневые обработчики
# ====================


@dp.message.middleware()
@dp.callback_query.middleware()
async def db_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Callable[[Update, dict[str, Any]], Awaitable[Any]]:
    """Логирование для сообщений и подсчёт использованных команд."""
    if isinstance(event, CallbackQuery) and event.callback_query is not None:
        logger.info("[c] {}", event.callback_query.data)
        if event.callback_query.from_user is not None:
            data["user"] = users_db.get_user(event.callback_query.from_user.id)
    elif isinstance(event, Message) and event.text is not None:
        logger.debug("[m] {}", event.text)
        if event.from_user is not None and event.text is not None:
            metrics.use_command(
                event.from_user.id, event.text.split()[0][1:]
            )
            data["user"] = users_db.get_user(event.from_user.id)
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

    logger.info("Setup bot and parser")
    bot = Bot(token=config.tg_token, default=default)
    await parser.connect()

    # Connect handlers
    for router in ROUTERS:
        logger.debug("Include router: {} ...", router.name)
        dp.include_router(router)

    # Starting
    logger.info("Bot start polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
