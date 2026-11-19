"""Тесты лексического анализатора."""

from __future__ import annotations

import unittest

from src.errors import ConfigurationError
from src.lexer import tokenize


class LexerTests(unittest.TestCase):
    def test_skips_comments_and_tracks_lines(self) -> None:
        tokens = tokenize("NB. comment\n{ value: 1.0; }")
        self.assertEqual(tokens[0].kind, "LBRACE")
        self.assertEqual(tokens[0].line, 2)

    def test_rejects_invalid_character(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "недопустимый"):
            tokenize("{")
            tokenize("@")


if __name__ == "__main__":
    unittest.main()
