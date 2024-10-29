from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from utils.messages import not_auth_keyboard, start_new_user, start_old_user, error
from utils import db

router = Router(name=__name__)

# Команды /start, /help
@router.message()
@router.message(Command(commands=['start', 'help']))
async def command_start_handler(msg: Message) -> None:
    # Если пользователь зарегистрирован (если не пустой ответ)
    if db.get_cookie(msg.from_user.id):
        # Отвечаем пользователю
        await msg.answer(start_old_user(msg.from_user.first_name, msg.from_user.language_code))

    # Если пользователь не зарегистрирован
    else:
        # Отвечаем пользователю
        await msg.answer(start_new_user(msg.from_user.first_name, msg.from_user.language_code), reply_markup=not_auth_keyboard())

    # Добавляем в базу данных пользователя или данные о его активности
    db.add_user(msg.from_user.id, msg.text)