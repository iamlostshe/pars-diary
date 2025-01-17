"""Нейросеть для помощи в учёбе.

Использует API Hugging Face
"""

# TODO @iamlostshe: Желательно заменить на парсинг через requests
# вариант который реализован на данный момент полностью блокирует бота
# (в момент ожидания ответа от API бот не ответи)
# ЕЩЕ ОКАЗАЛОСЬ ЧТО У HF ЕСТЬ ЛИМИТЫ НА КОЛИЧЕСТВО ЗАПОСОВ
# => временно изолирован

# from gradio_client import Client
from loguru import logger

# from utils.load_env import HF_TOKEN


def ask_gpt(prompt: str, firstname: str) -> str:
    """Формирует запрос к API и возвращает ответ."""
    logger.debug(f"[chatgpt] {prompt}")

    # system_message =
    (
        'Тебя зовут "PARS-DIARY".\n'
        "Ты дружелюбный и эффективный помощник в учёбе.\n"
        "Отвечаешь только на русском языке, кроме случаев, когда "
        "тебя просит пользователь или в случае "
        "применения иностранных терминов.\n\n"
        f"Пользователя, который с тобой общается зовут {firstname}\n"
        "Желательно не использовать markdown- или html-разметку"
    )

    """
    client = Client("gokaygokay/Gemma-2-llamacpp", HF_TOKEN)
    result = client.predict(
        message=prompt,
        model="2b_it_v2.gguf",
        system_message=system_message,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        repeat_penalty=1.1,
        api_name="/chat"
    )

    logger.debug(f'[chatgpt] {result}')
    """

    return "К сожалению, данный функционал пока в разработке("
