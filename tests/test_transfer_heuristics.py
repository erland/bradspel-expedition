from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "transfer_heuristic_sim",
    ROOT / "scripts" / "simulate_game.py",
)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def make_game():
    strategy = MOD.load_yaml(ROOT / "data" / "simulation.yaml")["strategies"][1]
    return MOD.ExpeditionSimulation(
        ROOT, strategy, 140001, "station_nordanvind", 2
    )


def test_no_transfer_without_logistical_improvement():
    game = make_game()
    giver, receiver = game.characters[:2]
    giver.location = receiver.location = game.base
    giver.tools = 1
    receiver.tools = 0
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(giver) is None
    assert game.metrics["transfers"] == 0


def test_objective_transfer_requires_receiver_to_be_closer():
    game = make_game()
    giver, receiver = game.characters[:2]
    giver.id = "medic"
    receiver.id = "scout"
    objective = next(iter(game.objective_by_id))
    giver.objectives = [objective]
    giver.location = receiver.location = game.base
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(giver) is None


def test_same_activation_cannot_transfer_twice():
    game = make_game()
    giver, receiver = game.characters[:2]
    giver.location = receiver.location = game.base
    giver.equipment = ["medical_kit"]
    receiver.damage = 1
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(giver) == 1
    giver.tools = 2
    receiver.objectives = [next(iter(game.objective_by_id))]
    assert game.transfer_if_useful(giver) is None


def test_reverse_transfer_is_blocked_for_next_round():
    game = make_game()
    first, second = game.characters[:2]
    first.location = second.location = game.base
    first.equipment = ["medical_kit"]
    second.damage = 1
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(first) == 1

    game.round += 1
    game.activation_serial += 1
    game.transfer_used_activations.clear()
    second.damage = 0
    first.damage = 1
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(second) is None


def test_objective_can_transfer_to_clearly_better_carrier_same_location():
    game = make_game()
    giver, receiver = game.characters[:2]
    giver.id = "medic"
    receiver.id = "carrier"
    giver.location = receiver.location = game.base
    objective = next(iter(game.objective_by_id))
    giver.objectives = [objective]
    game.current_actions_remaining = 2
    assert game.transfer_if_useful(giver) == 1
    assert objective in receiver.objectives
    assert objective not in giver.objectives
