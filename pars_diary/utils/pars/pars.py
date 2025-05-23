"""Модуль для парсинга."""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import TYPE_CHECKING, Self

from aiohttp import ClientSession
from fake_useragent import UserAgent
from loguru import logger

from pars_diary.utils.exceptions import (
    GetRegionsListError,
    NoRegionError,
    UnexpectedStatusCodeError,
    UserNotAuthenticatedError,
    ValidationError,
)
from pars_diary.utils.pars.demo_data import get_data

from .consts import (
    AGGREGATOR_URL,
    COLOR_MARKERS,
    MARK_STR_TO_FLOAT,
    MINIFY_LESSON_TITLE,
    NO_I_MARKS_DATA,
    SPAN_CLEANER,
)

if TYPE_CHECKING:
    from pydantic import SecretStr


class Parser:
    """Парсинг."""

    async def init(self: Self) -> None:
        """Инициализация парсера."""
        self.session = ClientSession()
        self.ua = UserAgent()

    async def init_user(self: Self, cookie: SecretStr, server_name: str) -> None:
        """Инициализация пользователя."""
        if not server_name:
            raise NoRegionError

        self.server_name = server_name
        self.cookie = cookie

        self.headers = {
            "cookie": self.cookie,
            "user-agent": self.ua.random,
        }

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
            if r.status != 200:
                raise UnexpectedStatusCodeError(r.status)

            data = json.loads(await r.text())
            result = {}

            if data.get("success") and data.get("data"):
                for region in data["data"]:
                    name = region.get("name")
                    url = region.get("url")
                    if name and url:
                        if url[-1] == "/":
                            url = url[:-1]
                        result[name] = url
                    else:
                        raise GetRegionsListError
                return result
            raise GetRegionsListError

    async def check_cookie(self: Self) -> tuple[bool, str]:
        """Функция для проверки cookie."""
        # Если используется демоверсия
        if self.cookie in ["demo", "демо"]:
            return True, (
                "Пользователь успешно добавлен в базу данных, однако учтите, что "
                "демонстрационный режим открывает не все функции, для "
                "вас будут недоступны уведомления."
            )

        # Простые тесты
        if "sessionid=" not in self.cookie:
            return False, 'Ваши cookie должны содержать "sessionid="'
        if "sessionid=xxx..." in self.cookie:
            return False, "Нельзя использовать пример"

        # Тест путем запроса к серверу
        try:
            self.url = "ProfileService/GetPersonData"
            await self.request()
        except NoRegionError:
            return False, "Укажите ваш регион -> /start"
        except Exception as e:  # noqa: BLE001
            return False, (
                "Не правильно введены cookie, "
                f"при проверке сервер выдаёт ошибку:\n\n{e}"
            )
        return True, "Пользователь успешно добавлен в базу данных."

    async def request(self: Self) -> dict | str:
        """Функция для осуществеления запроса по id пользователя и url."""
        if self.headers["cookie"] in ["demo", "демо"]:
            text = get_data(self.url)

        else:
            url = f"{self.server_name}/api/{self.url}"
            print(url)

            async with self.session.post(url, headers=self.headers) as r:
                text = await r.text()

                # Проверяем ответ сервера на наличае ошибок в ответе
                if "Server.UserNotAuthenticatedError" in text or r.status == 403:
                    raise UserNotAuthenticatedError

                # Проверяем какой статус-код вернул сервер
                if r.status != 200:
                    raise UnexpectedStatusCodeError(r.status)

                if "Client.ValidationError" in text:
                    raise ValidationError

        # Преобразуем в json
        data = json.loads(
            # Фильруем ответ
            re.sub(SPAN_CLEANER, r"\1", text.replace("\u200b", "")),
        )

        # Выводим лог в консоль
        logger.debug(data)

        return data

    async def me(self: Self) -> str:
        """Информация о пользователе."""
        self.url = "ProfileService/GetPersonData"
        data = await self.request()

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

    async def events(self: Self) -> str:
        """Информация о ивентах."""
        self.url = "WidgetService/getEvents"
        data = await self.request()

        if not data:
            return "Кажется, ивентов не намечается)"

        return f"{data}"

    async def birthdays(self: Self) -> str:
        """Информация о днях рождения."""
        self.url = "WidgetService/getBirthdays"
        data = await self.request()

        if not data:
            return "Кажется, дней рождений не намечается)"

        data = data[0]

        return f"{data['date'].replace('-', ' ')}\n{data['short_name']}"

    async def marks(self: Self) -> str:
        """Информация об оценках."""
        self.url = f"MarkService/GetSummaryMarks?date={dt.datetime.now().date()}"
        data = await self.request()

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

    async def i_marks(self: Self) -> str:
        """Информация об итоговых оценках."""
        self.url = "MarkService/GetTotalMarks"
        data = await self.request()

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

    async def homework(self: Self) -> dict:
        """Домашнее задание."""
        # Получаем данные из api
        self.url = (
            "HomeworkService/GetHomeworkFromRange"
            f"?date={dt.datetime.now().date()}"
        )
        return await self.request()
