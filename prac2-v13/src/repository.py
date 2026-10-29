"""Чтение индекса Packages репозитория Ubuntu без пакетных менеджеров."""

from __future__ import annotations

import gzip
import lzma
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_INDEX_PATHS = (
    "dists/noble-updates/main/binary-amd64/Packages.xz",
    "dists/noble/main/binary-amd64/Packages.xz",
    "dists/noble-updates/universe/binary-amd64/Packages.xz",
    "dists/noble/universe/binary-amd64/Packages.xz",
)


class RepositoryError(Exception):
    """Ошибка чтения или поиска данных в репозитории."""


@dataclass(frozen=True)
class PackageRecord:
    """Минимальные сведения о пакете из файла Packages."""

    name: str
    version: str
    dependencies: tuple[str, ...]


def candidate_urls(repository_url: str) -> tuple[str, ...]:
    """Получить URL индексов для прямого URL или корня Ubuntu-репозитория."""
    clean_url = repository_url.rstrip("/")
    if clean_url.endswith(("/Packages", "/Packages.gz", "/Packages.xz")):
        return (clean_url,)
    return tuple(f"{clean_url}/{path}" for path in DEFAULT_INDEX_PATHS)


def download_index(url: str) -> str:
    """Скачать и распаковать Packages.

    Для загрузки используются только средства стандартной библиотеки.
    """
    try:
        with urlopen(url, timeout=30) as response:
            data = response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise RepositoryError(f"не удалось загрузить {url}: {error}") from error

    try:
        if url.endswith(".gz"):
            data = gzip.decompress(data)
        elif url.endswith(".xz"):
            data = lzma.decompress(data)
        return data.decode("utf-8")
    except (OSError, UnicodeDecodeError, lzma.LZMAError) as error:
        raise RepositoryError(f"не удалось распаковать индекс {url}") from error


def parse_control_stanzas(text: str) -> list[dict[str, str]]:
    """Разобрать абзацы Debian Control из файла Packages."""
    stanzas: list[dict[str, str]] = []
    current: dict[str, str] = {}
    last_key: str | None = None

    for line in (*text.splitlines(), ""):
        if not line:
            if current:
                stanzas.append(current)
                current = {}
                last_key = None
            continue
        if line[0].isspace() and last_key:
            current[last_key] += " " + line.strip()
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        last_key = key
        current[key] = value.strip()

    return stanzas


def dependency_names(value: str) -> tuple[str, ...]:
    """Извлечь имена зависимостей, выбирая первую альтернативу каждой группы."""
    result: list[str] = []
    for group in value.split(","):
        first_alternative = group.split("|", 1)[0].strip()
        name = first_alternative.split("(", 1)[0].split("[", 1)[0].strip()
        name = name.split(":", 1)[0]
        if name and name not in result:
            result.append(name)
    return tuple(result)


def record_from_stanza(stanza: dict[str, str]) -> PackageRecord | None:
    """Преобразовать абзац Packages в используемую модель."""
    name = stanza.get("Package")
    version = stanza.get("Version")
    if not name or not version:
        return None
    dependency_text = ", ".join(
        value
        for field in ("Pre-Depends", "Depends")
        if (value := stanza.get(field))
    )
    return PackageRecord(name, version, dependency_names(dependency_text))


def parse_packages(text: str) -> list[PackageRecord]:
    """Разобрать все пакеты из индекса."""
    return [
        record
        for stanza in parse_control_stanzas(text)
        if (record := record_from_stanza(stanza)) is not None
    ]


def load_index_for_package(
    repository_url: str, package: str, version: str
) -> tuple[list[PackageRecord], str]:
    """Найти индекс, содержащий заданные имя и версию пакета."""
    errors: list[str] = []
    for url in candidate_urls(repository_url):
        try:
            records = parse_packages(download_index(url))
        except RepositoryError as error:
            errors.append(str(error))
            continue
        package_found = any(
            record.name == package and record.version == version
            for record in records
        )
        if package_found:
            return records, url

    details = f" Последняя ошибка: {errors[-1]}" if errors else ""
    message = (
        f"пакет {package} версии {version} не найден "
        f"в указанных индексах.{details}"
    )
    raise RepositoryError(
        message
    )


def find_package(
    records: list[PackageRecord], package: str, version: str
) -> PackageRecord:
    """Найти точную версию пакета в уже загруженном индексе."""
    for record in records:
        if record.name == package and record.version == version:
            return record
    raise RepositoryError(f"пакет {package} версии {version} не найден")
