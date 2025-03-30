"""Общие клавиатуры.

Могут использоваться в нескольких обработчиках.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


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
