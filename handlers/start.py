'''
Приветственное сообщение
'''

from aiogram import Router
from aiogram.types import Message

from utils.messages import not_auth_keyboard, start_new_user, start_old_user
from utils import db

router = Router(name=__name__)


# Команды /start, /help, любое другое сообщение, если предыдущие хендлеры не сработали
@router.message()
async def command_start_handler(msg: Message) -> None:
    'Отвечает за обработку любых сообщений, кроме указанных ранее'
    # Если пользователь зарегистрирован (если не пустой ответ)
    if db.get_cookie(msg.from_user.id):
        # Отвечаем пользователю
        await msg.answer(start_old_user(msg.from_user.first_name, msg.from_user.language_code))

    # Если пользователь не зарегистрирован
    else:
        # Отвечаем пользователю
        await msg.answer(
            start_new_user(msg.from_user.first_name, msg.from_user.language_code),
            reply_markup=not_auth_keyboard()
        )

    # Добавляем в базу данных пользователя или данные о его активности
    db.add_user(msg.from_user.id, msg.text)
