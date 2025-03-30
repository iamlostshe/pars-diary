"""Классификация ошибок."""


# unknown error
class UnknownError(Exception):
    """Неизвестная ошибка."""

    def __init__(self, e: Exception) -> None:
        """Неизвестная ошибка."""
        self.text = f"Неизвестная ошибка ({e})"
        super().__init__(self.text)


# pars.py
class UserNotAuthenticatedError(Exception):
    """Пользователь не найден."""

    def __init__(self) -> None:
        """Пользователь не найден."""
        self.text = (
            "<b>Ошибка во время парсинга:</b> "
            "Для выполнения этого действия необходимо авторизоваться в боте.\n\n"
            "Инструкция по авторизации доступна по -> "
            "/start (Server.UserNotAuthenticatedError)"
        )
        super().__init__(self.text)


class ValidationError(Exception):
    """Ошибка валидации."""

    def __init__(self) -> None:
        """Ошибка валидации."""
        self.text = (
            "<b>Ошибка во время парсинга:</b> "
            "Для выполнения этого действия необходимо авторизоваться в боте.\n\n"
            "Инструкция по авторизации доступна по -> /start (Client.ValidationError)"
        )
        super().__init__(self.text)


class MyTimeoutError(Exception):
    """Превышено время ожидания ответа сервера."""

    def __init__(self) -> None:
        """Превышено время ожидания ответа сервера."""
        self.text = (
            "<b>Ошибка во время парсинга:</b> "
            "Превышено время ожидания отклика сервера, "
            "ошибка на стороне сервера дневника, и не зависит "
            "от нас. Для исправления ситуации попробуйте повторить запрос чуть позже."
        )
        super().__init__(self.text)


class UnexpectedStatusCodeError(Exception):
    """Неожиданный статус-код."""

    def __init__(self, status_code: int) -> None:
        """Неожиданный статус-код."""
        self.text = (
            "<b>Ошибка во время парсинга:</b> Сервер вернул неожиданный статус-код "
            f"({status_code})"
        )
        super().__init__(self.text)


# db.py
class UserNotAuthorizatedError(Exception):
    """Пользователь не авторизован."""

    def __init__(self) -> None:
        """Пользователь не авторизован."""
        self.text = (
            "Для выполнения этого действия необходимо авторизоваться в боте.\n\n"
            "Инструкция по авторизации доступна по -> /start"
        )
        super().__init__(self.text)


class UserNotFoundError(Exception):
    """Пользователь не найден."""

    def __init__(self) -> None:
        """Пользователь не найден."""
        self.text = (
            "<b>Ошибка во время работы с базой данных:</b> "
            "Пользователь не найден. Попробуйте зарегистрироваться повторно "
            "(инструкция -> /start)"
        )
        super().__init__(self.text)


class DBFileNotFoundError(Exception):
    """Файл базы данных не найден."""

    def __init__(self, db_name: str) -> None:
        """Файл базы данных не найден."""
        self.text = f"<b>Ошибка во время работы с базой данных:</b> Файл {db_name} не найден."
        super().__init__(self.text)


# hw.py
class DayIndexError(Exception):
    """Неправильный индекс дня."""

    def __init__(self) -> None:
        """Неправильный индекс дня."""
        self.text = (
            "<b>Ошибка модуля работы с дз</b> Неправильно задан день недели"
        )


# ask_gpt.py
class ChatGPTError(Exception):
    """Ошибка при работе с нейросетью."""

    def __init__(self, text: str) -> None:
        """Ошибка при работе с нейросетью."""
        self.text = f"<b>Ошибка при работе с неросетью</b> {text}"
