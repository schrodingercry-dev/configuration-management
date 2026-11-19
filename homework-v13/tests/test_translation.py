"""Интеграционные тесты CLI, YAML и примеров."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.main import translate
from src.yaml_writer import dump_yaml


PROJECT_DIR = Path(__file__).resolve().parents[1]


class TranslationTests(unittest.TestCase):
    def test_yaml_writer_handles_nested_values(self) -> None:
        value = {"items": [1.0, {"nested": 2.0}], "empty": []}
        expected = (
            "items:\n"
            "  - 1.0\n"
            "  -\n"
            "    nested: 2.0\n"
            "empty:\n"
            "  []\n"
        )
        self.assertEqual(dump_yaml(value), expected)

    def test_two_examples_match_expected_yaml(self) -> None:
        for name in ("server", "experiment"):
            with self.subTest(name=name):
                source = PROJECT_DIR / "examples" / f"{name}.conf"
                expected = PROJECT_DIR / "examples" / f"{name}.yaml"
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "result.yaml"
                    translate(source, output)
                    self.assertEqual(
                        output.read_text(encoding="utf-8"),
                        expected.read_text(encoding="utf-8"),
                    )

    def test_cli_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.conf"
            output = root / "output.yaml"
            source.write_text("{ value: 1.5; }", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.main",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=PROJECT_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(), "value: 1.5\n")

    def test_cli_reports_syntax_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bad.conf"
            output = root / "output.yaml"
            source.write_text("{ value: 1.0 }", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.main",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=PROJECT_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("строка 1", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
