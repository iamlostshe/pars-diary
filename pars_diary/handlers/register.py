"""процесс регистрации пользователя.

предоставляет:
- Создание новой сессии пользователя.
- Начало регистрации пользователя.
- Выбор региона пользователя.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.i18n import gettext as _

from pars_diary.parser.db import UsersDataBase
from pars_diary.utils.pars import get_regions

router = Router(name="User registration")

# Обработчики команд
# ==================


@router.message(Command("new"))
async def new_msg(
    msg: Message, command: CommandObject, db: UsersDataBase
) -> None:
    """Вход в новую учебную запись при помощи cookie."""
    if command.args is None:
        await msg.answer('Команда работает так - "/new sessionid=xxx..."')
        return

    await msg.answer(db.set_cookie(msg.from_user.id, command.args.strip()))


# callback обработчики
# ====================


@router.callback_query(F.data == "start_reg")
async def start_register_user(query: CallbackQuery) -> None:
    """Начало регистрации нового пользователя.

    Предлагает выбрать один из доступных регионов.
    """
    await query.message.edit_text(
        _("1. select_region"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=r, callback_data=f"reg_region:{u}")]
                for r, u in get_regions().items()
            ]
        ),
    )


class RegionCallback(CallbackData, prefix="reg_region"):
    """Выбранный пользователем регион при регистрации."""

    region: str


@router.callback_query(RegionCallback.filter())
async def select_region(
    query: CallbackQuery, callback_data: RegionCallback, db: UsersDataBase
) -> None:
    """Выбирает регион пользователя при регистрации."""
    db.set_server_name(query.from_user.id, callback_data.region)
    await query.message.edit_text(
        _("2. select cookie"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("instruction"),
                        url="https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25",
                    ),
                ],
            ],
        ),
    )
