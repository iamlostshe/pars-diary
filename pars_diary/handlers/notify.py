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
from pars_diary.parser.db import NotifyStatus, UsersDataBase

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


def _notify_markup(status: NotifyStatus) -> InlineKeyboardMarkup:
    """Получает клавиатуру для настройки уведомлений."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text="🔔 Оценки" if status.notify else "🔕 Оценки",
                callback_data="n_n",
            ),
            InlineKeyboardButton(
                text="🔔 Умные" if status.smart else "🔕 Умные",
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
async def notify_settings(msg: Message, db: UsersDataBase) -> None:
    """Настройки для уведомлений."""
    if db.get_cookie(msg.from_user.id) is None:
        await msg.answer(not_auth(), reply_markup=not_auth_keyboard())
        return

    notify = db.get_notify(Message.from_user.id)
    await msg.answer(_SMART_NOTIFY, reply_markup=_notify_markup(notify))


# Обработчики кнопок
# ==================


@router.callback_query(F.data == "n_n")
async def call_set_notify(query: CallbackQuery, db: UsersDataBase) -> None:
    """Отвечает за все callback кнопки."""
    notify = db.get_notify(query.from_user.id)
    notify = db.set_notify(
        query.from_user.id, NotifyStatus(not notify.notify, notify.smart)
    )
    await query.message.answer(
        _SMART_NOTIFY, reply_markup=_notify_markup(notify)
    )


@router.callback_query(F.data == "n_s")
async def call_set_smart_notify(
    query: CallbackQuery, db: UsersDataBase
) -> None:
    """Изменение состояния умных уведомлений."""
    notify = db.get_notify(query.from_user.id)
    notify = db.set_notify(
        query.from_user.id, NotifyStatus(notify.notify, not notify.smart)
    )
    await query.message.answer(
        _SMART_NOTIFY, reply_markup=_notify_markup(notify)
    )
