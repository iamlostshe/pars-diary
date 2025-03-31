"""Модуль отслеживания статистики использования бота."""

import json
import time
from collections import Counter
from pathlib import Path
from typing import TypeAlias

from loguru import logger

from pars_diary.parser import exceptions

MetricData: TypeAlias = dict[str, dict[str, list[int]]]


class MetricsDatabase:
    """Сохраняет данные об использовании бота."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._file_data: MetricData | None = None

    @property
    def data(self) -> MetricData:
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
            f.write(json.dumps(self._file_data, ensure_ascii=False))

    def use_command(self, user_id: int, command: str) -> None:
        """Записывает в метрику что пользователем была выполнена команда."""
        user_data = self.data.get(str(user_id))
        if user_data is None:
            raise exceptions.UserNotFoundError from None

        try:
            user_data[command].append(time.time())
        except KeyError:
            user_data[command] = [time.time()]

        self._file_data[str(user_id)] = user_data
        self._write()

    def count_commands(self) -> Counter[str]:
        """Подсчитывается использованные пользователями команды."""
        counter = Counter()

        for u in self.data.values():
            for cmd, usage_times in u:
                counter[cmd] += len(usage_times)

        return counter
