"""Промежуточный слой для проброса данных пользователя из бд."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from bars_api import BarsAPI
from loguru import logger

from pars_diary.config import config
from pars_diary.types import User
from pars_diary.utils import db
from pars_diary.utils.keyboards import not_sub_keyboard
from pars_diary.utils.messages import not_sub

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from aiogram.types import Message

CHECK_SUB_CHANNEL = "@iamlostshe_blog"


class AuthMiddleware(BaseMiddleware):
    """Промежуточный слой для проброса данных пользователя из бд."""

    async def __call__(
        self,
        handler: callable[[Message | CallbackQuery, dict[str, any]], Awaitable[any]],
        event: Message | CallbackQuery,
        data: dict[str, any],
    ) -> tuple[Message, User]:
        """Обработка и проброс данных о пользователе из бд."""
        # Приводим к единому типу
        if isinstance(event, CallbackQuery):
            logger.debug("[c] {}", event.data)
            _event = event.message
        else:
            logger.debug("[m] {}", event.text)
            _event = event

        # Записываем пользователя в бд, если его еще там нет
        refer = (
            _event.text[7:]
            if _event.text and _event.text.startswith("/start ")
            else None
        )
        db.add_user(_event.from_user.id, refer)

        # Обновляем значение счётчика
        db.counter(_event.from_user.id, _event.text.split()[0][1:])

        # Проверяем подписку на канал
        user_channel_status = await _event.bot.get_chat_member(
            chat_id=CHECK_SUB_CHANNEL,
            user_id=_event.from_user.id,
        )
        if user_channel_status.status == "left":
            return await _event.answer(not_sub, reply_markup=not_sub_keyboard)

        provider = db.get_provider(event.from_user.id)
        cookie = db.get_cookie(event.from_user.id)

        # Пробрасываем объект пользователя
        data["user"] = User(
            is_auth=provider and cookie,
            is_admin=event.from_user.id in config.admin_ids,
            provider=provider,
            parser=BarsAPI(provider, cookie) if provider and cookie else None,
        )

        return await handler(event, data)
