from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "rule-coverage.yaml"


def load_matrix():
    return yaml.safe_load(DATA.read_text(encoding="utf-8"))


def test_rule_coverage_ids_are_unique():
    matrix = load_matrix()
    ids = [item["id"] for item in matrix["rules"]]
    assert len(ids) == len(set(ids))


def test_full_rules_have_automated_tests():
    matrix = load_matrix()
    full = [item for item in matrix["rules"] if item["status"] == "full"]
    assert full
    assert all(item["tests"] for item in full)


def test_rule_coverage_summary_matches_rows():
    matrix = load_matrix()
    expected = {}
    for item in matrix["rules"]:
        expected[item["status"]] = expected.get(item["status"], 0) + 1
    assert matrix["summary"] == expected
