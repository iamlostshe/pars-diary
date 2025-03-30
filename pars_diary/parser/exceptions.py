"""Общие исключение.

Во время работы бота могут возникнуть некоторые исключения.
"""

# Базовая ошибка
# ==============


class DiaryParserError(Exception):
    """Базовая ошибка в проекте."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


# Исключения парсера
# ==================


class UserNotAuthenticatedError(DiaryParserError):
    """Пользователь не найден или не авторизован."""

    def __init__(self) -> None:
        super().__init__(
            "<b>Ошибка парсера</b>: "
            "Для выполнения этого действия необходимо авторизоваться в боте."
            "\n\nИнструкция по авторизации доступна по -> /start"
        )


class ValidationError(DiaryParserError):
    """Ошибка валидации данных."""

    def __init__(self) -> None:
        super().__init__(
            "<b>Ошибка парсера</b>: "
            "Не удалось обработать полученные данные."
            "\n\nИнструкция по авторизации доступна по -> /start"
        )


class ParseTimeoutError(DiaryParserError):
    """Превышено время ожидания ответа сервера."""

    def __init__(self) -> None:
        super().__init__(
            "<b>Ошибка парсера</b>: "
            "Превышено время ожидания отклика сервера. "
            "\n\nОшибка на стороне сервера дневника, и не зависит от бота."
            "\nПопробуйте повторить запрос чуть позже."
        )


class UnexpectedStatusCodeError(DiaryParserError):
    """Неожиданный статус-код от сервера."""

    def __init__(self, status_code: int) -> None:
        super().__init__(
            "<b>Ошибка парсера</b>: "
            f"Сервер вернул неожиданный результат -> {status_code} "
        )


# Исключения базы данных
# ======================


class DatabaseError(DiaryParserError):
    """Исключения, возникающие во время работы с базой данных."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UserNotAuthorizedError(DatabaseError):
    """Пользователь не авторизован."""

    def __init__(self) -> None:
        super().__init__(
            "<b>Ошибка базы данных</b>: "
            "Для выполнения этого действия необходимо авторизоваться в боте."
            "\n\nИнструкция по авторизации доступна по -> /start"
        )


class UserNotFoundError(DatabaseError):
    """Пользователь не найден в базе данных."""

    def __init__(self) -> None:
        super().__init__(
            "<b>Ошибка базы данных</b>: "
            "Пользователь не найден. Попробуйте зарегистрироваться повторно "
            "(инструкция -> /start)"
        )


class DBFileNotFoundError(DatabaseError):
    """Файл базы данных не найден."""

    def __init__(self, db_name: str) -> None:
        super().__init__(f"<b>Ошибка данных</b>: Файл {db_name} не найден.")


# Исключения в домашних заданиях
# ==============================


class DayIndexError(DiaryParserError):
    """Неправильный индекс дня."""

    def __init__(self) -> None:
        self.text = "<b>Ошибка модуля дз</b> Неправильно задан день недели."


# Исключения при работа с AI
# ==========================


class ChatGPTError(Exception):
    """Ошибка при работе с нейросетью."""

    def __init__(self, text: str) -> None:
        self.text = f"<b>Ошибка ChatGPT API</b>: {text}"
