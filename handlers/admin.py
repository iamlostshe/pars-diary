from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from utils import db
from utils import messages
from utils.load_env import ADMINS_TG

router = Router(name=__name__)

# Комманда /admin
@router.message(Command('admin'))
async def new_msg(msg: Message) -> None:
    # Если пользователь - админ
    if str(msg.from_user.id) in ADMINS_TG:
        # Обновляем график
        db.get_graph()
        # Отвечаем пользователю
        await msg.answer_photo(FSInputFile(db.GRAPH_NAME), messages.admin())