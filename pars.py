import requests
import json
import datetime
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from users_cookie_db import get_cookie_from_db


def pars(msg: Message) -> str:
    
    if 'me' in msg.text or 'ball' in msg.text:
        url = 'https://es.ciur.ru/api/ProfileService/GetPersonData'
    elif 'cs' in msg.text:
        url = 'https://es.ciur.ru/api/WidgetService/getClassHours'
    elif 'events' in msg.text:
        url = 'https://es.ciur.ru/api/WidgetService/getEvents'
    elif 'birtdays' in msg.text:
        url = 'https://es.ciur.ru/api/WidgetService/getBirthdays'
    elif 'i_marks' in msg.text:
        url = 'https://es.ciur.ru/api/MarkService/GetTotalMarks'
    elif 'marks' in msg.text:
        url = 'https://es.ciur.ru/api/MarkService/GetSummaryMarks?date='+str(datetime.datetime.now().date())


    cookie = get_cookie_from_db(msg.from_user.id)

    if cookie == '':
        return 'Сначала добавь свою учетную запись -> /new'

    headers = {'Cookie':cookie}
    post = requests.post(url, headers=headers)
    print(post.text)
    b = json.loads(post.text)

    if 'Server.UserNotAuthenticated' in post.text:
        return 'Ошибка авторизации, пожалуйста, удалите текущую учетную запись -> /del и поробуйте войти снова по <a href="https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25">инструкции.</a>'
    else:
        if 'me' in msg.text:
            if b['children_persons'] == []:
                # Вошел через аккаунт ребенка
                if b['user_is_male']:
                    sex = 'Мужской'
                else:
                    sex = 'Женский'

                return f'''ФИО - {b['user_fullname']}
Пол - {sex}
Школа - {b['selected_pupil_school']}
Класс - {b['selected_pupil_classyear']}'''
            
            else:
                # Вошел через аккаунт родителя
                msg_text = ''

                # Записываем данные о родителе
                msg_text += f"ФИО (родителя) - {b['user_fullname']}\n"

                try:
                    msg_text += f"Номер телефона - +{b['phone']}"
                except:
                    pass

                # Записываем данные о ребенке/детях
                children_counter = 0

                for i in b['children_persons']:
                    children_counter += 1
                    name = ' '.join(i['fullname'].split(' ')[0:-1])
                    dr = i['fullname'].split(' ')[-1]
                    school = i['school']
                    classyear = i['classyear']

                    msg_text += f'\n\n{children_counter} ребенок:\n\nФИО - {name}\nДата рождения - {dr}\nШкола - {school}\nКласс - {classyear}'
            
                return msg_text

        elif 'cs' in msg.text:
            return f'''КЛАССНЫЙ ЧАС

{b['date']}
{b['begin']}-{b['end']}

{b['place']}
{b['theme']}
    '''
        elif 'events' in msg.text:
            if str(b) == '[]':
                return 'Кажется, ивентов не намечается)'
            else:
                return f'{b}'
            
        elif 'birtdays' in msg.text:
            if str(b) == '[]':
                return 'Кажется, дней рождений не намечается)'
            else:
                return f"{b[0]['date'].replace('-', ' ')}\n{b[0]['short_name']}"
    
        
        elif 'i_marks' in msg.text:
            msg_text = 'Итоговые оценки:\n\nПредмет   │ 1 │ 2 │ 3 │ 4 \n───────────────────────\n'
            for discipline in b['discipline_marks']:
                g = discipline['discipline'].replace('Иностранный язык (английский)', 'Англ. Яз.').replace('Физическая культура', 'Физ-ра').replace('Литература', 'Литер.').replace('Технология', 'Техн.').replace('Информатика', 'Информ.').replace('Обществознание', 'Обществ.').replace('Русский язык', 'Рус. Яз.').replace('Математика', 'Матем.')
                while len(g) < 9:
                    g += ' '
                msg_text += f"{g} │ "
                for period_mark in discipline['period_marks']:
                    msg_text += f"{period_mark['mark']} │ "
                msg_text += '\n'
            return f'<pre>{msg_text}</pre>'
                

        elif 'marks' in  msg.text:
            msg_text = 'Оценки:\n\n'
            for subject in b['discipline_marks']:
                marks = ''
                g = subject['discipline'].replace('Иностранный язык (английский)', 'Англ. Яз.').replace('Физическая культура', 'Физ-ра').replace('Литература', 'Литер.').replace('Технология', 'Техн.').replace('Информатика', 'Информ.').replace('Обществознание', 'Обществ.').replace('Русский язык', 'Рус. Яз.').replace('Математика', 'Матем.')
                while len(g) < 9:
                    g += ' '
                for i in subject['marks']:
                    marks += f"{i['mark']} "

                    if float(subject['average_mark']) >= 4.5:
                        color_mark = '🟩'
                    else:
                        color_mark = '🟨'
                    
                msg_text += f"{color_mark} {g}│ {subject['average_mark']} │ {marks}\n"


            return f'<pre>{msg_text}</pre>'