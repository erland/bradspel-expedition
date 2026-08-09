from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sim_rules_alignment", ROOT / "scripts/simulate_game.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def strategy():
    return MOD.load_yaml(ROOT / "data/simulation.yaml")["strategies"][0]


def test_scenario_events_can_be_disabled():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 111, "station_nordanvind", 2)
    game.scenario_events_enabled = False
    before = game.endurance
    game.objectives_found = 1
    changed = game.process_scenario_event_milestones(
        "objective_found", objective_id="research_server"
    )
    assert changed == []
    assert game.endurance == before
    assert game.scenario_event_log == []


def test_event_log_contains_balance_fields():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 222, "station_nordanvind", 2)
    before = game.endurance
    game.objectives_found = 1
    game.process_scenario_event_milestones(
        "objective_found", objective_id="research_server"
    )
    entry = game.scenario_event_log[0]
    assert entry["card_id"] == "polar_stormfront"
    assert entry["endurance_delta"] == game.endurance - before
    assert "opened_connections" in entry
    assert "closed_connections" in entry


def test_game_result_exports_scenario_event_metrics():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 333, "station_nordanvind", 2)
    result = game.run()
    assert isinstance(result.scenario_event_cards, list)
    assert isinstance(result.scenario_event_rounds, list)
    assert isinstance(result.scenario_event_log, list)
    assert result.scenario_events_resolved == len(result.scenario_event_log)
