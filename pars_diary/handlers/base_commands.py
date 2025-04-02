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
from pars_diary.parser.parser import DiaryParser

router = Router(name="Base commands")


# Базовые команды (парсинг + небольшое изменение)
# TODO @milinuri: Я кусаться буду, что за беспредел в командах?
@router.message(
    Command(
        commands=["marks", "i_marks", "me", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message, user: User, parser: DiaryParser) -> None:
    """Отвечает за /marks, /i_marks, /me, /events, /birthdays."""
    if user.cookie is None or msg.text is None:
        # Выводим сообщение о необходимости регистрации и клавиатуру
        await msg.answer(not_auth(), reply_markup=not_auth_keyboard())
        return

    # Создаем объект класса
    # Выбираем функцию, в зависимости от команды
    commands = {
        "/me": parser.me,
        "/events": parser.events,
        "/birthdays": parser.birthdays,
        "/i_marks": parser.i_marks,
        "/marks": parser.marks,
    }

    # Создаем ответ и отправляем пользователю
    # TODO @milinuri: Тут лучше создать конкретный датакласс
    answer = await commands[msg.text](user)
    if isinstance(answer, tuple):
        await msg.answer(answer[0], reply_markup=answer[1])
    else:
        await msg.answer(answer)
