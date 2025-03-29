"""Работа с классными часами."""

import datetime as dt

from conversations_about_important_api import CAIParser
from conversations_about_important_api.pars import NoDataForThisDayError


# Вспомогательные функции
def get_next_date(minus_week: int | None = None) -> str:
    """Получаем ссылку для парсинга."""
    # Получаем параметр сдвига
    if not minus_week:
        minus_week = 0

    # Получаем текущую дату
    now = dt.datetime.now()

    # Меняем дату на следующий понедельник
    now += dt.timedelta(days=7 - now.weekday())

    # Учитываем сдвиг
    now -= dt.timedelta(days=7 * minus_week)

    # Переводим дату в строку и возвращаем её
    return now.strftime("%d-%m-%Y")


def ch() -> str:
    """Информация о классных часах."""
    # Инициализируем объект парсера
    parser = CAIParser()
    count = 0

    while True:
        try:
            date = get_next_date(count)
            data = parser.get_info(date)
            break

        except NoDataForThisDayError:
            count += 1

    msg = (
        f"Данные по {'следующему' if count == 0 else 'последнему'} классному часу:\n\n"
        f"<b>{data.title}</b>\n\n"
        f"{data.str_date}"
    )

    return data.plakat_url, msg, f"https://xn--80aafadvc9bifbaeqg0p.xn--p1ai/{date}/"
