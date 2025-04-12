"""Модуль отвечающий за парсинг."""

from __future__ import annotations

import datetime
import functools
import html
import operator
from datetime import datetime as dt
from typing import TYPE_CHECKING
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models import DayHomework, Homework, WeekHomework
from utils import demo_data
from utils.ask_gpt import ask_gpt
from utils.exceptions import DayIndexError
from utils.pars import MINIFY_LESSON_TITLE, request

if TYPE_CHECKING:
    from utils.typing import HomeworkIndex, UserId

DAYS = [
    "понедельник",
    "вторник",
    "среду",
    "четверг",
    "пятницу",
    "субботу",
    "воскресень",
]

DAYS_SHORT = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


# Вспомогательные функции
def get_hw(data: list[dict]) -> tuple[list[str], list[list[InlineKeyboardButton]]]:
    """Функция для получения Д/З по дню недели."""
    week_data = WeekHomework()
    for day_data in data[:6]:
        day = DayHomework(
            date=html.escape(day_data["date"]).replace("-", "."),
            homeworks=[
                Homework(
                    discipline=html.escape(hw["discipline"]),
                    homework=html.escape(hw["homework"]),
                ) for hw in day_data["homeworks"]
            ],
        )
        week_data.days.append(day)

    inline_keyboards = []
    result = []

    for day_index, day in enumerate(week_data.days):
        msg_text = f"Д/З на {day.date} {DAYS[day_index]}\n\n"
        inline_keyboard = []

        try:
            space_len = max(len(MINIFY_LESSON_TITLE.get(
                hw.discipline, hw.discipline,
            )) for hw in day.homeworks if day.homeworks) + 1
        except ValueError:
            space_len = 0

        if day.homeworks:
            for count, hw in enumerate(day.homeworks):
                subject = MINIFY_LESSON_TITLE.get(
                    hw.discipline, hw.discipline,
                ).ljust(space_len)
                msg_text += f"{count + 1}. {subject} │ {hw.homework}\n"

                if hw.homework:
                    link = quote(f"ГДЗ {hw.discipline}: {hw.homework}")
                    google_url = f"https://www.google.com/search?q={link}"
                    ask_gpt_text = f"chatgpt_{day_index}_{count}"

                    inline_keyboard.append(
                        [
                            InlineKeyboardButton(
                                text=f"{DAYS_SHORT[day_index]} {subject.strip()}",
                                callback_data="None",
                            ),
                            InlineKeyboardButton(
                                text="chatgpt",
                                callback_data=ask_gpt_text,
                            ),
                            InlineKeyboardButton(text="google", url=google_url),
                        ],
                    )
        else:
            msg_text += "На этот день не указано д/з"

        result.append(msg_text)
        inline_keyboards.append(inline_keyboard)

    return result, inline_keyboards


async def chatgpt(user_id: UserId, index: str, firstname: str) -> str:
    """Функция для формирования запроса к GPT."""
    day = int(index.split("_")[1])
    subject_num = int(index.split("_")[2])

    url = "/api/HomeworkService/GetHomeworkFromRange"
    data = request(url, user_id)

    day_hw = data[day]["homeworks"]

    hwhw = day_hw[subject_num]["homework"]
    subject_name = day_hw[subject_num]["discipline"]

    return await ask_gpt(
        f"Помоги мне с решением домашнего задания по {subject_name}: {hwhw}",
        firstname,
    )


# Основная функция
def hw(user_id: UserId, index: HomeworkIndex) -> tuple[str, InlineKeyboardMarkup] | str:
    """Функция для парсинга Д/З.

    | index | функция                         |
    | ----- | ------------------------------- |
    | t     | Д/З на завтра                   |
    | w     | Д/З на неделю                   |
    | 0-6   | Д/З на определенный день недели |
    """
    # Подбираем следующий понедельник (специфика апи)
    date = dt.now(tz=datetime.UTC)

    if date.weekday() == 6:
        date += datetime.timedelta(days=1)

    while date.weekday() != 0:
        date -= datetime.timedelta(days=1)

    # Получаем данные из api
    url = f"/api/HomeworkService/GetHomeworkFromRange?date={date.date()}"
    data = request(url, user_id)

    # Проверяем не включена ли демо-версия
    if data == "demo":
        return demo_data.hw(index)

    # Д/З на неделю
    if index == "w":
        # Получем Д/З
        homework = get_hw(data)

        msg_text = "\n\n".join(homework[0])

        inline_keyboard = functools.reduce(operator.iadd, homework[1], [])

        # Редактируем клавиатуру
        inline_keyboard.append(
            [
                InlineKeyboardButton(text="На завтра", callback_data="hw_t"),
            ],
        )

    # Д/З на завтра
    elif index == "t":
        # Задаём день недели
        day = (dt.now(tz=datetime.UTC) + datetime.timedelta(days=1)).weekday()

        if day == 6:
            day = 0

        # Получем Д/З
        homework = get_hw(data)

        msg_text = homework[0][day]
        inline_keyboard = homework[1][day]

        # Редактируем клавиатуру
        inline_keyboard.append(
            [
                InlineKeyboardButton(text="На неделю", callback_data="hw_w"),
            ],
        )

    # Д/З на определённый день недели
    elif index in range(6):
        # Получем Д/З
        homework = get_hw(data)

        msg_text = homework[0][int(index)]
        inline_keyboard = homework[1][int(index)]

        # Редактируем клавиатуру
        inline_keyboard.append(
            [
                InlineKeyboardButton(text="На завтра", callback_data="hw_t"),
                InlineKeyboardButton(text="На неделю", callback_data="hw_w"),
            ],
        )

    # Если неправильно задан день недели
    else:
        raise DayIndexError

    # Редактриуем клавиатуру
    inline_keyboard.append(
        [
            InlineKeyboardButton(text="Дни недели", callback_data="hw_days"),
        ],
    )

    # Редактируем сообщение
    msg_text = (
        f"<pre>{msg_text}</pre>\n\n<b>Д/З МОЖЕТ БЫТЬ НЕ АКТУАЛЬНЫМ!!!</b>\n\nЕ"
        "го указывают (зачастую не указывают) учителя и мы никак не можем повл"
        "иять на этот процесс.\n\n<b>Для получения актуального Д/З попросите в"
        "ашего учителя указывать его в дневнике)</b>"
    )

    # Создаём клавиатуру
    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    # Возвращаем тект сообщения и клавиатуру
    return msg_text, markup
