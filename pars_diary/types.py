"""Typing."""

from dataclasses import dataclass

from bars_api import BarsAPI


@dataclass
class User:
    """Пользователь."""

    is_auth: bool
    is_admin: bool
    parser: BarsAPI
