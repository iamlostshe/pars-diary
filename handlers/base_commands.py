from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.pars import Pars
from utils import messages

router = Router(name=__name__)

# Базовые комманы (парсинг + небольшое изменение)
@router.message(Command(commands=['me', 'cs', 'events', 'birthdays', 'marks', 'i_marks']))
async def simple_msg(msg: Message) -> None:
    try:
        # Получаем user_id пользователя
        user_id = msg.from_user.id

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

    # Проверка ошибок
    except Exception as e:
        await msg.answer(messages.error(e, msg.from_user.language_code), 'HTML')