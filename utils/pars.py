"""Модуль для парсинга."""

from __future__ import annotations

import datetime
import json
import re

import requests
from loguru import logger

from utils import demo_data
from utils.exceptions import (
    MyTimeoutError,
    UnexpectedStatusCodeError,
    UnknownError,
    UserNotAuthenticatedError,
    ValidationError,
)

# Ссылка на страницу со ссылками на все сервера дневников в разных регионах
AGGREGATOR_URL = "http://aggregator-obr.bars-open.ru/my_diary"

# Регулярное выражение для удаления тегов <span>
SPAN_CLEANER = r"<span[^>]*>(.*?)</span>"


# Вспомогательные функции
def get_regions() -> dict:
    """Получаем все доступные регионы."""
    try:
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

    # Обработка ошибок
    except Exception as e:
        raise UnknownError(e) from e


def request(
    url: str,
    user_id: str | int | None = None,
    cookie: str | None = None,
) -> dict:
    """Функция для осуществеления запроса по id пользователя и url."""
    from utils import db

    try:
        # Получаем cookie по user_id
        if cookie is None and user_id is not None:
            # Получаем cookie из json базы данных
            cookie = db.get_cookie(user_id)

        if cookie in ["demo", "демо"]:
            return "demo", ""

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

        elif "Client.ValidationError" in r.text:
            raise ValidationError

        # Проверяем какой статус-код вернул сервер
        elif r.status_code != 200:
            raise UnexpectedStatusCodeError(r.status_code)

        # Если нет ошибок
        else:
            # Фильруем ответ
            text = re.sub(SPAN_CLEANER, r"\1", r.text.replace("\u200b", ""))

            # Преобразуем в json
            data = json.loads(text)

            # Выводим лог в консоль
            logger.debug(data)

            return data

    # На случай долгого ожидания ответа сервера (при нагрузке бывает)
    except requests.exceptions.Timeout as e:
        raise MyTimeoutError from e

    # Обработка других ошибок
    except Exception as e:
        raise UnknownError(e) from e


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


def minify_lesson_title(title: str) -> str:
    """Функция для сокращения названий уроков.

    `minify_lesson_title('Физическая культура')`
    >>> 'Физ-ра'
    """
    a = {
        "Иностранный язык (английский)": "Англ. Яз.",
        "Физическая культура": "Физ-ра",
        "Литература": "Литер.",
        "Технология": "Техн.",
        "Информатика": "Информ.",
        "Обществознание": "Обществ.",
        "Русский язык": "Рус. Яз.",
        "Математика": "Матем.",
        "Основы безопасности и защиты Родины": "ОБЗР",
        "Вероятность и статистика": "Теор. Вер.",
        "Индивидуальный проект": "Инд. пр.",
        'Факультатив "Функциональная грамотность"': "Функ. Гр.",
        'Факультатив "Основы 1С Предприятие"': "Фак. 1С",
    }.get(title)

    if a:
        return a
    return title


# Класс с основными функциями
class Pars:
    """Парсинг."""

    def me(self, user_id: str | int) -> str:
        """Информация о пользователе."""
        url = "/api/ProfileService/GetPersonData"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.me()

        if data["children_persons"] == []:
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

        for n, i in data["children_persons"]:
            name = " ".join(i["fullname"].split(" ")[0:-1])
            dr = i["fullname"].split(" ")[-1]
            school = i["school"]
            classyear = i["classyear"]

            msg_text += (
                f"\n\n{n + 1} ребенок:\n\n"
                f"ФИО - {name}\nДата рождения - {dr}\n"
                f"Школа - {school}\nКласс - {classyear}"
            )

        return msg_text

    def cs(self, user_id: str | int) -> str:
        """Информация о классных часах."""
        url = "/api/WidgetService/getClassHours"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.cs()

        if data == {}:
            return "Информация о классных часах отсутсвует"
        return (
            "КЛАССНЫЙ ЧАС\n\n"
            f"{data['date']}\n"
            f"{data['begin']}-{data['end']}\n\n"
            f"каб. {data['place']}\n"
            f"{data['theme']}\n"
        )

    def events(self, user_id: str | int) -> str:
        """Информация о ивентах."""
        url = "/api/WidgetService/getEvents"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.events()

        if str(data) == "[]":
            return "Кажется, ивентов не намечается)"
        return f"{data}"

    def birthdays(self, user_id: str | int) -> str:
        """Информация о днях рождения."""
        url = "/api/WidgetService/getBirthdays"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.birthdays()

        if str(data) == "[]":
            return "Кажется, дней рождений не намечается)"
        return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"

    def marks(self, user_id: str | int) -> str:
        """Информация об оценках."""
        url = f"/api/MarkService/GetSummaryMarks?date={datetime.now().date()}"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.marks()

        msg_text = ""
        for_midle_marks = []

        if data["discipline_marks"] == []:
            return (
                "Информация об оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        for subject in data["discipline_marks"]:
            marks = []
            g = minify_lesson_title(subject["discipline"])

            while len(g) < 10:
                g += " "

            for i in subject["marks"]:
                marks.append(i["mark"])

            if subject["average_mark"] == "":
                average_mark = "0.00"
            else:
                average_mark = subject["average_mark"]

            for_midle_marks.append(float(average_mark))

            if float(average_mark) >= 4.5:
                color_mark = "🟩"
            elif float(average_mark) >= 3.5:
                color_mark = "🟨"
            elif float(average_mark) >= 2.5:
                color_mark = "🟧"
            else:
                color_mark = "🟥"

            msg_text += f"{color_mark} {g}│ {average_mark} │ {' '.join(marks)}\n"

        msg_text += (
            "\nОбщий средний балл (рассичитан): "
            f"{sum(for_midle_marks) / len(for_midle_marks)}"
        )

        return f"Оценки:\n\n<pre>{msg_text}</pre>"

    def i_marks(self, user_id: str | int) -> str:
        """Информация об итоговых оценках."""
        url = "/api/MarkService/GetTotalMarks"
        data = request(url, user_id)

        if data == "demo":
            return demo_data.i_marks()

        msg_text = (
            "Итоговые оценки:\n\n1-4 - Четвертные оценки\nГ - Годовая\n"
            "Э - Экзаменационная (если есть)\nИ - Итоговая\n\n<pre>\n"
            "Предмет    │ 1 │ 2 │ 3 │ 4 │ Г │ Э │ И │\n"
            "───────────┼───┼───┼───┼───┼───┼───┼───┤\n"
        )

        if data["discipline_marks"] == []:
            return (
                "Информация об итоговых оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        for discipline in data["discipline_marks"]:
            stroka = ["-", "-", "-", "-", "-", "-", "-"]
            g = minify_lesson_title(discipline["discipline"])

            while len(g) < 10:
                g += " "

            msg_text += f"{g} │ "

            for period_mark in discipline["period_marks"]:
                # Словарь для сопоставления subperiod_code с индексами
                subperiod_index = {
                    "1_1": 0,  # 1 четверть
                    "1_2": 1,  # 2 четверть
                    "1_3": 2,  # 3 четверть
                    "1_4": 3,  # 4 четверть
                    "4_1": 4,  # Годовая
                    "4_2": 5,  # Экзаменационная (если есть)
                    "4_3": 6,  # Итоговая
                }

                # Получаем индекс из словаря и присваиваем значение
                if period_mark["subperiod_code"] in subperiod_index:
                    stroka[subperiod_index[period_mark["subperiod_code"]]] = (
                        period_mark["mark"]
                    )

            msg_text += f"{' │ '.join(stroka)}"

            msg_text += " │\n"

        return f"{msg_text}</pre>"
