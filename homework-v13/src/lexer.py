"""Лексический анализ учебного конфигурационного языка."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import ConfigurationError


NUMBER_RE = re.compile(r"[+-]?\d+(?:\.\d+)?")
NAME_RE = re.compile(r"[_a-z]+")


@dataclass(frozen=True)
class Token:
    """Один элемент входного языка."""

    kind: str
    value: str
    line: int
    column: int


SYMBOLS = {
    "{": "LBRACE",
    "}": "RBRACE",
    "(": "LPAREN",
    ")": "RPAREN",
    ":": "COLON",
    ";": "SEMICOLON",
    "+": "PLUS",
}


class Lexer:
    """Последовательно преобразовывать исходный текст в токены."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[Token] = []
        self.index = 0
        self.line = 1
        self.column = 1

    def advance(self, text: str) -> None:
        """Сдвинуть текущую позицию с учётом переводов строк."""
        newline_count = text.count("\n")
        if newline_count:
            self.line += newline_count
            self.column = len(text.rsplit("\n", 1)[-1]) + 1
        else:
            self.column += len(text)

    def add_token(self, kind: str, value: str) -> None:
        """Добавить токен и перейти к следующему фрагменту."""
        self.tokens.append(Token(kind, value, self.line, self.column))
        self.advance(value)
        self.index += len(value)

    def skip_comment(self) -> None:
        """Пропустить комментарий от ``NB.`` до конца строки."""
        end = self.source.find("\n", self.index)
        if end == -1:
            end = len(self.source)
        comment = self.source[self.index:end]
        self.advance(comment)
        self.index = end

    def match_pattern(self, pattern: re.Pattern[str], kind: str) -> bool:
        """Добавить токен, если регулярное выражение совпало."""
        match = pattern.match(self.source, self.index)
        if match is None:
            return False
        self.add_token(kind, match.group())
        return True

    def scan_token(self) -> None:
        """Распознать один токен или пропустить служебный текст."""
        if self.source.startswith("NB.", self.index):
            self.skip_comment()
            return
        delimiters = ((".[", "EXPR_START"), ('].', "EXPR_END"))
        for value, kind in delimiters:
            if self.source.startswith(value, self.index):
                self.add_token(kind, value)
                return

        character = self.source[self.index]
        if character.isspace():
            self.advance(character)
            self.index += 1
            return
        if self.match_pattern(NUMBER_RE, "NUMBER"):
            return
        if self.match_pattern(NAME_RE, "NAME"):
            return

        kind = SYMBOLS.get(character)
        if kind:
            self.add_token(kind, character)
            return
        raise ConfigurationError(
            f"недопустимый символ {character!r}",
            self.line,
            self.column,
        )

    def tokenize(self) -> list[Token]:
        """Преобразовать весь исходный текст в токены."""
        while self.index < len(self.source):
            self.scan_token()
        self.tokens.append(Token("EOF", "", self.line, self.column))
        return self.tokens


def tokenize(source: str) -> list[Token]:
    """Преобразовать исходный текст в последовательность токенов."""
    return Lexer(source).tokenize()
