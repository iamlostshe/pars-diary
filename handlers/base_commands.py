from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from utils.pars import Pars
from utils import messages
from utils import db

router = Router(name=__name__)

# Базовые комманы (парсинг + небольшое изменение)
@router.message(Command(commands=['me', 'cs', 'events', 'birthdays', 'marks', 'i_marks']))
async def simple_msg(msg: Message) -> None:
    try:
        # Получаем user_id пользователя
        user_id = msg.from_user.id

        # Проверяем зарегестирован ли пользователь
        if db.get_cookie(user_id):

            # Создаем объект класса
            pars = Pars()

            # Выбираем функцию, в зависимости от комманды
            commands = {
                '/me': pars.me,
                '/cs': pars.cs,
                '/events': pars.events,
                '/birthdays': pars.birthdays,
                '/i_marks': pars.i_marks,
                '/marks': pars.marks
            }

            # Отвечаем пользователю
            await msg.answer(commands[msg.text](user_id), 'HTML')

        else:
            # TODO Централизовать клавиатуры в файле messages.py
            # чтобы не создавать одинаковые (повтор handlers.start)

            # Создаем клавиатуру
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Инструкция', url='https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25')
            ]])
            # Выводим сообщение о необходимости регестрации и клавиатуру
            await msg.answer(messages.not_auth(msg.from_user.language_code), 'HTML', reply_markup=markup)

    # Проверка ошибок
    # TODO Разобраться почему ошибки иногда не выводятся в сообщении
    except Exception as e:
        await msg.answer(messages.error(e, msg.from_user.language_code), 'HTML')