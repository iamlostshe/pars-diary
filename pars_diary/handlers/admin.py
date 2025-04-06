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

router = Router(name="Admin commands")


@router.message(Command("admin"))
async def new_msg(msg: Message) -> None:
    """Отвечает за /admin."""
    # Если пользователь не админ - кусаемся
    if str(msg.from_user.id) not in config.admins_tg:
        logger.warning("{} try to use /admin", msg.from_user.id)
        return

    metrics.save_graph()
    stat = metrics.get_db_stats()
    cc = metrics.count_commands()
    commands_str = "<b>Использований команд</b>:"
    for cmd, uses in cc.items():
        commands_str += f"\n-- /{cmd}: {uses}"

    # Отвечаем пользователю
    await msg.answer_photo(
        FSInputFile("stat_img.png"),
        (
            f"<b>Всего пользователей: {stat.users}</b>\n\n"
            f"Авторизованных пользователей: {stat.cookie}\n\n"
            f"Уведомления: {stat.notify} / {stat.users}"
            f" ({stat.notify / stat.users * 100}%)\n"
            f"Умные уведомления: {stat.smart_notify} / {stat.users}"
            f" ({stat.smart_notify / stat.users * 100}%)\n\n"
            f"{commands_str}"
            "<b>Источники прихода аудитории (рефералы)"
            " (в порядке уменьшения выгоды):</b>\n\n"
            f"{metrics.get_ref_stats()}\n"
        ),
    )
