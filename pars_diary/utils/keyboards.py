"""Билдеры клавиатур."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

INSTRUCTION_URL = "https://telegra.ph/Instrukciya-po-registracii-v-bote-04-25"

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
    result = []
    regions = await parser.get_regions()

    for r, u in regions.items():
        result.append(
            [
                InlineKeyboardButton(
                    text=r,
                    callback_data=f"reg_1_{u}",
                ),
            ],
        )

    return InlineKeyboardMarkup(inline_keyboard=result)
