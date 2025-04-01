"""Модуль работы с базой данных пользователей.

TODO @milinuri: Когда-нибудь надо переписать под бд. Вот прям бд.
"""

import json
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from loguru import logger

from pars_diary.parser import exceptions
from pars_diary.utils.pars import check_cookie

DB_NAME = Path("users.json")

# Данные пользователя
# ===================


@dataclass(slots=True)
class User:
    """Данные пользователя из базы.

    Доступны только для чтения.
    Для изменения воспользуйтесь методами базы данных.
    """

    reg_time: int
    ref_code: str
    cookie: str | None
    notify: bool
    smart_notify: bool
    # TODO @milinuri: По хорошему тут должны быть маленькие объекты
    lesson_marks: list[str]
    server_name: str | None


# TODO @milinuri: С переходом на нормальную бд будет не нужен
class UserDict(TypedDict):
    """Представление пользователя в виде словаря."""

    reg_time: int
    ref_code: str
    cookie: str | None
    notify: bool
    smart_notify: bool
    lesson_marks: list[str]
    server_name: str | None


@dataclass(frozen=True, slots=True)
class NotifyStatus:
    """Статус уведомлений пользователя."""

    notify: bool
    smart: bool


# Главный класс
# =============


class UsersDataBase:
    """База данных пользователей в одном файле.

    При каждом изменении данные записываются в файл.
    """

    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file
        self._file_data: dict[str, UserDict] | None = None

    # Работа с базой данных
    # =====================

    @property
    def data(self) -> dict[str, UserDict]:
        """Загружает сырые данные из файла."""
        if self._file_data is None:
            try:
                with self.db_file.open() as f:
                    self._file_data = json.loads(f.read())
            except FileExistsError:
                logger.warning("File {} not found, creating new", self.db_file)
                with self.db_file.open("w") as f:
                    f.write("{}\n")
                self._file_data = {}

        return self._file_data

    def write(self) -> None:
        """Записывает изменения в файл."""
        with self.db_file.open("w") as f:
            f.write(json.dumps(self._file_data))

    # Сериализация и десериализация
    # =============================

    def _to_user(self, user_data: UserDict) -> User:
        return User(
            reg_time=user_data["reg_time"],
            ref_code=user_data["ref_code"],
            cookie=user_data["cookie"],
            notify=user_data["notify"],
            smart_notify=user_data["smart_notify"],
            lesson_marks=user_data["lesson_marks"],
            server_name=user_data["server_name"],
        )

    def _to_dict(self, user: User) -> UserDict:
        return {
            "reg_time": user.reg_time,
            "ref_code": user.ref_code,
            "cookie": user.cookie,
            "notify": user.notify,
            "smart_notify": user.smart_notify,
            "lesson_marks": user.lesson_marks,
            "server_name": user.server_name,
        }

    # Прямая работа с данными пользователя
    # ====================================

    def get_user(self, user_id: int) -> User:
        """получает пользователя из базы."""
        try:
            return self._to_user(self.data[str(user_id)])
        except KeyError as e:
            raise exceptions.UserNotAuthorizedError from e

    def __iter__(self) -> Iterator[tuple(str, User)]:
        """Проходится по всем пользователям из базы."""
        for k, v in self.data.items():
            yield k, self._to_user(v)

    def update_user(self, user_id: int, user: User) -> None:
        """Обновляет данные пользователя БЕЗ сохранения."""
        self._file_data[str(user_id)] = self._to_dict(user)

    def add_user(self, user_id: int, ref_code: str) -> None:
        """Добавляет нового пользователя в базу.

        Если пользователь уже существует, обновляет время регистрации.
        """
        user_data = self.data.get(str(user_id))
        if user_data is None:
            self._file_data[str(user_id)] = {
                "reg_time": int(time),
                "ref_code": ref_code,
                "cookie": None,
                "notify": True,
                "smart_notify": True,
                "lesson_marks": [],
                "server_name": None,
            }
        else:
            self._file_data[str(user_id)] = int(time.time())

        self.write()

    def get_cookie(self, user_id: int) -> str | None:
        """Получает печенье пользователя, если было установлено."""
        return self.get_user(user_id)["cookie"]

    def set_cookie(self, user_id: int, cookie: str) -> str:
        """Устанавливает печенье для пользователя.

        Возвращает сообщение с результатом добавления печеньки.
        """
        user = self.get_user(user_id)
        res, message = check_cookie(cookie, user.server_name)

        if res:
            user.cookie = cookie
            self.update_user(user_id, user)
            self.write()

        return message
