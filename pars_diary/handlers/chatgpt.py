"""Нейросеть для помощи в учебе."""

from secrets import choice

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pars_diary.services.ask_gpt import ask_gpt

router = Router(name=__name__)


# Нейронная сеть, для помощи в учебе
@router.message(Command("chatgpt"))
async def lessons_msg(msg: Message) -> None:
    """Спрашиваем у ChatGPT."""
    examples = [
        "Напиши сочинение по роману Отцы и дети",
        "Расскажи о теореме пифагора",
        "Что такое диалектизмы?",
        "Что такое гигабайт?",
        "Расскажи о булевой алгебре",
        "Напиши реферат о лыжных гонках",
        "Что такое конфессия?",
        "Напиши ТТХ Автомата Калашникова",
        "Как рассчитать вероятность события?",
        "Напиши вступление проекта о создании telegram бота",
        "Что такое функциональная грамотность?",
    ]

    if msg.text == "/chatgpt":
        await msg.answer(
            f'Команда работает так - <b>"/chatgpt {choice(examples)}"</b>',
            "HTML",
        )
    else:
        # TODO @iamlostshe: answer_msg = await msg.answer('ChatGPT думает...')
        send_text = await ask_gpt(
            " ".join(msg.text.split()[1:]),
            msg.from_user.first_name,
        )
        # TODO @iamlostshe: await msg.edit_text(send_text)

        # ВРЕМЕННОЕ РЕШЕНИЕ >>>
        await msg.answer(send_text)
