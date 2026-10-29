"""Тесты рекурсивного построения графа зависимостей."""

from __future__ import annotations

import unittest

from src.graph import (
    build_dependency_graph,
    dependency_load_order,
    parse_test_repository,
)
from src.repository import RepositoryError


class GraphTests(unittest.TestCase):
    def test_parses_uppercase_test_repository(self) -> None:
        repository = parse_test_repository("A: B, C\nB: C\nC:\n")
        self.assertEqual(repository["A"], ("B", "C"))

    def test_rejects_invalid_test_package_name(self) -> None:
        with self.assertRaisesRegex(RepositoryError, "больших латинских"):
            parse_test_repository("A: lower\n")

    def test_dfs_honors_maximum_depth(self) -> None:
        repository = parse_test_repository("A: B\nB: C\nC: D\nD:\n")
        graph = build_dependency_graph(repository, "A", 2)
        self.assertEqual(
            graph.adjacency,
            {"A": ("B",), "B": ("C",), "C": ()},
        )

    def test_dfs_detects_cycle_without_infinite_recursion(self) -> None:
        repository = parse_test_repository("A: B\nB: C\nC: A\n")
        graph = build_dependency_graph(repository, "A", 10)
        self.assertEqual(graph.cycles, (("C", "A"),))
        self.assertEqual(graph.adjacency["C"], ("A",))

    def test_shared_dependency_is_not_expanded_repeatedly(self) -> None:
        repository = parse_test_repository("A: B, C\nB: D\nC: D\nD:\n")
        graph = build_dependency_graph(repository, "A", 5)
        self.assertEqual(set(graph.adjacency), {"A", "B", "C", "D"})

    def test_load_order_places_dependencies_before_package(self) -> None:
        repository = parse_test_repository("A: B, C\nB: D\nC: D\nD:\n")
        graph = build_dependency_graph(repository, "A", 5)
        self.assertEqual(
            dependency_load_order(graph, "A"),
            ("D", "B", "C", "A"),
        )

    def test_load_order_handles_cycle_once(self) -> None:
        repository = parse_test_repository("A: B\nB: C\nC: A\n")
        graph = build_dependency_graph(repository, "A", 5)
        order = dependency_load_order(graph, "A")
        self.assertEqual(order, ("C", "B", "A"))
        self.assertEqual(len(order), len(set(order)))
