"""Билдеры клавиатур."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bars_api import BarsAPI

INSTRUCTION_URL = "https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25"
CHECK_SUB_CHANNEL = "https://t.me/+Bgus_b4EFSZiYmQy"

not_sub_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться",
                url=CHECK_SUB_CHANNEL,
            ),
        ],
    ],
)

not_auth_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Инструкция",
                url=INSTRUCTION_URL,
            ),
        ],
    ],
)
reg_0 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Начнём!", callback_data="reg_0")]],
)
reg_2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Инструкция",
                url=INSTRUCTION_URL,
            ),
        ],
    ],
)


async def reg_1() -> InlineKeyboardMarkup:
    """Нулевая стадия регистрации."""
    async with BarsAPI() as parser:
        regions = await parser.get_regions()

    return InlineKeyboardMarkup(
        inline_keyboard=(
            [
                InlineKeyboardButton(
                    text=r,
                    callback_data=f"reg_1_{u}",
                ),
            ]
            for r, u in regions.items()
        ),
    )
