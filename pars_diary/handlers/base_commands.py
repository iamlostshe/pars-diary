"""Базовые команды.

- /marks - Оценки
- /i_marks - Итоговые оценки
- /me - Данные о пользователе
- /events - Ивенты
- /birthdays - Дни рождения
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.keyboards import not_auth_keyboard
from pars_diary.messages import not_auth
from pars_diary.parser.db import User
from pars_diary.utils.pars import Pars

router = Router(name="Base commands")


# Базовые команды (парсинг + небольшое изменение)
# TODO @milinuri: Я кусаться буду, что за беспредел в командах?
@router.message(
    Command(
        commands=["marks", "i_marks", "me", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message, user: User) -> None:
    """Отвечает за /marks, /i_marks, /me, /events, /birthdays."""
    if user.cookie is None:
        # Выводим сообщение о необходимости регистрации и клавиатуру
        await msg.answer(
            not_auth(),
            reply_markup=not_auth_keyboard(msg.from_user.language_code),
        )
        return

    # Создаем объект класса
    # Выбираем функцию, в зависимости от команды
    pars = Pars()
    commands = {
        "/me": pars.me,
        "/events": pars.events,
        "/birthdays": pars.birthdays,
        "/i_marks": pars.i_marks,
        "/marks": pars.marks,
    }

    # Создаем ответ
    answer = commands[msg.text](msg.from_user.id)

    # Отвечаем пользователю
    if len(answer) == 2 and isinstance(answer, tuple):
        await msg.answer(answer[0], reply_markup=answer[1])
    else:
        await msg.answer(answer)
