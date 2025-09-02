"""Промежуточный слой для проброса данных пользователя из бд."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from bars_api import BarsAPI
from loguru import logger

from pars_diary.config import config
from pars_diary.types import User
from pars_diary.utils import db

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from aiogram.types import Message, TelegramObject


class AuthMiddleware(BaseMiddleware):
    """Промежуточный слой для проброса данных пользователя из бд."""

    async def __call__(
        self,
        handler: callable[[TelegramObject, dict[str, any]], Awaitable[any]],
        event: Message,
        data: dict[str, any],
    ) -> tuple[Message, User]:
        """Обработка и проброс данных о пользователе из бд."""
        # Выводим лог в консоль
        logger.debug("[m] {}", event.text)

        # Записываем пользователя в бд, если его еще там нет
        refer = (
            event.text[7:]
            if event.text and event.text.startswith("/start ")
            else None
        )
        db.add_user(event.from_user.id, refer)

        # Обновляем значение счётчика
        db.counter(event.from_user.id, event.text.split()[0][1:])

        server_name = db.get_server_name(event.from_user.id)
        cookie = db.get_cookie(event.from_user.id)

        parser = None
        if server_name and cookie:
            parser = BarsAPI(
                server_name,
                cookie,
            )

        # Пробрасываем объект пользователя
        data["user"] = User(
            is_auth=server_name and cookie,
            is_admin=event.from_user.id in config.admin_ids,
            parser=parser,
        )

        return await handler(event, data)
