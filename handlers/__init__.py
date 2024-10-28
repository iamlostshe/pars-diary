# TODO Написать докстроки всем router-ам

# Импортируем все обработчики
from handlers import (

    # Публичные комманды (в меню)
    about, # О проекте
    notify, # Настройка уведомлений
    base_commands, # Основные комманды (marks, i_marks, hw, me, cs, events, birthdays)
    chatgpt, # Нейросеть для помощи в учёбе

    # Приватные комманды (нет в меню)
    admin, # Админка
    new, # Авторизация в боте
    keyboard, # Клавиатуры и кнопки
    start # Начало диалога в боте (гл. меню)
)

routers = (
    
    # Публичные комманды (в меню)
    about.router, # О проекте
    notify.router, # Настройка уведомлений
    base_commands.router, # Основные комманды (marks, i_marks, hw, me, cs, events, birthdays)
    chatgpt.router, # Нейросеть для помощи в учёбе

    # Приватные комманды (нет в меню)
    admin.router, # Админка
    new.router, # Авторизация в боте
    keyboard.router, # Клавиатуры и кнопки
    start.router # Начало диалога в боте (гл. меню)
)

__all__ = ("routers")