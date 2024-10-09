from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from utils import db
from utils import messages

from os import getenv
from dotenv import load_dotenv

router = Router(name=__name__)

# Комманда /admin
@router.message(Command('admin'))
async def new_msg(msg: Message) -> None:
    # TODO Костыль 1
    load_dotenv()
    ADMINS_TG = getenv('ADMINS_TG').replace(' ', '').split(',')

    # Если пользователь - админ
    if str(msg.from_user.id) in ADMINS_TG:
        await msg.answer_photo(FSInputFile(db.GRAPH_NAME), messages.admin())