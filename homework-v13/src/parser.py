"""Синтаксический анализ и вычисление константных выражений."""

from __future__ import annotations

import math
from typing import Any

from .errors import ConfigurationError
from .lexer import Token, tokenize


class Parser:
    """Рекурсивный нисходящий парсер учебного языка."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0
        self.constants: dict[str, Any] = {}

    @property
    def current(self) -> Token:
        """Вернуть текущий токен."""
        return self.tokens[self.position]

    def peek(self, offset: int = 1) -> Token:
        """Посмотреть следующий токен без изменения позиции."""
        target = min(self.position + offset, len(self.tokens) - 1)
        return self.tokens[target]

    def accept(self, kind: str) -> Token | None:
        """Принять токен указанного типа, если он текущий."""
        if self.current.kind != kind:
            return None
        token = self.current
        self.position += 1
        return token

    def expect(self, kind: str, description: str) -> Token:
        """Принять обязательный токен или сообщить об ошибке."""
        token = self.accept(kind)
        if token is None:
            self.fail(f"ожидалось {description}")
        return token

    def fail(self, message: str, token: Token | None = None) -> None:
        """Вызвать ошибку в позиции указанного или текущего токена."""
        target = token or self.current
        raise ConfigurationError(message, target.line, target.column)

    def parse(self) -> Any:
        """Разобрать объявления констант и итоговое значение."""
        while self.current.kind == "NAME" and self.peek().kind == "COLON":
            self.parse_constant()

        if self.current.kind == "EOF":
            self.fail("после констант отсутствует итоговая конфигурация")

        result = self.parse_value()
        self.expect("EOF", "конец файла")
        return result

    def parse_constant(self) -> None:
        """Разобрать объявление константы времени трансляции."""
        name_token = self.expect("NAME", "имя константы")
        self.expect("COLON", "':'")
        value = self.parse_value()
        if name_token.value in self.constants:
            self.fail(
                f"константа {name_token.value!r} объявлена повторно",
                name_token,
            )
        self.constants[name_token.value] = value

    def parse_value(self) -> Any:
        """Разобрать число, массив, словарь или выражение."""
        if self.current.kind == "NUMBER":
            token = self.expect("NUMBER", "число")
            if "." not in token.value:
                self.fail(
                    "число в конфигурации должно иметь дробную часть",
                    token,
                )
            return float(token.value)
        if self.current.kind == "LPAREN":
            return self.parse_list()
        if self.current.kind == "LBRACE":
            return self.parse_dictionary()
        if self.current.kind == "EXPR_START":
            return self.parse_expression()
        self.fail("ожидалось значение")

    def parse_list(self) -> list[Any]:
        """Разобрать массив в форме ``(list значение ...)``."""
        self.expect("LPAREN", "'('")
        marker = self.expect("NAME", "слово list")
        if marker.value != "list":
            self.fail("массив должен начинаться со слова list", marker)
        values: list[Any] = []
        while self.current.kind != "RPAREN":
            if self.current.kind == "EOF":
                self.fail("массив не закрыт символом ')'")
            values.append(self.parse_value())
        self.expect("RPAREN", "')'")
        return values

    def parse_dictionary(self) -> dict[str, Any]:
        """Разобрать словарь с обязательными точками с запятой."""
        self.expect("LBRACE", "'{'")
        result: dict[str, Any] = {}
        while self.current.kind != "RBRACE":
            if self.current.kind == "EOF":
                self.fail("словарь не закрыт символом '}'")
            name_token = self.expect("NAME", "имя поля")
            self.expect("COLON", "':'")
            value = self.parse_value()
            self.expect("SEMICOLON", "';'")
            if name_token.value in result:
                self.fail(
                    f"поле {name_token.value!r} задано повторно",
                    name_token,
                )
            result[name_token.value] = value
        self.expect("RBRACE", "'}'")
        return result

    def parse_expression(self) -> float:
        """Разобрать и сразу вычислить константное выражение."""
        self.expect("EXPR_START", "'.['")
        operation = self.current
        if self.accept("PLUS"):
            operation_name = "+"
        else:
            operation_name = self.expect("NAME", "операцию").value

        parenthesized = self.accept("LPAREN") is not None
        arguments: list[float] = []
        end_kind = "RPAREN" if parenthesized else "EXPR_END"
        while self.current.kind != end_kind:
            if self.current.kind == "EOF":
                self.fail("константное выражение не закрыто")
            arguments.append(self.parse_operand())

        if parenthesized:
            self.expect("RPAREN", "')'")
        self.expect("EXPR_END", "'].'")
        return self.evaluate(operation_name, arguments, operation)

    def parse_operand(self) -> float:
        """Разобрать число, константу или вложенное выражение."""
        if self.current.kind == "NUMBER":
            token = self.expect("NUMBER", "число")
            return float(token.value)
        if self.current.kind == "NAME":
            token = self.expect("NAME", "имя константы")
            if token.value not in self.constants:
                self.fail(f"неизвестная константа {token.value!r}", token)
            value = self.constants[token.value]
            if not isinstance(value, (int, float)):
                self.fail(
                    f"константа {token.value!r} не является числом",
                    token,
                )
            return float(value)
        if self.current.kind == "EXPR_START":
            return self.parse_expression()
        self.fail("ожидался аргумент константного выражения")

    def evaluate(
        self,
        operation: str,
        arguments: list[float],
        token: Token,
    ) -> float:
        """Выполнить разрешённую операцию времени трансляции."""
        if operation == "+":
            if len(arguments) != 2:
                self.fail("сложение требует два аргумента", token)
            return arguments[0] + arguments[1]
        if operation == "sqrt":
            if len(arguments) != 1:
                self.fail("sqrt требует один аргумент", token)
            if arguments[0] < 0:
                self.fail("sqrt не определён для отрицательного числа", token)
            return math.sqrt(arguments[0])
        if operation == "max":
            if not arguments:
                self.fail("max требует хотя бы один аргумент", token)
            return max(arguments)
        self.fail(f"неизвестная операция {operation!r}", token)


def parse(source: str) -> Any:
    """Разобрать исходный текст и вернуть готовую структуру Python."""
    return Parser(tokenize(source)).parse()
