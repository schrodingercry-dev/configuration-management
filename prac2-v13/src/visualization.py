"""Текстовые представления графа зависимостей."""

from __future__ import annotations

from .graph import DependencyGraph


def d2_quote(value: str) -> str:
    """Безопасно заключить имя узла в кавычки D2."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_d2(graph: DependencyGraph) -> str:
    """Сформировать описание графа на языке диаграмм D2."""
    lines = ["direction: right"]
    declared_nodes: set[str] = set()
    edges: set[tuple[str, str]] = set()

    for package, dependencies in graph.adjacency.items():
        declared_nodes.add(package)
        if not dependencies:
            continue
        for dependency in dependencies:
            declared_nodes.add(dependency)
            edges.add((package, dependency))

    connected_nodes = {node for edge in edges for node in edge}
    for node in sorted(declared_nodes - connected_nodes):
        lines.append(d2_quote(node))
    for source, target in sorted(edges):
        lines.append(f"{d2_quote(source)} -> {d2_quote(target)}")
    return "\n".join(lines)


def to_ascii_tree(graph: DependencyGraph, root: str) -> str:
    """Сформировать ASCII-дерево, отмечая циклы и повторные узлы."""
    lines = [root]
    expanded: set[str] = {root}

    def add_children(package: str, prefix: str, active: set[str]) -> None:
        dependencies = graph.adjacency.get(package, ())
        for index, dependency in enumerate(dependencies):
            is_last = index == len(dependencies) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")

            if dependency in active:
                lines.append(f"{prefix}{connector}{dependency} [cycle]")
                continue
            if dependency in expanded:
                lines.append(f"{prefix}{connector}{dependency} [already shown]")
                continue

            lines.append(f"{prefix}{connector}{dependency}")
            expanded.add(dependency)
            add_children(dependency, child_prefix, active | {dependency})

    add_children(root, "", {root})
    return "\n".join(lines)
