"""Класс для работы с json базой данных."""

# TODO @iamlostshe: Использовать метод get для безопасного доступа к данным

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

from utils.exceptions import (
    DBFileNotFoundError,
    UnknownError,
    UserNotAuthorizatedError,
    UserNotFoundError,
)
from utils.pars import check_cookie

DB_NAME = "users.json"
GRAPH_NAME = "stat_img.png"


def check_db() -> None:
    """Проверяет наличие базы данных."""
    if not Path.is_file(Path(DB_NAME)):
        # and creating if it does not exist
        with Path.open(DB_NAME, "a+", encoding="UTF-8") as f:
            f.write("{}\n")


def add_user(user_id: int | str, refer: str) -> None | dict:
    """Добавляет пользователя в json базу данных."""
    # Получаем реферальные сведения
    refer = refer[7:].split("/n") if refer[:7] == "/start " else None

    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения и записи
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Если пользователя нет в json базе данных
            if user_id not in data:
                data[user_id] = {
                    "start": [time.time()],
                    "refer": [],
                    "cookie": None,
                    "notify": True,
                    "smart_notify": True,
                    "notify_marks": [],
                }
            # Если пользователь уже есть в json базе данных
            else:
                data[user_id]["start"].append(time.time())

            # В случае если поле refer не пусто указываем его в json бд
            if refer is not None:
                data[user_id]["refer"].append(refer)

            # Сохраняем изменения в json базе данных
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def add_user_server_name(user_id: int | str, server_name: str) -> str:
    """Добавляет пользователю cookie в json базе данных."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения и записи
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Запись cookie в json базу данных
            data[user_id]["server_name"] = server_name

            # Сохраняем изменения в json базе данных
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Обработчики ошибок
    except KeyError as e:
        raise UserNotFoundError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def add_user_cookie(user_id: int | str, cookie: str) -> str:
    """Добавляет пользователю cookie в json базе данных."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Получаем server_name из бд
        server_name = get_server_name(user_id)

        c_c = check_cookie(cookie, server_name)
        if c_c[0]:
            # Открываем файл для чтения и записи
            with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
                # Загрузка и десериализация данных из файла
                data = json.load(f)

                # Запись cookie в json базу данных
                data[user_id]["cookie"] = cookie

                # Сохраняем изменения в json базе данных
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4, ensure_ascii=False)

        # В любом случае возвращаем ответ
        return c_c[1]

    # Обработчики ошибок
    except KeyError as e:
        raise UserNotFoundError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_cookie(user_id: str | int) -> None | str | dict:
    """Возвращает куки из базы данных (Если они прежде были записаны)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем cookie пользователя
            if data.get(user_id):
                return data[user_id].get("cookie")
            return None

    # Обработчики ошибок
    except KeyError as e:
        raise UserNotAuthorizatedError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_notify(user_id: str | int, index: str | None = None) -> str | dict:
    """Возвращает значение уведомлений."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, "r", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем notify пользователя
            if index == "s":
                return data[user_id]["smart_notify"]
            return data[user_id]["notify"]

    # Обработчики ошибок
    except KeyError as e:
        raise UserNotFoundError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def swith_notify(user_id: str | int, index: str | None = None) -> None | dict:
    """Меняет значение уведомлений (вкл -> выкл | выкл -> вкл)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Меняем значение cookie пользователя на противоположное
            if index == "s":
                data[user_id]["smart_notify"] = not data[user_id]["smart_notify"]
            else:
                data[user_id]["notify"] = not data[user_id]["notify"]

            # Сохраняем изменения в json базе данных
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Возвращаем новое значение переменной
        if index == "s":
            return data[user_id]["smart_notify"]
        return data[user_id]["notify"]

    # Обработчики ошибок
    except KeyError as e:
        raise UserNotFoundError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_graph() -> None:
    """Генерирует график для анализа прироста пользователей."""
    try:
        with Path.open(DB_NAME, "r", encoding="UTF-8") as file:
            data = json.load(file)

        times = []
        users = []

        for counter, user in enumerate(data):
            times.append(int(str(data[user]["start"][0]).split(".", maxsplit=1)[0]))
            users.append(counter)

        plt.plot(times, users)
        plt.ylabel("Пользователи")
        plt.xlabel("Время входа")
        plt.title("График времени входа пользователей")
        plt.savefig(GRAPH_NAME)

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_stat() -> tuple[int, str]:
    """Возвращает статистику для (сис-) админов."""
    try:
        with Path.open(DB_NAME, "r", encoding="UTF-8") as file:
            data = json.load(file)

        refers = []

        for user in data:
            for i in data[user]["refer"]:
                refers.append(i)

        refers = "\n".join([f"{k} - {v}" for k, v in Counter(refers).items()])

        return len(data), refers

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_marks(user_id: str | int) -> dict | str:
    """Возвращает оценки из базы данных (Если они прежде были записаны)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем оценки пользователя
            if data.get(user_id):
                return data[user_id]["notify_marks"]
            raise UserNotFoundError

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def counter(user_id: str | int, counter_name: str) -> None:
    """Счётчик для аналитики."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # TODO @iamlostshe: Оптимизировать эту функцию
            # (смотри ниже для примера)

            # Работа со счётчиками
            user = data.get(user_id)
            if user:
                if user.get(counter_name):
                    user[counter_name].append(time.time())
                else:
                    user[counter_name] = [time.time()]
            else:
                raise UserNotFoundError

            # Сохраняем изменения в json базе данных
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


def get_server_name(user_id: int | str) -> str:
    """Возвращает server_name по user_id."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with Path.open(DB_NAME, "r", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем server_name
            user = data.get(user_id)

            if user:
                server_name = data[user_id].get("server_name")

                if server_name:
                    return server_name

                # TODO @iamlostshe: Сделать специальное исключение
                msg = "Не указан регион."
                raise FileNotFoundError(msg)
            raise UserNotFoundError

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e
