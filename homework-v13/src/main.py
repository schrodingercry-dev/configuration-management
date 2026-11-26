"""Командная строка транслятора учебного языка в YAML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

from src.errors import ConfigurationError
from src.parser import parse
from src.yaml_writer import dump_yaml


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Транслятор учебного конфигурационного языка в YAML"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="путь к входному файлу",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="путь к выходному YAML-файлу",
    )
    return parser


def translate(input_path: Path, output_path: Path) -> None:
    """Прочитать конфигурацию, преобразовать и записать YAML."""
    source = input_path.read_text(encoding="utf-8")
    result = parse(source)
    output_path.write_text(dump_yaml(result), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Запустить трансляцию и обработать пользовательские ошибки."""
    arguments = build_parser().parse_args(argv)
    try:
        translate(arguments.input, arguments.output)
    except ConfigurationError as error:
        print(f"syntax error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"file error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
