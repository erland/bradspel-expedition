import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_session_report.py"


def run_report(tmp_path):
    output = tmp_path / "session"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ROOT),
            "--scenario",
            "station_nordanvind",
            "--characters",
            "2",
            "--strategy",
            "nearest_unknown",
            "--seed",
            "600000",
            "--output-dir",
            str(output),
        ],
        check=True,
        cwd=ROOT,
    )
    return (
        (output / "session-report.md").read_text(encoding="utf-8"),
        json.loads((output / "session-raw.json").read_text(encoding="utf-8")),
    )


def test_session_report_uses_rule_action_names_and_objective_term(tmp_path):
    report, raw = run_report(tmp_path)
    assert "**Flytta:**" in report
    assert "**Utforska:**" in report
    assert "**Hämta verktyg:**" in report
    assert "**Lämna målobjekt:**" in report
    assert "Målobjektet **Medicinskt prov**" in report
    assert "Fyndkortet" not in report
    assert all(
        event["action_name"]
        for event in raw["events"]
        if event["event_type"] == "action"
    )


def test_triggered_event_is_presented_after_action_and_drawn_card(tmp_path):
    report, raw = run_report(tmp_path)
    explore = report.index("**Utforska:** Bäraren utforskar Plats 1")
    objective = report.index("Målobjektet **Medicinskt prov** dras")
    stormfront = report.index("Scenariohändelsen **Stormfront**")
    assert explore < objective < stormfront


def test_raw_log_keeps_ids_and_flags_possible_inefficiency(tmp_path):
    _, raw = run_report(tmp_path)
    actions = [event for event in raw["events"] if event["event_type"] == "action"]
    assert any(event["action_id"] == "move" for event in actions)
    assert all(isinstance(event["possible_inefficiency"], bool) for event in actions)
