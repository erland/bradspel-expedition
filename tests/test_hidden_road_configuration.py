from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_board_has_six_unique_d_slots_with_open_base_icons():
    board = load_yaml(ROOT / "data/board.yaml")
    roads = [
        connection for connection in board["connections"]
        if connection.get("category") == "hidden"
    ]
    assert sorted(road["label"] for road in roads) == ["D1", "D2", "D3", "D4", "D5", "D6"]
    assert len({road["id"] for road in roads}) == 6
    assert all(road["default_state"] == "open" for road in roads)
    assert all(road["discovery"] == "hidden_marker" for road in roads)


def test_scenarios_only_reference_existing_d_roads():
    board = load_yaml(ROOT / "data/board.yaml")
    valid = {
        connection["id"] for connection in board["connections"]
        if connection.get("category") == "hidden"
    }
    registry = load_yaml(ROOT / "data/scenarios.yaml")
    for scenario in registry["scenarios"]:
        hidden = scenario["setup"]["hidden_roads"]
        assert len(hidden) == len(set(hidden)), scenario["id"]
        assert set(hidden) <= valid, scenario["id"]


def test_road_marker_sheet_covers_every_scenario_pool():
    registry = load_yaml(ROOT / "data/scenarios.yaml")
    marker_data = load_yaml(ROOT / "data/road-markers.yaml")
    physical_counts = {
        marker["result"]: marker["count"]
        for marker in marker_data["markers"]
        if marker["result"] in {"open", "blocked", "travel_event"}
    }
    # The printed sheet is a reusable reserve. Each scenario selects its own smaller composition.
    assert physical_counts["open"] >= 3
    assert physical_counts["blocked"] >= 2
    assert physical_counts["travel_event"] >= 1
    for scenario in registry["scenarios"]:
        pool = scenario["setup"]["hidden_road_marker_pool"]
        assert sum(pool.values()) >= len(scenario["setup"]["hidden_roads"])
        for result, count in pool.items():
            assert count <= physical_counts[result], scenario["id"]


def test_station_and_desert_can_use_different_hidden_roads():
    registry = load_yaml(ROOT / "data/scenarios.yaml")
    scenarios = {scenario["id"]: scenario for scenario in registry["scenarios"]}
    assert scenarios["station_nordanvind"]["setup"]["hidden_roads"] == [
        "road_hidden_01",
        "road_hidden_02",
        "road_hidden_03",
        "road_hidden_05",
        "road_hidden_06",
    ]
    assert scenarios["okenrelaet"]["setup"]["hidden_roads"] == [
        "road_hidden_01",
        "road_hidden_02",
        "road_hidden_03",
        "road_hidden_04",
    ]


def test_scenario_marker_pools_are_explicit():
    registry = load_yaml(ROOT / "data/scenarios.yaml")
    scenarios = {scenario["id"]: scenario for scenario in registry["scenarios"]}
    assert scenarios["station_nordanvind"]["setup"]["hidden_road_marker_pool"] == {
        "open": 3,
        "blocked": 2,
        "travel_event": 1,
    }
    assert scenarios["okenrelaet"]["setup"]["hidden_road_marker_pool"] == {
        "open": 2,
        "blocked": 1,
        "travel_event": 1,
    }


def test_rulebook_explains_hidden_road_setup_procedure():
    rulebook = (ROOT / "docs/rulebook-playtest.md").read_text(encoding="utf-8")
    assert "Ta fram de dolda vägbrickor som scenarioarket anger" in rulebook
    assert "baksidan upp på varje D-väg" in rulebook
    assert "läggs de åt sidan med baksidan upp utan att avslöjas" in rulebook
