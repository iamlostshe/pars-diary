from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import ask_gpt

router = Router(name=__name__)

# Нейронная сеть, для помощи в учебе
@router.message(Command('chatgpt'))
async def lessons_msg(msg: Message) -> None:
    if msg.text == '/chatgpt':
        send_text = 'Комманда работает так - "/chatgpt расскажи о теореме пифагора"'
    else:
        send_text = ask_gpt(msg.text.replace('/chatgpt ', ''))

    await msg.answer(send_text)