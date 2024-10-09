from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import hw

router = Router(name=__name__)

# Комманда /hw
@router.message(Command('hw'))
async def lessons_msg(msg: Message) -> None:
    # Получаем дз на завтра (t)
    send_data = hw(msg.from_user.id, 't')

    # Проверяем ответ
    if send_data == 'Сначала добавь свою учетную запись -> /new':
        await msg.answer(send_data)
    else:
        await msg.answer(send_data, 'HTML', reply_markup=send_data[1])