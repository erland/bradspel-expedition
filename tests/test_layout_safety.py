from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_long_location_titles_use_safe_two_line_layout():
    modules = [
        load_module("scenario_cards_layout", "scripts/generate_scenario_cards.py"),
        load_module("desert_cards_layout", "scripts/generate_okenrelaet_content.py"),
    ]
    titles = [
        "Övergivet laboratorium",
        "Rasade servicegångar",
        "Norra relästationen",
        "Klippfyrens kontrollhus",
        "Sandbegravet förråd",
    ]
    for module in modules:
        for title in titles:
            layout = module.title_layout(title)
            assert len(layout["lines"]) == 2
            assert layout["title_y"] >= 17
            assert layout["symbol_y"] >= 35
            assert layout["size"] <= 3.8


def test_single_line_titles_keep_default_vertical_positions():
    module = load_module("scenario_cards_single", "scripts/generate_scenario_cards.py")
    layout = module.title_layout("Basläger")
    assert layout["lines"] == ["Basläger"]
    assert layout["title_y"] == 15.0
    assert layout["symbol_y"] == 34.0


def test_reference_end_box_uses_separate_text_rows():
    template = (ROOT / "templates/reference/a6-reference.svg.j2").read_text(
        encoding="utf-8"
    )
    assert 'box(54,123,47,13,"SLUT",True)' in template
    assert 'y="129.2"' in template
    assert 'y="133.1"' in template
