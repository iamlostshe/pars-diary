"""Глобальные настройки бота."""

from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings

from pars_diary.services.metrics import MetricsDatabase


class Config(BaseSettings):
    """Глобальные настройки бота.

    Подгружаются один раз при запуске бота из .env файла.

    - telegram_token: От какого бота будут происходить действия.
    - admins: Список ID администраторов бота.
    - git_url: Ссылка на репозиторий с исходным кодом проекта.
    - hf_token: Токен для Hugging Face LLM модели.
    """

    telegram_token: str
    admins: list[str]
    git_url: str
    hf_token: str
    demo_mode: bool


config: Config = Config(_env_file=".env")
metrics = MetricsDatabase(Path("metrics.json"))

# настройки часового пояса
TIMEZONE = 3

# Настройки бота по умолчанию
default = DefaultBotProperties(parse_mode="html")
