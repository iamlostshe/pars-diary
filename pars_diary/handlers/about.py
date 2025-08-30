"""Информация о боте.

Содержит подробную информацию о боте, включая:

- отличая от конкурентов
- информацию об умных уведомлениях
- ссылку на админа
- ссылку на исходный код
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.types import User
from pars_diary.utils.messages import about

router = Router(name=__name__)


# О проекте
@router.message(Command("about"))
async def lessons_msg(msg: Message, user: User) -> None:
    """Отвечает за /about."""
    # Отвечаем пользователю
    await msg.answer(about, "HTML")
