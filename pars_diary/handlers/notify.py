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


# Настройки для уведомлений
@router.message(Command("notify"))
async def notify_msg(msg: Message, user: User) -> None:
    """Отвечает за /notify."""
    if user.is_auth:
        await msg.answer("⚙️ <b>Настройки уведомлений:</b>")
        await msg.answer(
            "🔔 <b>Уведомления об изменении оценок</b>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Отключить"
                            if db.get_notify(msg.from_user.id)
                            else "✅ Включить",
                            callback_data="n_n",
                        ),
                    ],
                ],
            ),
        )
        await msg.answer(
            (
                "🔔 <b>Умные уведомления</b>* - [в разработке] "
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
                            text="❌ Отключить"
                            if db.get_notify(msg.from_user.id, index="s")
                            else "✅ Включить",
                            callback_data="n_s",
                        ),
                    ],
                ],
            ),
        )
        await msg.answer(
            "🔔 <b>Уведомления об изменении расписания</b>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Перейти",
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


@router.callback_query(F.data == "n_n")
async def callback_n_n(callback_query: CallbackQuery) -> None:
    """Изменение сосотяния уведомлений."""
    await callback_query.message.edit_text(
        "🔔 <b>Уведомления об изменении оценок</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if db.swith_notify(callback_query.from_user.id)
                        else "✅ Включить",
                        callback_data="n_n",
                    ),
                ],
            ],
        ),
    )


@router.callback_query(F.data == "n_s")
async def callback_n_s(callback_query: CallbackQuery) -> None:
    """Изменение сосотяния умных уведомлений."""
    await callback_query.message.edit_text(
        (
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
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if db.swith_notify(callback_query.from_user.id, index="s")
                        else "✅ Включить",
                        callback_data="n_s",
                    ),
                ],
            ],
        ),
    )
