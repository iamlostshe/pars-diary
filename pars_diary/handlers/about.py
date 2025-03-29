"""Информация о боте.

Содержит подробную информацию о боте, включая:

- отличая от конкурентов.
- информацию об умных уведомлениях.
- ссылку на админа.
- ссылку на исходный код.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.utils.messages import about

router = Router(name="About bot")


@router.message(Command("about"))
async def about_bot(msg: Message) -> None:
    """Рассказывает о проекте."""
    await msg.answer(about(msg.from_user.language_code), "HTML")
