"""Typing."""

# TODO(@): Тут цикличный импорт будет, если стили пробрасывать
#from bars_api import BarsAPI  # noqa: ERA001


class User:
    """Пользователь."""

    is_auth: bool
    is_admin: bool
    parser: any
