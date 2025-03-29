"""/ch - Классные часы."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from pars_diary.utils.ch import ch
from pars_diary.utils.db import counter
from pars_diary.utils.messages import error

router = Router(name=__name__)


# Базовые комманы (парсинг + небольшое изменение)
@router.message(Command("ch"))
async def ch_msg(msg: Message) -> None:
    """Отвечает за /ch."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    try:
        # Обновляем значение счётчика
        counter(msg.from_user.id, msg.text.split()[0][1:])

        # Создаем ответ
        answer = ch()

        # Отвечаем пользователю
        await msg.answer_photo(
            answer[0],
            answer[1],
            "HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Подробнее", url=answer[2])],
                ],
            ),
        )

    except Exception as e:
        # Отвечаем пользователю
        await msg.answer(error(e, msg.from_user.language_code), "HTML")

        # Выводим лог
        logger.error(e)
