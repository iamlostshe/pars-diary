"""Клавиатуры.

Здесь следующие находятся callback_handler-ы:

- Изменение состояния уведомлений (Вкл./Откл.)
- Изменение состояния умных уведомлений (Вкл./Откл.)
- Домашнее задание (на завтра, на неделю, на конкретный день)
- Нейросеть для помощи в учебе
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from pars_diary.parser import hw
from pars_diary.types import User
from pars_diary.utils import db
from pars_diary.utils.keyboards import not_auth_keyboard, reg_2
from pars_diary.utils.messages import not_auth, registration_2

router = Router(name=__name__)


@router.callback_query()
async def callback(call: CallbackQuery, user: User) -> None:
    """Отвечает за все callback-хендлеры (кнопки)."""
    if "hw_" in call.data:
        if user.is_auth:
            async with user.parser as parser:
                msg_text, markup = hw(
                    await parser.get_homework(),
                    call.data.replace("hw_", ""),
                )
                await call.message.edit_text(msg_text, reply_markup=markup)

        else:
            # Выводим сообщение о необходимости регестрации и клавиатуру
            await call.message.edit_text(
                not_auth,
                reply_markup=not_auth_keyboard,
            )

    elif "reg_1_" in call.data:
        db.add_user_provider(
            call.from_user.id,
            call.data.replace("reg_1_", ""),
        )

        await call.message.edit_text(
            registration_2,
            reply_markup=reg_2,
        )
