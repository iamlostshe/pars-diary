from dataclasses import dataclass

@dataclass
class User:
    cookie: str | None = None
    notify: bool = False
    smart_notify: bool = False
    notify_marks: list[str] = None
