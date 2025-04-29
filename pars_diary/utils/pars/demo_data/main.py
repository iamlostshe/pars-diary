"""Инициализация демонстрационных данных (заглушек)."""

from pathlib import Path

from .consts import (
    DEMO_DIR,
    MODULE_NAMES,
)


def _clean_url(url: str) -> str:
    """Очищает url для работы в словаре."""
    return (url.split("?")[0].split("/")[-1])


def get_data(url: str) -> str:
    """Возвращает домнстрационные данные по url."""
    with Path(
        f"pars_diary/utils/pars/demo_data/{DEMO_DIR}/{MODULE_NAMES[_clean_url(url)]}.json",
    ).open(encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    res = get_data("https://es.ciur.ru/api/BirthdaysServices/getBirthdays?a=2991")
    print(res)
