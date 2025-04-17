"""Модуль для парсинга."""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Self

from aiohttp import ClientSession
from loguru import logger

from pars_diary.utils import demo_data
from pars_diary.utils.exceptions import (
    UnexpectedStatusCodeError,
    UserNotAuthenticatedError,
    ValidationError,
)

from .consts import (
    AGGREGATOR_URL,
    COLOR_MARKERS,
    MARK_STR_TO_FLOAT,
    MINIFY_LESSON_TITLE,
    NO_I_MARKS_DATA,
    SPAN_CLEANER,
)


class Parser:
    """Парсинг."""

    async def init(self: Self) -> None:
        """Инициализация парсера."""
        self.session = ClientSession()

    async def _get_space_len(self: Self, child: str, parent: dict) -> int:
        """Возвращает кол-во симовлов, для отступов."""
        try:
            return max(len(MINIFY_LESSON_TITLE.get(
                s[child], s[child],
            )) for s in parent) + 1
        except ValueError:
            return 0

    async def get_regions(self: Self) -> dict:
        """Получаем все доступные регионы."""
        async with self.session.get(AGGREGATOR_URL) as r:
            # Проверяем какой статус-код вернул сервер
            status = await r.status_code

            if status != 200:
                raise UnexpectedStatusCodeError(status)

            data = await r.json()
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

    async def check_cookie(
            self: Self,
            cookie: str,
            server_name: str | None = None,
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
        r = self.session.get(
            f"{server_name}/api/ProfileService/GetPersonData",
            headers=headers,
        )

        logger.debug(r.json())

        if r.status_code == 200:
            return True, "Пользователь успешно добавлен в базу данных."
        return False, (
            "Не правильно введены cookie, возможно они "
            f"устарели (сервер выдает неверный ответ - {r.status_code})"
        )

    async def request(
            self: Self,
            url: str,
            user_id: str | int,
        ) -> dict | str:
        """Функция для осуществеления запроса по id пользователя и url."""
        from pars_diary.utils import db

        # Получаем cookie из json базы данных
        cookie = await db.get_cookie(user_id)

        if cookie in ["demo", "демо"]:
            return "demo"

        # Получаем server_name из бд
        server_name = await db.get_server_name(user_id)

        # Преобразуем url
        url = f"{server_name}{url}"

        # Отпраляем запрос
        headers = {
            "cookie": cookie,
        }

        async with self.session.post(url, headers=headers) as r:
            # Получаем текст ответа
            text = await r.text()

            # Проверяем ответ сервера на наличае ошибок в ответе
            if "Server.UserNotAuthenticatedError" in text:
                raise UserNotAuthenticatedError

            if "Client.ValidationError" in text:
                raise ValidationError

            # Проверяем какой статус-код вернул сервер
            if r.status != 200:
                raise UnexpectedStatusCodeError(r.status_code)

            # Преобразуем в json
            data = json.loads(
                # Фильруем ответ
                re.sub(SPAN_CLEANER, r"\1", text.replace("\u200b", "")),
            )

            # Выводим лог в консоль
            logger.debug(data)

            return data

    async def me(self: Self, user_id: str | int) -> str:
        """Информация о пользователе."""
        url = "/api/ProfileService/GetPersonData"
        data = await self.request(url, user_id)

        if data == "demo":
            return await demo_data.me()

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

    async def events(self: Self, user_id: str | int) -> str:
        """Информация о ивентах."""
        url = "/api/WidgetService/getEvents"
        data = await self.request(url, user_id)

        if data == "demo":
            return await demo_data.events()

        if not data:
            return "Кажется, ивентов не намечается)"

        return f"{data}"

    async def birthdays(self: Self, user_id: str | int) -> str:
        """Информация о днях рождения."""
        url = "/api/WidgetService/getBirthdays"
        data = await self.request(url, user_id)

        if data == "demo":
            return await demo_data.birthdays()

        if not data:
            return "Кажется, дней рождений не намечается)"

        return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"

    async def marks(self: Self, user_id: str | int) -> str:
        """Информация об оценках."""
        url = f"/api/MarkService/GetSummaryMarks?date={dt.datetime.now().date()}"
        data = await self.request(url, user_id)

        if data == "demo":
            return await demo_data.marks()

        if not data.get("discipline_marks"):
            return (
                "Информация об оценках отсутствует\n\n"
                "Кажется, вам пока не поставили ни одной("
            )

        msg_text = ""
        for_midle_marks = []

        space_len = await self._get_space_len("discipline", data["discipline_marks"])

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

    async def i_marks(self: Self, user_id: str | int) -> str:
        """Информация об итоговых оценках."""
        url = "/api/MarkService/GetTotalMarks"
        data = await self.request(url, user_id)

        if data == "demo":
            return await demo_data.i_marks()

        try:
            total_marks_data = data["total_marks_data"][0]

            subperiods_data = total_marks_data["subperiods"]
            discipline_marks_data = total_marks_data["discipline_marks"]
        except KeyError:
            return NO_I_MARKS_DATA

        if not discipline_marks_data:
            return NO_I_MARKS_DATA

        subperiods = {i["code"]: i["name"] for i in subperiods_data}

        subperiods_names = list(subperiods.values())
        len_subperiods_names = len(subperiods_names)

        subperiods_names_first_letter = [i[0] for i in subperiods_names]

        explanation = [
            f"{subperiods_names_first_letter[i]} - {subperiods_names[i]}"\
            for i, _ in enumerate(subperiods_names)
        ]

        space_len = await self._get_space_len("discipline", discipline_marks_data)

        msg_text = (
            f'Итоговые оценки:\n\n{"\n".join(explanation)}\n\n<pre>\n'
            f'{"Предмет".ljust(space_len)}│ '
            f'{" | ".join(subperiods_names_first_letter)} |\n'
            f'{space_len * "─"}┼{("───┼" * len_subperiods_names)[:-1]}┤\n'
        )

        subperiod_index = list(subperiods.keys())

        for discipline in discipline_marks_data:
            stroka = list("-" * len_subperiods_names)
            g = MINIFY_LESSON_TITLE.get(
                discipline["discipline"], discipline["discipline"],
            ).ljust(space_len)

            msg_text += f"{g}│ "

            for period_mark in discipline["period_marks"]:
                # Получаем индекс и присваиваем значение
                if period_mark["subperiod_code"] in subperiod_index:
                    stroka[subperiod_index.index(period_mark["subperiod_code"])] = (
                        period_mark["mark"]
                    )

            msg_text += f"{' │ '.join(stroka)}"

            msg_text += " │\n"

        return f"{msg_text}</pre>"
