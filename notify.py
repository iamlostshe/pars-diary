"""Модуль для создания и отправки уведомлений."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Bot
from loguru import logger
from models import User

from pars_diary.config import TOKEN, parser
from pars_diary.utils import db
from pars_diary.utils.db import DB_NAME
from pars_diary.utils.exceptions import (
    DBFileNotFoundError,
    UnknownError,
    UserNotFoundError,
)

if TYPE_CHECKING:
    from .utils.typing import UserId

# Задержка между обычными уведомлениями (в часах, целое число)
NOTIFY_DURATION = 1

# Задержка между умными уведомлениями (в часах, целое число)
SMART_NOTIFY_DURATION = 24

async def send_notify(bot: Bot, smart: bool = False) -> None:
    """Асинхронная функция для обновления оценок."""
    try:
        # Открываем файл для чтения и записи
        with Path.open(DB_NAME, "r+", encoding="UTF-8") as f:
            data = json.load(f)

            # Проходимся по всем пользователям
            for user_id in data:
                user = User(**data[user_id])
                # Проверяем указаны ли у пользователя cookie
                if user.cookie not in [None, "demo"]:
                    new_data = await parser.marks(user_id).split("\n")[3:-1]

                    # Получаем старые оценки
                    old_data = await db.get_marks(user_id)

                    # Регестрируем изменения
                    user.notify_marks = new_data
                    data[user]["notify_marks"] = new_data

                    # Записываем изменения в файл
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4, ensure_ascii=False)

                    # Если у пользователя включены уведомления
                    if user.notify:
                        # Проверяем уведомления
                        await check_notify(user_id, new_data, old_data)

                    # Если нужно отправить умное уведомление
                    # и у пользователя включены умные уведомления
                    if smart and user.smart_notify:
                        await check_smart_notify(user_id, new_data)

    except KeyError as e:
        logger.error(UserNotFoundError(e))

    except FileNotFoundError as e:
        logger.error(DBFileNotFoundError(e))

    except Exception as e:
        logger.error(UnknownError(e))

    finally:
        await bot.session.close()


async def check_notify(user_id: UserId, new_data: dict, old_data: dict) -> None:
    """Проверка наличия уведомлений об изменении оценок."""
    # Выводим лог в консоль
    logger.debug(f"Проверяю пользователя {user_id} на наличие изменённых оценок")

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
        await bot.send_message(user_id, msg_text, parse_mode="HTML")


async def check_smart_notify(user_id: UserId, new_data: dict) -> None:
    """Проверка наличия умных уведомлений."""
    # Выводим лог в консоль
    logger.debug(f"Проверяю пользователя {user_id} на наличие умных уведомлений")

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
        await bot.send_message(user_id, msg_text, parse_mode="HTML")


# Инициализируем бота
bot = Bot(token=TOKEN)


async def main() -> None:
    """Запуск проверки уведомлений."""
    # Счётчик часов
    count = SMART_NOTIFY_DURATION

    while True:
        # Инициализируем переменную для проверки умных уведомлений
        smart = False
        # Определяем нужно ли запускать умные уведомления
        if count >= SMART_NOTIFY_DURATION:
            # Меняем значение проверки умных уведомлений
            smart = True

            # Обнуляем счётчик
            count = 0

        # Запускаем скрипт отправки уведомлений
        await send_notify(bot, smart=smart)

        # Выводим лог об ожидании заданого времени
        logger.debug(f"Ожидаю {NOTIFY_DURATION} час")

        # Задержка (час в секундах)
        await asyncio.sleep(NOTIFY_DURATION * 3600)

        # Обновляем значение счётчика
        count += NOTIFY_DURATION


if __name__ == "__main__":
    asyncio.run(main())
