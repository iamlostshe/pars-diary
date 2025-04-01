"""Модуль работы с базой данных пользователей.

TODO @milinuri: Когда-нибудь надо переписать под бд. Вот прям бд.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from pars_diary.parser import exceptions
from pars_diary.utils.pars import check_cookie

DB_NAME = Path("users.json")

# Данные пользователя
# ===================


@dataclass(frozen=True, slots=True)
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
        self._file_data: dict[str, dict] | None = None

    @property
    def data(self) -> dict[str, dict]:
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

    def _write(self) -> None:
        """Записывает изменения в файл."""
        with self.db_file.open("w") as f:
            f.write(json.dumps(self._file_data))

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
                "notify_marks": [],
                "server_name": None,
            }
        else:
            self._file_data[str(user_id)] = int(time.time())

        self._write()

    def get_server_name(self, user_id: int) -> str:
        """Получает имя сервера пользователя, если было установлено."""
        try:
            return self.data[str(user_id)]["server_name"]
        except KeyError as e:
            raise exceptions.UserNotAuthorizedError from e

    def set_server_name(self, user_id: int, server_name: str) -> None:
        """Устанавливает сервер для пользователя."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        self._file_data[str(user_id)]["server_name"] = server_name
        self._write()

    def set_cookie(self, user_id: int, cookie: str) -> str:
        """Устанавливает печенье для пользователя.

        Возвращает сообщение с результатом добавления печеньки.
        """
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        server_name = user_data.get("server_name")
        res, message = check_cookie(cookie, server_name)

        if res:
            self._file_data[(str(user_id))]["cookie"] = cookie
            self._write()

        return message

    def get_cookie(self, user_id: int) -> str | None:
        """Получает печенье пользователя, если было установлено."""
        try:
            return self.data[str(user_id)].get("cookie")
        except KeyError as e:
            raise exceptions.UserNotAuthorizedError from e

    def get_notify(self, user_id: int) -> NotifyStatus:
        """Получает статус уведомлений пользователя."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        return NotifyStatus(
            notify=user_data.get("notify"), smart=user_data.get("smart")
        )

    def set_notify(self, user_id: int, status: NotifyStatus) -> NotifyStatus:
        """Обновляет статус уведомлений пользователя."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        self._file_data[str(user_id)]["notify"] = status.notify
        self._file_data[str(user_id)]["smart"] = status.smart
        self._write()

        return status

    def get_marks(self, user_id: str | int) -> list[str]:
        """Возвращает оценки из базы данных (Если они прежде были записаны)."""
        try:
            return self.data[str(user_id)].get("notify_marks")
        except KeyError as e:
            raise exceptions.UserNotAuthorizedError from e

    def set_marks(self, user_id: int, marks: list[str]) -> str:
        """Устанавливает новые оценки пользователя."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        self._file_data[(str(user_id))]["cookie"] = marks
        self._write()
