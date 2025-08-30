"""Собирает все мидлвари во едино."""

from .db import DataBaseMiddleware

mv = (DataBaseMiddleware, )

__all__ = ("mv",)
