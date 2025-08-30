"""Авторизация в боте."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.types import User
from pars_diary.utils.db import add_user_cookie

router = Router(name=__name__)


# Вход в новую учебную запись
@router.message(Command("new"))
async def new_msg(msg: Message, user: User) -> None:
    """Отвечает за /new."""
    # Проверяем ошибки
    if msg.text == "/new":
        # Отвечаем пользователю
        await msg.answer('Комманда работает так - "/new sessionid=xxx..."')
    else:
        # Добавляем cookie пользователя в дб и отвечаем пользователю
        await msg.answer(
            await add_user_cookie(
                msg.from_user.id,
                "".join("".join(msg.text[5:].split()).split("\n")),
            ),
        )
