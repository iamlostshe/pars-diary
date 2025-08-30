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

from pars_diary.types import User
from pars_diary.utils.hw import hw
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
    if user.isauth:
        answer = {
            "/me": await user.parser.me(),
            "/events": await user.parser.events(),
            "/birthdays": await user.parser.birthdays(),
            "/i_marks": await user.parser.i_marks(),
            "/marks": await user.parser.marks(),
            "/hw": await hw(await user.parser.homework(), "t"),
        }[msg.text]

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
