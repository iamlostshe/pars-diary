"""Нейросеть для помощи в учёбе."""

from pars_diary.config import gpt_client

SYS_MESSAGE = (
    '1) Тебя зовут "pars-diary".\n'
    "2) Ты дружелюбный и эффективный помощник в учёбе для школьников.\n"
    "3) Не используй markdown/html разметку."
    "4) Максимальная длинна твоего ответа - 4000 символов."
)


async def ask_gpt(prompt: str) -> str:
    """Обработка запроса gpt."""
    response = await gpt_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYS_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
