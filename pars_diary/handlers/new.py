"""Авторизация в боте."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bars_api import BarsAPI

from pars_diary.types import User
from pars_diary.utils import db

router = Router(name=__name__)


async def add_user_cookie(user_id: str, provider: str, cookie: str) -> str:
    """Функция для проверки и обновления значения cookie."""
    if "sessionid=" not in cookie:
        return 'Ваши cookie должны содержать "sessionid="'
    if "sessionid=xxx..." in cookie:
        return "Нельзя использовать пример"

    # Тест путем запроса к серверу
    try:
        parser = BarsAPI(provider, cookie)
        await parser.get_person_data()

        db.add_user_cookie(user_id, cookie)

    except Exception as e:  # noqa: BLE001
        return f"Не правильно введены cookie, при проверке сервер выдаёт ошибку:\n\n{e}"

    else:
        return "Пользователь успешно добавлен в базу данных."


@router.message(Command("new"))
async def new_msg(msg: Message, user: User) -> None:
    """Отвечает за /new."""
    if msg.text == "/new":
        await msg.answer('Комманда работает так - "/new sessionid=xxx..."')
    else:
        await msg.answer(
            await add_user_cookie(
                msg.from_user.id,
                user.provider,
                msg.text[5:].replace("\n", ""),
            ),
        )
