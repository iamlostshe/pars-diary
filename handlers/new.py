from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import db

router = Router(name=__name__)

# Вход в новую учебную запись
@router.message(Command('new'))
async def new_msg(msg: Message) -> None:
    if msg.text == '/new':
        # Отвечаем пользователю
        await msg.answer('Комманда работает так - "/new sessionid=xxx..."')
    else:
        # Добавляем cookie пользователя в дб и отвечаем пользователю
        await msg.answer(db.add_user_cookie(msg.from_user.id, msg.text[5:]))