# Импортируем все обработчики
from handlers import (
    hw,
    chatgpt,
    notify,
    admin,
    new,
    keyboard,
    base_commands,
    start
)

routers = (
    hw.router,
    chatgpt.router,
    notify.router,
    admin.router,
    new.router,
    keyboard.router,
    base_commands.router,
    start.router
)

__all__ = ("routers")