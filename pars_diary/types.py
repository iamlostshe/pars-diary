"""Typing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bars_api import BarsAPI


@dataclass
class User:
    """Пользователь."""

    is_auth: bool
    is_admin: bool
    provider: str | None
    parser: BarsAPI | None
