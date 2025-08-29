"""Глобальные настройки бота."""

from __future__ import annotations

from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings

from .utils.pars import Parser

TIMEZONE = ZoneInfo("Europe/Moscow")


class Config(BaseSettings):
    """Глобальные настройки бота.

    Подгружаются один раз при запуске бота из .env файла.

    - bot_token: От какого бота будут происходить действия.
    - admin_ids: Список ID администраторов бота.
    """

    bot_token: str
    admin_ids: str

config: Config = Config(_env_file=".env")
config.admin_ids: list[int] = [int(i) for i in config.admin_ids.split(",")]

parser = Parser()

# Инициализируем бот
bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode="html"))
