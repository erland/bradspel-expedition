
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("simulate_game", ROOT / "scripts" / "simulate_game.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_climbing_rope_is_optional_zero_action_equipment():
    equipment = MOD.load_yaml(ROOT / "data" / "base" / "equipment.yaml")["equipment"]
    rope = next(card for card in equipment if card["id"] == "climbing_rope")
    assert rope["use"]["cost_actions"] == 0
    assert rope["use"]["optional"] is True
    assert rope["use"]["timing"] == "after_drawing_travel_event_before_resolution"
    assert rope["use"]["discard_after_use"] is True
    assert rope["use"]["effect"] == [{"action": "ignore_current_travel_event"}]


def test_character_cards_use_action_and_equipment_terms():
    characters = MOD.load_yaml(ROOT / "data" / "characters.yaml")["characters"]
    engineer = next(card for card in characters if card["id"] == "engineer")
    technician = next(card for card in characters if card["id"] == "technician")
    assert "handlingspoäng" not in engineer["ability"]["text"]
    assert "utan att använda en handling" in engineer["ability"]["text"]
    assert "engångsutrustning" in technician["ability"]["text"]
    assert "engångsföremål" not in technician["ability"]["text"]
