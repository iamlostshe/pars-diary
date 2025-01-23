"""Управление уведомлениями.

- Вкл./Откл. уведомлений
- Вкл./Откл. умных уведомлений
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from utils.db import counter, get_cookie, get_notify
from utils.keyboards import not_auth_keyboard
from utils.messages import error, not_auth

router = Router(name=__name__)


# Настройки для уведомлений
@router.message(Command("notify"))
async def lessons_msg(msg: Message) -> None:
    """Отвечает за /notify."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Обновляем значение счётчика
    counter(msg.from_user.id, f"{msg.text.split()[0][1:]}-settings")

    # Проверяем ошибки
    try:
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
            # Выводим сообщение о необходимости регестрации и клавиатуру
            await msg.answer(
                not_auth(msg.from_user.language_code),
                "HTML",
                reply_markup=not_auth_keyboard(msg.from_user.language_code),
            )

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
