"""Класс для работы с json базой данных."""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Self

import matplotlib.pyplot as plt

from pars_diary.config import parser

from .exceptions import (
    UserNotAuthorizatedError,
    UserNotFoundError,
)

GRAPH_NAME = "stat_img.png"
db_path = Path("users.json")


def check_db() -> None:
    """Проверяет наличие базы данных."""
    if not Path.is_file(db_path):
        with db_path.open("a+", encoding="UTF-8") as f:
            f.write("{}\n")


def add_user(user_id: int | str, refer: str) -> None | dict:
    """Добавляет пользователя в json базу данных."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    with db_path.open("r+", encoding="UTF-8") as f:
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


def add_user_server_name(user_id: int | str, server_name: str) -> str:
    """Добавляет пользователю cookie в json базе данных."""
    # Конвертируем id пользователя в строку
    try:
        # Открываем файл для чтения и записи
        with db_path.open("r+", encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Запись cookie в json базу данных
            data[str(user_id)]["server_name"] = server_name

            # Сохраняем изменения в json базе данных
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    except KeyError as e:
        raise UserNotFoundError from e


async def add_user_cookie(user_id: int | str, cookie: str) -> str:
    """Добавляет пользователю cookie в json базе данных."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    # Открываем файл для чтения и записи
    with db_path.open("r+", encoding="UTF-8") as f:
        # Загрузка и десериализация данных из файла
        data = json.load(f)

        # Проверяем есть ли пользователь в базе дланных
        user = data[user_id]
        if not user:
            raise UserNotFoundError

        # Проверяем cookie пользователя
        c_c = await parser.check_cookie()
        if c_c[0]:
            # Записываем cookie в базу данных
            user["cookie"] = cookie

            # Сохраняем изменения в json базе данных
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    # В любом случае возвращаем ответ
    return c_c[1]


def get_cookie(user_id: str | int) -> None | str | dict:
    """Возвращает куки из базы данных (Если они прежде были записаны)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with db_path.open(encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем cookie пользователя
            if data.get(user_id):
                return data[user_id].get("cookie")
            return None

    except KeyError as e:
        raise UserNotAuthorizatedError from e


def get_notify(user_id: str | int, index: str | None = None) -> str | dict:
    """Возвращает значение уведомлений."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with db_path.open(encoding="UTF-8") as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем notify пользователя
            if index == "s":
                return data[user_id]["smart_notify"]
            return data[user_id]["notify"]

    except KeyError as e:
        raise UserNotFoundError from e


def swith_notify(user_id: str | int, index: str | None = None) -> None | dict:
    """Меняет значение уведомлений (вкл -> выкл | выкл -> вкл)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with db_path.open("r+", encoding="UTF-8") as f:
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

    except KeyError as e:
        raise UserNotFoundError from e


async def get_graph() -> None:
    """Генерирует график для анализа прироста пользователей."""
    with db_path(encoding="UTF-8") as file:
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


async def get_marks(user_id: str | int) -> dict | str:
    """Возвращает оценки из базы данных (Если они прежде были записаны)."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    with db_path(encoding="UTF-8") as f:
        # Загрузка и десериализация данных из файла
        data = json.load(f)

        # Возвращаем оценки пользователя
        if data.get(user_id):
            return data[user_id]["notify_marks"]
        raise UserNotFoundError


def counter(user_id: str | int, counter_name: str) -> None:
    """Счётчик для аналитики."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    # Открываем файл для чтения
    with db_path.open("r+", encoding="UTF-8") as f:
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


def get_server_name(user_id: int | str) -> str:
    """Возвращает server_name по user_id."""
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    # Открываем файл для чтения
    with db_path.open(encoding="UTF-8") as f:
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


class Stat:
    """Возвращает статистику для (сис-) админов."""

    def get_stat(self: Self) -> tuple[int, str]:
        """Возвращает статистику для (сис-) админов."""
        # Инициализируем переменные для хранения статистики
        self.refer = []

        self.cookie = 0

        self.notify = 0
        self.smart_notify = 0

        self.command_about = 0
        self.command_admin = 0
        self.command_birthdays = 0
        self.command_ch = 0
        self.command_cs = 0
        self.command_events = 0
        self.command_hw = 0
        self.command_i_marks = 0
        self.command_marks = 0
        self.command_me = 0
        self.command_new = 0
        self.command_notify_settings = 0
        self.command_start = 0

        with db_path.open(encoding="UTF-8") as f:
            data = json.load(f)

        self.users_count = len(data)

        for u in data:
            data_u = data[u]

            self.refer.append(data_u.get("refer"))

            self.cookie += int(bool(data_u.get("cookie")))

            self.notify += int(data_u.get("notify"))
            self.smart_notify += int(data_u.get("smart_notify"))

            self.command_about += len(data_u.get("about", []))
            self.command_admin += len(data_u.get("admin", []))
            self.command_birthdays += len(data_u.get("birthdays", []))
            self.command_ch += len(data_u.get("ch", []))
            self.command_cs += len(data_u.get("cs", []))
            self.command_events += len(data_u.get("events", []))
            self.command_hw += len(data_u.get("hw", []))
            self.command_i_marks += len(data_u.get("i_marks", []))
            self.command_marks += len(data_u.get("marks", []))
            self.command_me += len(data_u.get("me", []))
            self.command_new += len(data_u.get("new", []))
            self.command_notify_settings += len(data_u.get("notify-settings", []))
            self.command_start += len(data_u.get("start", []))

    def str_refer(self: Self) -> str:
        """Создаёт строковое представление источников прихода аудитории."""
        # Создаем Counter для подсчета вхождений каждого элемента
        count_dict = Counter(item for item in self.refer if item is not None)

        # Создаем список кортежей из словаря и сортируем его по убыванию
        sorted_items = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)

        # Формируем строку результата
        result = "\n".join(f"{item} - {count}" for item, count in sorted_items)

        # Добавляем количество None в конце
        result += f"\n\nБез указания реферала - {self.refer.count(None)}"

        # Возвращаем результат в виде строки
        return result
