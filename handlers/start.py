"""Приветственное сообщение."""

from aiogram import Router
from aiogram.types import Message
from loguru import logger

from utils.db import add_user, get_cookie
from utils.keyboards import not_auth_keyboard, reg_0
from utils.messages import error, registration_0, start_old_user

router = Router(name=__name__)


# Команды /start, /help, любое другое сообщение, если предыдущие хендлеры не сработали
@router.message()
async def command_start_handler(msg: Message) -> None:
    """Отвечает за обработку любых сообщений, кроме указанных ранее."""
    # Выводим лог в консоль
    logger.debug("[m] {}", msg.text)

    # Проверяем ошибки
    try:
        # Если пользователь зарегистрирован (если не пустой ответ)
        if get_cookie(msg.from_user.id):
            # Отвечаем пользователю
            await msg.answer(
                start_old_user(msg.from_user.first_name, msg.from_user.language_code),
                reply_markup=not_auth_keyboard(),
            )

        # Если пользователь не зарегистрирован
        else:
            # Отвечаем пользователю
            await msg.answer(
                registration_0(msg.from_user.first_name, msg.from_user.language_code),
                reply_markup=reg_0(),
            )

        # Получаем реферальные сведения
        refer = msg.text[7:] if msg.text.startswith("/start ") else None

        # Добавляем в базу данных пользователя или данные о его активности
        add_user(msg.from_user.id, refer)

    except Exception as e:
        await msg.answer(error(e, msg.from_user.language_code), "HTML")
