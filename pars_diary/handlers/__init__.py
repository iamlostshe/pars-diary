"""Собирает все роутеры воедино.

- Публичные комманды (в меню)
    - /about - О проекте
    - /notify - Настройка уведомлений
    - /base_commands - Основные комманды (marks, i_marks, hw, me, ch, events, birthdays)
    - /chatgpt - Нейросеть для помощи в учёбе

- Приватные комманды (нет в меню)
    - /admin - Админка
    - /new - Авторизация в боте
    - /keyboard - Клавиатуры и кнопки
    - /start - Начало диалога в боте (гл. меню)
"""

# Импортируем все обработчики
from . import (
    about,
    admin,
    base_commands,
    ch,
    chatgpt,
    keyboard,
    new,
    notify,
    start,
)

routers = (
    about.router,
    notify.router,
    base_commands.router,
    ch.router,
    chatgpt.router,
    admin.router,
    new.router,
    keyboard.router,
    start.router,
)

__all__ = ("routers",)
