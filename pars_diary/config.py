"""Глобальные настройки бота."""

from __future__ import annotations

from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from cait_api import CAITParser
from g4f.client import AsyncClient
from pydantic_settings import BaseSettings

from pars_diary.utils.db import check_db

TIMEZONE = ZoneInfo("Europe/Moscow")


class Config(BaseSettings):
    """Глобальные настройки бота.

    Подгружаются один раз при запуске бота из .env файла.

    - bot_token: От имени какого бота будут происходить действия.
    - admin_ids: Список ID администраторов бота.
    """

    bot_token: str
    admin_ids: str


config: Config = Config(_env_file=".env")
config.admin_ids: list[int] = [int(i) for i in config.admin_ids.split(",")]

# Инициализируем бота
bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode="html"))

# Проверяем наличае базы данных
# TODO(): Перейти на postgreSQL
check_db()

# Инициализируем парсер разговоров о важном
cait_parser = CAITParser()

gpt_client = AsyncClient()
