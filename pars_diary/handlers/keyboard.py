"""Клавиатуры.

Здесь следующие находятся callback_handler-ы:

- Изменение состояния уведомлений (Вкл./Отключить.)
- Изменение состояния умных уведомлений (Вкл./Отключить.)
- Домашнее задание (на завтра, на неделю, на конкретный день)
- Нейросеть для помощи в учебе
"""

from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from pars_diary.utils import db

router = Router(name=__name__)


# TODO @milinuri: Один обработчик для всех кнопок?
@router.callback_query()
async def callback(call: CallbackQuery) -> None:
    """Отвечает за все callback кнопки."""
    # Изменение состояния уведомлений
    if "n_n" in call.data:
        # Меняем состояние и создаем клавиатуру
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if db.swith_notify(call.from_user.id)
                        else "✅ Включить",
                        callback_data="n_n",
                    ),
                ],
            ],
        )

        # Отправляем сообщение
        await call.message.edit_text(
            "🔔 <b>Уведомления об изменении оценок</b>",
            reply_markup=markup,
        )

    # Изменение состояния умных уведомлений
    elif "n_s" in call.data:
        # Меняем состояние и создаем клавиатуру
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отключить"
                        if db.swith_notify(call.from_user.id, index="s")
                        else "✅ Включить",
                        callback_data="n_s",
                    ),
                ],
            ],
        )

        # Отправляем сообщение
        await call.message.edit_text(
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
            reply_markup=markup,
        )
