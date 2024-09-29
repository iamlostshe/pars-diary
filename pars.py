import json
import datetime

import requests

from loguru import logger


def minify_lesson_title(title: str) -> str:
    '''Функция для сокращения названий уроков.

``` python
minify_lesson_title('Физическая культура')

>>> 'Физ-ра'
```'''
                    
    a = ['Иностранный язык (английский)', 'Физическая культура', 'Литература', 'Технология', 'Информатика', 'Обществознание', 'Русский язык', 'Математика']
    b = ['Англ. Яз.', 'Физ-ра', 'Литер.', 'Техн.', 'Информ.', 'Обществ.', 'Рус. Яз.', 'Матем.']

    for i in range(len(a)):
        title = title.replace(a[i], b[i])

    return title


def request(cookie: str, url: str) -> dict:
    'Функция для осуществеления запроса по cookie и url'
    # Проверяем авторизован ли пользователь
    if cookie == None:
        raise Exception({'error': 403, 'message': 'Для выполнения этого действия необходимо авторизоваться в боте.\n\nИнструкция по авторизации доступна по -> /start'})

    # Отпраляем запрос
    headers = {'cookie': cookie}
    r = requests.post(url, headers=headers)

    # Выводим лог в консоль
    logger.debug(r.text)

    # Проверяем какой статус-код вернул сервер
    if r.status_code != 200:
        raise Exception({'error': r.status_code, 'message': f'Неизвестная ошибка, сервер вернул неверный статус-код'})
    
    # Проверяем ответ сервера на наличае ошибок в тексте
    elif 'Server.UserNotAuthenticated' in r.text:
        raise Exception({'error': 403, 'message': 'Для выполнения этого действия необходимо авторизоваться в боте.\n\nИнструкция по авторизации доступна по -> /start'})
    
    elif 'Client.ValidationError' in r.text:
        raise Exception({'error': 403, 'message': 'Для выполнения этого действия необходимо авторизоваться в боте.\n\nИнструкция по авторизации доступна по -> /start'})

    # Возвращаем загруженные и десериализованные данные из файла
    return json.loads(r.text)


class Pars:
    def me(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/ProfileService/GetPersonData'
        data = request(cookie, url)

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

            try:
                msg_text += f"Номер телефона - +{data['phone']}"
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
    

    def cs(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getClassHours'
        data = request(cookie, url)

        if data == {}:
            return 'Информация о классных часах отсутсвует'
        return f'''КЛАССНЫЙ ЧАС

{data['date']}
{data['begin']}-{data['end']}

{data['place']}
{data['theme']}'''
    

    def events(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getEvents'
        data = request(cookie, url)
    
        if str(data) == '[]':
            return 'Кажется, ивентов не намечается)'
        else:
            return f'{data}'


    def birthdays(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/WidgetService/getBirthdays'
        data = request(cookie, url)

        if str(data) == '[]':
            return 'Кажется, дней рождений не намечается)'
        else:
            return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"


    def marks(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/MarkService/GetSummaryMarks?date='+str(datetime.datetime.now().date())
        data = request(cookie, url)

        msg_text = 'Оценки:\n\n<pre>\n'
        
        for subject in data['discipline_marks']:
            marks = []
            g = minify_lesson_title(subject['discipline'])

            while len(g) < 9:
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


        return f'{msg_text}</pre>'
    

    def i_marks(self, cookie: str) -> str:
        url = 'https://es.ciur.ru/api/MarkService/GetTotalMarks'
        data = request(cookie, url)
    
        msg_text = 'Итоговые оценки:\n\n1-4 - Четвертные оценки\nГ - Годовая\nЭ - Экзаменационная (если есть)\nИ - Итоговая\n\n<pre>\nПредмет   │ 1 │ 2 │ 3 │ 4 │ Г │ Э │ И │\n──────────┼───┼───┼───┼───┼───┼───┼───┤\n'

        for discipline in data['discipline_marks']:
            list = ['-', '-', '-', '-', '-', '-', '-']
            g = minify_lesson_title(discipline['discipline'])
            
            while len(g) < 9:
                g += ' '
            
            msg_text += f"{g} │ "

            for period_mark in discipline['period_marks']:
                if period_mark['subperiod_code'] == '1_1':
                    list[0] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '1_2':
                    list[1] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '1_3':
                    list[2] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '1_4':
                    list[3] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '4_1':
                    list[4] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '4_2':
                    list[5] = (period_mark['mark'])
                elif period_mark['subperiod_code'] == '4_3':
                    list[6] = (period_mark['mark'])

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