"""Типизация."""

from dataclasses import dataclass

from pydantic import SecretStr


@dataclass
class User:
    """Пользователь бота."""

    cookie: SecretStr
    notify: bool
    smart_notify: bool
    notify_marks: list[str]
    provider: str
