"""Тесты сбора прямых зависимостей из формата apt Packages."""

from __future__ import annotations

import unittest

from src.repository import (
    PackageRecord,
    dependency_names,
    find_package,
    parse_control_stanzas,
    parse_packages,
)


PACKAGES_TEXT = """\
Package: demo
Version: 1.2-3
Pre-Depends: init-system (>= 1)
Depends: python3 (>= 3.12), libc6 | libc6.1, shared:any
Description: first line
 continuation line

Package: empty
Version: 2.0
Description: no dependencies
"""


class RepositoryTests(unittest.TestCase):
    def test_parses_control_stanzas_and_continuations(self) -> None:
        stanzas = parse_control_stanzas(PACKAGES_TEXT)
        self.assertEqual(len(stanzas), 2)
        self.assertEqual(
            stanzas[0]["Description"],
            "first line continuation line",
        )

    def test_extracts_predepends_depends_and_first_alternative(self) -> None:
        records = parse_packages(PACKAGES_TEXT)
        self.assertEqual(
            records[0],
            PackageRecord(
                "demo", "1.2-3", ("init-system", "python3", "libc6", "shared")
            ),
        )
        self.assertEqual(records[1].dependencies, ())

    def test_dependency_names_remove_constraints_and_duplicates(self) -> None:
        self.assertEqual(
            dependency_names("a (>= 1), b:any | c, a"),
            ("a", "b"),
        )

    def test_finds_exact_package_version(self) -> None:
        record = find_package(parse_packages(PACKAGES_TEXT), "demo", "1.2-3")
        self.assertEqual(record.name, "demo")
