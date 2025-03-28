"""Билдеры сообщений."""

# TODO @iamlostshe: Додель поддержку английского языка

# Врядли ботом будет пользоваться не говорящий
# по русски человек. Эта функция нужна больше
# для эстетики, ибо у меня, думаю как и у многих
# тг на английском и было бы приятнее получать
# ответы на английском)

from __future__ import annotations

# Modules need to be installed
from loguru import logger

# Writed by me modules
from utils import db
from utils.load_env import GIT_URL


def start_old_user(first_name: int | str, lang_code: str | None = "ru") -> str:
    """Начало для старых пользователей."""
    if lang_code != "ru":
        lang_code = "en"

    return (
        f"👾 Здравствуйте, {first_name}!\n\n"
        "⭐️ Доступные комманды:\n\n"
        "/start - Начать диалог\n"
        "/me - Данные о тебе\n"
        "/ch - Классные часы\n"
        "/events - Ивенты\n"
        "/birtdays - Дни рождения\n"
        "/marks - Оценки\n"
        "/i_marks - Итоговые оценки\n"
        "/hw - Домашнее задание\n\n"
        '💡 Всегда доступны в "Меню" (нижний левый угол).'
    )


def error(e: str, lang_code: str | None = "ru", notify: bool | None = False) -> str:
    """Сообщение об ошибке."""
    if lang_code != "ru":
        lang_code = "en"

    text_e = f"Ошибка во время отправки уведомления ({e})" if notify else e

    logger.error(e)

    return (
        "Произошла непредвиденная ошибка, возможно "
        "информация ниже поможет вам понять в чем дело:\n\n"
        "Ошибка:\n\n"
        f"{type(e).__name__}\n\n"
        "Пояснение:\n\n"
        f"{text_e}\n\n"
        "Если ошибка произошла не по вашей вине напишите админу @iamlostshe"
    )


def not_auth(lang_code: None = "ru") -> str:
    """Если этот контент не доступен без авторизациия."""
    if lang_code != "ru":
        lang_code = "en"

    return "Для выполнения этого действия вам необходимо зарегистрироваться."


def about(lang_code: None = "ru") -> str:
    """Информация о боте."""
    if lang_code != "ru":
        lang_code = "en"

    return (
        "<b>PARS-DIARY</b> - это проект с открытым исходным кодом, направленный "
        "на улучшение успеваемости учеников путем введения современных технологий.\n\n"
        "Что отличает нас от конкурентов?\n\n"
        "- <b>Бесплатно</b>\n"
        "- <b>Открыто</b>\n"
        "- <b>Безопасно</b>\n"
        "- <b>Эффективно</b>\n"
        "- <b>Есть функционал уведомлений</b>\n"
        "- <b>Есть функционал умных уведомлений*</b>\n"
        "- <b>Есть интеграции с нейросетями и инструменты "
        "для быстрого решения домашнего задания</b>\n\n\n"
        "*<b>умные уведомления</b> - [в разработке] уникальная функция "
        "для анализа оценок и простых уведомлений, например:\n\n"
        "<blockquote>Спорная оценка по математике, "
        "необходимо исправить, иначе может выйти 4!\n\n"
        "Для настройки уведомлений используйте /notify\n"
        "</blockquote>\n"
        "или\n\n"
        "<blockquote>Вам не хватает всего 0.25 балла до "
        "оценки 5, стоит постараться!\n\n"
        "Для настройки уведомлений используйте /notify\n"
        "</blockquote>\n\n"
        "Что-то сломалось? - пиши админу @iamlostshe\n\n"
        f"<b>Исходный код</b>: {GIT_URL}"
    )


def registration_0(first_name: int | str, lang_code: str | None = "ru") -> str:
    """Начало для новых пользоватлей."""
    if lang_code != "ru":
        lang_code = "en"

    return (
        f"👾 Добро пожаловать, {first_name}!\n\n"
        "Для начала Вам нужно пройти небольшую регистрацию в боте."
    )


def registration_1(lang_code: str | None = "ru") -> str:
    """Начало для новых пользоватлей."""
    if lang_code != "ru":
        lang_code = "en"

    return "1. Укажите Ваш регион:"


def registration_2(lang_code: str | None = "ru") -> str:
    """Начало для новых пользоватлей."""
    if lang_code != "ru":
        lang_code = "en"

    return "2. Укажите Ваши cookie:\n\n"
