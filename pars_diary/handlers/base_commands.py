"""Базовые команды.

- /marks - Оценки
- /i_marks - Итоговые оценки
- /hw - Домашнее задание
- /me - Данные о пользователе
- /events - Ивенты
- /birthdays - Дни рождения
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.utils.db import get_cookie
from pars_diary.utils.hw import hw
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth
from pars_diary.utils.pars import Pars

router = Router(name="Base commands")


# Базовые команды (парсинг + небольшое изменение)
# TODO @milinuri: Я кусаться буду, что за беспредел в командах?
@router.message(
    Command(
        commands=["marks", "i_marks", "hw", "me", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message) -> None:
    """Отвечает за /marks, /i_marks, /hw, /me, /events, /birthdays."""
    user_id = msg.from_user.id

    # Проверяем зарегистрирован ли пользователь
    if not get_cookie(user_id):
        # Выводим сообщение о необходимости регистрации и клавиатуру
        await msg.answer(
            not_auth(msg.from_user.language_code),
            "HTML",
            reply_markup=not_auth_keyboard(msg.from_user.language_code),
        )
        return

    # Создаем объект класса
    pars = Pars()

    # Выбираем функцию, в зависимости от команды
    commands = {
        "/me": pars.me,
        "/events": pars.events,
        "/birthdays": pars.birthdays,
        "/i_marks": pars.i_marks,
        "/marks": pars.marks,
        "/hw": lambda user_id: hw(user_id, "t"),
    }

    # Создаем ответ
    answer = commands[msg.text](user_id)

    # Отвечаем пользователю
    if len(answer) == 2 and isinstance(answer, tuple):
        await msg.answer(answer[0], "HTML", reply_markup=answer[1])
    else:
        await msg.answer(answer, "HTML")
