"""Админка.

Включает в себя информацию для админов:

- график прихода пользователей
- количество пользователей
- список рефералов
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from loguru import logger

from utils.db import GRAPH_NAME, counter, get_graph
from utils.load_env import ADMINS_TG
from utils.messages import admin, error

router = Router(name=__name__)


# Комманда /admin
@router.message(Command("admin"))
async def new_msg(msg: Message) -> None:
    """Отвечает за /admin."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    try:
        # Обновляем значение счётчика
        counter(msg.from_user.id, msg.text.split()[0][1:])

        # Если пользователь - админ
        if str(msg.from_user.id) in ADMINS_TG:
            # Обновляем график
            get_graph()
            # Отвечаем пользователю
            await msg.answer_photo(FSInputFile(GRAPH_NAME), admin())

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
