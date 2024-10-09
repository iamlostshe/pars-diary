from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from utils import db, hw

router = Router(name=__name__)

# Хендлеры для кнопок
@router.callback_query()
async def callback(call: CallbackQuery) -> None:
    if call.data == 'notyfi_on':
        db.swith_notify(call.from_user.id)
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='notyfi_off')]])
        await call.message.edit_text('Сейчас уведомления <strong>включены</strong>, для <strong>отключения</strong> нажми кнопку ниже:', reply_markup=markup)


    elif call.data == 'notyfi_off':
        db.swith_notify(call.from_user.id)
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='notyfi_on')]])
        await call.message.edit_text('Сейчас уведомления <strong>отключены</strong>, для <strong>включения</strong> нажми кнопку ниже:', reply_markup=markup)


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