"""Нейросеть для помощи в учебе."""

from secrets import choice

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.utils.gpt import ask_gpt

router = Router(name=__name__)


@router.message(Command("chatgpt"))
@router.message(Command("gpt"))
async def lessons_message(message: Message) -> None:
    """Отвечает за /gpt."""
    examples = (
        "Напиши сочинение по роману Отцы и дети",
        "Расскажи о теореме пифагора",
        "Что такое диактелизмы?",
        "Что такое гигабайт?",
        "Расскажи о булиевой алгебре",
        "Напиши реферат о лыжных гонках",
        "Что такое конфессия?",
        "Напиши ТТХ Автомата Калашникова",
        "Как рассчитать вероятность события?",
        "Напиши вступление проекта о создании telegram бота",
        "Что такое функциональная грамотность?",
    )

    if message.text in ("/chatgpt", "/gpt"):
        await message.answer(
            f'Комманда работает так - <b>"/gpt {choice(examples)}"</b>',
        )
    else:
        answer_message = await message.answer("Нейросеть думает...")
        await answer_message.edit_text(await ask_gpt(message.text.split(" ", 1)[1]))
