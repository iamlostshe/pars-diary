"""Классные часы."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from pars_diary.services.ch import ch

router = Router(name="Class hour")


@router.message(Command("ch"))
async def ch_msg(msg: Message) -> None:
    """Отвечает за /ch."""
    answer = ch()
    await msg.answer_photo(
        answer.image_url,
        answer.description,
        "HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подробнее", url=answer.url)],
            ],
        ),
    )
