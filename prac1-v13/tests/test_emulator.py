"""Тесты первых трёх этапов практической работы, вариант 13."""
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from src.emulator import execute, load_vfs, parse_command

ROOT = Path(__file__).resolve().parents[1]


class EmulatorTests(unittest.TestCase):
    """Проверяет парсер, команды, настройки и загрузку VFS."""

    def test_environment_expansion(self):
        """Проверяет раскрытие переменной окружения основной ОС."""
        os.environ["CM_TEST_VAR"] = "/tmp/example"
        self.assertEqual(parse_command("ls $CM_TEST_VAR"),
                         ["ls", "/tmp/example"])

    def test_quoted_arguments(self):
        """Проверяет сохранение аргумента с пробелами в кавычках."""
        self.assertEqual(parse_command('cd "two words"'),
                         ["cd", "two words"])

    def test_valid_vfs(self):
        """Проверяет загрузку трёх корректных примеров VFS."""
        for name in ("minimal", "several_files", "deep_tree"):
            with self.subTest(name=name):
                node = load_vfs(ROOT / "vfs" / f"{name}.json")
                self.assertEqual(node["type"], "directory")

    def test_invalid_vfs(self):
        """Проверяет отказ при повреждённом или отсутствующем файле VFS."""
        for name in ("invalid", "missing"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    load_vfs(ROOT / "vfs" / f"{name}.json")

    def test_commands(self):
        """Проверяет поддерживаемые команды и обработку ошибок."""
        config = SimpleNamespace(vfs="test.json", script="test.txt")
        cases = (("ls /tmp", (True, False)),
                 ("cd x", (True, False)),
                 ("conf-dump", (True, False)),
                 ("conf-dump extra", (False, False)),
                 ("unknown", (False, False)),
                 ("exit", (True, True)),
                 ("exit extra", (False, False)))
        for command, expected in cases:
            with self.subTest(command=command):
                with redirect_stdout(StringIO()):
                    self.assertEqual(execute(command, config), expected)

    def test_script_skips_errors(self):
        """Проверяет продолжение скрипта после ошибочной команды."""
        result = self.run_emulator("--script", "scripts/startup.txt")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Unknown command: unknown-command", result.stdout)
        self.assertIn("Command: ls", result.stdout)

    def test_missing_script(self):
        """Проверяет ошибку при отсутствии стартового скрипта."""
        result = self.run_emulator("--script", "missing.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Startup error:", result.stderr)

    def test_conf_dump(self):
        """Проверяет вывод путей, переданных через параметры CLI."""
        result = self.run_emulator("--vfs", "vfs/minimal.json",
                                   "--script", "scripts/startup.txt")
        self.assertIn("vfs_path=vfs/minimal.json", result.stdout)
        self.assertIn("script_path=scripts/startup.txt", result.stdout)

    @staticmethod
    def run_emulator(*args):
        """Запускает CLI в отдельном процессе с командой завершения."""
        return subprocess.run(
            [sys.executable, "-m", "src.emulator", *args],
            cwd=ROOT, input="exit\n", text=True,
            capture_output=True, check=False,
        )
