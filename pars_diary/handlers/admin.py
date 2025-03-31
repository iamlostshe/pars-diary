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

from pars_diary.config import config, metrics
from pars_diary.utils.db import GRAPH_NAME, GetStat, get_graph

router = Router(name="Admin commands")


@router.message(Command("admin"))
async def new_msg(msg: Message) -> None:
    """Отвечает за /admin."""
    # Если пользователь не админ - кусаемся
    if str(msg.from_user.id) not in config.admins:
        logger.warning("{} try to use /admin", msg.from_user.id)
        return

    # Обновляем график
    get_graph()

    # Подсчитываем использованные команды
    cc = metrics.count_commands()
    commands_str = "<b>Использований команд</b>:"
    for cmd, uses in cc.items():
        commands_str += f"\n-- /{cmd}: {uses}"

    # Получаем значения
    stat = GetStat()

    # Отвечаем пользователю
    await msg.answer_photo(
        FSInputFile(GRAPH_NAME),
        (
            f"<b>Всего пользователей: {stat.users_count}</b>\n\n"
            f"Авторизованных пользователей: {stat.cookie}\n\n"
            f"Уведомления: {stat.notify} / {stat.users_count}"
            f" ({stat.notify / stat.users_count * 100}%)\n"
            f"Умные уведомления: {stat.smart_notify} / {stat.users_count}"
            f" ({stat.smart_notify / stat.users_count * 100}%)\n\n"
            f"{commands_str}"
            "<b>Источники прихода аудитории (рефералы)"
            " (в порядке уменьшения выгоды):</b>\n\n"
            f"{stat.str_refer()}\n"
        ),
    )
