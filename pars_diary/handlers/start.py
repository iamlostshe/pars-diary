"""Приветственное сообщение."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from pars_diary.types import User
from pars_diary.utils.keyboards import not_auth_keyboard, reg_0
from pars_diary.utils.messages import registration_0, start_old_user

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(msg: Message, user: User) -> None:
    """Обработка /start."""
    # Если пользователь зарегистрирован
    if user.is_auth:
        await msg.answer(
            start_old_user(
                msg.from_user.first_name,
            ),
            reply_markup=not_auth_keyboard,
        )

    # Если пользователь не зарегистрирован
    else:
        await msg.answer(
            registration_0(msg.from_user.first_name),
            reply_markup=reg_0,
        )
