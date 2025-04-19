"""Базовые комманды.

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
from loguru import logger

from pars_diary.config import parser
from pars_diary.utils.db import counter, get_cookie
from pars_diary.utils.hw import hw
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth

router = Router(name=__name__)


# Базовые комманы (парсинг + небольшое изменение)
@router.message(
    Command(
        commands=["marks", "i_marks", "hw", "me", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message) -> None:
    """Отвечает за /marks, /i_marks, /hw, /me, /events, /birthdays."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    # Обновляем значение счётчика
    await counter(msg.from_user.id, msg.text.split()[0][1:])

    # Получаем user_id пользователя
    user_id = msg.from_user.id

    # Проверяем зарегестирован ли пользователь
    if await get_cookie(user_id):
        # Выбираем функцию, в зависимости от комманды
        commands = {
            "/me": parser.me,
            "/events": parser.events,
            "/birthdays": parser.birthdays,
            "/i_marks": parser.i_marks,
            "/marks": parser.marks,
            "/hw": lambda user_id: hw(user_id, "t"),
        }

        # Создаем ответ
        answer = await commands[msg.text](user_id)

        # Отвечаем пользователю
        if len(answer) == 2 and isinstance(answer, tuple):
            await msg.answer(answer[0], "HTML", reply_markup=answer[1])
        else:
            await msg.answer(answer, "HTML")

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await msg.answer(
            await not_auth(msg.from_user.language_code),
            "HTML",
            reply_markup=await not_auth_keyboard(msg.from_user.language_code),
        )
