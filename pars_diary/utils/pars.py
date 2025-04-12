"""Модуль для парсинга."""

from __future__ import annotations

import datetime as dt
import json
import re

import requests
from loguru import logger

from . import demo_data
from .exceptions import (
    MyTimeoutError,
    UnexpectedStatusCodeError,
    UserNotAuthenticatedError,
    ValidationError,
)

# Ссылка на страницу со ссылками на все сервера дневников в разных регионах
AGGREGATOR_URL = "http://aggregator-obr.bars-open.ru/my_diary"

# Регулярное выражение для удаления тегов <span>
SPAN_CLEANER = r"<span[^>]*>(.*?)</span>"

# Маркеры, в зависимости от балла
COLOR_MARKERS = "🟥🟥🟥🟧🟨🟩"

# Оценка, из строки в дробное число
MARK_STR_TO_FLOAT = {
    "5-": 4.5,
    "4+": 4.5,
    "4-": 3.5,
    "3+": 3.5,
    "3-": 2.5,
    "2+": 2.5,
}

# Сокращённые названия некоторых уроков
MINIFY_LESSON_TITLE = {
    "Иностранный язык (английский)": "Англ. Яз.",
    "Иностранный язык: английский": "Англ. Яз.",
    "Изобразительное искусство": "ИЗО",
    "Физическая культура": "Физ-ра",
    "Литература": "Литер.",
    "Технология": "Техн.",
    "Труд (технология)": "Техн.",
    "Информатика": "Информ.",
    "Обществознание": "Обществ.",
    "Русский язык": "Рус. Яз.",
    "Математика": "Матем.",
    "Основы безопасности и защиты Родины": "ОБЗР",
    "Вероятность и статистика": "Теор. Вер.",
    "Индивидуальный проект": "Инд. пр.",
    'Факультатив "Функциональная грамотность"': "Функ. Гр.",
    'Факультатив "Основы 1С Предприятие"': "Фак. 1С",
}

# Вспомогательные функции
def get_regions() -> dict:
    """Получаем все доступные регионы."""
    r = requests.get(AGGREGATOR_URL, timeout=20)

    # Проверяем какой статус-код вернул сервер
    if r.status_code != 200:
        raise UnexpectedStatusCodeError(r.status_code)

    data = r.json()
    result = {}

    if data.get("success") and data.get("data"):
        for region in r.json()["data"]:
            name = region.get("name")
            url = region.get("url")
            if name and url:
                if url[-1] == "/":
                    url = url[:-1]
                result[name] = url
            else:
                # TODO @iamlostshe: Сделать специальное исключение
                raise UnexpectedStatusCodeError(data.get("success"))
        return result
    # TODO @iamlostshe: Сделать специальное исключение
    raise UnexpectedStatusCodeError(data.get("success"))


def request(
        url: str,
        user_id: str | int,
    ) -> dict | str:
    """Функция для осуществеления запроса по id пользователя и url."""
    from . import db

    try:
        # Получаем cookie из json базы данных
        cookie = db.get_cookie(user_id)

        if cookie in ["demo", "демо"]:
            return "demo"

        # Получаем server_name из бд
        server_name = db.get_server_name(user_id)

        # Преобразуем url
        url = server_name + url

        # Отпраляем запрос
        headers = {"cookie": cookie}
        r = requests.post(url, headers=headers, timeout=20)

        # Проверяем ответ сервера на наличае ошибок в ответе
        if "Server.UserNotAuthenticatedError" in r.text:
            raise UserNotAuthenticatedError

        if "Client.ValidationError" in r.text:
            raise ValidationError

        # Проверяем какой статус-код вернул сервер
        if r.status_code != 200:
            raise UnexpectedStatusCodeError(r.status_code)

        # Если нет ошибок
        # Фильруем ответ
        text = re.sub(SPAN_CLEANER, r"\1", r.text.replace("\u200b", ""))

        # Преобразуем в json
        data = json.loads(text)

        # Выводим лог в консоль
        logger.debug(data)

    except requests.exceptions.Timeout as e:
        raise MyTimeoutError from e

    else:
        return data


def check_cookie(cookie: str, server_name: str | None = None) -> tuple[bool, str]:
    """Функция для проверки cookie."""
    # Если используется демоверсия
    if cookie in ["demo", "демо"]:
        return True, (
            "Пользователь успешно добавлен в базу данных, однако учтите, что "
            "демонстрационный режим открывает не все функции, для "
            "вас будут недоступны уведомления."
        )

    # Простые тесты
    if "sessionid=" not in cookie:
        return False, 'Ваши cookie должны содержать "sessionid="'
    if "sessionid=xxx..." in cookie:
        return False, "Нельзя использовать пример"
    if not server_name:
        return False, "Укажите ваш регион -> /start"

    # Тест путем запроса к серверу
    headers = {"cookie": cookie}
    r = requests.get(
        f"{server_name}/api/ProfileService/GetPersonData",
        headers=headers,
        timeout=20,
    )

    logger.debug(r.json())

    if r.status_code == 200:
        return True, "Пользователь успешно добавлен в базу данных."
    return False, (
        "Не правильно введены cookie, возможно они "
        f"устарели (сервер выдает неверный ответ - {r.status_code})"
    )


def get_space_len(child: str, parent: dict) -> int:
    """Возвращает кол-во симовлов, для отступов."""
    try:
        return max(len(MINIFY_LESSON_TITLE.get(
            s[child], s[child],
        )) for s in parent) + 1
    except ValueError:
        return 0


# Класс с основными функциями
class Pars:
    """Парсинг."""

    def me(self, user_id: str | int) -> str:
        """Информация о пользователе."""
        url = "/api/ProfileService/GetPersonData"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.me()

        if not data.get("children_persons"):
            # Logged in on children account
            sex = "Мужской" if data["user_is_male"] else "Женский"

            return (
                f"ФИО - {data['user_fullname']}\n"
                f"Пол - {sex}\n"
                f"Школа - {data['selected_pupil_school']}\n"
                f"Класс - {data['selected_pupil_classyear']}"
            )

        # Logged in on parent account
        msg_text = ""

        # Parent data
        msg_text += f"ФИО (родителя) - {data['user_fullname']}\n"

        # Номера может и не быть
        number = data.get("phone")

        if number:
            msg_text += f"Номер телефона - {number}"

        for n, i in enumerate(data["children_persons"]):
            name = " ".join(i["fullname"].split()[:-1])
            dr = i["fullname"].split()[-1]
            school = i["school"]
            classyear = i["classyear"]

            msg_text += (
                f"\n\n{n + 1} ребенок:\n\n"
                f"ФИО - {name}\nДата рождения - {dr}\n"
                f"Школа - {school}\nКласс - {classyear}"
            )

        return msg_text

    def events(self, user_id: str | int) -> str:
        """Информация о ивентах."""
        url = "/api/WidgetService/getEvents"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.events()

        if not data:
            return "Кажется, ивентов не намечается)"

        return f"{data}"

    def birthdays(self, user_id: str | int) -> str:
        """Информация о днях рождения."""
        url = "/api/WidgetService/getBirthdays"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.birthdays()

        if not data:
            return "Кажется, дней рождений не намечается)"

        return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"

    def marks(self, user_id: str | int) -> str:
        """Информация об оценках."""
        url = f"/api/MarkService/GetSummaryMarks?date={dt.datetime.now().date()}"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.marks()

        if not data.get("discipline_marks"):
            return (
                "Информация об оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        msg_text = ""
        for_midle_marks = []

        space_len = get_space_len("discipline", data["discipline_marks"])

        for subject in data["discipline_marks"]:
            # Получаем название предмета
            g = MINIFY_LESSON_TITLE.get(
                subject["discipline"], subject["discipline"],
            ).ljust(space_len)

            # Получаем список оценок по предмету
            marks = []
            str_marks = []

            for m in subject["marks"]:
                mm = m["mark"]
                str_marks.append(mm)
                try:
                    marks.append(float(mm))
                except ValueError:
                    marks.append(MARK_STR_TO_FLOAT[mm])

            # Получаем правильные (рассчитанные) средние быллы по предметам,
            # потому что сервер иногда возвращает нули.
            len_marks = len(marks)
            average_mark = f"{sum(marks) / len_marks:.2f}" if len_marks else "0.00"
            float_average_mark = float(average_mark)

            # Добавляем средний балл по предмету в список
            # для рассчёта общего среднего балла
            for_midle_marks.append(float_average_mark)

            # Определяем цвет маркера, в зависимости от балла
            color_mark = COLOR_MARKERS[round(float_average_mark)]

            # Формируем сообщение
            msg_text += (
                f"{color_mark} {g}│ {average_mark} │ "
                f"{' '.join(str_marks)}\n"
            )

        msg_text += (
            "\nОбщий средний балл (рассичитан): "
            f"{sum(for_midle_marks) / len(for_midle_marks):.2f}"
        )

        return f"Оценки:\n\n<pre>{msg_text}</pre>"

    def i_marks(self, user_id: str | int) -> str:
        """Информация об итоговых оценках."""
        url = "/api/MarkService/GetTotalMarks"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.i_marks()

        if not data.get("discipline_marks"):
            return (
                "Информация об итоговых оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        subperiods = {i["code"]:i["name"] for i in data["subperiods"]}

        subperiods_names = list(subperiods.values())
        len_subperiods_names = len(subperiods_names)

        subperiods_names_first_letter = [i[0] for i in subperiods_names]

        explanation = [
            f"{subperiods_names_first_letter[i]} - {subperiods_names[i]}"\
            for i, _ in enumerate(subperiods_names)
        ]

        msg_text = (
            f'Итоговые оценки:\n\n{"\n".join(explanation)}\n\n<pre>\n'
            f'Предмет    │ {" | ".join(subperiods_names_first_letter)} |\n'
            f'───────────┼{("───┼" * len_subperiods_names)[:-1]}┤\n'
        )

        subperiod_index = list(subperiods.keys())
        space_len = get_space_len("discipline", data["discipline_marks"])

        for discipline in data["discipline_marks"]:
            stroka = list("-" * len_subperiods_names)
            g = MINIFY_LESSON_TITLE.get(
                discipline["discipline"], discipline["discipline"],
            ).ljust(space_len)

            msg_text += f"{g} │ "

            for period_mark in discipline["period_marks"]:
                # Получаем индекс и присваиваем значение
                if period_mark["subperiod_code"] in subperiod_index:
                    stroka[subperiod_index.index(period_mark["subperiod_code"])] = (
                        period_mark["mark"]
                    )

            msg_text += f"{' │ '.join(stroka)}"

            msg_text += " │\n"

        return f"{msg_text}</pre>"
