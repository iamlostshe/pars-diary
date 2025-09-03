"""/ch - Классные часы."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from pars_diary.utils.ch import ch

router = Router(name=__name__)


# Базовые комманы (парсинг + небольшое изменение)
@router.message(Command("ch"))
async def ch_msg(msg: Message) -> None:
    """Отвечает за /ch."""
    # Создаем ответ
    answer = await ch()

    # Отвечаем пользователю
    await msg.answer_photo(
        answer[0],
        answer[1],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подробнее", url=answer[2])],
            ],
        ),
    )
