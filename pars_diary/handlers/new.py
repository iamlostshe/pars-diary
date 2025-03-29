"""Авторизация в боте."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.utils.db import add_user_cookie

router = Router(name="Register user")


@router.message(Command("new"))
async def new_msg(msg: Message) -> None:
    """Вход в новую учебную запись."""
    # Если пользователь не передал куки
    if msg.text == "/new":
        await msg.answer('Команда работает так - "/new sessionid=xxx..."')
        return

    # Добавляем cookie пользователя в дб и отвечаем пользователю
    await msg.answer(
        add_user_cookie(
            msg.from_user.id,
            "".join("".join(msg.text[5:].split()).split("\n")),
        ),
    )
