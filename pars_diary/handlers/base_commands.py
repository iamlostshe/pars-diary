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
from pars_diary.utils.db import counter, get_cookie, get_server_name
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

    # Обновляем значение счётчика
    await counter(msg.from_user.id, msg.text.split()[0][1:])

    user_cookie = await get_cookie(msg.from_user.id)
    server_name = await get_server_name(msg.from_user.id)

    # Проверяем зарегестирован ли пользователь
    if user_cookie:
        # Инициализируем пользователя
        await parser.init_user(user_cookie, server_name)

        # Выбираем функцию, в зависимости от комманды
        answer = {
            "/me": await parser.me(),
            "/events": await parser.events(),
            "/birthdays": await parser.birthdays(),
            "/i_marks": await parser.i_marks(),
            "/marks": await parser.marks(),
            "/hw": await hw(await parser.homework(), "t"),
        }[msg.text]

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
