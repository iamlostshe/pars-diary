# TODO Переписать с нуля, добавить больше функций:

# - Вкл./Откл. уведомлений
# - Вкл./Откл. умных уведомлений
# - настройка времени оповещения
# - настройка времени оповещения для умных уведомлений

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from utils import db

router = Router(name=__name__)

# Настройки для уведомлений
@router.message(Command('notify'))
async def lessons_msg(msg: Message) -> None:
    if db.get(msg.from_user.id):
        await msg.answer('Для этого действия необходимо зарегестрироваться -> /start', 'HTML')
    else:
        if db.get_notify(msg.from_user.id):
            msg_text = 'Сейчас уведомления <strong>включены</strong>, для <strong>отключения</strong> нажми кнопку ниже:'
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='notyfi_off')]])
        else:
            msg_text = 'Сейчас уведомления <strong>отключены</strong>, для <strong>включения</strong> нажми кнопку ниже:'
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='notyfi_on')]])

        await msg.answer(msg_text, 'HTML', reply_markup=markup)
