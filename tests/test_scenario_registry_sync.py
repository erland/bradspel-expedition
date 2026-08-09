from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_scenario_registry_setup_matches_scenario_source():
    registry = load_yaml(ROOT / "data" / "scenarios.yaml")
    for scenario in registry["scenarios"]:
        source = load_yaml(ROOT / scenario["scenario_pack"])["scenario_pack"]
        assert (
            scenario["setup"]["endurance_by_character_count"]
            == source["setup"]["endurance_by_character_count"]
        ), scenario["id"]
        assert (
            scenario["setup"]["hidden_roads"]
            == source["setup"]["hidden_roads"]
        ), scenario["id"]
        assert (
            scenario["setup"]["hidden_road_marker_pool"]
            == source["setup"]["hidden_road_marker_pool"]
        ), scenario["id"]
