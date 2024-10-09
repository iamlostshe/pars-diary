from os import getenv
import asyncio
import json

from loguru import logger
from dotenv import load_dotenv

from aiogram import Bot

from utils import db
from utils.db import DB_NAME
from utils.pars import Pars

# Получаем токен из .env
load_dotenv()
TOKEN = getenv('TOKEN_TG')

# Инициализируем бота
bot = Bot(token=TOKEN)




async def update_marks() -> None:
    'Асинхронная функция для обновления оценок'
    try:
        # Открываем файл для чтения и записи
        with open(DB_NAME, "r+", encoding='UTF-8') as f:
            data = json.load(f)

            # Проходимся по всем пользователям
            for user in data:
                # Если у пользователя включены уведомления
                if data[user]['notify']:
                    # Пустая переменная для сообщения
                    msg_text = []
                    # Получаем новые оценки
                    pars = Pars()
                    new_data = '\n'.join(pars.marks(data[user]['cookie']).split('\n')[3:-1])
                    # Получаем старые оценки
                    old_data = db.get_marks(user)
                    # Сверяем их со старыми
                    for n in new_data.split('\n'):
                        for o in old_data.split('\n'):
                            if n != o and f'++ {n}' not in msg_text:
                                msg_text.append(f'++ {n}')
                    # Если есть изменения
                    if msg_text != []:
                        # Отправляем сообщение пользователю
                        msg_text = 'Новые оценки!\n<pre>'+'\n'.join(msg_text)+'</pre>'
                        await bot.send_message(user, msg_text, parse_mode='HTML')
                        # Регестрируем изменения
                        data[user]["marks"] = new_data

            # Записываем изменения в файл
            f.seek(0)
            json.dump(data, f, indent=4)
    
    # Обработчики ошибок
    except KeyError:
        raise KeyError({'error': '404', 'message': 'Пользователь не найден.'})
    
    except FileNotFoundError:
        raise FileNotFoundError({'error': '404', 'message': f'Файл {DB_NAME} не найден.'})
    
    except Exception as e:
        raise Exception({'error': '500', 'message': f'Неизвестная ошибка: {e}.'})

if __name__ == '__main__':
    try:
        logger.info('Начинаю проверку обновлений.')
        asyncio.run(update_marks())
    except Exception as e:
        logger.error('Ошибка во время проверки обновлений {}', e)