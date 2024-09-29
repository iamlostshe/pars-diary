import datetime
import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pars import request, minify_lesson_title
from ask_gpt import ask_gpt
import db


def hw(user_id: str | int, index: str | int) -> str | tuple:
    '''Функция для парсинга дз
    
| index | функция                        |
| ----- | ------------------------------ |
| t     | дз на завтра                   |
| w     | дз на неделю                   |
| 0-6   | дз на определенный день недели |'''

    cookie = db.get_cookie(user_id)
    url = 'https://es.ciur.ru/api/HomeworkService/GetHomeworkFromRange'

    data = request(cookie, url)

    inline_keyboard = []
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    
    if index == 'w':
        msg_text = ''
        for day in range(7):
            if day == 6:
                msg_text += f"Д/З на {data[day]['date'].replace('-', ' ')} {days[day]} нет!\n\nВОСКРЕСЕНЬЕ!"
            else:
                msg_text += f"Д/З на {data[day]['date'].replace('-', ' ')} {days[day]}\n\n"
                counter = 1
                i = 0

                for i in data[day]['homeworks']:
                    subject = minify_lesson_title(i['discipline'])
                    p_subject = subject

                    while len(p_subject) < 9:
                        p_subject += ' '

                    msg_text += f"{counter}. {p_subject} │ {i['homework']}\n"

                    if i['homework'] != '':
                        
                        google_url = f"https://www.google.com/search?q={urllib.parse.quote(i['discipline'])} ГДЗ {urllib.parse.quote(i['homework']).replace(' ', '+')}"
                        ask_gpt_text = f"chatgpt_{day}_{counter-1}"

                        inline_keyboard.append([
                            InlineKeyboardButton(text=f'{days[day]} {subject}', callback_data='None'),
                            InlineKeyboardButton(text='chatgpt', callback_data=ask_gpt_text),
                            InlineKeyboardButton(text='google', url=google_url)
                        ])
                    counter += 1

                msg_text += '\n'

        inline_keyboard.append([
            InlineKeyboardButton(text='На завтра', callback_data=f'hw_t'),
            InlineKeyboardButton(text='Дни недели', callback_data='hw_days')
        ])           

        markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        return f'<pre>{msg_text}</pre>', markup
                
    else:
        if index == 't':
            day = (datetime.datetime.today() + datetime.timedelta(days=1)).weekday()
        else:
            day = int(index)

        if day == 6:
            msg_text = f"Д/З на {data[day]['date'].replace('-', ' ')} {days[day]} нет!\n\nВОСКРЕСЕНЬЕ!"

        else:
            msg_text = f"Д/З на {data[day]['date'].replace('-', ' ')} {days[day]} \n\n"
            counter = 1
            i = 0

            for i in data[day]['homeworks']:
                subject = minify_lesson_title(i['discipline'])
                p_subject = subject

                while len(p_subject) < 9:
                    p_subject += ' '

                msg_text += f"{counter}. {p_subject} │ {i['homework']}\n"

                if i['homework'] != '':

                    google_url = f"https://www.google.com/search?q={urllib.parse.quote(i['discipline'])} ГДЗ {urllib.parse.quote(i['homework']).replace(' ', '+')}"
                    ask_gpt_text = f"chatgpt_{day}_{counter-1}"

                    inline_keyboard.append([
                        InlineKeyboardButton(text=subject, callback_data='None'),
                        InlineKeyboardButton(text='chatgpt', callback_data=ask_gpt_text),
                        InlineKeyboardButton(text='google', url=google_url)
                    ])
                counter += 1

            inline_keyboard.append([
                InlineKeyboardButton(text='На неделю', callback_data=f'hw_w'),
                InlineKeyboardButton(text='Дни недели', callback_data='hw_days')
            ])           

            markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

            return f'<pre>{msg_text}</pre>', markup
                
        return f'<pre>{msg_text}</pre>', InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Нет дз', callback_data='None')]])
    

def chatgpt(user_id: str | int, index: str) -> str:
    'Функция для формирования запроса к GPT'

    day = int(index.split('_')[1])
    subject_num = int(index.split('_')[2])

    cookie = db.get_cookie(user_id)
    url = 'https://es.ciur.ru/api/HomeworkService/GetHomeworkFromRange'

    data = request(cookie, url)

    hw = data[day]['homeworks'][subject_num]['homework']
    subject_name = data[day]['homeworks'][subject_num]['discipline']

    return ask_gpt(f'Пожалуйста, отвечай на русском. Помоги мне с решением домашнего задания по {subject_name}: {hw}')