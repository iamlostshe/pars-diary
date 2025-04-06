"""Модуль отслеживания статистики использования бота."""

import json
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import matplotlib.pyplot as plt

from pars_diary.parser import exceptions
from pars_diary.parser.db import UsersDataBase

MetricData: TypeAlias = dict[str, dict[str, list[int]]]


@dataclass(frozen=True, slots=True)
class UserStats:
    """Статистика базы данных."""

    users: int
    cookie: int
    notify: int
    smart_notify: int


class MetricsDatabase:
    """Сохраняет данные об использовании бота."""

    def __init__(self, db_path: Path, users_db: UsersDataBase) -> None:
        self.db_path = db_path
        self.users_db = users_db
        self._file_data: MetricData | None = None

    @property
    def data(self) -> MetricData:
        """Загружает сырые данные из файла."""
        if not self.db_path.exists():
            with self.db_path.open("w", encoding="utf-8") as f:
                f.write("{}\n")
                self.write()

        with self.db_path.open(encoding="utf-8") as f:
            self._file_data = json.loads(f.read())

        return self._file_data

    def write(self) -> None:
        """Записывает изменения в файл."""
        with self.db_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self._file_data, ensure_ascii=False))

    def use_command(self, user_id: int, command: str) -> None:
        """Записывает в метрику что пользователем была выполнена команда."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        try:
            user_data[command].append(int(time.time()))
        except KeyError:
            user_data[command] = [int(time.time())]

        if self._file_data is None:
            raise exceptions.DatabaseError(str(self.db_path)) from None

        self._file_data[str(user_id)] = user_data
        self.write()

    def count_commands(self) -> Counter[str]:
        """Подсчитывается использованные пользователями команды."""
        counter: Counter[str] = Counter()
        for u in self.data.values():
            for cmd, usage_times in u.items():
                counter[cmd] += len(usage_times)
        return counter

    def save_graph(self) -> None:
        """Генерирует график для анализа прироста пользователей."""
        times = [user.reg_time for _, user in self.users_db]
        users = list(range(len(self.users_db.data)))
        plt.plot(times, users)
        plt.ylabel("Пользователи")
        plt.xlabel("Время входа")
        plt.title("График времени входа пользователей")
        plt.savefig("stat_img.png")

    def get_ref_stats(self) -> str:
        """Расписывает откуда приходит аудитория."""
        ref_cnt: Counter[str | None] = Counter()
        for _, u in self.users_db:
            ref_cnt[u.ref_code] += 1

        res = ""
        for k, v in sorted(ref_cnt.items(), key=lambda x: x[1], reverse=True):
            res += f"\n-- {k}: {v}"
        res += f"\n\nБез приглашения: {ref_cnt.get(None)}"
        return res

    def get_db_stats(self) -> UserStats:
        """Собирает информацию о базе данных пользователей."""
        users = len(self.users_db.data)
        cookie = 0
        notify = 0
        smart_notify = 0

        for _, u in self.users_db:
            if u.cookie is not None:
                cookie += 1
            if u.notify:
                notify += 1
            if u.smart_notify:
                smart_notify += 1

        return UserStats(users, cookie, notify, smart_notify)
