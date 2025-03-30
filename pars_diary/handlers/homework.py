"""Работа с домашним заданием.

Предоставляет:
- /hw: Домашнее задание на завтра
- /hw_week: Домашнее задание на неделю.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from pars_diary.parser.hw import Homework, chatgpt
from pars_diary.utils.hw import DAYS_SHORT

router = Router(name="Homework")

# Команды
# =======


@router.message(Command("hw"))
async def get_tomorrow_hw(message: Message) -> None:
    """получает домашнее задание на завтра."""
    hw = Homework(message.from_user.id).tomorrow()
    await message.answer(hw.message, hw.markup)


@router.message(Command("hw_week"))
async def get_week_hw(message: Message) -> None:
    """получает домашнее задание на неделю."""
    hw = Homework(message.from_user.id).week()
    await message.answer(hw.message, hw.markup)


# Callback обработчики
# ====================


@router.message(F.data == "hw_tomorrow")
async def call_tomorrow_hw(query: CallbackQuery) -> None:
    """получает домашнее задание на завтра."""
    hw = Homework(query.from_user.id).tomorrow()
    await query.message.answer(hw.message, hw.markup)


@router.message(F.data == "hw_week")
async def call_week_hw(query: CallbackQuery) -> None:
    """получает домашнее задание на неделю."""
    hw = Homework(query.from_user.id).week()
    await query.message.answer(hw.message, hw.markup)


# Домашнее задание на выбранный день
# ==================================


@router.message(F.data == "hw_days")
async def call_select_dya(query: CallbackQuery) -> None:
    """Клавиатура выбора дня недели для получения домашнего задания."""
    await query.message.edit_text(
        "Выбери день недели:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=day, callback_data=f"hw:{n}")
                    for n, day in enumerate(DAYS_SHORT[:-1])
                ]
            ]
        ),
    )


class DayHomework(CallbackData, prefix="hw"):
    """Для какого дня показывать домашнее задание."""

    day: int


@router.message(DayHomework.filter())
async def call_day_hw(query: CallbackQuery, callback_data: DayHomework) -> None:
    """получает домашнее задание на завтра."""
    hw = Homework(query.from_user.id).on_day(callback_data.day)
    await query.message.answer(hw.message, hw.markup)


# Помощь с дз от AI
# =================


class ChatHomework(CallbackData, prefix="chatgpt"):
    """Для какого дня показывать домашнее задание."""

    day: int
    index: int


@router.message(ChatHomework.filter())
async def call_gpt_hw(
    query: CallbackQuery, callback_data: ChatHomework
) -> None:
    """Отправляет сообщение для GPT чтобы он подсказал с заданием."""
    await query.message.edit_text("Chatgpt думает...")
    await query.message.edit_text(
        chatgpt(
            query.from_user.id,
            callback_data.day,
            callback_data.index,
            query.from_user.first_name,
        )
    )
