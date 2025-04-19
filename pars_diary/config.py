"""Глобальные настройки бота."""

from __future__ import annotations

from zoneinfo import ZoneInfo

from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings

from .utils.pars import Parser

# Настройки часового пояса
TIMEZONE = ZoneInfo("Europe/Moscow")

# USERS_DB_FILE = "users.json"  # noqa: ERA001
# METRICS_DB_FILE = "metrics.json"  # noqa: ERA001

class Config(BaseSettings):
    """Глобальные настройки бота.

    Подгружаются один раз при запуске бота из .env файла.

    - tg_token: От какого бота будут происходить действия.
    - admins_tg: Список ID администраторов бота.
    - git_url: Ссылка на репозиторий с исходным кодом проекта.
    - hf_token: Токен для Hugging Face LLM модели.
    """

    token_tg: str
    admins_tg: str
    git_url: str

config: Config = Config(_env_file=".env")
config.admins_tg = list(map(int, config.admins_tg.split(",")))

parser = Parser()

# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")

# TODO(@iamlostshe): Разобраться с базами данных:

# users_db = UsersDataBase(Path(USERS_DB_FILE))  # noqa: ERA001
# metrics = MetricsDatabase(Path(METRICS_DB_FILE), users_db)  # noqa: ERA001
