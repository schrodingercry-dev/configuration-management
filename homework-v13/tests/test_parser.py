"""Тесты конструкций учебного конфигурационного языка."""

from __future__ import annotations

import unittest

from src.errors import ConfigurationError
from src.parser import parse


class ParserTests(unittest.TestCase):
    def test_parses_number(self) -> None:
        self.assertEqual(parse("-12.5"), -12.5)

    def test_parses_nested_lists_and_dictionaries(self) -> None:
        result = parse(
            "{ outer: { values: (list 1.0 (list 2.0 3.0)); }; }"
        )
        self.assertEqual(
            result,
            {"outer": {"values": [1.0, [2.0, 3.0]]}},
        )

    def test_evaluates_all_constant_operations(self) -> None:
        source = """
        base: 9.0
        {
          sum: .[+ base 1].;
          root: .[sqrt(base)].;
          biggest: .[max 1.0 base 4.0].;
        }
        """
        self.assertEqual(
            parse(source),
            {"sum": 10.0, "root": 3.0, "biggest": 9.0},
        )

    def test_evaluates_nested_expression(self) -> None:
        self.assertEqual(parse(".[sqrt .[+ 7 2].]."), 3.0)

    def test_rejects_integer_as_regular_value(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "дробную часть"):
            parse("{ value: 1; }")

    def test_rejects_missing_semicolon(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "ожидалось ';'"):
            parse("{ value: 1.0 }")

    def test_rejects_duplicate_dictionary_field(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "повторно"):
            parse("{ value: 1.0; value: 2.0; }")

    def test_rejects_unknown_constant(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "неизвестная"):
            parse(".[+ missing 1].")

    def test_rejects_negative_square_root(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "отрицательного"):
            parse(".[sqrt -1].")

    def test_rejects_empty_max(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "хотя бы один"):
            parse(".[max].")


if __name__ == "__main__":
    unittest.main()
