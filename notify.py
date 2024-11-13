'Модуль для создания и отправки уведомлений'

# Integrated python modules
import asyncio
import json

# Modules need to be installed
from loguru import logger

# Aiogram
from aiogram import Bot

# Writed by me modules
from utils import db
from utils.db import DB_NAME
from utils.pars import Pars
from utils.exceptions import UnknownError, UserNotFoundError, DBFileNotFoundError
from utils.load_env import TOKEN

# Инициализируем бота
bot = Bot(token=TOKEN)


async def send_notify() -> None:
    'Асинхронная функция для обновления оценок'
    try:
        # Открываем файл для чтения и записи
        with open(DB_NAME, "r+", encoding='UTF-8') as f:
            data = json.load(f)

            # Проходимся по всем пользователям
            for user in data:

                # Проверяем указаны ли у пользователя cookie
                if db.get_cookie(user):

                    # Если у пользователя включены уведомления
                    if data[user].get('notify'):
                        data = await check_notify(user, data)

                    # Если у пользователя включены умные уведомления
                    if data[user].get('smart_notify'):
                        await check_smart_notify(user)

            # Записываем изменения в файл
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4, ensure_ascii=False)

    except KeyError as e:
        raise UserNotFoundError() from e

    except FileNotFoundError as e:
        raise DBFileNotFoundError(DB_NAME) from e

    except Exception as e:
        raise UnknownError(e) from e


async def check_notify(user: str | int, data: dict):
    'Проверка наличия уведомлений об изменении оценок'

    # Выводим лог в консоль
    logger.debug(f'Проверяю пользователя {user} на наличие изменённых оценок')

    # Пустая переменная для сообщения
    msg_text = []

    # Получаем новые оценки
    pars = Pars()
    new_data = pars.marks(user).split('\n')[3:-1]

    # Получаем старые оценки
    old_data = db.get_marks(user)

    # Ищем изменения
    for n in new_data:
        n_title = n.split('│')[0][2:].strip()
        found = False  # Флаг для отслеживания, найден ли предмет в old_data

        for o in old_data:
            o_title = o.split('│')[0][2:].strip()

            # Сравниваем значения
            if n_title == o_title:
                found = True  # Предмет найден в old_data
                if n != o:
                    msg_text.append(f'-- {o}')
                    msg_text.append(f'++ {n}')
                break  # Выходим из внутреннего цикла, так как предмет найден

        # Если предмет не найден в old_data, добавляем его как новый
        if not found:
            msg_text.append(f'++ {n} (новый предмет)')

    # Проверяем на удаленные предметы
    for o in old_data:
        o_title = o.split('│')[0][2:].strip()
        found = False  # Сбрасываем флаг для проверки удаленных предметов

        for n in new_data:
            n_title = n.split('│')[0][2:].strip()

            if n_title == o_title:
                found = True  # Предмет найден в new_data
                break  # Выходим из внутреннего цикла, так как предмет найден

        # Если предмет не найден в new_data и не пуст, добавляем его как удаленный
        if not found:
            msg_text.append(f'-- {o} (удаленный предмет)')

    # Если есть изменения
    if msg_text:
        logger.info(msg_text)
        # Отправляем сообщение пользователю
        msg_text = (
            'У Вас изменились оценки (управление уведомлениями - /notify):\n<pre>'
            f"{'\n'.join(msg_text)}</pre>"
        )
        await bot.send_message(user, msg_text, parse_mode='HTML')
        # Регестрируем изменения
        data[user]["marks"] = new_data

    return data


async def check_smart_notify(user: str | int):
    'Проверка наличия умных уведомлений'

    # Выводим лог в консоль
    logger.debug(f'Проверяю пользователя {user} на наличие умных уведомлений')

    # Получаем оценки пользователя по всем предметам

    # Получаем спорные
    # Полчаем те, до которых не хватает одной-двух оценок

    # Отправляем ответ пользователю
    # bot.send_message(...)


if __name__ == '__main__':
    asyncio.run(send_notify())
