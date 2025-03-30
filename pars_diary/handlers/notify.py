"""Управление уведомлениями.

- Вкл./Отключить. уведомлений
- Вкл./Отключить. умных уведомлений
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from pars_diary.keyboards import not_auth_keyboard
from pars_diary.utils.db import get_cookie, get_notify
from pars_diary.utils.messages import not_auth

router = Router(name="Notify settings")


@router.message(Command("notify"))
async def lessons_msg(msg: Message) -> None:
    """Настройки для уведомлений."""
    if get_cookie(msg.from_user.id):
        await msg.answer("⚙️ <b>Настройки уведомлений:</b>", "HTML")

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if get_notify(msg.from_user.id)
                        else "✅ Включить",
                        callback_data="n_n",
                    ),
                ],
            ],
        )

        await msg.answer(
            "🔔 <b>Уведомления об изменении оценок</b>",
            "HTML",
            reply_markup=markup,
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if get_notify(msg.from_user.id, index="s")
                        else "✅ Включить",
                        callback_data="n_s",
                    ),
                ],
            ],
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
            parse_mode="HTML",
            reply_markup=markup,
        )

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Перейти",
                        url="https://t.me/mili_sp_bot",
                    ),
                ],
            ],
        )
        await msg.answer(
            "🔔 <b>Уведомления об изменении расписания</b>",
            "HTML",
            reply_markup=markup,
        )

    else:
        # Выводим сообщение о необходимости регистрации и клавиатуру
        await msg.answer(
            not_auth(msg.from_user.language_code),
            "HTML",
            reply_markup=not_auth_keyboard(),
        )
