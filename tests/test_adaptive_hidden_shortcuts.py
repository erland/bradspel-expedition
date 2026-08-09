from pathlib import Path

from agents.standard import build_agents
from engine.game_engine import GameEngine

ROOT = Path(__file__).resolve().parents[1]


def adaptive_agent():
    return next(agent for agent in build_agents() if agent.id == "adaptive_agent")


def test_adaptive_agent_is_registered():
    agent = adaptive_agent()
    params = agent.strategy_config()["parameters"]
    assert params["adaptive_hidden_shortcuts"] is True
    assert params["hidden_shortcut_min_savings"] == 2


def test_adaptive_agent_uses_hidden_route_when_it_saves_two_actions():
    game = GameEngine(ROOT).create_game(
        adaptive_agent(), 12345, 2, "station_nordanvind"
    )
    char = game.characters[0]
    char.location = "slot_1"
    assert game.adaptive_hidden_allowed("slot_1", "slot_5", char) is True


def test_adaptive_agent_avoids_hidden_route_without_required_savings():
    game = GameEngine(ROOT).create_game(
        adaptive_agent(), 12345, 2, "station_nordanvind"
    )
    char = game.characters[0]
    char.location = "slot_1"
    assert game.adaptive_hidden_allowed("slot_1", "slot_3", char) is False


def test_adaptive_choice_is_exported_in_result():
    game = GameEngine(ROOT).create_game(
        adaptive_agent(), 12345, 2, "station_nordanvind"
    )
    char = game.characters[0]
    char.location = "slot_1"
    game.move_action(char, "slot_5")
    assert game.metrics["adaptive_hidden_choices"] == 1
