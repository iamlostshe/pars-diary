"""Авторизация в боте."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from pars_diary.utils.db import add_user_cookie, counter
from pars_diary.utils.messages import error

router = Router(name=__name__)


# Вход в новую учебную запись
@router.message(Command("new"))
async def new_msg(msg: Message) -> None:
    """Отвечает за /new."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Обновляем значение счётчика
    counter(msg.from_user.id, msg.text.split()[0][1:])

    # Проверяем ошибки
    try:
        if msg.text == "/new":
            # Отвечаем пользователю
            await msg.answer('Комманда работает так - "/new sessionid=xxx..."')
        else:
            # Добавляем cookie пользователя в дб и отвечаем пользователю
            await msg.answer(
                add_user_cookie(
                    msg.from_user.id,
                    "".join("".join(msg.text[5:].split()).split("\n")),
                ),
            )

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
