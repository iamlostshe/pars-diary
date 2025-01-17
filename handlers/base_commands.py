"""Базовые комманды.

- /marks - Оценки
- /i_marks - Итоговые оценки
- /hw - Домашнее задание
- /me - Данные о пользователе
- /cs - Классные часы
- /events - Ивенты
- /birthdays - Дни рождения
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from utils.db import counter, get_cookie
from utils.hw import hw
from utils.keyboards import not_auth_keyboard
from utils.messages import error, not_auth
from utils.pars import Pars

router = Router(name=__name__)


# Базовые комманы (парсинг + небольшое изменение)
@router.message(
    Command(
        commands=["marks", "i_marks", "hw", "me", "cs", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message) -> None:
    """Отвечает за /marks, /i_marks, /hw, /me, /cs, /events, /birthdays."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    try:
        # Обновляем значение счётчика
        counter(msg.from_user.id, msg.text.split()[0][1:])

        # Получаем user_id пользователя
        user_id = msg.from_user.id

        # Проверяем зарегестирован ли пользователь
        if get_cookie(user_id):
            # Создаем объект класса
            pars = Pars()

            # Выбираем функцию, в зависимости от комманды
            commands = {
                "/me": pars.me,
                "/cs": pars.cs,
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

        else:
            # Выводим сообщение о необходимости регестрации и клавиатуру
            await msg.answer(
                not_auth(msg.from_user.language_code),
                "HTML",
                reply_markup=not_auth_keyboard(msg.from_user.language_code),
            )

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
