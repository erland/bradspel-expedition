"""Tester för runtime-state och dynamisk pathfinding."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_rules():
    path = ROOT / "scripts/simulate_game.py"
    spec = importlib.util.spec_from_file_location("_test_expedition_rules", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Kunde inte ladda simulatorn")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DynamicConnectionRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules()
        simulation_data = cls.rules.load_yaml(ROOT / "data/simulation.yaml")
        cls.strategy = next(
            item for item in simulation_data["strategies"]
            if item["id"] == "nearest_unknown"
        )

    def make_game(self):
        return self.rules.ExpeditionSimulation(
            ROOT,
            self.strategy,
            seed=19702,
            scenario_id="station_nordanvind",
            characters_per_game=2,
        )

    def test_scenario_connections_start_closed(self):
        game = self.make_game()
        for connection_id in ("route_v1", "route_v2", "route_v3", "route_v4"):
            self.assertEqual(game.get_connection_state(connection_id), "closed")
            self.assertFalse(game.is_connection_traversable(connection_id))

    def test_closed_connection_is_not_used_by_pathfinding(self):
        game = self.make_game()
        character = game.characters[0]
        character.location = "slot_3"
        path = game.shortest_path(
            "slot_3",
            {"supply_depot"},
            allow_hidden=False,
            char=character,
        )
        self.assertNotEqual(path, [("supply_depot", "route_v1")])
        self.assertGreaterEqual(len(path), 2)

    def test_open_connection_is_used_immediately(self):
        game = self.make_game()
        character = game.characters[0]
        character.location = "slot_3"
        changed = game.open_connection("route_v1")
        path = game.shortest_path(
            "slot_3",
            {"supply_depot"},
            allow_hidden=False,
            char=character,
        )
        self.assertTrue(changed)
        self.assertEqual(path, [("supply_depot", "route_v1")])
        self.assertEqual(game.get_connection_state("route_v1"), "open")

    def test_open_is_idempotent(self):
        game = self.make_game()
        self.assertTrue(game.open_connection("route_v1"))
        self.assertFalse(game.open_connection("route_v1"))

    def test_sealed_connection_cannot_open(self):
        game = self.make_game()
        self.assertTrue(game.seal_connection("route_v1"))
        with self.assertRaises(ValueError):
            game.open_connection("route_v1")

    def test_invalid_transition_is_rejected(self):
        game = self.make_game()
        with self.assertRaises(ValueError):
            game.set_connection_state("route_v1", "hidden")


if __name__ == "__main__":
    unittest.main()
