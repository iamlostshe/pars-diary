"""Приветственное сообщение."""

from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import _

from pars_diary.keyboards import not_auth_keyboard
from pars_diary.messages import start_old_user
from pars_diary.parser.db import UsersDataBase

router = Router(name="Message catcher")


@router.message()
async def command_start_handler(message: Message, db: UsersDataBase) -> None:
    """принимает все сообщения.

    Команды /start, /help, любое другое сообщение.
    Если предыдущие обработчики не сработали.
    """
    # Если пользователь зарегистрирован (если не пустой ответ)
    if db.get_cookie(message.from_user.id):
        await message.answer(
            start_old_user(message.from_user.first_name),
            reply_markup=not_auth_keyboard(),
        )

    else:
        await message.answer(
            _("welcome, {first_name}! you need register.").format(
                Message.from_user.first_name
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("start"), callback_data="start_reg"
                        )
                    ]
                ],
            ),
        )

    # Получаем реферальные сведения
    refer = message.text[7:] if message.text.startswith("/start ") else None

    # Добавляем в базу данных пользователя или данные о его активности
    db.add_user(message.from_user.id, refer)
