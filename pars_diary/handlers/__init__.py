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
    error,
    keyboard,
    new,
    notify,
    start,
)

routers = (
    about.router,
    admin.router,
    base_commands.router,
    ch.router,
    chatgpt.router,
    error.router,
    keyboard.router,
    new.router,
    notify.router,
    start.router,
)

__all__ = ("routers",)
