"""Модуль для получения данных."""

import datetime as dt
import json
import re

import requests

from pars_diary.loguru import logger
from pars_diary.parser.exceptions import (
    DiaryParserError,
    ServerTimeoutError,
    UnexpectedStatusCodeError,
    UserNotAuthenticatedError,
    ValidationError,
)
from pars_diary.utils import demo_data

# Ссылка на страницу со ссылками на все сервера дневников в разных регионах
AGGREGATOR_URL = "http://aggregator-obr.bars-open.ru/my_diary"

# Регулярное выражение для удаления тегов <span>
SPAN_CLEANER = r"<span[^>]*>(.*?)</span>"

# Маркеры, в зависимости от балла
COLOR_MARKERS = ["🟥", "🟥", "🟥", "🟧", "🟨", "🟩"]


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
        raise DiaryParserError(e) from e


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

        return data

    # На случай долгого ожидания ответа сервера (при нагрузке бывает)
    except requests.exceptions.Timeout as e:
        raise ServerTimeoutError from e

    # Обработка других ошибок
    except Exception as e:
        raise DiaryParserError(e) from e


def check_cookie(
    cookie: str, server_name: str | None = None
) -> tuple[bool, str]:
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
        url = (
            f"/api/MarkService/GetSummaryMarks?date={dt.datetime.now().date()}"
        )
        # data = request(url, user_id)
        data = {
            "subperiod": {"code": "Полугодие_2", "name": "2 Полугодие"},
            "discipline_marks": [
                {
                    "discipline": "История",
                    "marks": [
                        {
                            "date": "2025-01-13",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-20",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-27",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-31",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-03",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-07",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-17",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Русский язык",
                    "marks": [
                        {
                            "date": "2025-01-13",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-16",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-27",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-30",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-20",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-03",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-13",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-17",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-06",
                            "mark": "3",
                            "description": "Контрольная работа: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Физическая культура",
                    "marks": [
                        {
                            "date": "2025-01-14",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-21",
                            "mark": "5",
                            "description": "Контрольная работа: нет темы",
                        },
                        {
                            "date": "2025-01-28",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-04",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-04",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-11",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-11",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-18",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Информатика",
                    "marks": [
                        {
                            "date": "2025-01-14",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-18",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-28",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-01",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-01",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-08",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-08",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-22",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-04",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Алгебра",
                    "marks": [
                        {
                            "date": "2025-01-16",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-20",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-22",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-27",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-29",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-30",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-20",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-03",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-05",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-13",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-17",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-10",
                            "mark": "2",
                            "description": ": нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Биология",
                    "marks": [
                        {
                            "date": "2025-01-18",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-01",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-08",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-22",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Вероятность и статистика",
                    "marks": [
                        {
                            "date": "2025-01-18",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-08",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Физика",
                    "marks": [
                        {
                            "date": "2025-01-18",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-01",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-04",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-08",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Геометрия",
                    "marks": [
                        {
                            "date": "2025-01-21",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-31",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-07",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-18",
                            "mark": "3",
                            "description": ": нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Иностранный язык (английский)",
                    "marks": [
                        {
                            "date": "2025-01-22",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-03",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-12",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-19",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-24",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-05",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-12",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-17",
                            "mark": "2",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-19",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-01-15",
                            "mark": "3",
                            "description": ": нет темы",
                        },
                        {
                            "date": "2025-02-12",
                            "mark": "5",
                            "description": ": нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Обществознание",
                    "marks": [
                        {
                            "date": "2025-01-28",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-04",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-07",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-11",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-14",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Индивидуальный проект",
                    "marks": [
                        {
                            "date": "2025-01-29",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-05",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "География",
                    "marks": [
                        {
                            "date": "2025-01-29",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        }
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Основы безопасности и защиты Родины",
                    "marks": [
                        {
                            "date": "2025-01-30",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-20",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
                {
                    "discipline": "Литература",
                    "marks": [
                        {
                            "date": "2025-01-31",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-21",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-07",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-14",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-14",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-03-17",
                            "mark": "4",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "3.33",
                },
                {
                    "discipline": "Химия",
                    "marks": [
                        {
                            "date": "2025-02-03",
                            "mark": "5",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-10",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                        {
                            "date": "2025-02-24",
                            "mark": "3",
                            "description": "Работа на уроке: нет темы",
                        },
                    ],
                    "average_mark": "0.00",
                },
            ],
            "dates": [
                "2025-01-13",
                "2025-01-14",
                "2025-01-15",
                "2025-01-16",
                "2025-01-17",
                "2025-01-18",
                "2025-01-20",
                "2025-01-21",
                "2025-01-22",
                "2025-01-23",
                "2025-01-24",
                "2025-01-25",
                "2025-01-27",
                "2025-01-28",
                "2025-01-29",
                "2025-01-30",
                "2025-01-31",
                "2025-02-01",
                "2025-02-03",
                "2025-02-04",
                "2025-02-05",
                "2025-02-06",
                "2025-02-07",
                "2025-02-08",
                "2025-02-10",
                "2025-02-11",
                "2025-02-12",
                "2025-02-13",
                "2025-02-14",
                "2025-02-15",
                "2025-02-17",
                "2025-02-18",
                "2025-02-19",
                "2025-02-20",
                "2025-02-21",
                "2025-02-22",
                "2025-02-24",
                "2025-02-25",
                "2025-02-26",
                "2025-02-27",
                "2025-02-28",
                "2025-03-01",
                "2025-03-03",
                "2025-03-04",
                "2025-03-05",
                "2025-03-06",
                "2025-03-07",
                "2025-03-10",
                "2025-03-11",
                "2025-03-12",
                "2025-03-13",
                "2025-03-14",
                "2025-03-15",
                "2025-03-17",
                "2025-03-18",
                "2025-03-19",
                "2025-03-20",
                "2025-03-21",
                "2025-03-22",
                "2025-04-01",
                "2025-04-02",
                "2025-04-03",
                "2025-04-04",
                "2025-04-05",
                "2025-04-07",
                "2025-04-08",
                "2025-04-09",
                "2025-04-10",
                "2025-04-11",
                "2025-04-12",
            ],
        }

        if data == "demo":
            return demo_data.marks()

        if not data.get("discipline_marks"):
            return (
                "Информация об оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        msg_text = ""
        for_midle_marks = []

        for subject in data["discipline_marks"]:
            # Получаем название предмета
            g = minify_lesson_title(subject["discipline"])

            # Приводим название предмета к единой длинне
            g += " " * (10 - len(g))

            # Получаем список оценок по предмету
            marks = [int(m["mark"]) for m in subject["marks"]]

            # Получаем правильные (рассчитанные) средние быллы по предметам,
            # потому что сервер иногда возвращает нули.
            len_marks = len(marks)
            average_mark = (
                "0.00" if not len_marks else f"{sum(marks) / len_marks:.2f}"
            )
            float_average_mark = float(average_mark)

            # Добавляем средний балл по предмету в список
            # для рассчёта общего среднего балла
            for_midle_marks.append(float_average_mark)

            # Определяем цвет маркера, в зависимости от балла
            color_mark = COLOR_MARKERS[round(float_average_mark)]

            # Формируем сообщение
            msg_text += f"{color_mark} {g}│ {average_mark} │ {' '.join([str(m) for m in marks])}\n"

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

        subperiods = {i["code"]: i["name"] for i in data["subperiods"]}

        subperiods_names = list(subperiods.values())
        len_subperiods_names = len(subperiods_names)

        subperiods_names_first_letter = [i[0] for i in subperiods_names]

        explanation = [
            f"{subperiods_names_first_letter[i]} - {subperiods_names[i]}"
            for i, _ in enumerate(subperiods_names)
        ]

        msg_text = (
            f"Итоговые оценки:\n\n{'\n'.join(explanation)}\n\n<pre>\n"
            f"Предмет    │ {' | '.join(subperiods_names_first_letter)} |\n"
            f"───────────┼{('───┼' * len_subperiods_names)[:-1]}┤\n"
        )

        subperiod_index = list(subperiods.keys())

        for discipline in data["discipline_marks"]:
            stroka = list("-" * len_subperiods_names)
            g = minify_lesson_title(discipline["discipline"])

            while len(g) < 10:
                g += " "

            msg_text += f"{g} │ "

            for period_mark in discipline["period_marks"]:
                # Получаем индекс и присваиваем значение
                if period_mark["subperiod_code"] in subperiod_index:
                    stroka[
                        subperiod_index.index(period_mark["subperiod_code"])
                    ] = period_mark["mark"]

            msg_text += f"{' │ '.join(stroka)}"

            msg_text += " │\n"

        return f"{msg_text}</pre>"
