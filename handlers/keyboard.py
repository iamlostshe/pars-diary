'''
Клавиатуры

Здесь следующие находятся callback_handler-ы:

    - Изменение состояния уведомлений (Вкл./Откл.)
    - Изменение состояния умных уведомлений (Вкл./Откл.)
    - Домашнее задание (на завтра, на недлю, на конкретный день)
    - Нейросеть для помощи в учебе
'''

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from loguru import logger

from utils import db
from utils.hw import hw, chatgpt
from utils.messages import error

router = Router(name=__name__)


# Хендлеры для кнопок
@router.callback_query()
async def callback(call: CallbackQuery) -> None:
    'Отвечает за все callback-хендлеры (кнопки)'

    # Выводим лог в консоль
    logger.debug('[c] {}', call.data)

    # Проверяем ошибки
    try:
        # Изменение состояния уведомлений
        if 'n_n' in call.data:
            # Меняем состояние и создаем клавиатуру
            if db.swith_notify(call.from_user.id):
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='❌ Отключить', callback_data='n_n')]
                    ])
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='✅ Включить', callback_data='n_n')
                    ]])

            # Отправляем сообщение
            await call.message.edit_text(
                '🔔 <b>Уведомления об изменении оценок</b>',
                parse_mode='HTML',
                reply_markup=markup
                )

        # Изменение состояния умных уведомлений
        elif 'n_s' in call.data:
            # Меняем состояние и создаем клавиатуру
            if db.swith_notify(call.from_user.id, index='s'):
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='❌ Отключить', callback_data='n_s')
                    ]])
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text='✅ Включить', callback_data='n_s')
                    ]])

            # Отправлем сообщение
            await call.message.edit_text(
                (
                    '🔔 <b>Умные уведомления</b>* - [в разработке] '
                    'уникальная функция для анализа оценок '
                    'и простых уведомлений, например:\n\n'
                    '<blockquote>Спорная оценка по математике,'
                    'необходимо исправить, иначе может выйти 4!\n\n'
                    'Для настройки уведомлений используйте /notify\n'
                    '</blockquote>\n'
                    'или\n\n'
                    '<blockquote>Вам не хватает всего 0.25 балла до оценки 5, стоит постараться!\n'
                    'Для настройки уведомлений используйте /notify\n'
                    '</blockquote>'
                ),
                parse_mode='HTML',
                reply_markup=markup)

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
                answer = hw(call.from_user.id, index)

                await call.message.edit_text(answer[0], parse_mode='HTML', reply_markup=answer[1])

        # Нейросеть для помощи в учебе
        elif 'chatgpt' in call.data:
            await call.message.edit_text('Chatgpt думает...')
            send_text = chatgpt(call.from_user.id, call.data, call.from_user.first_name)
            await call.message.edit_text(send_text)

    except Exception as e:
        await call.message.edit_text(error(e, call.from_user.language_code))
