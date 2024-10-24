# TODO Можно заменить на парсинг через requests
# вариант который реализован на данный момент полностью блокирует бота
# (в момент ожидания ответа от API бот не ответи)

from gradio_client import Client
from loguru import logger

def ask_gpt(prompt: str, system_prompt: str | None = 'You are a helpful assistant.') -> str:
    logger.debug(prompt)

    client = Client("gokaygokay/Gemma-2-llamacpp")
    result = client.predict(
            message=prompt,
            model="2b_it_v2.gguf",
            system_message=system_prompt,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            repeat_penalty=1.1,
            api_name="/chat"
    )
    
    logger.debug(result)
    return result