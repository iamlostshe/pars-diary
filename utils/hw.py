import datetime
import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.pars import minify_lesson_title, request
from utils.ask_gpt import ask_gpt
from utils.exceptions import *


DAYS = [
    'понедельник',
    'вторник',
    'среду',
    'четверг',
    'пятницу',
    'субботу',
    'воскресенье'
    ]

DAYS_SHORT = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']


def get_hw(data: str | int, day: int, msg_text: str, inline_keyboard: InlineKeyboardMarkup) -> str:
    'Функция для получения дз по дню недели'
    # если завтра воскресенье - выводим дз на понедельник
    # мы же не учимся по воскресеньям?
    if day == 6:
        day == 0

    msg_text += f"Д/З на {data[day]['date'].replace('-', ' ')} {DAYS[day]} \n\n"
    count = 0

    day_hw = data[day]['homeworks']

    if day_hw != []:
        for i in enumerate(day_hw):
            subject = minify_lesson_title(day_hw[i]['discipline'])

            while len(subject) < 9:
                subject += ' '

            msg_text += f"{count}. {subject} │ {day_hw[i]['homework']}\n"

            if i['homework'] != '':
                google_url = f"https://www.google.com/search?q={urllib.parse.quote(day_hw[i]['discipline'])} ГДЗ {urllib.parse.quote(day_hw[i]['homework']).replace(' ', '+')}"
                ask_gpt_text = f"chatgpt_{day}_{i}"

                inline_keyboard.append([
                    InlineKeyboardButton(text=f'{DAYS_SHORT[day]} {subject}', callback_data='None'),
                    InlineKeyboardButton(text='chatgpt', callback_data=ask_gpt_text),
                    InlineKeyboardButton(text='google', url=google_url)
                ])
            count += 1
    else:
        msg_text += 'Нет д/з'
    
    msg_text += '\n'


def hw(user_id: str | int, index: str | int) -> str | tuple:
    '''Функция для парсинга дз
    
| index | функция                        |
| ----- | ------------------------------ |
| t     | дз на завтра                   |
| w     | дз на неделю                   |
| 0-6   | дз на определенный день недели |'''

    # Получаем данные из api
    url = 'https://es.ciur.ru/api/HomeworkService/GetHomeworkFromRange'
    data = request(url, user_id)

    msg_text = ''
    inline_keyboard = []

    # дз на неделю
    if index == 'w':
        for day in range(6):
            get_hw(data, day)

        inline_keyboard.append([
            InlineKeyboardButton(text='На завтра', callback_data=f'hw_t'),
            InlineKeyboardButton(text='Дни недели', callback_data='hw_days')
        ])           

    # дз на завтра
    elif index == 't':
        day = (datetime.datetime.today() + datetime.timedelta(days=1)).weekday()
        # дз на определенный день недели
    else:
        # Проверим корректно ли задан день недели
        if int(index) in range(6):
            day = int(index)
        else:
            DayIndexError()

        get_hw(data, day)

        inline_keyboard.append([
            InlineKeyboardButton(text='На неделю', callback_data=f'hw_w'),
            InlineKeyboardButton(text='Дни недели', callback_data='hw_days')
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return f'<pre>{msg_text}</pre>', markup
                


# Tests
if __name__ == '__main__':
    user_id = ''

    hw(user_id, 't') # Дз на завтра
    hw(user_id, 'w') # Дз на неделю
    hw(user_id, '1') # Дз на вторник

    chatgpt(user_id, 'chatgpt_1_0') # Дз на первый урок во вторник