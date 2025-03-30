"""Модуль отвечающий за парсинг."""

import functools
import operator
from dataclasses import dataclass, field
from datetime import date, datetime
from urllib.parse import quote

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pars_diary.config import TIMEZONE
from pars_diary.services import demo
from pars_diary.services.ask_gpt import ask_gpt
from pars_diary.utils.pars import minify_lesson_title, request

SPACES_AFTER_SUBJECT = 10

DAYS = [
    "понедельник",
    "вторник",
    "среду",
    "четверг",
    "пятницу",
    "субботу",
    "воскресенье",
]

DAYS_SHORT = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

_WEEKDAYS_BUTTON = (
    InlineKeyboardButton(text="Дни недели", callback_data="hw_days"),
)


# Определение донных домашнего задания
# ====================================


@dataclass(frozen=True, slots=True)
class HomeworkItem:
    """Домашнее задание."""

    discipline: str
    homework: str = ""


@dataclass(frozen=True, slots=True)
class DayHomework:
    """Домашнее задание на день."""

    date: date
    homeworks: list[HomeworkItem] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class WeekHomework:
    """Домашнее задание на неделю."""

    days: list[DayHomework] = field(default_factory=list)


def _construct_homework(raw_data: list[dict]) -> WeekHomework:
    return WeekHomework(
        DayHomework(
            date=datetime.strptime(day_data["date"], "%Y-%m-%d").date(),  # noqa: DTZ007
            homeworks=[
                Homework(
                    discipline=hw["discipline"],
                    homework=hw["homework"],
                )
                for hw in day_data["homeworks"]
            ],
        )
        for day_data in raw_data[:6]
    )


# Вспомогательные функции
# =======================


def get_hw(
    raw_data: list[dict],
) -> tuple[list[str], list[list[InlineKeyboardButton]]]:
    """Функция для получения Д/З по дню недели."""
    inline_keyboards = []
    result = []

    for d_i, day_hw in enumerate(_construct_homework(raw_data).days):
        date_str = day_hw.date.strftime("%d.%m.%Y")
        msg_text = f"Д/З на {date_str} {DAYS[d_i]}\n\n"
        inline_keyboard = []

        if day_hw.homeworks:
            for hw_i, hw in enumerate(day_hw.homeworks):
                subject = minify_lesson_title(hw.discipline)
                subject = subject.ljust(SPACES_AFTER_SUBJECT)
                msg_text += f"{hw_i + 1}. {subject} │ {hw.homework}\n"

                if hw.homework:
                    link = quote(f"ГДЗ {hw.discipline}: {hw.homework}")
                    inline_keyboard.append(
                        [
                            InlineKeyboardButton(
                                text=f"{DAYS_SHORT[d_i]} {subject.strip()}",
                                callback_data="None",
                            ),
                            InlineKeyboardButton(
                                text="chatgpt",
                                callback_data=f"chatgpt_{d_i}_{hw_i}",
                            ),
                            InlineKeyboardButton(
                                text="google",
                                url=f"https://www.google.com/search?q={link}",
                            ),
                        ],
                    )
        else:
            msg_text += "На этот день не указано д/з"

        result.append(msg_text)
        inline_keyboards.append(inline_keyboard)

    return result, inline_keyboards


async def chatgpt(user_id: int, day: int, index: int, first_name: str) -> str:
    """Функция для формирования запроса к GPT."""
    url = "/api/HomeworkService/GetHomeworkFromRange"
    data = request(url, user_id)
    day_hw = data[day]["homeworks"]
    description = day_hw[index]["homework"]
    subject_name = day_hw[index]["discipline"]

    return await ask_gpt(
        f"Помоги мне с решением задания по {subject_name}: {description}",
        first_name,
    )


def _get_normalized_date() -> date:
    # Подбираем следующий понедельник (специфика апи)
    now_date = datetime.now(tz=TIMEZONE)

    if now_date.weekday() == 6:  # noqa: PLR2004
        now_date += datetime.timedelta(days=1)

    while now_date.weekday() != 0:
        now_date -= datetime.timedelta(days=1)

    return now_date.date()


# Основные функции
# ================


@dataclass(frozen=True)
class HomeworkResult:
    """Результат получения домашнего задания."""

    message: str
    markup: InlineKeyboardMarkup


class Homework:
    """Домашние задания."""

    def __init__(self, user_id: int, demo_mode: bool | None = False) -> None:
        self.user_id = user_id

        # TODO @milinuri: Тут бы глобальные функции сделать
        # TODO @milinuri: Подключить к общей БД пользователя
        if demo_mode:
            self.homework = demo.hw()
        else:
            self.homework_data = request(
                f"/api/HomeworkService/GetHomeworkFromRange?date={_get_normalized_date()}",
                self.user_id,
            )
            self.homework = get_hw(self.homework_data)

    def _to_result(
        self, message: str, markup: list[list[InlineKeyboardButton]]
    ) -> HomeworkResult:
        markup.append([_WEEKDAYS_BUTTON])
        return HomeworkResult(
            message=(
                f"<pre>{message}</pre>\n\n"
                "<b>Д/З МОЖЕТ БЫТЬ НЕ АКТУАЛЬНЫМ!!!</b>"
                "\n\nЕго указывают (зачастую не указывают) учителя. "
                "Мы никак не можем повлиять на этот процесс."
                "\n\n<b>Для получения актуального Д/З попросите вашего учителя "
                "указывать его в дневнике)</b>"
            ),
            markup=InlineKeyboardMarkup(inline_keyboard=markup),
        )

    # Методы получения домашнего задания
    # ==================================

    def on_day(self, day: int) -> HomeworkResult:
        """Получает домашнее задание на определённый день недели.

        День нужно указывать в диапазоне от 0 до 5.
        """
        markup = self.homework[1][day]
        markup.append(
            [
                InlineKeyboardButton(
                    text="На завтра", callback_data="hw_tomorrow"
                ),
                InlineKeyboardButton(text="На неделю", callback_data="hw_week"),
            ],
        )
        return self._to_result(self.homework[0][day], markup)

    def tomorrow(self) -> HomeworkResult:
        """Получает домашнее задние на неделю."""
        day = (
            datetime.now(tz=datetime.UTC) + datetime.timedelta(days=1)
        ).weekday()

        if day == 6:  # noqa: PLR2004
            day = 0

        markup = self.homework[1][day]
        markup.append(
            [
                InlineKeyboardButton(text="На неделю", callback_data="hw_w"),
            ],
        )
        return self._to_result(self.homework[0][day], markup)

    def week(self) -> HomeworkResult:
        """Получает домашнее задание на всю неделю."""
        markup = functools.reduce(operator.iadd, self.homework[1], [])
        markup.append(
            [
                InlineKeyboardButton(text="На завтра", callback_data="hw_t"),
            ],
        )
        return self._to_result("\n\n".join(self.homework[0]), markup)
