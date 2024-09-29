from config import TOKEN
from pars import pars
from hw import hw, chatgpt
from ask_gpt import ask_gpt
from users_cookie_db import del_db, new_user_in_db, user_in_db
from notify import notify_info, notify_swith, update_marks

import asyncio
import logging
import sys
import urllib.parse

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Обработка комманд-приветствий
@dp.message(Command(commands=['start', 'help']))
async def command_start_handler(msg: Message) -> None:

    if user_in_db(msg.from_user.id):
        await msg.answer(f'''Приветствую, {msg.from_user.full_name}!

/start - начать диалог
/me - данные о тебе
/cs - классные часы
/events - ивенты
/birtdays - дни рождения
/marks - оценки
/i_marks - итоговые оценки
/hw - дз''')
        
    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Инструкция', url='https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25')
                ]
            ]
        )

        await msg.answer(f'''Приветствую, {msg.from_user.full_name}!
                         
Для использования бота необходимо добавить свою учетную запись -> нажми на кнопку ниже:
''', reply_markup=markup)

# Основные комманды (парсинг + небольшие преобразования)
@dp.message(Command(commands=['me', 'cs', 'events', 'birtdays', 'marks', 'i_marks']))
async def simple_msg(msg: Message):
    send_text = pars(msg)

    if send_text == 'Сначала добавь свою учетную запись -> /new':
        await msg.answer(f'{send_text}', 'HTML')
    else:
        await msg.answer(f'{send_text}', 'HTML')


# дз
@dp.message(Command(commands=['hw']))
async def lessons_msg(msg: Message):
    send_data = hw(msg.from_user.id, 't')
    print(send_data)
    if send_data == 'Сначала добавь свою учетную запись -> /new':
        await msg.answer(send_data)
    else:
        await msg.answer(f'<pre>{send_data[0]}</pre>', 'HTML', reply_markup=send_data[1])


# Нейросеть для помощи в учебе
@dp.message(Command(commands=['chatgpt']))
async def lessons_msg(msg: Message):
    if msg.text == '/chatgpt':
        send_text = 'Комманда работает так - "/chatgpt расскажи о теореме пифагора"'
    else:
        send_text = ask_gpt(msg.text.replace('/chatgpt ', ''))

    await msg.answer(send_text)


# Уведомления о новых оценках
@dp.message(Command(commands=['notify']))
async def lessons_msg(msg: Message):
    if user_in_db(msg.from_user.id):
        await msg.answer('Для этого действия необходимо зарегестрироваться -> /start', 'HTML')
    else:
        if notify_info(msg.from_user.id):
            msg_text = 'Сейчас уведомления <strong>включены</strong>, для <strong>отключения</strong> нажми кнопку ниже:'
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='notyfi_off')]])
        else:
            msg_text = 'Сейчас уведомления <strong>отключены</strong>, для <strong>включения</strong> нажми кнопку ниже:'
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Включить', callback_data='notyfi_on')]])

        await msg.answer(msg_text, 'HTML', reply_markup=markup)


# Авторизация и выход из учетной записи
@dp.message(Command(commands=['new', 'del']))
async def new_msg(msg: Message):
    if msg.text == '/new':
        msg_text = 'Комманда работает так - "/new sessionid=xxx..."'
    elif msg.text == '/del':
        msg_text = del_db(msg.from_user.id)
    else:
        msg_text = new_user_in_db(msg)

    await msg.answer(msg_text)

# Кнопки для решения дз (обработчик)
@dp.callback_query()
async def callback(call):
    if call.data == 'notyfi_on':
        notify_swith(call.from_user.id)

        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отключить', callback_data='notyfi_off')]])
        
        await call.message.edit_text('Сейчас уведомления <strong>включены</strong>, для <strong>отключения</strong> нажми кнопку ниже:', reply_markup=markup)


    elif call.data == 'notyfi_off':
        notify_swith(call.from_user.id)
        
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
                InlineKeyboardButton(text='сб', callback_data='hw_5'),
                InlineKeyboardButton(text='вс', callback_data='hw_6')
            ]])

            await call.message.edit_text('Выбери день недели:', reply_markup=markup)

        else:
            index = call.data.replace('hw_', '')
            msg_text = hw(call.from_user.id, index)

            await call.message.edit_text(f'<pre>{msg_text[0]}</pre>', reply_markup=msg_text[1])

    elif 'chatgpt' in call.data:
        await call.message.edit_text('Chatgpt думает...')

        send_text = chatgpt(call.from_user.id, call.data)

        await call.message.edit_text(send_text)


async def scheduled_task():
    while True:
        a = update_marks()
        print('Отправляю сообщение', a[0], a[1])


        if a[1] != '':
            await bot.send_message(a[0], [1])

        # Ожидаем один час
        await asyncio.sleep(60)

async def on_startup(dp):
    asyncio.create_task(scheduled_task())

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())