import datetime

import requests
from loguru import logger

from utils.exceptions import *


def request(url: str, user_id: str | int | None = None, cookie: str | None = None) -> dict:
    'Функция для осуществеления запроса по id пользователя и url'
    from utils import db
    try:
        # Получаем cookie по user_id
        if cookie == None and user_id != None:
            # Получаем cookie из json базы данных
            cookie = db.get_cookie(str(user_id))

        # Отпраляем запрос
        headers = {'cookie': cookie}
        r = requests.post(url, headers=headers, timeout=20)

        # Преобразуем в json
        r_json = r.json()

        # Выводим лог в консоль
        logger.debug(r_json)

        # Проверяем какой статус-код вернул сервер
        if r.status_code != 200:
            raise UnexpectedStatusCodeError(r.status_code)
        
        # Проверяем ответ сервера на наличае ошибок в тексте
        elif 'Server.UserNotAuthenticated' in r.text:
            raise UserNotAuthenticated()
        
        elif 'Client.ValidationError' in r.text:
            raise ValidationError()

        # Возвращаем загруженные и десериализованные данные из файла
        return r_json
    
    # На случай долгого ожидания ответа сервера (при нагрузке бывает)
    except requests.exceptions.Timeout:
        raise TimeoutError()

    # Обработка других ошибок
    except Exception as e:
        raise UnknownError(e)


def check_cookie(cookie: str) -> tuple[bool, str]:
    'Функция для проверки cookie'
    # Простые тесты
    if 'sessionid=' not in cookie:
        return False, 'Ваши cookie должны содержать "sessionid="'
    elif 'sessionid=xxx...' in cookie:
        return False, 'Нельзя использовать пример'
    else:
        try:
            # Тест путем запроса к серверу
            request('https://es.ciur.ru/api/ProfileService/GetPersonData', cookie=cookie)
            return True, 'ok'

        except UnexpectedStatusCodeError:
            return False, 'Не правильно введены cookie, возможно они устарели (сервер выдает неверный ответ)'


def minify_lesson_title(title: str) -> str:
    '''Функция для сокращения названий уроков.

``` python
minify_lesson_title('Физическая культура')

>>> 'Физ-ра'
```'''
                    
    a = {
        'Иностранный язык (английский)': 'Англ. Яз.',
        'Физическая культура': 'Физ-ра',
        'Литература': 'Литер.',
        'Технология': 'Техн.',
        'Информатика': 'Информ.',
        'Обществознание': 'Обществ.',
        'Русский язык': 'Рус. Яз.',
        'Математика': 'Матем.',
        'Основы безопасности и защиты Родины': 'ОБЗР',
        'Вероятность и статистика': 'Теор. Вер.',
        'Индивидуальный проект': 'Инд. пр.'
    }.get(title)

    if a:
        return a
    else:
        return title


class Pars:
    def me(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/ProfileService/GetPersonData'
        data = request(url, user_id)

        if data['children_persons'] == []:
            # Logged in on children account
            if data['user_is_male']:
                sex = 'Мужской'
            else:
                sex = 'Женский'

            return f'''ФИО - {data['user_fullname']}
Пол - {sex}
Школа - {data['selected_pupil_school']}
Класс - {data['selected_pupil_classyear']}'''
        
        else:
            # Logged in on parent account
            msg_text = ''

            # Parent data
            msg_text += f"ФИО (родителя) - {data['user_fullname']}\n"

            # Номера может и не быть
            try:
                msg_text += f"Номер телефона - {data['phone']}"
            except:
                pass

            # Children (-s) data
            children_counter = 0

            for i in data['children_persons']:
                children_counter += 1
                name = ' '.join(i['fullname'].split(' ')[0:-1])
                dr = i['fullname'].split(' ')[-1]
                school = i['school']
                classyear = i['classyear']

                msg_text += f'\n\n{children_counter} ребенок:\n\nФИО - {name}\nДата рождения - {dr}\nШкола - {school}\nКласс - {classyear}'
        
            return msg_text
    

    def cs(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getClassHours'
        data = request(url, user_id)

        if data == {}:
            return 'Информация о классных часах отсутсвует'
        return f'''КЛАССНЫЙ ЧАС

{data['date']}
{data['begin']}-{data['end']}

{data['place']}
{data['theme']}'''
    

    def events(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getEvents'
        data = request(url, user_id)
    
        if str(data) == '[]':
            return 'Кажется, ивентов не намечается)'
        else:
            return f'{data}'


    def birthdays(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getBirthdays'
        data = request(url, user_id)

        if str(data) == '[]':
            return 'Кажется, дней рождений не намечается)'
        else:
            return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"


    def marks(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/MarkService/GetSummaryMarks?date='+str(datetime.datetime.now().date())
        data = request(url, user_id)

        msg_text = ''
        
        if data['discipline_marks'] == []:
            return 'Информация об оценках отсутствует\n\nКажется, вам пока не поставили ни одной('
        
        for subject in data['discipline_marks']:
            marks = []
            g = minify_lesson_title(subject['discipline'])

            while len(g) < 10:
                g += ' '

            for i in subject['marks']:
                marks.append(i['mark'])

            if float(subject['average_mark']) >= 4.5:
                color_mark = '🟩'
            elif float(subject['average_mark']) >= 3.5:
                color_mark = '🟨'
            elif float(subject['average_mark']) >= 2.5:
                color_mark = '🟧'
            else:
                color_mark = '🟥'
                
            msg_text += f"{color_mark} {g}│ {subject['average_mark']} │ {' '.join(marks)}\n"


        return f'Оценки:\n\n<pre>\n{msg_text}</pre>'
    

    def i_marks(self, user_id: str | int) -> str:
        url = 'https://es.ciur.ru/api/MarkService/GetTotalMarks'
        data = request(url, user_id)
    
        msg_text = 'Итоговые оценки:\n\n1-4 - Четвертные оценки\nГ - Годовая\nЭ - Экзаменационная (если есть)\nИ - Итоговая\n\n<pre>\nПредмет    │ 1 │ 2 │ 3 │ 4 │ Г │ Э │ И │\n───────────┼───┼───┼───┼───┼───┼───┼───┤\n'

        if data['discipline_marks'] == []:
            return 'Информация об итоговых оценках отсутствует\n\nКажется, вам пока не поставили ни одной('

        for discipline in data['discipline_marks']:
            list = ['-', '-', '-', '-', '-', '-', '-']
            g = minify_lesson_title(discipline['discipline'])
            
            while len(g) < 10:
                g += ' '
            
            msg_text += f"{g} │ "

            for period_mark in discipline['period_marks']:
                # Словарь для сопоставления subperiod_code с индексами
                subperiod_index = {
                    '1_1': 0, # 1 четверть
                    '1_2': 1, # 2 четверть
                    '1_3': 2, # 3 четверть
                    '1_4': 3, # 4 четверть
                    '4_1': 4, # Годовая
                    '4_2': 5, # Экзаменационная (если есть)
                    '4_3': 6  # Итоговая
                }

                # Получаем индекс из словаря и присваиваем значение
                if period_mark['subperiod_code'] in subperiod_index:
                    list[subperiod_index[period_mark['subperiod_code']]] = period_mark['mark']

            msg_text += f"{' │ '.join(list)}"

            msg_text += ' │\n'

        return f'{msg_text}</pre>'
    

# Тесты
if __name__ == '__main__':
    
    cookie = ''
    pars = Pars()

    print(pars.me(cookie))
    print(pars.cs(cookie))
    print(pars.birtdays(cookie))
    print(pars.events(cookie))
    print(pars.marks(cookie))
    print(pars.i_marks(cookie))