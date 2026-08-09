from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "simulator_rule_contracts",
    ROOT / "scripts" / "simulate_game.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def strategy():
    return MOD.load_yaml(ROOT / "data" / "simulation.yaml")["strategies"][0]


def make_game(scenario="station_nordanvind"):
    return MOD.ExpeditionSimulation(ROOT, strategy(), 424242, scenario, 2)


def test_objective_capacity_uses_yaml_slots():
    game = make_game()
    char = game.characters[0]
    objective_id = next(iter(game.objective_by_id))
    game.objective_by_id[objective_id]["slots"] = 3
    char.objectives = [objective_id]
    assert game.occupied(char) == 3


def test_move_cost_cannot_exceed_remaining_actions():
    game = make_game()
    char = game.characters[0]
    neighbor, _ = game.open_adjacency[char.location][0]
    original = char.location
    char.next_move_cost = 2
    game.current_actions_remaining = 1
    assert game.move_action(char, neighbor) == 0
    assert char.location == original
    assert char.next_move_cost == 2


def test_regular_character_can_transfer_equipment():
    game = make_game()
    giver, receiver = game.characters[:2]
    giver.location = receiver.location = game.base
    giver.equipment = ["medical_kit"]
    receiver.damage = 1
    game.current_actions_remaining = 1
    cost = game.transfer_if_useful(giver)
    assert cost == 1
    assert "medical_kit" in receiver.equipment
    assert "medical_kit" not in giver.equipment


def test_medical_kit_can_heal_other_character_same_location():
    game = make_game()
    healer, patient = game.characters[:2]
    healer.id = "scout"
    patient.id = "medic"
    healer.location = patient.location = game.base
    healer.equipment = ["medical_kit"]
    patient.damage = 2
    game.current_actions_remaining = 1
    cost = game.use_equipment(healer)
    assert cost == 1
    assert patient.damage == 0
    assert "medical_kit" not in healer.equipment


def test_choice_can_keep_last_tool_and_take_damage():
    game = make_game()
    char = game.characters[0]
    char.tools = 1
    char.damage = 0
    assert game.choose_pay_tool_or_damage(char, 1) == "damage"


def test_water_reserve_triggers_at_actual_endurance_loss():
    game = make_game("okenrelaet")
    char = game.characters[0]
    char.equipment = ["water_reserve"]
    game.travel_deck = [{
        "id": "test_endurance_loss",
        "effect": [{"action": "lose_endurance", "amount": 1}],
    }]
    before = game.endurance
    game.resolve_travel_event(char)
    assert game.endurance == before
    assert "water_reserve" not in char.equipment


def test_diagnostic_tool_triggers_when_objective_is_activated():
    game = make_game("okenrelaet")
    char = game.characters[0]
    site = next(iter(game.location_assignment))
    game.repair_sites.add(site)
    char.location = site
    char.objectives = [next(iter(game.objective_by_id))]
    char.equipment = ["diagnostic_tool"]
    game.current_actions_remaining = 0
    assert game.install_module(char) == 0
    assert "diagnostic_tool" not in char.equipment
    assert site in game.repaired_sites


def test_activation_stops_immediately_when_endurance_runs_out():
    game = make_game()
    char = game.characters[0]
    game.endurance = 0
    before = dict(game.actions)
    game.activate(char)
    assert dict(game.actions) == before
