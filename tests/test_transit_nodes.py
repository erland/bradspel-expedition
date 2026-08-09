from pathlib import Path
import importlib.util
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(path):
    return yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))

def load_simulator():
    spec=importlib.util.spec_from_file_location("simulate_game", ROOT/"scripts/simulate_game.py")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def test_transit_nodes_are_real_non_explorable_nodes():
    board=load_yaml("data/board.yaml")
    transits=[n for n in board["locations"] if n.get("node_role")=="transit"]
    assert [n["label"] for n in transits]==["T1","T2","T3","T4"]
    assert all(n["explorable"] is False and n["occupiable"] is True for n in transits)
    scenario=load_yaml("data/scenarios/station-nordanvind/scenario.yaml")["scenario_pack"]
    assert scenario["setup"]["location_slots"] == 6

def test_transit_routes_have_two_segments():
    board=load_yaml("data/board.yaml")
    routes={}
    for edge in board["connections"]:
        if "route_id" in edge:
            routes.setdefault(edge["route_id"],[]).append(edge)
    assert set(routes)=={"route_1_3","route_2_5","route_3_6","route_5_6"}
    assert all(sorted(e["segment_index"] for e in edges)==[1,2] for edges in routes.values())

def test_transit_marker_count_matches_nodes():
    board=load_yaml("data/board.yaml")
    markers=load_yaml("data/transit-markers.yaml")
    nodes=sum(1 for n in board["locations"] if n.get("node_role")=="transit")
    count=sum(m["count"] for m in markers["markers"] if m["family"]=="transit")
    assert count >= nodes
