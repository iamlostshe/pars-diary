"""Модуль запуска уведомлений."""

import asyncio

from loguru import logger

from notify.main import send_notify

# Задержка между обычными уведомлениями (в часах, целое число)
NOTIFY_DURATION = 1

# Задержка между умными уведомлениями (в часах, целое число)
SMART_NOTIFY_DURATION = 24


async def main() -> None:
    """Запуск проверки уведомлений."""
    # Счётчик часов
    count = SMART_NOTIFY_DURATION

    while True:
        logger.info("Выполняю проверку")

        # Инициализируем переменную для проверки умных уведомлений
        smart = False

        # Определяем нужно ли запускать умные уведомления
        if count >= SMART_NOTIFY_DURATION:
            # Меняем значение проверки умных уведомлений
            smart = True

            # Обнуляем счётчик
            count = 0

        # Запускаем скрипт отправки уведомлений
        await send_notify(smart)

        # Задержка (час в секундах)
        await asyncio.sleep(NOTIFY_DURATION * 3600)

        # Обновляем значение счётчика
        count += NOTIFY_DURATION


if __name__ == "__main__":
    asyncio.run(main())
