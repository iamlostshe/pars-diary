"""Общие сообщения.

Доступные сразу в нескольких обработчиках.
"""

from aiogram.utils.i18n import gettext as _


def start_old_user(first_name: str) -> str:
    """Начало для старых пользователей."""
    return (
        f"👾 Здравствуйте, {first_name}!\n\n"
        "⭐️ Доступные команды:\n\n"
        "/start - Начать диалог\n"
        "/me - Данные о тебе\n"
        "/ch - Классные часы\n"
        "/events - Ивенты\n"
        "/birthdays - Дни рождения\n"
        "/marks - Оценки\n"
        "/i_marks - Итоговые оценки\n"
        "/hw - Домашнее задание\n\n"
        '💡 Всегда доступны в "Меню" (нижний левый угол).'
    )


def error_message(e: str) -> str:
    """Сообщение об ошибке."""
    return (
        "Произошла непредвиденная ошибка, возможно "
        "информация ниже поможет вам понять в чем дело:\n\n"
        "Ошибка:\n\n"
        f"{type(e).__name__}\n\n"
        "Пояснение:\n\n"
        f"{e}\n\n"
        "Если ошибка произошла не по вашей вине напишите админу @iamlostshe"
    )


def not_auth() -> str:
    """Если этот контент не доступен без авторизации."""
    return _("need auth for action")


# Процесс регистрации
# ===================


def registration_0(first_name: str) -> str:
    """Начало для новых пользователей."""
    return _("welcome, {first_name}! you need register.").format(first_name)


def registration_1() -> str:
    """Начало для новых пользователей."""
    return _("1. select_region")


def registration_2() -> str:
    """Начало для новых пользователей."""
    return _("2. select cookie")
