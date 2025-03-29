from dataclasses import dataclass, field
from datetime import date

@dataclass
class User:
    cookie: str | None = None 
    notify: bool = False
    smart_notify: bool = False
    notify_marks: list[str] | None = None

@dataclass
class Homework:
    discipline: str
    homework: str = ""

@dataclass 
class DayHomework:
    date: date 
    homeworks: list[Homework] = field(default_factory=list)

@dataclass
class WeekHomework:
    days: list[DayHomework] = field(default_factory=list)
