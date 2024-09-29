import requests
import json
import datetime
import urllib.parse
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ask_gpt import ask_gpt
from users_cookie_db import get_cookie_from_db


def hw(user_id: str | int, index: str | int) -> str | tuple:
    'Функция для парсинга дз\n-\nindex:\n t - дз на завтра\n0-6 - дз на определенный день недели\nц - дз на неделю'

    cookie = get_cookie_from_db(user_id)
    url = 'https://es.ciur.ru/api/HomeworkService/GetHomeworkFromRange'

    if cookie == '':
        return 'Сначала добавь свою учетную запись -> /new'

    headers = {'Cookie':cookie}
    post = requests.post(url, headers=headers)
    print(post.text)
    b = json.loads(post.text)

    inline_keyboard = []
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    
    if index == 'w':
        msg_text = ''
        for day in range(7):

            if day == 6:
                msg_text += f"Д/З на {b[day]['date'].replace('-', ' ')} {days[day]} нет!\n\nВОСКРЕСЕНЬЕ!"

            else:
                msg_text += f"Д/З на {b[day]['date'].replace('-', ' ')} {days[day]}\n\n"
                counter = 1
                i = 0

                for i in b[day]['homeworks']:
                    subject = i['discipline'].replace('Иностранный язык (английский)', 'Англ. Яз.').replace('Физическая культура', 'Физ-ра').replace('Литература', 'Литер.').replace('Технология', 'Техн.').replace('Информатика', 'Информ.').replace('Обществознание', 'Обществ.').replace('Русский язык', 'Рус. Яз.').replace('Математика', 'Матем.')
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

        return msg_text, markup
                
    else:
        if index == 't':
            day = (datetime.datetime.today() + datetime.timedelta(days=1)).weekday()
        else:
            day = int(index)

        if day == 6:
            msg_text = f"Д/З на {b[day]['date'].replace('-', ' ')} {days[day]} нет!\n\nВОСКРЕСЕНЬЕ!"

        else:
            msg_text = f"Д/З на {b[day]['date'].replace('-', ' ')} {days[day]} \n\n"
            counter = 1
            i = 0

            for i in b[day]['homeworks']:
                subject = i['discipline'].replace('Иностранный язык (английский)', 'Англ. Яз.').replace('Физическая культура', 'Физ-ра').replace('Литература', 'Литер.').replace('Технология', 'Техн.').replace('Информатика', 'Информ.').replace('Обществознание', 'Обществ.').replace('Русский язык', 'Рус. Яз.').replace('Математика', 'Матем.')
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

            return msg_text, markup
                
        return msg_text, InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Нет дз', callback_data='None')]])
    

def chatgpt(user_id: str | int, index: str):

    try:
        day = int(index.split('_')[1])
        subject_num = int(index.split('_')[2])

        cookie = get_cookie_from_db(user_id)
        url = 'https://es.ciur.ru/api/HomeworkService/GetHomeworkFromRange'

        if cookie == '':
            return 'Сначала добавь свою учетную запись -> /new'

        headers = {'Cookie':cookie}
        post = requests.post(url, headers=headers)
        print(post.text)
        b = json.loads(post.text)

        hw = b[day]['homeworks'][subject_num]['homework']
        subject_name = b[day]['homeworks'][subject_num]['discipline']

        msg_text = ask_gpt(
            f'Помоги мне с решением домашнего задания по {subject_name}: {hw}'
        )

        return msg_text

    except Exception as e:
        return f'Неизвестная ошибка - {e}'
