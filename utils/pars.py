'Модуль для парсинга'

import datetime

import requests
from loguru import logger

from utils.exceptions import UnexpectedStatusCodeError, UserNotAuthenticated
from utils.exceptions import UnknownError, ValidationError, MyTimeoutError
from utils import demo_data


# Вспомогательные функции

def request(url: str, user_id: str | int | None = None, cookie: str | None = None) -> dict:
    'Функция для осуществеления запроса по id пользователя и url'
    from utils import db

    try:
        # Получаем cookie по user_id
        if cookie is None and user_id is not None:
            # Получаем cookie из json базы данных
            cookie = db.get_cookie(user_id)

        if cookie in ['demo', 'демо']:
            return 'demo'

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
    except requests.exceptions.Timeout as e:
        raise MyTimeoutError() from e

    # Обработка других ошибок
    except Exception as e:
        raise UnknownError(e) from e


def check_cookie(cookie: str) -> tuple[bool, str]:
    'Функция для проверки cookie'
    # Если используется демоверсия, то проверки она не пройдет)
    if cookie == 'demo' or cookie == 'демо':
        return True, (
            'Пользователь успешно добавлен в базу данных, однако учтите, что '
            'демонстрационный режим открывает не все функции, для вас будут недоступны уведомления.'
        )
    else:
        # Простые тесты
        if 'sessionid=' not in cookie:
            return False, 'Ваши cookie должны содержать "sessionid="'
        elif 'sessionid=xxx...' in cookie:
            return False, 'Нельзя использовать пример'
        else:
            try:
                # Тест путем запроса к серверу
                request('https://es.ciur.ru/api/ProfileService/GetPersonData', cookie=cookie)
                return True, 'Пользователь успешно добавлен в базу данных.'

            except UnexpectedStatusCodeError:
                return False, (
                    'Не правильно введены cookie, возможно они '
                    'устарели (сервер выдает неверный ответ)'
                )


def minify_lesson_title(title: str) -> str:
    '''Функция для сокращения названий уроков.

    `minify_lesson_title('Физическая культура')`
    >>> 'Физ-ра'
    '''

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
        'Индивидуальный проект': 'Инд. пр.',
        'Факультатив "Функциональная грамотность"': 'Функ. Гр.'
    }.get(title)

    if a:
        return a
    else:
        return title


# Класс с основными функциями
class Pars:
    'Парсинг'
    def me(self, user_id: str | int) -> str:
        'Информация о пользователе'

        url = 'https://es.ciur.ru/api/ProfileService/GetPersonData'
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.me()

        if data['children_persons'] == []:
            # Logged in on children account
            if data['user_is_male']:
                sex = 'Мужской'
            else:
                sex = 'Женский'

            return (
                f'ФИО - {data['user_fullname']}\n',
                f'Пол - {sex}\n',
                f'Школа - {data['selected_pupil_school']}\n',
                f'Класс - {data['selected_pupil_classyear']}'
            )

        else:
            # Logged in on parent account
            msg_text = ''

            # Parent data
            msg_text += f"ФИО (родителя) - {data['user_fullname']}\n"

            # Номера может и не быть
            number = data.get('phone')
            if number:
                msg_text += f"Номер телефона - {number}"

            # Children (-s) data
            children_counter = 0

            for i in data['children_persons']:
                children_counter += 1
                name = ' '.join(i['fullname'].split(' ')[0:-1])
                dr = i['fullname'].split(' ')[-1]
                school = i['school']
                classyear = i['classyear']

                msg_text += (
                    f'\n\n{children_counter} ребенок:\n\n'
                    f'ФИО - {name}\nДата рождения - {dr}\nШкола - {school}\nКласс - {classyear}'
                )

            return msg_text

    def cs(self, user_id: str | int) -> str:
        'Информация о классных часах'

        url = 'https://es.ciur.ru/api/WidgetService/getClassHours'
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.cs()

        if data == {}:
            return 'Информация о классных часах отсутсвует'
        return (
            'КЛАССНЫЙ ЧАС\n\n',
            f'{data['date']}\n',
            f'{data['begin']}-{data['end']}\n\n',
            f'{data['place']}\n',
            f'{data['theme']}\n'
        )

    def events(self, user_id: str | int) -> str:
        'Информация о ивентах'

        url = 'https://es.ciur.ru/api/WidgetService/getEvents'
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.events()

        if str(data) == '[]':
            return 'Кажется, ивентов не намечается)'
        else:
            return f'{data}'

    def birthdays(self, user_id: str | int) -> str:
        'Информация о днях рождения'

        url = 'https://es.ciur.ru/api/WidgetService/getBirthdays'
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.birthdays()

        if str(data) == '[]':
            return 'Кажется, дней рождений не намечается)'
        else:
            return f"{data[0]['date'].replace('-', ' ')}\n{data[0]['short_name']}"

    def marks(self, user_id: str | int) -> str:
        'Информация об оценках'

        url = (
            'https://es.ciur.ru/api/MarkService/GetSummaryMarks?'
            f'date={datetime.datetime.now().date()}'
        )
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.marks()

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

            if subject['average_mark'] == '':
                average_mark = '0.00'
            else:
                average_mark = subject['average_mark']

            if float(average_mark) >= 4.5:
                color_mark = '🟩'
            elif float(average_mark) >= 3.5:
                color_mark = '🟨'
            elif float(average_mark) >= 2.5:
                color_mark = '🟧'
            else:
                color_mark = '🟥'

            msg_text += f"{color_mark} {g}│ {average_mark} │ {' '.join(marks)}\n"

        return f'Оценки:\n\n<pre>\n{msg_text}</pre>'

    def i_marks(self, user_id: str | int) -> str:
        'Информация об итоговых оценках'

        url = 'https://es.ciur.ru/api/MarkService/GetTotalMarks'
        data = request(url, user_id)

        if data == 'demo':
            return demo_data.i_marks()

        msg_text = (
            'Итоговые оценки:\n\n1-4 - Четвертные оценки\nГ - Годовая\n'
            'Э - Экзаменационная (если есть)\nИ - Итоговая\n\n<pre>\n'
            'Предмет    │ 1 │ 2 │ 3 │ 4 │ Г │ Э │ И │\n───────────┼───┼───┼───┼───┼───┼───┼───┤\n'
        )

        if data['discipline_marks'] == []:
            return (
                'Информация об итоговых оценках отсутствует\n\n'
                'Кажется, вам пока не поставили ни одной('
            )

        for discipline in data['discipline_marks']:
            stroka = ['-', '-', '-', '-', '-', '-', '-']
            g = minify_lesson_title(discipline['discipline'])

            while len(g) < 10:
                g += ' '

            msg_text += f"{g} │ "

            for period_mark in discipline['period_marks']:
                # Словарь для сопоставления subperiod_code с индексами
                subperiod_index = {
                    '1_1': 0,  # 1 четверть
                    '1_2': 1,  # 2 четверть
                    '1_3': 2,  # 3 четверть
                    '1_4': 3,  # 4 четверть
                    '4_1': 4,  # Годовая
                    '4_2': 5,  # Экзаменационная (если есть)
                    '4_3': 6  # Итоговая
                }

                # Получаем индекс из словаря и присваиваем значение
                if period_mark['subperiod_code'] in subperiod_index:
                    stroka[subperiod_index[period_mark['subperiod_code']]] = period_mark['mark']

            msg_text += f"{' │ '.join(stroka)}"

            msg_text += ' │\n'

        return f'{msg_text}</pre>'
