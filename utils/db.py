'Класс для работы с json базой данных'

DB_NAME = 'users.json'
GRAPH_NAME = 'stat_img.png'

from collections import Counter
import json
import time

import matplotlib.pyplot as plt

from utils.exceptions import *
from utils.pars import check_cookie

def add_user(user_id: int | str, refer: str | None = None) -> None | dict:
    'Добавляет пользователя в json базу данных'
    # Получаем реферальные сведения
    if refer[:7] == '/start ':
        refer = refer[7:]
    else:
        refer = None

    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения и записи
        with open(DB_NAME, "r+", encoding='UTF-8') as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Если пользователя нет в json базе данных
            if user_id not in data:
                data[user_id] = {
                    "time_online": [time.time()],
                    "refer": [],
                    "cookie": None,
                    "notify": True,
                    "marks": ''
                }
            # Если пользователь уже есть в json базе данных
            else:
                data[user_id]['time_online'].append(time.time())

            # В случае если поле refer не пусто указываем его в json базе данных
            if refer != None:
                data[user_id]['refer'].append(refer)

            # Сохраняем изменения в json базе данных
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Обработчики ошибок
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def add_user_cookie(user_id: int | str, cookie: str) -> None | str | dict: 
    'Добавляет пользователю cookie в json базе данных'
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        c_c = check_cookie(cookie)
        if c_c:
            # Открываем файл для чтения и записи
            with open(DB_NAME, "r+", encoding='UTF-8') as f:
                # Загрузка и десериализация данных из файла
                data = json.load(f)

                # Запись cookie в json базу данных
                data[user_id]['cookie'] = cookie

                # Сохраняем изменения в json базе данных
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)

                # Отправляем сообщение об успешной записи в дб
                return 'Пользователь успешно добавлен в базу данных'
        else:
            return c_c
            
    # Обработчики ошибок
    except KeyError:
        raise UserNotFoundError()
    
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)
    

def get_cookie(user_id: str | int) -> None | str | dict:
    'Возвращает куки из базы данных (Если они прежде были записаны)'
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with open(DB_NAME, 'r', encoding='UTF-8') as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем cookie пользователя
            return data[user_id]['cookie']
    
    # Обработчики ошибок
    except KeyError:
        return UserNotAuthorizatedError()
    
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def get_notify(user_id: str | int) -> str | dict:
    'Возвращает значение уведомлений'
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with open(DB_NAME, 'r', encoding='UTF-8') as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем notify пользователя
            return data[user_id]['notify']
    
    # Обработчики ошибок
    except KeyError:
        raise UserNotFoundError()
    
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def swith_notify(user_id: str | int) -> None | dict: 
    'Меняет значение уведомлений (вкл -> выкл | выкл -> вкл)'
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with open(DB_NAME, 'r+', encoding='UTF-8') as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Меняем значение cookie пользователя на противоположное
            data[user_id]['notify'] = not data[user_id]['notify']
        
            # Сохраняем изменения в json базе данных
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)

            # Возвращаем новое значение переменной notify
            return data[user_id]['notify']
    
    # Обработчики ошибок
    except KeyError:
        raise UserNotFoundError()
    
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def get_graph() -> None:
    'Генерирует график для анализа прироста пользователей'
    try:
        with open(DB_NAME, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            
        conuter = 0

        times = []
        users = []

        for user in data:
            conuter += 1

            times.append(int(str(data[user]['time_online'][0]).split('.')[0]))
            users.append(conuter)
                
        plt.plot(times, users)
        plt.ylabel('Пользователи')
        plt.xlabel('Время входа')
        plt.title('График времени входа пользователей')
        plt.savefig(GRAPH_NAME)
    
    # Обработчики ошибок
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def get_stat() -> tuple[int, str]:
    'Возвращает статистику для (сис-) админов'
    try:
        with open(DB_NAME, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            
        refers = []

        for user in data:
            for i in data[user]['refer']:
                refers.append(i)

        refers = '\n'.join([f'{k} - {v}' for k, v in Counter(refers).items()])

        return len(data), refers
    
    # Обработчики ошибок
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


def get_marks(user_id: str | int) -> dict | str:
    'Возвращает оценки из базы данных (Если они прежде были записаны)'
    # Конвертируем id пользователя в строку
    user_id = str(user_id)

    try:
        # Открываем файл для чтения
        with open(DB_NAME, 'r', encoding='UTF-8') as f:
            # Загрузка и десериализация данных из файла
            data = json.load(f)

            # Возвращаем оценки пользователя
            return data[user_id]['marks']
    
    # Обработчики ошибок
    except KeyError:
        raise UserNotFoundError()
    
    except FileNotFoundError:
        raise DBFilleNotFoundError(DB_NAME)
    
    except Exception as e:
        raise UnknownError(e)


# Тесты (все, что вызывает ошибки закомментированно)
if __name__ == '__main__':
    print(1, add_user(12345)) # Без рефера (число)
    print(2, add_user('12345')) # Без рефера (строка)
    print(3, add_user(12345, 'abcdef')) # С рефером

    print(4, add_user_cookie(12345, 'qwert12345')) # Случайные cookie (число)
    print(5, add_user_cookie('12345', 'qwert12345')) # Случайные cookie (строка)
    print(6, add_user_cookie(12345, 'sessionid=xxx...')) # Используем cookie из примера
    print(7, add_user_cookie(12345, 'sessionid=12345678')) # Проверка путем запроса к серверу
    print(8, add_user_cookie(12345, '<куки-которые-пройдут-валидацию-сервером>')) # Правильные cookie
    #print(9, add_user_cookie(54321, '<куки-которые-пройдут-валидацию-сервером>')) # Несуществующий пользователь

    print(10, get_cookie('12345')) # Строка
    print(11, get_cookie(12345)) # Число
    #print(12, get_cookie(54321)) # Несуществующий пользователь

    print(13, get_notify('12345')) # Строка
    print(14, get_notify(12345)) # Число
    #print(15, get_notify(54321)) # Несуществующий пользователь

    print(16, swith_notify('12345')) # Строка
    print(17, swith_notify(12345)) # Число
    #print(18, swith_notify(54321)) # Несуществующий пользователь

    print(19, get_graph()) # Генерируем график

    print(20, get_stat()) # Получаем статистику