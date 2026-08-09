from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sim_rules", ROOT / "scripts/simulate_game.py")
MOD = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MOD)

def strategy():
    data = MOD.load_yaml(ROOT / "data/simulation.yaml")["strategies"][0]
    return data

def test_first_objective_found_resolves_fixed_event():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 123, "station_nordanvind", 2)
    before = game.endurance
    game.draw_objective(game.characters[0])
    assert game.endurance == before - 1
    assert game.scenario_event_log[0]["card_id"] == "polar_stormfront"

def test_objective_activated_is_generic_trigger():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 321, "okenrelaet", 2)
    game.objectives_found = 1
    game.completed_objective_ids.add("power_converter")
    game.mission_progress = lambda: 1
    game.process_scenario_event_milestones("objective_activated", objective_id="power_converter")
    assert [entry["card_id"] for entry in game.scenario_event_log] == [
        "desert_navigation_beacons",
        "desert_route_collapse",
    ]
    assert game.get_connection_state("route_v4") == "open"
    assert game.get_connection_state("road_hidden_03") == "closed"

def test_milestone_fires_once():
    game = MOD.ExpeditionSimulation(ROOT, strategy(), 999, "station_nordanvind", 2)
    before = game.endurance
    game.objectives_found = 1
    game.process_scenario_event_milestones("objective_found", objective_id="research_server")
    game.process_scenario_event_milestones("objective_found", objective_id="satellite_core")
    assert game.endurance == before - 1
    assert len(game.scenario_event_log) == 1
