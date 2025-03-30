"""Общие клавиатуры.

Могут использоваться в нескольких обработчиках.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from pars_diary.utils.pars import get_regions


def not_auth_keyboard() -> InlineKeyboardMarkup:
    """Если этот контент не доступен без авторизации (клавиатура)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("instruction"),
                    url="https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25",
                ),
            ],
        ],
    )


def reg_0() -> InlineKeyboardMarkup:
    """Начинаем регистрацию пользователя."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("start"), callback_data="reg_0")]
        ],
    )


def reg_1() -> InlineKeyboardMarkup:
    """Выбор региона пользователя."""
    regions = get_regions()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=r,
                    callback_data=f"reg_1_{u}",
                ),
            ]
            for r, u in regions.items()
        ]
    )


def reg_2() -> InlineKeyboardMarkup:
    """Получаем куки от пользователя."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("instruction"),
                    url="https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25",
                ),
            ],
        ],
    )
