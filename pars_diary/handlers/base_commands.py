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

from pars_diary.parser import (
    birthdays,
    events,
    i_marks,
    marks,
    me,
)
from pars_diary.types import User

# "from pars_diary.utils.hw import hw
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth

router = Router(name=__name__)


@router.message(
    Command(
        commands=["marks", "i_marks", "hw", "me", "events", "birthdays"],
    ),
)
async def simple_msg(msg: Message, user: User) -> None:
    """Отвечает за /marks, /i_marks, /hw, /me, /events, /birthdays."""
    if user.is_auth:
        answer = await {
            "/birthdays": birthdays,
            "/events": events,
            # "/hw": await hw(await user.parser.homework(), "t"),
            "/i_marks": i_marks,
            "/marks": marks,
            "/me": me,
        }[msg.text.split()[0]](user.parser)

        if len(answer) == 2 and isinstance(answer, tuple):
            await msg.answer(answer[0], reply_markup=answer[1])
        else:
            await msg.answer(answer)

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await msg.answer(
            not_auth,
            reply_markup=not_auth_keyboard,
        )
