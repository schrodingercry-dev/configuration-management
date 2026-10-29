"""Тесты D2 и ASCII-представлений графа."""

from __future__ import annotations

import unittest

from src.graph import build_dependency_graph, parse_test_repository
from src.visualization import to_ascii_tree, to_d2


class VisualizationTests(unittest.TestCase):
    def test_d2_contains_direction_edges_and_isolated_node(self) -> None:
        repository = parse_test_repository("A: B, C\nB:\nC:\n")
        graph = build_dependency_graph(repository, "A", 3)
        self.assertEqual(
            to_d2(graph).splitlines(),
            ['direction: right', '"A" -> "B"', '"A" -> "C"'],
        )

        isolated = build_dependency_graph({"A": ()}, "A", 3)
        self.assertEqual(to_d2(isolated), 'direction: right\n"A"')

    def test_ascii_tree_draws_branches_and_shared_node(self) -> None:
        repository = parse_test_repository("A: B, C\nB: D\nC: D\nD:\n")
        graph = build_dependency_graph(repository, "A", 4)
        self.assertEqual(
            to_ascii_tree(graph, "A"),
            "A\n"
            "├── B\n"
            "│   └── D\n"
            "└── C\n"
            "    └── D [already shown]",
        )

    def test_ascii_tree_marks_cycle(self) -> None:
        repository = parse_test_repository("A: B\nB: C\nC: A\n")
        graph = build_dependency_graph(repository, "A", 5)
        self.assertIn("└── A [cycle]", to_ascii_tree(graph, "A"))
