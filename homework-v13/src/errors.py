"""Ошибки транслятора с указанием позиции во входном файле."""

from __future__ import annotations


class ConfigurationError(Exception):
    """Синтаксическая или вычислительная ошибка конфигурации."""

    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"строка {line}, столбец {column}: {message}")
