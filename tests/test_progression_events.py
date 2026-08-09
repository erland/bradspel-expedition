"""Integrationstester för datadrivna progression events."""

from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_rules():
    path = ROOT / "scripts/simulate_game.py"
    spec = importlib.util.spec_from_file_location("_test_progression_rules", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class ProgressionEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rules()
        data = cls.rules.load_yaml(ROOT / "data/simulation.yaml")
        cls.strategy = next(x for x in data["strategies"] if x["id"] == "nearest_unknown")

    def make_game(self, scenario="station_nordanvind"):
        return self.rules.ExpeditionSimulation(
            ROOT, self.strategy, seed=19703,
            scenario_id=scenario, characters_per_game=2
        )

    def test_first_completed_objective_opens_connection(self):
        game = self.make_game()
        game.progression_events = [{
            "id": "open_v1_after_first",
            "trigger": {"event": "objective_completed", "count": 1},
            "effects": [{"action": "open_connection", "connection_id": "route_v1"}],
            "narrative": "Servicegången återställs."
        }]
        char = game.characters[0]
        char.location = game.base
        char.objectives = ["research_server"]
        game.deposit_objectives(char)
        self.assertEqual(game.get_connection_state("route_v1"), "open")
        self.assertEqual(len(game.progression_log), 1)

    def test_specific_objective_opens_connection(self):
        game = self.make_game()
        game.progression_events = [{
            "id": "server_opens_v2",
            "trigger": {"event": "objective_completed", "objective_id": "research_server"},
            "effects": [{"action": "open_connection", "connection_id": "route_v2"}]
        }]
        char = game.characters[0]
        char.location = game.base
        char.objectives = ["medical_sample"]
        game.deposit_objectives(char)
        self.assertEqual(game.get_connection_state("route_v2"), "closed")
        char.objectives = ["research_server"]
        game.deposit_objectives(char)
        self.assertEqual(game.get_connection_state("route_v2"), "open")

    def test_multiple_connections_open_from_one_event(self):
        game = self.make_game()
        game.progression_events = [{
            "id": "network_restored",
            "trigger": {"event": "objective_completed", "count": 1},
            "effects": [
                {"action": "open_connection", "connection_id": "route_v1"},
                {"action": "open_connection", "connection_id": "route_v2"},
                {"action": "open_connection", "connection_id": "route_v3"},
            ]
        }]
        char = game.characters[0]
        char.location = game.base
        char.objectives = ["research_server"]
        game.deposit_objectives(char)
        for cid in ("route_v1", "route_v2", "route_v3"):
            self.assertEqual(game.get_connection_state(cid), "open")

    def test_choice_opens_first_valid_connection(self):
        game = self.make_game()
        game.progression_events = [{
            "id": "choose_route",
            "trigger": {"event": "objective_completed", "count": 1},
            "effects": [{
                "action": "choose_connection", "choose": 1,
                "from": ["route_v1", "route_v2", "route_v3"]
            }]
        }]
        char = game.characters[0]
        char.location = game.base
        char.objectives = ["research_server"]
        game.deposit_objectives(char)
        self.assertEqual(game.get_connection_state("route_v1"), "open")
        self.assertEqual(game.get_connection_state("route_v2"), "closed")

    def test_relay_trigger_opens_connection(self):
        game = self.make_game("okenrelaet")
        game.progression_events = [{
            "id": "relay_opens_v4",
            "trigger": {"event": "objective_activated", "count": 1},
            "effects": [{"action": "open_connection", "connection_id": "route_v4"}]
        }]
        char = game.characters[0]
        site = "slot_1"
        game.repair_sites.add(site)
        char.location = site
        char.objectives = ["power_converter"]
        result = game.install_module(char)
        self.assertIsNotNone(result)
        self.assertEqual(game.get_connection_state("route_v4"), "open")

    def test_event_only_fires_once(self):
        game = self.make_game()
        game.progression_events = [{
            "id": "once",
            "trigger": {"event": "objective_completed", "count": 1},
            "effects": [{"action": "open_connection", "connection_id": "route_v1"}]
        }]
        char = game.characters[0]
        char.location = game.base
        char.objectives = ["research_server"]
        game.deposit_objectives(char)
        char.objectives = ["medical_sample"]
        game.deposit_objectives(char)
        self.assertEqual(len(game.progression_log), 1)

if __name__ == "__main__":
    unittest.main()
