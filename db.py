import json
from aiogram.types import Message

def user_in_db(user_id: str | int) -> bool:
    "Проверяет, есть ли пользователь в базе данных."
    in_db = False

    with open("json_users_db.json", "r") as f:
        data = json.load(f)
    
    if user_id in data:
        in_db = True

    return in_db

def get_cookie_from_db(user_id: str | int) -> str:
    "Получает cookie пользователя из базы данных."
    with open("json_users_db.json", "r") as f:
        data = json.load(f)
    for user in data:
        if user["tg_id"] == str(user_id):
            return user["cookie"]
    return ''  # Возвращает пустую строку, если пользователь не найден

def del_db(user_id: str | int) -> str:
    "Удаляет пользователя из базы данных."
    with open("json_users_db.json", "r") as f:
        data = json.load(f)
    new_data = [user for user in data if user["tg_id"] != str(user_id)]
    with open("json_users_db.json", "w") as f:
        json.dump(new_data, f, indent=4)
    return "Пользователь удален из базы данных."

def new_user_in_db(msg: Message) -> str: 
    "Функция для записи данных о пользователе в базу данных."
    if 'sessionid=' not in msg.text:
        msg_text = 'Ваши cookie должны содержать "sessionid="'
    elif 'sessionid=xxx...' in msg.text:
        msg_text = 'Нельзя использовать пример'
    elif user_in_db(msg.from_user.id):  # Проверяем, есть ли пользователь в БД
        msg_text = 'Ваш id уже есть в базе, для того чтобы записать новый, нужно удалить старый -> /del'
    else:
        with open("json_users_db.json", "r+") as f:
            data = json.load(f)
            new_user = {
                "tg_id": str(msg.from_user.id),
                "cookie": msg.text.replace('/new ', ''),
                "marks": {}  # Инициализируем пустой словарь для оценок
            }
            data.append(new_user)
            f.seek(0)
            json.dump(data, f, indent=4)
            msg_text = "Данные успешно записаны в базу данных."

    return msg_text