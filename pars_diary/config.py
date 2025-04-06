"""Глобальные настройки бота."""

from pathlib import Path
from zoneinfo import ZoneInfo

from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings

from pars_diary.parser.db import UsersDataBase
from pars_diary.parser.parser import DiaryParser
from pars_diary.services.metrics import MetricsDatabase

USERS_DB_FILE = "users.json"
METRICS_DB_FILE = "metrics.json"

class Config(BaseSettings):
    """Глобальные настройки бота.

    Подгружаются один раз при запуске бота из .env файла.

    - tg_token: От какого бота будут происходить действия.
    - admins_tg: Список ID администраторов бота.
    - git_url: Ссылка на репозиторий с исходным кодом проекта.
    - hf_token: Токен для Hugging Face LLM модели.
    """

    tg_token: str
    admins_tg: int
    hf_token: str
    git_url: str
    demo_mode: bool

config: Config = Config(_env_file=".env")
users_db = UsersDataBase(Path(USERS_DB_FILE))
metrics = MetricsDatabase(Path(METRICS_DB_FILE), users_db)
parser = DiaryParser()

# Настройки часового пояса
TIMEZONE = ZoneInfo("Europe/Moscow")

# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")
