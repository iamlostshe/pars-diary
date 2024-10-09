# Integrated python modules
import asyncio
from os import getenv

# Modules need to be installed
from dotenv import load_dotenv
from loguru import logger

# aiogram
from aiogram import Bot, Dispatcher

# Импортируем хендлеры
from handlers import routers


# Starting bot
async def main() -> None:
    # Get token for telegram bot from .env
    load_dotenv()
    TOKEN = getenv('TOKEN_TG')

    # Initializating dp and bot
    dp = Dispatcher()
    bot = Bot(token=TOKEN)

    # Connect hendlers
    for r in routers:
        logger.info("Include router: {} ...", r.name)
        dp.include_router(r)

    # Starting
    logger.info('Bot start polling...')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())