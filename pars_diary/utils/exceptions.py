"""Классификация ошибок."""


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
        self.text = (
            f"<b>Ошибка во время работы с базой данных:</b> Файл {db_name} не найден."
        )
        super().__init__(self.text)


# hw.py
class DayIndexError(Exception):
    """Неправильный индекс дня."""

    def __init__(self) -> None:
        """Неправильный индекс дня."""
        self.text = "<b>Ошибка модуля работы с дз</b> Неправильно задан день недели"


# ask_gpt.py
class ChatGPTError(Exception):
    """Ошибка при работе с нейросетью."""

    def __init__(self, text: str) -> None:
        """Ошибка при работе с нейросетью."""
        self.text = f"<b>Ошибка при работе с неросетью</b> {text}"
