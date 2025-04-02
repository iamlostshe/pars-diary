"""Модуль для создания и отправки уведомлений."""

import asyncio
from itertools import zip_longest

from aiogram import Bot
from loguru import logger

from pars_diary.config import config, parser, users_db
from pars_diary.parser.db import UsersDataBase
from pars_diary.parser.exceptions import DiaryParserError, UserNotFoundError
from pars_diary.parser.parser import DiaryParser

# Константы
# =========

# Задержка между обычными уведомлениями (в часах, целое число)
NOTIFY_DURATION = 1

# Задержка между умными уведомлениями (в часах, целое число)
SMART_NOTIFY_DURATION = 24

# Вспомогательные функции отправки уведомлений
# ============================================


async def update_users(
    parser: DiaryParser,
    users_db: UsersDataBase,
    bot: Bot,
    smart_notify: bool | None = False,
) -> None:
    """Обновляет оценки пользователей."""
    # Обновляем базу данных пользователе
    for user_id, user in users_db:
        # Нету куков, нету уведомлений
        if user.cookie in (None, "demo"):
            continue

        old_grades = user.marks
        new_grades = parser.marks(user).split("\n")[3:-1]
        user.marks = new_grades
        users_db.update_user(int(user_id), user)

        # Есть уведомления? Уведомляем
        if user.notify:
            await check_notify(bot, user_id, new_grades, old_grades)

        # Если нужно отправить умное уведомление
        # и у пользователя включены умные уведомления
        if smart_notify and user.smart_notify:
            await check_smart_notify(bot, user_id, new_grades)

    users_db.write()


async def check_notify(
    bot: Bot, user_id: int, new_grades: dict, old_grades: dict
) -> None:
    """Проверяем изменения в оценках.

    Если есть изменения => отправляем уведомления.
    """
    logger.debug(f"Проверяем оценки для {user_id} на наличие изменений")
    diff_grades: list[str] = []

    # Ищем изменения
    for og, ng in zip_longest(old_grades, new_grades):
        if og is None:
            diff_grades.append(f"++ {ng}")
        elif ng is None:
            diff_grades.append(f"-- {og}")
        elif og != ng:
            diff_grades.append(f"{og} -> {ng}")

    # Если есть изменения => Отправляем
    if len(diff_grades) > 0:
        msg_text = (
            "У Вас изменились оценки (управление уведомлениями - /notify):\n"
            f"<pre>{'\n'.join(diff_grades)}</pre>"
        )
        await bot.send_message(user_id, msg_text, parse_mode="HTML")


async def check_smart_notify(bot: Bot, user_id: int, new_grades: dict) -> None:
    """Проверка наличия умных уведомлений."""
    logger.debug(f"Проверяю оценки для {user_id} по умному")

    # Задаём переменные под сообщение и спорные оценки
    bad_grades = ""
    questionable_grades = ""

    # TODO @iamlostshe: Получаем те, до которых не хватает одной-двух оценок
    # TODO @milinuri: Не, ты сначала с форматом разберись
    # Так перегонять оценки по строкам не удобно
    for grade_line in new_grades:
        if "│ " not in grade_line:
            continue

        grade = float(grade_line.split("│ ")[1])

        # Получаем 3 и 2
        if grade < 3.5:  # noqa: PLR2004
            bad_grades += f"\n- {grade}"

        # Получаем спорные
        elif 4.6 < grade < 4.4 or grade < 3.6:  # noqa: PLR2004
            questionable_grades += f"{grade}\n"

    # Отправляем полученное сообщение, если есть что отправлять
    if bad_grades != "" or questionable_grades != "":
        message = "Привет, вот персональная сводка по оценкам!\n"

        if bad_grades != "":
            message += (
                "\n<b>По этим предметам могут выйти плохие оценки "
                f"(2 и 3):</b>\n\n<pre>{bad_grades}</pre>\n"
            )

        if questionable_grades != "":
            message += (
                "\n<b>У вас есть спорные оценки:</b>\n\n"
                f"<pre>{questionable_grades}</pre>"
            )

        message += "\nУправление уведомлениями -> /notify"
        await bot.send_message(user_id, message, parse_mode="HTML")


# Главная функция
# ===============


async def main() -> None:
    """Запуск проверки уведомлений."""
    bot = Bot(token=config.telegram_token)
    time_counter = SMART_NOTIFY_DURATION

    while True:
        # Инициализируем переменную для проверки умных уведомлений
        smart_notify = False

        if time_counter >= SMART_NOTIFY_DURATION:
            smart_notify = True
            count = 0

        try:
            await update_users(parser, users_db, bot, smart_notify=smart_notify)

        except KeyError:
            logger.error(UserNotFoundError())

        except Exception as e:  # noqa: BLE001
            logger.error(DiaryParserError(str(e)))

        finally:
            await bot.session.close()

        # TODO @milinuri: Я буду ждать появления cron :)
        logger.debug(f"Ожидаю {NOTIFY_DURATION} час")
        await asyncio.sleep(NOTIFY_DURATION * 3600)
        count += NOTIFY_DURATION


# Запуск скрипта
# ==============

if __name__ == "__main__":
    asyncio.run(main())
