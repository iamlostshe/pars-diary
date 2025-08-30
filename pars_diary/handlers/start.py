"""Приветственное сообщение."""

from aiogram import Router
from aiogram.types import Message
from loguru import logger

from pars_diary.utils.db import add_user, get_cookie
from pars_diary.utils.keyboards import not_auth_keyboard, reg_0
from pars_diary.utils.messages import registration_0, start_old_user
from 

router = Router(name=__name__)


@router.message()
async def command_start_handler(msg: Message, user: ) -> None:
    """Обработка /start."""
    # Если пользователь зарегистрирован
    if 
        await msg.answer(
            await start_old_user(
                msg.from_user.first_name, msg.from_user.language_code,
            ),
            reply_markup=await not_auth_keyboard(),
        )

    # Если пользователь не зарегистрирован
    else:
        await msg.answer(
            await registration_0(
                msg.from_user.first_name, msg.from_user.language_code,
            ),
            reply_markup=await reg_0(),
        )

    refer = msg.text[7:] if msg.text and msg.text.startswith("/start ") else None
    await add_user(msg.from_user.id, refer)
