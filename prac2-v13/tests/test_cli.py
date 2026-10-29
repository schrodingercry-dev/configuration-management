"""Тесты параметров CLI этапа 1."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
    def test_prints_all_parameters_as_key_value_pairs(self) -> None:
        result = run_cli(
            "--package",
            "curl",
            "--repository",
            "https://archive.ubuntu.com/ubuntu",
            "--version",
            "8.5.0-2ubuntu10.6",
            "--ascii-tree",
            "--max-depth",
            "3",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "package: curl",
                "repository: https://archive.ubuntu.com/ubuntu",
                "test_mode: False",
                "version: 8.5.0-2ubuntu10.6",
                "ascii_tree: True",
                "max_depth: 3",
            ],
        )

    def test_accepts_existing_test_repository_file(self) -> None:
        with tempfile.NamedTemporaryFile() as repository:
            result = run_cli(
                "--package",
                "a",
                "--repository",
                repository.name,
                "--test-mode",
                "--version",
                "1.0",
                "--max-depth",
                "0",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("test_mode: True", result.stdout)
        self.assertIn("ascii_tree: False", result.stdout)

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
