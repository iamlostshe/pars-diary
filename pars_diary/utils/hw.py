"""Модуль отвечающий за парсинг."""

import datetime
import functools
import operator
from datetime import datetime as dt
from typing import HomeworkIndex, UserId
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pars_diary.models import DayHomework, Homework, WeekHomework
from pars_diary.utils import demo_data
from pars_diary.utils.ask_gpt import ask_gpt
from pars_diary.utils.exceptions import DayIndexError
from pars_diary.utils.pars import minify_lesson_title, request

SPACES_AFTER_SUBJECT = 10

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
            date=datetime.strptime(day_data["date"], "%Y-%m-%d").date(),
            homeworks=[
                Homework(
                    discipline=hw["discipline"],
                    homework=hw["homework"],
                )
                for hw in day_data["homeworks"]
            ],
        )
        week_data.days.append(day)

    inline_keyboards = []
    result = []

    for day_index, day in enumerate(week_data.days):
        count = 1
        date_str = day.date.strftime("%d.%m.%Y")
        msg_text = f"Д/З на {date_str} {DAYS[day_index]}\n\n"
        inline_keyboard = []

        if day.homeworks:
            for hw in day.homeworks:
                subject = minify_lesson_title(hw.discipline)
                subject = subject.ljust(SPACES_AFTER_SUBJECT)
                msg_text += f"{count}. {subject} │ {hw.homework}\n"

                if hw.homework:
                    link = quote(f"ГДЗ {hw.discipline}: {hw.homework}")
                    google_url = f"https://www.google.com/search?q={link}"
                    ask_gpt_text = f"chatgpt_{day_index}_{count - 1}"

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
                count += 1
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
    elif str(index) in "0123456":
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
