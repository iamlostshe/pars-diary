# Integrated python modules
import asyncio
import logging
import sys
from os import getenv

# Modules need to be installed
from dotenv import load_dotenv

# aiogram
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, Message, CallbackQuery

# Local modules (writed me)
from pars import Pars
from hw import hw, chatgpt
from ask_gpt import ask_gpt
import db
import messages

# Get token for telegram bot from .env
load_dotenv()
TOKEN = getenv('TOKEN_TG')
ADMINS_TG = getenv('ADMINS_TG').split(', ')

# Initializating bot
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Коммнды /start, /help
@dp.message(Command(commands=['start', 'help']))
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
    refer = None
    if msg.text != '/start':
        refer = msg.text.replace('/start ', '')
    db.add_user(msg.from_user.id, refer)

# Базовые комманы (парсинг + небольшое изменение)
@dp.message(Command(commands=['me', 'cs', 'events', 'birthdays', 'marks', 'i_marks']))
async def simple_msg(msg: Message) -> None:
    try:
        # Получаем cookie пользователя
        cookie = db.get_cookie(msg.from_user.id)

        # Создаем объект класса
        pars = Pars()

        # Выбираем функцию, в зависимости от комманды
        if 'me' in msg.text:
            text = pars.me(cookie)
        elif 'cs' in msg.text:
            text = pars.cs(cookie)
        elif 'events' in msg.text:
            text = pars.events(cookie)
        elif 'birthdays' in msg.text:
            text = pars.birthdays(cookie)
        elif 'i_marks' in msg.text:
            text = pars.i_marks(cookie)
        elif 'marks' in msg.text:
            text = pars.marks(cookie)

        # Отвечаем пользователю
        await msg.answer(text, 'HTML')

    # Проверка ошибок
    except Exception as e:
        await msg.answer(messages.error(e, msg.from_user.language_code))


# Комманда /hw
@dp.message(Command('hw'))
async def lessons_msg(msg: Message) -> None:
    send_data = hw(msg.from_user.id, 't')
    print(send_data)
    if send_data == 'Сначала добавь свою учетную запись -> /new':
        await msg.answer(send_data)
    else:
        await msg.answer(f'<pre>{send_data[0]}</pre>', 'HTML', reply_markup=send_data[1])


# Нейронная сеть, для помощи в учебе
@dp.message(Command(commands=['chatgpt']))
async def lessons_msg(msg: Message) -> None:
    if msg.text == '/chatgpt':
        send_text = 'Комманда работает так - "/chatgpt расскажи о теореме пифагора"'
    else:
        send_text = ask_gpt(msg.text.replace('/chatgpt ', ''))

    await msg.answer(send_text)


# Настройки для уведомлений
@dp.message(Command(commands=['notify']))
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


# Вход в новую учебную запись
@dp.message(Command(commands=['new']))
async def new_msg(msg: Message) -> None:
    if msg.text == '/new':
        # Отвечаем пользователю
        await msg.answer('Комманда работает так - "/new sessionid=xxx..."')
    else:
        # Добавляем cookie пользователя в дб и отвечаем пользователю
        await msg.answer(db.add_user_cookie(msg.from_user.id, msg.text.replace('/new ', '')))
        

# Комманда /admin
@dp.message(Command(commands=['admin']))
async def new_msg(msg: Message) -> None:
    # Если пользователь - админ
    if str(msg.from_user.id) in ADMINS_TG:
        await msg.answer_photo(FSInputFile(db.GRAPH_NAME), messages.admin())
        

# Остальные сообщения
@dp.message()
async def any_msg(msg: Message) -> None:
    msg.answer(messages.start_old_user(msg.from_user.first_name, msg.from_user.language_code))


# Хендлеры для кнопок
@dp.callback_query()
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


# Starting bot
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())