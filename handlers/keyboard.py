from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from utils import db, hw

router = Router(name=__name__)

# Хендлеры для кнопок
@router.callback_query()
async def callback(call: CallbackQuery) -> None:
    # Изменение состояния уведомлений
    if 'n_n' in call.data:
        # Меняем состояние и создаем клавиатуру
        if db.swith_notify(call.from_user.id):
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='n_n')]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='n_n')]])

        # Отправляем сообщение
        await call.message.edit_text('🔔 <b>Уведомления об изменении оценок</b>', parse_mode='HTML', reply_markup=markup)

    # Изменение состояния умных уведомлений
    elif 'n_s' in call.data:
        # Меняем состояние и создаем клавиатуру
        if db.swith_notify(call.from_user.id, index='s'):
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='n_s')]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='n_s')]])

        # Отправлем сообщение
        await call.message.edit_text('''🔔 <b>Умные уведомления</b>* - [в разработке] уникальная функция для анализа оценок и простых уведомлений, например:

<blockquote>Спорная оценка по математике, необходимо исправить, иначе может выйти 4!

Для настройки уведомлений используйте /notify
</blockquote>
или

<blockquote>Вам не хватает всего 0.25 балла до оценки 5, стоит постараться!

Для настройки уведомлений используйте /notify
</blockquote>''', parse_mode='HTML', reply_markup=markup)


    # Домашнее задание
    elif 'hw' in call.data:
        if call.data == 'hw_days':
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='пн', callback_data='hw_0'),
                InlineKeyboardButton(text='вт', callback_data='hw_1'),
                InlineKeyboardButton(text='ср', callback_data='hw_2'),
                InlineKeyboardButton(text='чт', callback_data='hw_3'),
                InlineKeyboardButton(text='пт', callback_data='hw_4'),
                InlineKeyboardButton(text='сб', callback_data='hw_5')
            ]])

            await call.message.edit_text('Выбери день недели:', reply_markup=markup)

        else:
            index = call.data.replace('hw_', '')
            msg_text = hw(call.from_user.id, index)

            await call.message.edit_text(f'<pre>{msg_text[0]}</pre>', reply_markup=msg_text[1])

    elif 'chatgpt' in call.data:
        await call.message.edit_text('Chatgpt думает...')

        send_text = hw.chatgpt(call.from_user.id, call.data)

        await call.message.edit_text(send_text)