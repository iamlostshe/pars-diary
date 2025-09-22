"""Домашнее задание."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.parser.hw import hw
from pars_diary.types import User

router = Router(name=__name__)


@router.message(Command("hw"))
async def homework_msg(message: Message, user: User) -> None:
    """Отвечает за /hw."""
    msg_text, markup = hw(
        await user.parser.get_homework(),
        "t",
    )
    await message.answer(msg_text, reply_markup=markup)
