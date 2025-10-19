"""Анализ данных и отправка уведомлений."""

from __future__ import annotations

import json

from bars_api import BarsAPI
from loguru import logger
from pydantic import SecretStr

from notify.types import User
from pars_diary.config import bot
from pars_diary.parser.pars import marks
from pars_diary.utils.db import DB_PATH


async def send_notify(smart: bool = False) -> None:  # noqa: FBT001, FBT002
    """Асинхронная функция для обновления оценок."""
    with DB_PATH.open("r+", encoding="UTF-8") as f:
        data = json.load(f)

        # Проходимся по всем пользователям
        for user_id in data:
            user_json = data[user_id]
            user = User(
                cookie=SecretStr(user_json.get("cookie")),
                notify=user_json["notify"],
                smart_notify=user_json["smart_notify"],
                notify_marks=user_json["notify_marks"],
                provider=user_json.get("provider"),
            )

            # Проверяем указаны ли у пользователя cookie
            if (
                user.cookie.get_secret_value()
                and user.provider
                and (user.notify or user.smart_notify)
            ):
                # Получаем старые оценки
                old_data = user.notify_marks

                # Получаем новые оценки
                async with BarsAPI(
                    user.provider,
                    user.cookie.get_secret_value(),
                ) as parser:
                    new_data = [i.replace("<pre>", "") for i in (await marks(parser)).split("\n") if " │ " in i]

                is_notify = old_data != new_data

                if is_notify:
                    # Регестрируем изменения
                    data[user_id]["notify_marks"] = new_data

                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4, ensure_ascii=False)

    if is_notify and old_data:
        if smart and user.smart_notify:
            await check_smart_notify(user_id, new_data)

        if user.notify:
            await check_notify(user_id, new_data, old_data)


async def check_notify(user_id: int, new_data: list[str], old_data: list[str]) -> None:
    """Проверка наличия уведомлений об изменении оценок."""
    logger.debug("[{}] Отправлено уведомление", user_id)

    # Пустая переменная для сообщения
    msg_text = []

    # Ищем изменения
    for n in new_data:
        n_title = n.split("│")[0][2:].strip()
        found = False  # Флаг для отслеживания, найден ли предмет в old_data

        for o in old_data:
            o_title = o.split("│")[0][2:].strip()

            # Сравниваем значения
            if n_title == o_title:
                found = True  # Предмет найден в old_data
                if n != o:
                    msg_text.append(f"-- {o}")
                    msg_text.append(f"++ {n}")
                break  # Выходим из внутреннего цикла, так как предмет найден

        # Если предмет не найден в old_data, добавляем его как новый
        if not found:
            msg_text.append(f"++ {n} (новый предмет)")

    # Проверяем на удаленные предметы
    for o in old_data:
        o_title = o.split("│")[0][2:].strip()
        found = False  # Сбрасываем флаг для проверки удаленных предметов

        for n in new_data:
            n_title = n.split("│")[0][2:].strip()

            if n_title == o_title:
                found = True  # Предмет найден в new_data
                break  # Выходим из внутреннего цикла, так как предмет найден

        # Если предмет не найден в new_data и не пуст, добавляем его как удаленный
        if not found:
            msg_text.append(f"-- {o} (удаленный предмет)")

    # Если есть изменения
    if msg_text:
        # Отправляем сообщение пользователю
        msg_text = (
            "У Вас изменились оценки (управление уведомлениями - /notify):\n<pre>"
            f"{'\n'.join(msg_text)}</pre>"
        )
        await bot.send_message(user_id, msg_text)


async def check_smart_notify(user_id: int, new_data: list[str]) -> None:
    """Проверка наличия умных уведомлений."""
    logger.debug("[{}] Отправлено уведомление (умное)", user_id)

    # Задаём переменные под сообщение и спорные оценки
    msg_text = ""
    controversial = ""

    for i in new_data:
        if "│ " in i:
            mark = float(i.split("│ ")[1])

            # Получаем 3 и 2
            if mark < 3.5:
                msg_text += f"{i}\n"

            # Получаем спорные
            elif 4.6 < mark < 4.4 or mark < 3.6:
                controversial += f"{i}\n"

    # Добавляем к сообщению 3 и 2
    if msg_text:
        msg_text = (
            "Привет, вот персональная сводка по оценкам!\n\nПоторопись! "
            "<b>По этим предметам могут выйти плохие оценки "
            f"(2 и 3):</b>\n\n<pre>{msg_text}</pre>\n"
        )

    # Добавляем к сообщению спорные
    if controversial:
        if not msg_text:
            msg_text = "Привет, вот персональная сводка по оценкам!\n"
        msg_text += f"\n<b>У вас есть спорные оценки:</b>\n\n<pre>{controversial}</pre>"

    # TODO @iamlostshe: Полчаем те, до которых не хватает одной-двух оценок

    if msg_text:
        # Дорабатываем сообщение
        msg_text += "\nУправление уведомлениями -> /notify"

        # Отправляем ответ пользователю
        await bot.send_message(user_id, msg_text)
