from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_scenario_sheet_generator_prints_marker_pool_and_d_roads():
    source = (ROOT / "scripts/generate_scenario_sheet.py").read_text(encoding="utf-8")
    assert "Dolda vägbrickor:" in source
    assert "Dolda vägar:" in source
    assert "hidden_road_marker_pool" in source


def test_preparation_box_is_taller():
    template = (
        ROOT / "templates/scenarios/a5-scenario-card.svg.j2"
    ).read_text(encoding="utf-8")
    assert 'section_box(6,80,61,58,"FÖRBEREDELSER"' in template


def test_scenario_sheet_uses_full_setup_words_and_wraps_bullets():
    source = (ROOT / "scripts/generate_scenario_sheet.py").read_text(encoding="utf-8")
    assert "karaktärer:" in source
    assert "uthållighet" in source
    assert "startverktyg" not in source
    assert "wrapped_bullet" in source
    assert "Alla startar i Baslägret" not in source


def test_scenario_content_headings_use_requested_wording_without_counts():
    source = (ROOT / "scripts/generate_scenario_sheet.py").read_text(encoding="utf-8")
    assert "MÅLOBJEKT · EGEN HÖG" in source
    assert "SCENARIOHÄNDELSER · EGEN HÖG" in source
    assert "BLANDA MED ÖVRIGA" in source
    assert 'f"{title} ×{count}"' not in source
