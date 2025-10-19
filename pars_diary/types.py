"""Models."""

from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass
class Homework:
    discipline: str
    homework: str = ""


@dataclass
class DayHomework:
    date: str
    homeworks: list[Homework] = field(default_factory=list)


@dataclass
class WeekHomework:
    days: list[DayHomework] = field(default_factory=list)
