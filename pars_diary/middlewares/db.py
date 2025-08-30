"""Промежуточный слой для проброса данных пользователя из бд."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from bars_api import BarsAPI
from loguru import logger

from pars_diary.config import config, db
from pars_diary.types import User

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from aiogram.types import Message, TelegramObject


class DataBaseMiddleware(BaseMiddleware):
    """Промежуточный слой для проброса данных пользователя из бд."""

    async def __call__(
        self,
        handler: callable[[TelegramObject, dict[str, any]], Awaitable[any]],
        event: Message | CallbackQuery,
        data: dict[str, any],
    ) -> tuple[Message | CallbackQuery, User]:
        """Обработка и проброс данных о пользователе из бд."""
        # Приводим TelegramObject к единому виду (Message)
        _event = event.message if isinstance(event, CallbackQuery) else event

        # Выводим лог в консоль
        logger.debug("[m] {}", _event.text)

        # Записываем пользователя в бд, если его еще там нет
        refer = (
            _event.text[7:]
            if _event.text and _event.text.startswith("/start ")
            else None
        )
        await db.add_user(_event.from_user.id, refer)

        # Обновляем значение счётчика
        await db.counter(_event.from_user.id, _event.text.split()[0][1:])

        server_name = await db.get_server_name(_event.from_user.id)
        cookie = await db.get_cookie(_event.from_user.id)

        parser = None
        if server_name and cookie:
            parser = BarsAPI(
                server_name,
                cookie,
            )

        return await handler(event, data), User(
            is_auth=bool(cookie),
            is_admin=_event.from_user.id in config.admin_ids,
            parser=parser,
        )
