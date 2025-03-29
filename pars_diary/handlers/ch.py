"""Классные часы."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from pars_diary.utils.ch import ch
from pars_diary.utils.db import counter

router = Router(name="Class hour")


@router.message(Command("ch"))
async def ch_msg(msg: Message) -> None:
    """Отвечает за /ch."""
    logger.debug("[m] {}", msg.text)
    counter(msg.from_user.id, msg.text.split()[0][1:])

    # Создаем ответ
    answer = ch()
    await msg.answer_photo(
        answer[0],
        answer[1],
        "HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подробнее", url=answer[2])],
            ],
        ),
    )
