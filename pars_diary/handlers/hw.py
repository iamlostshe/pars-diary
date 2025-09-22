"""Домашнее задание."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.parser.hw import hw
from pars_diary.types import User
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth

router = Router(name=__name__)


@router.message(Command("hw"))
async def homework_msg(message: Message, user: User) -> None:
    """Отвечает за /hw."""
    if user.is_auth:
        async with user.parser as parser:
            msg_text, markup = hw(
                await parser.get_homework(),
                "t",
            )
            await message.answer(msg_text, reply_markup=markup)

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await message.answer(
            not_auth,
            reply_markup=not_auth_keyboard,
        )
