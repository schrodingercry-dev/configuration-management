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


def tokenize(source: str) -> list[Token]:
    """Преобразовать исходный текст в последовательность токенов."""
    tokens: list[Token] = []
    index = 0
    line = 1
    column = 1

    def advance(text: str) -> None:
        nonlocal line, column
        newline_count = text.count("\n")
        if newline_count:
            line += newline_count
            column = len(text.rsplit("\n", 1)[-1]) + 1
        else:
            column += len(text)

    while index < len(source):
        if source.startswith("NB.", index):
            end = source.find("\n", index)
            if end == -1:
                end = len(source)
            comment = source[index:end]
            advance(comment)
            index = end
            continue

        if source.startswith(".[", index):
            tokens.append(Token("EXPR_START", ".[", line, column))
            advance(".[")
            index += 2
            continue

        if source.startswith("].", index):
            tokens.append(Token("EXPR_END", "].", line, column))
            advance("].")
            index += 2
            continue

        character = source[index]
        if character.isspace():
            advance(character)
            index += 1
            continue

        number_match = NUMBER_RE.match(source, index)
        if number_match:
            value = number_match.group()
            tokens.append(Token("NUMBER", value, line, column))
            advance(value)
            index = number_match.end()
            continue

        name_match = NAME_RE.match(source, index)
        if name_match:
            value = name_match.group()
            tokens.append(Token("NAME", value, line, column))
            advance(value)
            index = name_match.end()
            continue

        kind = SYMBOLS.get(character)
        if kind:
            tokens.append(Token(kind, character, line, column))
            advance(character)
            index += 1
            continue

        raise ConfigurationError(
            f"недопустимый символ {character!r}",
            line,
            column,
        )

    tokens.append(Token("EOF", "", line, column))
    return tokens
