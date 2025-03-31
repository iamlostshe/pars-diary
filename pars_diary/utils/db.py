"""Класс для работы с json базой данных."""

import json
import time
from collections import Counter
from pathlib import Path
from typing import Self

import matplotlib.pyplot as plt

from pars_diary.parser.exceptions import (
    DBFileNotFoundError,
    DiaryParserError,
    UserNotAuthorizedError,
    UserNotFoundError,
)
from pars_diary.utils.pars import check_cookie

DB_NAME = Path("users.json")
GRAPH_NAME = Path("stat_img.png")


def check_db() -> None:
    """Проверяет наличие базы данных."""
    if not Path.is_file(Path(DB_NAME)):
        # and creating if it does not exist
        with Path.open(DB_NAME, "a+", encoding="UTF-8") as f:
            f.write("{}\n")


def add_user(user_id: int | str, refer: str) -> None | dict:
    """Добавляет пользователя в json базу данных."""
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
                    "refer": refer,
                    "cookie": None,
                    "notify": True,
                    "smart_notify": True,
                    "notify_marks": [],
                }
            # Если пользователь уже есть в json базе данных
            else:
                data[user_id]["start"].append(time.time())

            # Сохраняем изменения в json базе данных
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise DiaryParserError(str(e)) from e


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
        raise DiaryParserError(str(e)) from e


def add_user_cookie(user_id: int | str, cookie: str) -> str:
    """Добавляет пользователю cookie в json базе данных."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения и записи
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Проверяем есть ли пользователь в базе дланных
            user = data[user_id]
            if not user:
                raise UserNotFoundError()

            # Получаем server_name
            server_name = user.get("server_name")

            # Проверяем cookie пользователя
            c_c = check_cookie(cookie, server_name)
            if c_c[0]:
                # Записываем cookie в базу данных
                user["cookie"] = cookie

                # Сохраняем изменения в json базе данных
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4, ensure_ascii=False)

        # В любом случае возвращаем ответ
        return c_c[1]

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise DiaryParserError(str(e)) from e


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
        raise UserNotAuthorizedError from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise DiaryParserError(str(e)) from e


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
        raise DiaryParserError(str(e)) from e


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
                data[user_id]["smart_notify"] = not data[user_id][
                    "smart_notify"
                ]
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
        raise DiaryParserError(str(e)) from e


# TODO @milinuri: Ты будешь переписана, хы-хы.
def get_graph() -> None:
    """Генерирует график для анализа прироста пользователей."""
    try:
        with Path.open(DB_NAME, "r", encoding="UTF-8") as file:
            data = json.load(file)

        times = []
        users = list(range(len(data)))

        for user in data:
            start = str(data[user]["start"][0])
            times.append(int(start.split(".")[0]))

        plt.plot(times, users)
        plt.ylabel("Пользователи")
        plt.xlabel("Время входа")
        plt.title("График времени входа пользователей")
        plt.savefig(GRAPH_NAME)

    # Обработчики ошибок
    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise DiaryParserError(str(e)) from e


class GetStat:
    """Возвращает статистику для (сис-) админов."""

    def __init__(self: Self) -> tuple[int, str]:
        """Возвращает статистику для (сис-) админов."""
        # Инициализируем переменные для хранения статистики
        self.refer = []
        self.cookie = 0

        self.notify = 0
        self.smart_notify = 0

        try:
            with Path.open(DB_NAME, "r", encoding="UTF-8") as f:
                data = json.load(f)

            self.users_count = len(data)

            for u in data.values():
                self.refer.append(u.get("refer"))
                self.cookie += int(bool(u.get("cookie")))
                self.notify += int(u.get("notify"))
                self.smart_notify += int(u.get("smart_notify"))

        # Обработчики ошибок
        except FileNotFoundError as e:
            raise DBFileNotFoundError(DB_NAME) from e

        except Exception as e:
            raise DiaryParserError(str(e)) from e

    def str_refer(self: Self) -> str:
        """Создаёт строковое представление источников прихода аудитории."""
        # Создаем Counter для подсчета вхождений каждого элемента
        count_dict = Counter(item for item in self.refer if item is not None)

        # Создаем список кортежей из словаря и сортируем его по убыванию
        sorted_items = sorted(
            count_dict.items(), key=lambda x: x[1], reverse=True
        )

        # Формируем строку результата
        result = "\n".join(f"{item} - {count}" for item, count in sorted_items)

        # Добавляем количество None в конце
        result += f"\n\nБез указания реферала - {self.refer.count(None)}"

        # Возвращаем результат в виде строки
        return result


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
        raise DiaryParserError(str(e)) from e


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
        raise DiaryParserError(str(e)) from e
