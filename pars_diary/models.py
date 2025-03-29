"""Определение структур данных."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class User:
    """Пользователь."""

    cookie: str | None = None
    notify: bool = False
    smart_notify: bool = False
    notify_marks: list[str] | None = None


@dataclass
class Homework:
    """Домашнее задание."""

    discipline: str
    homework: str = ""


@dataclass
class DayHomework:
    """Домашнее задание на день."""

    date: date
    homeworks: list[Homework] = field(default_factory=list)


@dataclass
class WeekHomework:
    """Домашнее задание на неделю."""

    days: list[DayHomework] = field(default_factory=list)
