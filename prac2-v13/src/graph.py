"""Построение графа зависимостей рекурсивным DFS."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .repository import PackageRecord, RepositoryError


TEST_PACKAGE_RE = re.compile(r"^[A-Z]+$")


@dataclass(frozen=True)
class DependencyGraph:
    """Граф и обнаруженные обратные рёбра циклов."""

    adjacency: dict[str, tuple[str, ...]]
    cycles: tuple[tuple[str, str], ...]


def parse_test_repository(text: str) -> dict[str, tuple[str, ...]]:
    """Разобрать строки вида ``A: B, C`` тестового репозитория."""
    repository: dict[str, tuple[str, ...]] = {}
    for line_number, source_line in enumerate(text.splitlines(), start=1):
        line = source_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise RepositoryError(f"строка {line_number}: ожидается символ ':'")
        package, dependency_text = (part.strip() for part in line.split(":", 1))
        dependencies = tuple(
            item.strip() for item in dependency_text.split(",") if item.strip()
        )
        names = (package, *dependencies)
        if not all(TEST_PACKAGE_RE.fullmatch(name) for name in names):
            raise RepositoryError(
                f"строка {line_number}: имена должны состоять из больших латинских букв"
            )
        if package in repository:
            raise RepositoryError(f"строка {line_number}: пакет {package} задан повторно")
        repository[package] = dependencies
    return repository


def records_to_repository(
    records: list[PackageRecord], root_package: str, root_version: str
) -> dict[str, tuple[str, ...]]:
    """Преобразовать индекс apt в отображение пакетов на зависимости."""
    repository: dict[str, tuple[str, ...]] = {}
    for record in records:
        repository.setdefault(record.name, record.dependencies)
        if record.name == root_package and record.version == root_version:
            repository[root_package] = record.dependencies
    return repository


def build_dependency_graph(
    repository: dict[str, tuple[str, ...]], root: str, max_depth: int
) -> DependencyGraph:
    """Построить ограниченный по глубине граф рекурсивным DFS."""
    if root not in repository:
        raise RepositoryError(f"пакет {root} отсутствует в репозитории")

    adjacency: dict[str, tuple[str, ...]] = {}
    cycles: list[tuple[str, str]] = []
    expanded_depth: dict[str, int] = {}

    def dfs(package: str, depth: int, active: set[str]) -> None:
        previous_depth = expanded_depth.get(package)
        if previous_depth is not None and previous_depth <= depth:
            return
        expanded_depth[package] = depth

        if depth >= max_depth:
            adjacency.setdefault(package, ())
            return

        dependencies = repository.get(package, ())
        adjacency[package] = dependencies
        next_active = active | {package}
        for dependency in dependencies:
            if dependency in next_active:
                edge = (package, dependency)
                if edge not in cycles:
                    cycles.append(edge)
                continue
            dfs(dependency, depth + 1, next_active)

    dfs(root, 0, set())
    return DependencyGraph(adjacency, tuple(cycles))


def format_graph(graph: DependencyGraph) -> str:
    """Вывести граф построчно для демонстрации этапа 3."""
    lines = []
    for package, dependencies in graph.adjacency.items():
        lines.append(f"{package}: {', '.join(dependencies) if dependencies else '<none>'}")
    for source, target in graph.cycles:
        lines.append(f"cycle: {source} -> {target}")
    return "\n".join(lines)
