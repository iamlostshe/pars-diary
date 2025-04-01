"""Собирает все маршруты воедино.

- Публичные команды (в меню)
    - /about - О проекте
    - /notify - Настройка уведомлений
    - /base_commands - Основные команда (marks, i_marks, hw, me, ch, events, birthdays)
    - /chatgpt - Нейросеть для помощи в учёбе

- Приватные команды (нет в меню)
    - /admin - Админка
    - /new - Авторизация в боте
    - /keyboard - Клавиатуры и кнопки
    - /start - Начало диалога в боте (гл. меню)
"""

# Импортируем все обработчики
from pars_diary.handlers import (
    about,
    admin,
    base_commands,
    ch,
    chatgpt,
    keyboard,
    register,
    start,
)

ROUTERS = (
    about.router,
    admin.router,
    base_commands.router,
    ch.router,
    chatgpt.router,
    keyboard.router,
    register.router,
    start.router,
)

__all__ = ("routers",)
