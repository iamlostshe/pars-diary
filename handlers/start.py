from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from utils import messages
from utils import db

router = Router(name=__name__)

# Команды /start, /help
@router.message()
@router.message(Command(commands=['start', 'help']))
async def command_start_handler(msg: Message) -> None:
    # Если пользователь зарегистрирован
    if db.get_cookie(msg.from_user.id) != None:
        # Отвечаем пользователю
        await msg.answer(messages.start_old_user(msg.from_user.first_name, msg.from_user.language_code))
    # Если пользователь не зарегистрирован
    else:
        # Отвечаем пользователю
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Инструкция', url='https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25')
                ]
            ]
        )
        await msg.answer(messages.start_new_user(msg.from_user.first_name, msg.from_user.language_code), reply_markup=markup)
    # Добавляем пользователя в базу данных
    db.add_user(msg.from_user.id, msg.text)