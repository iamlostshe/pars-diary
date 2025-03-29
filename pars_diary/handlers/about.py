"""Информация о боте.

Содержит подробную информацию о боте, включая:

- отличая от конкурентов
- информацию об умных уведомлениях
- ссылку на админа
- ссылку на исходный код
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from pars_diary.utils.db import counter
from pars_diary.utils.messages import about, error

router = Router(name=__name__)


# О проекте
@router.message(Command("about"))
async def lessons_msg(msg: Message) -> None:
    """Отвечает за /about."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    try:
        # Обновляем значение счётчика
        counter(msg.from_user.id, msg.text.split()[0][1:])

        # Отвечаем пользователю
        await msg.answer(about(msg.from_user.language_code), "HTML")

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
