from pathlib import Path
from agents.standard import build_agents
from engine.game_engine import GameEngine

ROOT=Path(__file__).resolve().parents[1]

def agent():
    return next(a for a in build_agents() if a.id=="explorer_agent")

def test_dynamic_connection_usage_is_reported():
    game=GameEngine(ROOT).create_game(agent(),12345,2,"station_nordanvind")
    game.open_connection("route_v1")
    char=game.characters[0]
    char.location="slot_3"
    assert game.move_action(char,"supply_depot")==1
    assert game.connection_uses["route_v1"]==1

def test_choice_prefers_valid_closed_connection():
    game=GameEngine(ROOT).create_game(agent(),12345,2,"station_nordanvind")
    chosen=game.resolve_connection_choice(["route_v1","route_v2","route_v3"],1)
    assert len(chosen)==1
    assert chosen[0] in {"route_v1","route_v2","route_v3"}

def test_tie_breaker_modes_are_supported():
    game=GameEngine(ROOT).create_game(agent(),12345,2,"station_nordanvind")
    assert set(game.node_tie_rank)=={x["id"] for x in game.board["locations"]}
