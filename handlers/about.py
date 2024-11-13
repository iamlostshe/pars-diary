'''
Информация о боте

Содержит подробную информацию о боте, включая:

- отличая от конкурентов
- информацию об умных уведомлениях
- ссылку на админа
- ссылку на исходный код
'''

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.messages import about

router = Router(name=__name__)


# О проекте
@router.message(Command('about'))
async def lessons_msg(msg: Message) -> None:
    'Отвечает за /about'
    await msg.answer(about(msg.from_user.language_code), 'HTML')
