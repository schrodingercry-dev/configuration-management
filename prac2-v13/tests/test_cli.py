"""Тесты параметров CLI этапа 1."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.main import build_parser, format_configuration


PROJECT_DIR = Path(__file__).resolve().parents[1]


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.main", *arguments],
        cwd=PROJECT_DIR,
        text=True,
        capture_output=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_parser_keeps_all_stage1_parameters(self) -> None:
        args = build_parser().parse_args(
            [
            "--package",
            "curl",
            "--repository",
            "https://archive.ubuntu.com/ubuntu",
            "--version",
            "8.5.0-2ubuntu10.6",
            "--ascii-tree",
            "--max-depth",
            "3",
            ]
        )

        self.assertEqual(
            format_configuration(args).splitlines(),
            [
                "package: curl",
                "repository: https://archive.ubuntu.com/ubuntu",
                "test_mode: False",
                "version: 8.5.0-2ubuntu10.6",
                "ascii_tree: True",
                "max_depth: 3",
            ],
        )

    def test_runs_with_test_repository(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
        ) as repository:
            repository.write("A: B\nB:\n")
            repository.flush()
            result = run_cli(
                "--package",
                "A",
                "--repository",
                repository.name,
                "--test-mode",
                "--version",
                "1.0",
                "--ascii-tree",
                "--max-depth",
                "2",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"A" -> "B"', result.stdout)
        self.assertIn("ASCII tree:\nA\n└── B", result.stdout)

    def test_rejects_missing_required_parameter(self) -> None:
        result = run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required", result.stderr)

    def test_rejects_invalid_package_name(self) -> None:
        result = run_cli(
            "--package",
            "Bad Package",
            "--repository",
            "https://example.org/ubuntu",
            "--version",
            "1.0",
            "--max-depth",
            "1",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("имя пакета", result.stderr)

    def test_rejects_invalid_repository_url(self) -> None:
        result = run_cli(
            "--package",
            "curl",
            "--repository",
            "example.org/ubuntu",
            "--version",
            "1.0",
            "--max-depth",
            "1",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("корректным URL", result.stderr)

    def test_rejects_missing_test_repository_file(self) -> None:
        result = run_cli(
            "--package",
            "a",
            "--repository",
            "missing-repository.txt",
            "--test-mode",
            "--version",
            "1.0",
            "--max-depth",
            "1",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("не найден", result.stderr)

    def test_rejects_invalid_package_version(self) -> None:
        result = run_cli(
            "--package",
            "curl",
            "--repository",
            "https://example.org/ubuntu",
            "--version",
            "bad version",
            "--max-depth",
            "1",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("версия", result.stderr)

    def test_rejects_negative_or_non_integer_depth(self) -> None:
        base = (
            "--package",
            "curl",
            "--repository",
            "https://example.org/ubuntu",
            "--version",
            "1.0",
            "--max-depth",
        )
        for value in ("-1", "two"):
            with self.subTest(value=value):
                result = run_cli(*base, value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("глубин", result.stderr)

    def test_rejects_values_after_boolean_flags(self) -> None:
        result = run_cli(
            "--package",
            "curl",
            "--repository",
            "https://example.org/ubuntu",
            "--test-mode=false",
            "--version",
            "1.0",
            "--ascii-tree=yes",
            "--max-depth",
            "1",
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
