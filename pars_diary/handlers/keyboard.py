"""Клавиатуры.

Здесь следующие находятся callback_handler-ы:

- Изменение состояния уведомлений (Вкл./Откл.)
- Изменение состояния умных уведомлений (Вкл./Откл.)
- Домашнее задание (на завтра, на неделю, на конкретный день)
- Нейросеть для помощи в учебе
"""

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from pars_diary.parser.consts import DAYS_SHORT
from pars_diary.parser.hw import chatgpt, hw
from pars_diary.utils import db
from pars_diary.utils.keyboards import reg_1, reg_2
from pars_diary.utils.messages import registration_1, registration_2

router = Router(name=__name__)


@router.callback_query()
async def callback(call: CallbackQuery) -> None:
    """Отвечает за все callback-хендлеры (кнопки)."""
    # Выводим лог в консоль
    logger.debug("[c] {}", call.data)

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

        # Отправлем сообщение
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

    # Домашнее задание
    elif "hw" in call.data:
        if call.data == "hw_days":
            result = []
            for n, day in enumerate(DAYS_SHORT[:-1]):
                result.append(
                    InlineKeyboardButton(text=day, callback_data=f"hw_{n}"),
                )

            markup = InlineKeyboardMarkup(inline_keyboard=[result])

            await call.message.edit_text("Выбери день недели:", reply_markup=markup)

        else:
            index = call.data.replace("hw_", "")
            answer = await hw(call.from_user.id, index)

            await call.message.edit_text(
                answer[0],
                reply_markup=answer[1],
            )

    # Нейросеть для помощи в учебе
    elif "chatgpt" in call.data:
        await call.message.edit_text("Chatgpt думает...")
        send_text = chatgpt(call.from_user.id, call.data, call.from_user.first_name)
        await call.message.edit_text(send_text)

    # Регистрация в боте
    elif call.data == "reg_0":
        await call.message.edit_text(
            registration_1,
            reply_markup=await reg_1(),
        )

    elif "reg_1_" in call.data:
        # Записываем provider в бд
        provider = "".join(call.data.split("_")[2:])
        db.add_user_provider(call.from_user.id, provider)

        await call.message.edit_text(
            registration_2,
            reply_markup=reg_2,
        )
