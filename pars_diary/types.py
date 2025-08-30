"""Typing."""

from aiogram.types import Message


class User:
    """Пользователь."""

    async def __init__(self, message: Message) -> None:
        """Инициализация пользователя."""
        await db.get_cookie(message.from_user.id)
        await get_server_name(msg.from_user.id)

        # telegram
        # is_admin=message.user.id in config.admin_ids

        # bars

        # ФИО

        # parser
