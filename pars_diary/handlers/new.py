"""Авторизация в боте."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bars_api import BarsAPI

from pars_diary.types import User
from pars_diary.utils import db
from pars_diary.utils.keyboards import reg_1
from pars_diary.utils.messages import registration_1

router = Router(name=__name__)


async def add_user_cookie(user_id: str, provider: str, cookie: str) -> str:
    """Функция для проверки и обновления значения cookie."""
    if not provider:
        return (
            "Пожалуйста, укажите ваш регион -> /start, а затем повторно укажите cookie"
        )
    if "sessionid=" not in cookie:
        return 'Ваши cookie должны содержать "sessionid="'
    if "sessionid=xxx..." in cookie:
        return "Нельзя использовать пример"

    # Тест путем запроса к серверу
    try:
        async with BarsAPI(provider, cookie) as parser:
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


@router.callback_query(F.data == "reg_0")
async def callback_reg_0(callback_query: CallbackQuery) -> None:
    """Начальный этап авторизации."""
    await callback_query.message.edit_text(
        registration_1,
        reply_markup=await reg_1(),
    )
