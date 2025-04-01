"""Управление уведомлениями.

- Вкл./Отключить. уведомлений.
- Вкл./Отключить. умных уведомлений.
- Изменение состояния уведомлений (Вкл./Отключить.)
- Изменение состояния умных уведомлений (Вкл./Отключить.)
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from pars_diary.keyboards import not_auth_keyboard
from pars_diary.messages import not_auth
from pars_diary.parser.db import NotifyStatus, User, UsersDataBase

router = Router(name="Notify settings")

# Константы
# =========

_SMART_NOTIFY = (
    "⚙️ <b>Настройки уведомлений</b>:\n\n"
    "Здесь можно настроить:\n"
    "🔔 Уведомления об изменении оценок\n"
    "🔔 <b>Умные уведомления</b>* - [в разработке] "
    "уникальная функция для анализа оценок "
    "и простых уведомлений, например:\n\n"
    "<blockquote>Спорная оценка по математике,"
    "необходимо исправить, иначе может выйти 4!\n\n"
    "Для настройки уведомлений используйте /notify\n"
    "</blockquote>\n"
    "или\n\n"
    "<blockquote>Вам не хватает всего 0.25 "
    "балла до оценки 5, стоит постараться!\n"
    "Для настройки уведомлений используйте /notify\n"
    "</blockquote>"
)


def _notify_markup(user: User) -> InlineKeyboardMarkup:
    """Получает клавиатуру для настройки уведомлений."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text="🔔 Оценки" if user.notify else "🔕 Оценки",
                callback_data="n_n",
            ),
            InlineKeyboardButton(
                text="🔔 Умные" if user.smart_notify else "🔕 Умные",
                callback_data="n_s",
            ),
            [
                InlineKeyboardButton(
                    text="🔔 В расписании", url="https://t.me/mili_sp_bot"
                )
            ],
        ]
    )


# Обработчики команд
# ==================


@router.message(Command("notify"))
async def notify_settings(msg: Message, user: User) -> None:
    """Настройки для уведомлений."""
    if user.cookie is None:
        await msg.answer(not_auth(), reply_markup=not_auth_keyboard())
        return
    await msg.answer(_SMART_NOTIFY, reply_markup=_notify_markup(user))


# Обработчики кнопок
# ==================


@router.callback_query(F.data == "n_n")
async def call_set_notify(
    query: CallbackQuery, user: User, db: UsersDataBase
) -> None:
    """Отвечает за все callback кнопки."""
    user.notify = not user.notify
    db.update_user(Message.from_user.id, user)
    await query.message.answer(_SMART_NOTIFY, reply_markup=_notify_markup(user))


@router.callback_query(F.data == "n_s")
async def call_set_smart_notify(
    query: CallbackQuery, user: User, db: UsersDataBase
) -> None:
    """Изменение состояния умных уведомлений."""
    user.smart_notify = not user.smart_notify
    db.update_user(Message.from_user.id, user)
    await query.message.answer(_SMART_NOTIFY, reply_markup=_notify_markup(user))
