# TODO Переписать с нуля, добавить больше функций:

# - Вкл./Откл. уведомлений
# - Вкл./Откл. умных уведомлений
# - настройка времени оповещения
# - настройка времени оповещения для умных уведомлений

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

from utils import db
from utils import messages

router = Router(name=__name__)

# Настройки для уведомлений
@router.message(Command('notify'))
async def lessons_msg(msg: Message) -> None:
    if db.get_cookie(msg.from_user.id):
        # Текст: ⚙️ Настройки уведомлений:
        await msg.answer('⚙️ <b>Настройки уведомлений:</b>', 'HTML')

        # Текст: 🔔 Уведомления об изменении оценок
        # Кнопка: Вкл./Откл.
        if db.get_notify(msg.from_user.id):
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='n_n')]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='n_n')]])
    
        await msg.answer('🔔 <b>Уведомления об изменении оценок</b>', 'HTML', reply_markup=markup)

        # Текст: 🔔 Умные уведомления
        # Кнопка: Вкл./Откл.
        if db.get_notify(msg.from_user.id, index='s'):
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='n_s')]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='n_s')]])

        await msg.answer('''🔔 <b>Умные уведомления</b>* - [в разработке] уникальная функция для анализа оценок и простых уведомлений, например:

<blockquote>Спорная оценка по математике, необходимо исправить, иначе может выйти 4!

Для настройки уведомлений используйте /notify
</blockquote>
или

<blockquote>Вам не хватает всего 0.25 балла до оценки 5, стоит постараться!

Для настройки уведомлений используйте /notify
</blockquote>''', 'HTML', reply_markup=markup)

        # Текст: 🔔 Уведомления об изменении расписания
        # Кнопка: Перейти
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Перейти', url='https://t.me/mili_sp_bot')]])
        await msg.answer('🔔 <b>Уведомления об изменении расписания</b>', 'HTML', reply_markup=markup)

    else:
        # Выводим сообщение о необходимости регестрации и клавиатуру
        await msg.answer(messages.not_auth(msg.from_user.language_code), 'HTML', reply_markup=messages.not_auth_keyboard(msg.from_user.language_code))