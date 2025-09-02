"""Простой обработчик для ошибок."""

from aiogram import Router
from aiogram.types import ErrorEvent
from loguru import logger

from pars_diary.utils.messages import error

router = Router(name=__name__)

@router.errors()
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
            error(event.exception),
        )
