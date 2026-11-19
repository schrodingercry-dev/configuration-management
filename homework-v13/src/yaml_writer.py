"""Минимальный сериализатор поддерживаемых значений в YAML."""

from __future__ import annotations

from typing import Any


def scalar(value: float) -> str:
    """Представить числовое значение в YAML."""
    return str(float(value))


def render_lines(value: Any, indent: int = 0) -> list[str]:
    """Рекурсивно сформировать строки YAML."""
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return [prefix + "{}"]
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(render_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {scalar(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [prefix + "[]"]
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(prefix + "-")
                lines.extend(render_lines(item, indent + 2))
            else:
                lines.append(f"{prefix}- {scalar(item)}")
        return lines
    return [prefix + scalar(value)]


def dump_yaml(value: Any) -> str:
    """Сериализовать значение с завершающим переводом строки."""
    return "\n".join(render_lines(value)) + "\n"
