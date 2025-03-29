"""Нейросеть для помощи в учёбе.

Использует API Hugging Face
"""

import aiohttp
from loguru import logger

from pars_diary.config import config


async def ask_gpt(prompt: str, firstname: str) -> str:
    """Отправляет запрос в ChatGPT и получает ответ."""
    logger.debug(f"[chatgpt] {prompt}")

    system_prompt = (
        'Тебя зовут "PARS-DIARY".\n'
        "Ты дружелюбный и эффективный помощник в учёбе.\n"
        "Отвечаешь только на русском языке, кроме случаев, когда "
        "тебя просит пользователь или в случае "
        "применения иностранных терминов.\n\n"
        f"Пользователя, который с тобой общается зовут {firstname}\n"
        "Желательно не использовать markdown- или html-разметку"
    )

    payload = {
        "message": prompt,
        "model": "2b_it_v2.gguf",
        "system_message": system_prompt,
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "repeat_penalty": 1.1,
    }

    headers = {"Authorization": f"Bearer {config.hf_token}"}

    async with aiohttp.ClientSession().post(
        "https://api-inference.huggingface.co/models/gokaygokay/Gemma-2-llamacpp/chat",
        json=payload,
        headers=headers,
    ) as response:
        if response.status == 200:  # noqa: PLR2004
            result = await response.json()
            logger.debug(f"[chatgpt] {result}")
            return result.get("generated_text", "Извините, произошла ошибка")

    return "К сожалению, данный функционал пока в разработке("
