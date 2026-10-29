"""CLI-визуализатор зависимостей пакетов."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

from .repository import RepositoryError, find_package, load_index_for_package


PACKAGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9+.-]*$")
PACKAGE_VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z.+:~\-]*$")


def package_name(value: str) -> str:
    """Проверить имя пакета в формате Ubuntu/Debian."""
    if not PACKAGE_NAME_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "имя пакета должно начинаться со строчной буквы или цифры "
            "и содержать только a-z, 0-9, '+', '-' и '.'"
        )
    return value


def package_version(value: str) -> str:
    """Проверить базовый формат версии пакета."""
    if not PACKAGE_VERSION_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "версия должна начинаться с буквы или цифры и не содержать пробелов"
        )
    return value


def non_negative_int(value: str) -> int:
    """Преобразовать строку в целое число, не меньше нуля."""
    try:
        result = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("глубина должна быть целым числом") from error
    if result < 0:
        raise argparse.ArgumentTypeError("глубина не может быть отрицательной")
    return result


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Ubuntu"
    )
    parser.add_argument(
        "--package",
        required=True,
        type=package_name,
        help="имя анализируемого пакета",
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="URL репозитория или путь к тестовому репозиторию",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="использовать файл тестового репозитория",
    )
    parser.add_argument(
        "--version",
        required=True,
        type=package_version,
        help="версия пакета",
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="включить вывод зависимостей в виде ASCII-дерева",
    )
    parser.add_argument(
        "--max-depth",
        required=True,
        type=non_negative_int,
        help="максимальная глубина анализа зависимостей",
    )
    return parser


def validate_repository(
    parser: argparse.ArgumentParser, repository: str, test_mode: bool
) -> None:
    """Проверить URL обычного репозитория или путь к тестовому файлу."""
    if test_mode:
        path = Path(repository)
        if not path.is_file():
            parser.error(f"файл тестового репозитория не найден: {repository}")
        return

    parsed = urlparse(repository)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        parser.error(
            "репозиторий должен быть корректным URL с протоколом http или https; "
            "для файла укажите --test-mode"
        )


def format_configuration(args: argparse.Namespace) -> str:
    """Представить конфигурацию в требуемом формате ключ-значение."""
    values = (
        ("package", args.package),
        ("repository", args.repository),
        ("test_mode", args.test_mode),
        ("version", args.version),
        ("ascii_tree", args.ascii_tree),
        ("max_depth", args.max_depth),
    )
    return "\n".join(f"{key}: {value}" for key, value in values)


def main(argv: list[str] | None = None) -> int:
    """Получить и вывести прямые зависимости пакета (этап 2)."""
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_repository(parser, args.repository, args.test_mode)
    if args.test_mode:
        parser.error("тестовый репозиторий будет поддержан на этапе 3")
    try:
        records, source_url = load_index_for_package(
            args.repository, args.package, args.version
        )
        package = find_package(records, args.package, args.version)
    except RepositoryError as error:
        parser.error(str(error))

    print(f"source: {source_url}")
    if package.dependencies:
        for dependency in package.dependencies:
            print(f"dependency: {dependency}")
    else:
        print("dependency: <none>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
