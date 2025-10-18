"""Управление уведомлениями.

- Вкл./Откл. уведомлений
- Вкл./Откл. умных уведомлений
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from pars_diary.types import User
from pars_diary.utils import db
from pars_diary.utils.keyboards import not_auth_keyboard
from pars_diary.utils.messages import not_auth

router = Router(name=__name__)


@router.callback_query(F.data == "n_n")
@router.callback_query(F.data == "n_s")
@router.message(Command("notify"))
async def notify_msg(msg: Message, user: User) -> None:
    """Отвечает за /notify (настройки уведомлений)."""
    if isinstance(msg, CallbackQuery):
        method = msg.message.edit_text

        if msg.data == "n_n":
            db.swith_notify(msg.from_user.id)
        elif msg.data == "n_s":
            db.swith_notify(msg.from_user.id, "s")

    else:
        method = msg.answer

    if user.is_auth:
        await method(
            (
                "⚙️ <b>Настройки уведомлений:</b>\n\n"
                "В боте есть 2 вида уведомлений:\n\n"
                "🔔 <b>Уведомления об изменении оценок</b>\n\n"
                "🔔 <b>Умные уведомления</b> - "
                "уникальная функция для анализа оценок "
                "и простых уведомлений, например:\n\n"
                "<blockquote>Спорная оценка по математике,"
                "необходимо исправить, иначе может выйти 4!\n\n"
                "Для настройки уведомлений используйте /notify\n"
                "</blockquote>\n"
                "или\n\n"
                "<blockquote>Вам не хватает всего 0.25 балла "
                "до оценки 5, стоит постараться!\n"
                "Для настройки уведомлений используйте /notify\n"
                "</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Отключить (о новых оценках)"
                            if db.get_notify(msg.from_user.id)
                            else "✅ Включить (о новых оценках)",
                            callback_data="n_n",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Отключить (умные)"
                            if db.get_notify(msg.from_user.id, index="s")
                            else "✅ Включить (умные)",
                            callback_data="n_s",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Об изменении расписания",
                            url="https://t.me/mili_sp_bot",
                        ),
                    ],
                ],
            ),
        )

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await msg.answer(
            not_auth,
            reply_markup=not_auth_keyboard,
        )
