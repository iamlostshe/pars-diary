"""Работа с классными часами."""

import datetime as dt
from dataclasses import dataclass

from conversations_about_important_api import CAIParser
from conversations_about_important_api.pars import NoDataForThisDayError

from pars_diary.config import TIMEZONE

# Вспомогательные функции
# =======================


def _get_next_date(week_offset: int | None = None) -> str:
    """Получаем даты для ссылки на классный час."""
    week_offset = week_offset or 0
    now = dt.datetime.now(tz=TIMEZONE)

    # Меняем дату на следующий понедельник
    now += dt.timedelta(days=7 - now.weekday())
    now -= dt.timedelta(days=7 * week_offset)

    # Переводим дату в строку и возвращаем её
    return now.strftime("%d-%m-%Y")


@dataclass
class ClassHourData:
    """Информация о классном часе для разговоров о важном."""

    image_url: str
    description: str
    url: str


# Основная функция
# ================


def ch() -> ClassHourData:
    """Информация о классных часах."""
    # Инициализируем объект парсера
    parser = CAIParser()
    count = 0

    while True:
        try:
            date = _get_next_date(count)
            data = parser.get_info(date)
            break
        except NoDataForThisDayError:
            count += 1

    return ClassHourData(
        image_url=data.plakat_url,
        description=(
            f"Данные по {'следующему' if count == 0 else 'последнему'} классному часу:\n\n"
            f"<b>{data.title}</b>\n\n"
            f"{data.str_date}"
        ),
        url=f"https://xn--80aafadvc9bifbaeqg0p.xn--p1ai/{date}/",
    )
