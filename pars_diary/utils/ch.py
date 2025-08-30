"""Работа с классными часами."""

from __future__ import annotations

import datetime as dt

from pars_diary.config import cait_parser


def _get_next_date(minus_week: int | None = None) -> str:
    """Получаем ссылку для парсинга."""
    if not minus_week:
        minus_week = 0

    now = dt.datetime.now()

    now += dt.timedelta(days=7 - now.weekday())
    now -= dt.timedelta(days=7 * minus_week)

    return now.strftime("%d-%m-%Y")


async def ch() -> str:
    """Информация о классных часах."""
    count = 0

    while True:
        try:
            date = _get_next_date(count)
            data = await cait_parser.get_info(date)
            break

        except NoDataForThisDayError:
            count += 1

    msg = (
        f"Данные по {'следующему' if count == 0 else 'последнему'} классному часу:\n\n"
        f"<b>{data.title}</b>\n\n"
        f"{data.date}"
    )

    return data.plakat_url, msg, f"https://xn--80aafadvc9bifbaeqg0p.xn--p1ai/{date}/"
