"""Парсер для работы с API дневника.

TODO @milinuri: Декомпозируй логику, отдельно парсер (bars-api),
отдельно сборщик сообщений.
Это позволит не привязываться к боту, а например в будущем сделать webapp.
"""

import json
import re
from datetime import UTC, datetime

import aiohttp
from loguru import logger

from pars_diary.parser import exceptions
from pars_diary.parser.db import User
from pars_diary.services import demo

# Ссылка на страницу со ссылками на все сервера дневников в разных регионах
AGGREGATOR_URL = "http://aggregator-obr.bars-open.ru/my_diary"

# Регулярное выражение для удаления тегов <span>
SPAN_CLEANER = re.compile(r"<span[^>]*>(.*?)</span>")

# Маркеры, в зависимости от балла
# TODO @milinuri: Цветовая палитра в виде датакласса?
COLOR_MARKERS = "🟥🟥🟥🟧🟨🟩"

# Сокращения для слишком длинных названия уроков
_SHORT_LESSONS = {
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
}


class DiaryParser:
    """Класс для работы с дневником.

    Результат возвращает в виде готовых сообщений для бота.
    """

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    # Работа с соединением
    # ====================

    async def connect(self) -> None:
        """Создаёт новую сессию AioHttp."""
        self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Закрывает сессию."""
        await self._session.close()

    async def _request(
        self,
        url: str,
        method: str | None = "get",
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> dict:
        """Выполняет запрос к дневнику."""
        if self._session is None:
            err = "Inactive session. Before using parser you need to connect"
            raise exceptions.DiaryParserError(err) from None

        try:
            res = await self._session.request(
                method, url, timeout=20, headers=headers, cookies=cookies
            )
        except aiohttp.client_exceptions.ServerTimeoutError as e:
            raise exceptions.ParseTimeoutError from e

        # Обратим внимание что если произойдёт другой нормальный код (301)
        # То он тоже вернётся как ошибка
        if res.status != 200:  # noqa: PLR2004
            raise exceptions.UnexpectedStatusCodeError(res.status) from None

        # TODO @milinuri: Тут можно вернуть проверки на авторизацию
        # Ну и другие проверки что всё корректно
        res_text = (await res.read()).replace("\u200b", "").strip()
        res_text = SPAN_CLEANER.sub(r"\1", res_text)

        return json.loads(res_text)

    async def _user_request(self, method: str, url: str, user: User) -> dict:
        """Выполняет запрос к API от лица пользователя."""
        return await self._request(
            method, user.server_name + url, headers={"cookie": user.cookie}
        )

    # Вспомогательные методы
    # ======================

    async def get_regions(self) -> dict:
        """Получаем все доступные регионы."""
        data = await self._request(AGGREGATOR_URL)
        if data.get("success") is None or data.get("data") is None:
            raise exceptions.ValidationError

        res = {}
        for region in data["data"]:
            name = region.get("name")
            url = region.get("url")
            if name is None or url is None:
                raise exceptions.ValidationError
            res[name] = url.strip("/")

        return res

    async def check_cookie(
        self, cookie: str, server_name: str | None = None
    ) -> tuple[bool, str]:
        """Функция для проверки cookie."""
        # Если используется демоверсия
        if cookie == "demo":
            return True, (
                "Пользователь успешно добавлен в базу данных!\n"
                "однако учтите, что демонстрационный режим открывает "
                "не все функции.\b"
                "Вам будут недоступны уведомления."
            )

        # Простые тесты
        if "sessionid=" not in cookie:
            return False, 'Ваши cookie должны содержать "sessionid="'
        if "sessionid=xxx..." in cookie:
            return False, "Нельзя использовать пример"
        if server_name is None:
            return False, "Укажите ваш регион -> /start"

        # Тест путем запроса к серверу
        res = await self._request(
            f"{server_name}/api/ProfileService/GetPersonData",
            headers={"cookie": cookie},
        )
        logger.debug(res)
        return True, "Пользователь успешно добавлен в базу данных."

    # Основные методы работы с дневником
    # ==================================

    async def me(self, user: User) -> str:
        """Информация о пользователе."""
        if user.cookie == "demo":
            data = demo.me()
        else:
            data = await self._user_request(
                "post", "/api/ProfileService/GetPersonData", user
            )

        if not data.get("children_persons"):
            # Logged in on children account
            sex = "Мужской" if data["user_is_male"] else "Женский"

            return (
                f"ФИО - {data['user_fullname']}\n"
                f"Пол - {sex}\n"
                f"Школа - {data['selected_pupil_school']}\n"
                f"Класс - {data['selected_pupil_classyear']}"
            )

        msg_text = f"ФИО (родителя) - {data['user_fullname']}\n"

        number = data.get("phone")
        if number:
            msg_text += f"Номер телефона - {number}"

        for n, i in data["children_persons"]:
            name = " ".join(i["fullname"].split(" ")[0:-1])
            dr = i["fullname"].split(" ")[-1]
            school = i["school"]
            class_year = i["classyear"]

            msg_text += (
                f"\n\n{n + 1} ребенок:\n\n"
                f"ФИО - {name}\nДата рождения - {dr}\n"
                f"Школа - {school}\nКласс - {class_year}"
            )

        return msg_text

    async def events(self, user: User) -> str:
        """Информация о событиях."""
        if user.cookie == "demo":
            data = demo.events()
        else:
            data = await self._user_request(
                "post", "/api/WidgetService/getEvents", user
            )

        if len(data) == 0:
            return "Кажется, событий не намечается)"

        return f"{data}"

    async def birthdays(self, user: User) -> str:
        """Информация о днях рождения."""
        if user.cookie == "demo":
            data = demo.birthdays()
        else:
            data = await self._user_request(
                "post", "/api/WidgetService/getBirthdays", user
            )

        if len(data) == 0:
            return "Кажется, дней рождений не намечается)"

        return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"

    def marks(self, user: User) -> str:
        """Информация об оценках."""
        if user.cookie == "demo":
            data = demo.marks()
        else:
            today = datetime.now(tz=UTC).date()
            data = self._user_request(
                "POST", f"/api/MarkService/GetSummaryMarks?date={today}", user
            )

        if not data.get("discipline_marks"):
            return (
                "Информация об оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        message = ""
        user_av_marks = []
        for subject in data["discipline_marks"]:
            # Получаем короткое название предмета
            d = _SHORT_LESSONS.get(subject["discipline"], subject["discipline"])
            marks = [int(m["mark"]) for m in subject["marks"]]

            # Получаем правильные (рассчитанные) средние баллы по предметам,
            # потому что сервер иногда возвращает нули.
            av_marks = round(sum(marks) / len(marks), 2) if len(marks) > 0 else 0.0

            user_av_marks.append(av_marks)
            av_color = COLOR_MARKERS[round(av_marks)]

            # Формируем сообщение
            marks_line = " ".join([str(m) for m in marks])
            message += f"{av_color} {d:10}│ {av_marks} │ {marks_line}\n"

        message += (
            f"\nОбщий средний балл: {sum(user_av_marks) / len(user_av_marks):.2f}"
        )

        return f"Оценки:\n\n<pre>{message}</pre>"

    def i_marks(self, user: User) -> str:
        """Информация об итоговых оценках."""
        if user.cookie == "demo":
            data = demo.i_marks()

        else:
            data = self._user_request("post", "/api/MarkService/GetTotalMarks", user)

        if data.get("discipline_marks") is None:
            return (
                "Информация об итоговых оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        subperiods = {i["code"]: i["name"] for i in data["subperiods"]}
        subperiods_names = [i["name"] for i in data["subperiods"]]
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
            d = _SHORT_LESSONS.get(discipline["discipline"], discipline["discipline"])
            msg_text += f"\n{d:10} │ "
            line = ["-"] * len_subperiods_names
            for period_mark in discipline["period_marks"]:
                # Получаем индекс и присваиваем значение
                if period_mark["subperiod_code"] in subperiod_index:
                    line[subperiod_index.index(period_mark["subperiod_code"])] = (
                        period_mark["mark"]
                    )

            msg_text += f"{' │ '.join(line)} │"
        return f"{msg_text}</pre>"
