"""Базовые комманды.

- /marks - Оценки
- /i_marks - Итоговые оценки
- /me - Данные о пользователе
- /events - Ивенты
- /birthdays - Дни рождения
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.parser import (
    birthdays,
    events,
    i_marks,
    marks,
    me,
)
from pars_diary.types import User
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth

router = Router(name=__name__)


@router.message(
    Command(
        commands=["marks", "i_marks", "me", "events", "birthdays"],
    ),
)
async def simple_msg(message: Message, user: User) -> None:
    """Отвечает за /marks, /i_marks, /me, /events, /birthdays."""
    if user.is_auth:
        async with user.parser as parser:
            answer = await {
                "/birthdays": birthdays,
                "/events": events,
                "/i_marks": i_marks,
                "/marks": marks,
                "/me": me,
            }[message.text.split()[0]](parser)

        if len(answer) == 2 and isinstance(answer, tuple):
            await message.answer(answer[0], reply_markup=answer[1])
        else:
            await message.answer(answer)

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await message.answer(
            not_auth,
            reply_markup=not_auth_keyboard,
        )
