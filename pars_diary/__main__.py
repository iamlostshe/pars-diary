"""Запуск бота."""

import asyncio

from .bot import main

if __name__ == "__main__":
    asyncio.run(main())
