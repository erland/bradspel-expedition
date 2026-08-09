#!/usr/bin/env python3
"""Validate Expedition YAML sources against JSON Schema and cross-file rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit(
        "Saknat beroende: jsonschema. Installera med: pip install jsonschema PyYAML"
    ) from exc


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Filen saknas: {path}")
    except yaml.YAMLError as exc:
        raise ValueError(f"Ogiltig YAML i {path}: {exc}") from exc


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Filen saknas: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ogiltig JSON i {path}: {exc}") from exc


def json_path(parts: list[Any]) -> str:
    if not parts:
        return "$"
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result


def validate_schema(data: Any, schema: Any, label: str) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    return [
        f"{label} {json_path(list(error.absolute_path))}: {error.message}"
        for error in errors
    ]


def duplicate_ids(items: list[dict[str, Any]], label: str) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for item in items:
        item_id = item.get("id")
        if item_id in seen:
            errors.append(f"Duplicerat id i {label}: {item_id}")
        seen.add(item_id)
    return errors


def cross_validate(project: dict[str, Any], game: dict[str, Any], rules: dict[str, Any], root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    resources = game.get("resources", [])
    tracks = game.get("tracks", [])
    resource_ids = {item["id"] for item in resources}
    track_ids = {item["id"] for item in tracks}

    errors.extend(duplicate_ids(resources, "resources"))
    errors.extend(duplicate_ids(tracks, "tracks"))
    errors.extend(duplicate_ids(rules["round"]["phases"], "round.phases"))

    action_ids = list(rules.get("actions", {}).keys())
    if len(action_ids) != len(set(action_ids)):
        errors.append("Duplicerade handlings-id:n i rules.actions.")

    player_count = game["game"]["player_count"]
    if player_count["minimum"] > player_count["maximum"]:
        errors.append("game.player_count.minimum får inte vara större än maximum.")

    play_time = game["game"]["play_time_minutes"]
    if play_time["minimum"] > play_time["maximum"]:
        errors.append("game.play_time_minutes.minimum får inte vara större än maximum.")

    for track in tracks:
        if not (track["minimum"] <= track["start"] <= track["maximum"]):
            errors.append(
                f"Spåret {track['id']} har startvärde utanför intervallet."
            )

    if "health" in game["characters"]:
        health = game["characters"]["health"]
        if health["start"] > health["maximum"]:
            errors.append("characters.health.start får inte överstiga maximum.")

    budget = game["prototype_component_budget"]
    if budget["cards_minimum"] > budget["cards_maximum"]:
        errors.append("cards_minimum får inte överstiga cards_maximum.")
    if budget["tokens_minimum"] > budget["tokens_maximum"]:
        errors.append("tokens_minimum får inte överstiga tokens_maximum.")

    vocabulary = set(rules.get("effect_vocabulary_draft", []))

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            action = value.get("action")
            if action and action not in vocabulary:
                warnings.append(
                    f"Effekten '{action}' används men saknas i effect_vocabulary_draft."
                )
            track = value.get("track")
            if track and track not in track_ids:
                errors.append(f"Okänd track-referens: {track}")
            resource = value.get("resource")
            if resource and resource not in resource_ids and resource not in {
                "from_location"
            }:
                errors.append(f"Okänd resource-referens: {resource}")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(rules)

    project_sources = project.get("sources", {})
    component_status = {c["id"]: c for c in project.get("components", [])}
    for component_id, component in component_status.items():
        source_path = root / component["source"]
        if component["enabled"] and not source_path.exists():
            errors.append(
                f"Komponenten '{component_id}' är aktiverad men källfilen saknas: "
                f"{component['source']}"
            )
        elif not component["enabled"] and not source_path.exists():
            warnings.append(
                f"Komponenten '{component_id}' är avstängd och dess framtida källfil "
                f"saknas: {component['source']}"
            )

    if project["project"]["id"] != game["game"]["id"]:
        errors.append("project.project.id matchar inte game.game.id.")

    required_objectives = game["objectives"].get(
        "required_objective_cards",
        game["objectives"].get("required_objective_tokens"),
    )
    victory_objectives = [
        condition.get("amount")
        for condition in rules["victory"]["all"]
        if condition.get("type") in {
            "objective_tokens_collected",
            "objective_cards_at_location",
        }
    ]
    if victory_objectives and victory_objectives[0] != required_objectives:
        errors.append(
            "Antal målobjekt skiljer sig mellan game.yaml och rules.yaml."
        )

    actions_per_round = game["characters"]["actions_per_round"]
    activation_steps = [
        step.get("actions_per_character")
        for phase in rules["round"]["phases"]
        for step in phase["steps"]
        if step.get("action") == "activate_each_active_character"
    ]
    if activation_steps and activation_steps[0] != actions_per_round:
        errors.append(
            "Antal handlingar skiljer sig mellan game.yaml och rules.yaml."
        )

    return errors, sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Projektets rotmapp.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Behandla varningar som fel.",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    pairs = [
        ("project", root / "data/project.yaml", root / "schemas/project.schema.json"),
        ("game", root / "data/game.yaml", root / "schemas/game.schema.json"),
        ("rules", root / "data/rules.yaml", root / "schemas/rules.schema.json"),
        ("rule_coverage", root / "data/rule-coverage.yaml", root / "schemas/rule-coverage.schema.json"),
        ("cards", root / "data/cards.yaml", root / "schemas/cards.schema.json"),
        ("card_layout", root / "data/layouts/card-standard.yaml", root / "schemas/card-layout.schema.json"),
        ("print_layout", root / "data/print-layouts/cards-a4.yaml", root / "schemas/print-layout.schema.json"),
        ("board", root / "data/board.yaml", root / "schemas/board.schema.json"),
        ("board_layout", root / "data/layouts/board-standard.yaml", root / "schemas/board-layout.schema.json"),
        ("board_print_layout", root / "data/print-layouts/board-a4.yaml", root / "schemas/board-print-layout.schema.json"),
        ("location_tile_layout", root / "data/layouts/location-tile.yaml", root / "schemas/location-tile-layout.schema.json"),
        ("reference_cards", root / "data/reference-cards.yaml", root / "schemas/reference-cards.schema.json"),
        ("reference_layout", root / "data/layouts/reference-a6.yaml", root / "schemas/reference-layout.schema.json"),
        ("reference_print_layout", root / "data/print-layouts/reference-a4.yaml", root / "schemas/reference-print-layout.schema.json"),
        ("tokens", root / "data/tokens.yaml", root / "schemas/tokens.schema.json"),
        ("token_layout", root / "data/layouts/token-standard.yaml", root / "schemas/token-layout.schema.json"),
        ("token_print_layout", root / "data/print-layouts/tokens-a4.yaml", root / "schemas/token-print-layout.schema.json"),
        ("scenarios", root / "data/scenarios.yaml", root / "schemas/scenarios.schema.json"),
        ("locations", root / "data/scenarios/station-nordanvind/locations.yaml", root / "schemas/locations.schema.json"),
        ("road_markers", root / "data/road-markers.yaml", root / "schemas/road-markers.schema.json"),
        ("transit_markers", root / "data/transit-markers.yaml", root / "schemas/transit-markers.schema.json"),
        ("travel_events", root / "data/base/travel-events.yaml", root / "schemas/travel-events.schema.json"),
        ("characters", root / "data/characters.yaml", root / "schemas/characters.schema.json"),
        ("equipment", root / "data/base/equipment.yaml", root / "schemas/equipment.schema.json"),
        ("objectives", root / "data/scenarios/station-nordanvind/objectives.yaml", root / "schemas/objectives.schema.json"),
        ("inventory", root / "data/inventory.yaml", root / "schemas/inventory.schema.json"),
        ("simulation", root / "data/simulation.yaml", root / "schemas/simulation.schema.json"),
        ("cooperation_ablation", root / "data/cooperation-ablation.yaml", root / "schemas/cooperation-ablation.schema.json"),
        ("base_profiles", root / "data/base-profiles.yaml", root / "schemas/base-profiles.schema.json"),
        ("component_policy", root / "data/base/component-policy.yaml", root / "schemas/component-policy.schema.json"),
        ("simulation_coverage", root / "data/simulation-coverage.yaml", root / "schemas/simulation-coverage.schema.json"),
        ("station_nordanvind", root / "data/scenarios/station-nordanvind/scenario.yaml", root / "schemas/scenario-pack.schema.json"),
        ("okenrelaet", root / "data/scenarios/okenrelaet/scenario.yaml", root / "schemas/scenario-pack.schema.json"),
        ("okenrelaet_locations", root / "data/scenarios/okenrelaet/locations.yaml", root / "schemas/locations.schema.json"),
        ("okenrelaet_objectives", root / "data/scenarios/okenrelaet/objectives.yaml", root / "schemas/objectives.schema.json"),
        ("okenrelaet_equipment", root / "data/environments/desert/equipment.yaml", root / "schemas/equipment.schema.json"),
        ("okenrelaet_travel_events", root / "data/environments/desert/travel-events.yaml", root / "schemas/travel-events.schema.json"),
    ]

    loaded: dict[str, Any] = {}
    errors: list[str] = []
    warnings: list[str] = []

    for label, data_path, schema_path in pairs:
        try:
            data = load_yaml(data_path)
            schema = load_json(schema_path)
            loaded[label] = data
            errors.extend(validate_schema(data, schema, label))
        except ValueError as exc:
            errors.append(str(exc))

    if not errors and all(k in loaded for k in ("project", "game", "rules")):
        cross_errors, cross_warnings = cross_validate(
            loaded["project"], loaded["game"], loaded["rules"], root
        )
        if "cards" in loaded:
            cards = loaded["cards"]
            deck_ids = {d["id"] for d in cards["decks"]}
            card_ids = [c["id"] for c in cards["cards"]]
            if len(card_ids) != len(set(card_ids)):
                cross_errors.append("Duplicerade kort-id:n i cards.yaml.")
            game_resource_ids = {r["id"] for r in loaded["game"]["resources"]}
            game_track_ids = {t["id"] for t in loaded["game"]["tracks"]}
            vocabulary = set(loaded["rules"]["effect_vocabulary_draft"])
            for card in cards["cards"]:
                if card["deck"] not in deck_ids:
                    cross_errors.append(f"Okänd kortlek för {card['id']}: {card['deck']}")
                icon_path = root / "assets/icons" / f"{card['icon']}.svg"
                if not icon_path.exists():
                    cross_errors.append(f"Ikon saknas för {card['id']}: {card['icon']}")
                for effect in card["rules"]["effects"]:
                    if effect["action"] not in vocabulary:
                        cross_errors.append(f"Okänd korteffekt: {effect['action']}")
                    resource = effect.get("resource")
                    if resource and resource not in game_resource_ids:
                        cross_errors.append(f"Okänd kortresurs: {resource}")
                    track = effect.get("track")
                    if track and track not in game_track_ids:
                        cross_errors.append(f"Okänt kortspår: {track}")

        # Målobjektskort ska vara scenariogeneriska: destination och slutförande hör hemma i scenario-YAML.
        for objective_label in ("objectives", "okenrelaet_objectives"):
            if objective_label in loaded:
                for objective in loaded[objective_label].get("objectives", []):
                    text = objective.get("text", "").lower()
                    forbidden = ("måste transporteras", "installera den", "för till baslägret", "leverera till")
                    if any(term in text for term in forbidden):
                        cross_errors.append(
                            f"Målobjektet {objective['id']} innehåller scenariologik i korttexten."
                        )

        for scenario_label in ("station_nordanvind", "okenrelaet"):
            if scenario_label in loaded:
                pack = loaded[scenario_label]["scenario_pack"]
                mission = pack["mission"]
                completion = mission["completion"]
                if not mission.get("player_instructions"):
                    cross_errors.append(f"{pack['name']} saknar spelartext för mål och progression.")
                if completion.get("required") != mission.get("required_objectives"):
                    cross_errors.append(f"{pack['name']} har olika antal mål i mission och completion.")

        if "board" in loaded:
            board = loaded["board"]
            location_ids = [loc["id"] for loc in board["locations"]]
            location_id_set = set(location_ids)
            type_ids = {item["id"] for item in board["location_types"]}
            resource_ids = {item["id"] for item in loaded["game"]["resources"]}
            game_track_ids = {item["id"] for item in loaded["game"]["tracks"]}
            if len(location_ids) != len(location_id_set):
                cross_errors.append("Duplicerade plats-id:n i board.yaml.")
            connection_ids = [c["id"] for c in board["connections"]]
            if len(connection_ids) != len(set(connection_ids)):
                cross_errors.append("Duplicerade kopplings-id:n i board.yaml.")
            if board["board"]["start_location"] not in location_id_set:
                cross_errors.append("Startplatsen i board.yaml finns inte.")
            for location in board["locations"]:
                if location["type"] not in type_ids:
                    cross_errors.append(f"Okänd platstyp: {location['type']}")
                resource = location.get("resource")
                if resource and resource not in resource_ids:
                    cross_errors.append(f"Okänd platsresurs: {resource}")
                if not (0 <= location["x"] <= board["board"]["width_mm"]):
                    cross_errors.append(f"Platsen {location['id']} ligger utanför brädets bredd.")
                if not (0 <= location["y"] <= board["board"]["height_mm"]):
                    cross_errors.append(f"Platsen {location['id']} ligger utanför brädets höjd.")
            connection_labels: set[str] = set()
            undirected_pairs: dict[tuple[str, str], str] = {}
            for connection in board["connections"]:
                connection_id = connection["id"]
                if connection["from"] not in location_id_set:
                    cross_errors.append(f"Okänd startnod i koppling {connection_id}.")
                if connection["to"] not in location_id_set:
                    cross_errors.append(f"Okänd slutnod i koppling {connection_id}.")
                if connection["from"] == connection["to"]:
                    cross_errors.append(f"Självkoppling tillåts inte: {connection_id}.")

                pair = tuple(sorted((connection["from"], connection["to"])))
                if pair in undirected_pairs:
                    cross_errors.append(
                        f"Dubblerad odirektionell koppling: {connection_id} och "
                        f"{undirected_pairs[pair]} binder samma noder."
                    )
                else:
                    undirected_pairs[pair] = connection_id

                label = connection.get("label")
                if label:
                    if label in connection_labels:
                        cross_errors.append(f"Dubblerad spelarlabel för väg: {label}.")
                    connection_labels.add(label)

                category = connection.get("category")
                state = connection.get("default_state")
                discovery = connection.get("discovery")
                style = connection.get("printed_style")

                if category == "fixed" and state != "open":
                    cross_errors.append(
                        f"Fast väg {connection_id} måste ha default_state=open."
                    )
                if category == "hidden" and state not in {"open", "hidden"}:
                    cross_errors.append(
                        f"D-väg {connection_id} måste ha default_state=open eller hidden."
                    )
                if category == "hidden" and not label:
                    cross_errors.append(
                        f"D-väg {connection_id} saknar spelarvänlig label."
                    )
                if category == "scenario" and state not in {"closed", "sealed"}:
                    cross_errors.append(
                        f"Scenarioväg {connection_id} ska börja closed eller sealed."
                    )
                if state == "hidden" and discovery != "hidden_marker":
                    cross_errors.append(
                        f"Dold väg {connection_id} måste använda discovery=hidden_marker."
                    )
                if state in {"closed", "sealed"} and style not in {"potential", "none"}:
                    cross_errors.append(
                        f"Stängd väg {connection_id} måste ha printed_style=potential eller none."
                    )
                if category == "scenario" and not label:
                    cross_errors.append(
                        f"Scenarioväg {connection_id} saknar spelarvänlig label."
                    )
            for track in board["tracks"]:
                if track["id"] not in game_track_ids:
                    cross_errors.append(f"Brädspåret {track['id']} saknas i game.yaml.")
                expected_columns = track["maximum"] - track["minimum"] + 1
                if track["columns"] != expected_columns:
                    cross_errors.append(
                        f"Brädspåret {track['id']} har {track['columns']} kolumner men behöver {expected_columns}."
                    )
        if "reference_cards" in loaded:
            reference_cards = loaded["reference_cards"]["reference_cards"]
            ids = [card["id"] for card in reference_cards]
            if len(ids) != len(set(ids)):
                cross_errors.append("Duplicerade referenskorts-id:n.")
            for card in reference_cards:
                if card["source_ruleset"] != loaded["rules"]["ruleset"]["id"]:
                    cross_errors.append(
                        f"Referenskortet {card['id']} pekar på okänt ruleset."
                    )
                template_path = root / card["template"]
                if not template_path.exists():
                    cross_errors.append(
                        f"Referenskortets template saknas: {card['template']}"
                    )
                section_ids = [section["id"] for section in card["sections"]]
                required_sections = {"round", "actions", "symbols", "ending"}
                if set(section_ids) != required_sections:
                    cross_errors.append(
                        f"Referenskortet {card['id']} måste ha sektionerna "
                        "round, actions, symbols och ending."
                    )
        if "tokens" in loaded:
            token_data = loaded["tokens"]
            token_ids = [token["id"] for token in token_data["tokens"]]
            set_ids = {item["id"] for item in token_data["token_sets"]}
            if len(token_ids) != len(set(token_ids)):
                cross_errors.append("Duplicerade token-id:n i tokens.yaml.")
            game_resource_ids = {r["id"] for r in loaded["game"]["resources"]}
            game_track_ids = {t["id"] for t in loaded["game"]["tracks"]}
            for token in token_data["tokens"]:
                if token["set"] not in set_ids:
                    cross_errors.append(
                        f"Token {token['id']} pekar på okänt token-set."
                    )
                if token["type"] == "resource":
                    resource_id = token["id"].replace("resource_", "", 1)
                    if resource_id not in game_resource_ids:
                        cross_errors.append(
                            f"Resurstoken {token['id']} saknar motsvarande resurs."
                        )
                if token["type"] == "track":
                    track_id = token["id"].replace("track_", "", 1)
                    if track_id not in game_track_ids:
                        cross_errors.append(
                            f"Spårtoken {token['id']} saknar motsvarande spår."
                        )
        if "locations" in loaded:
            location_cards = loaded["locations"]["locations"]
            location_card_ids = [item["id"] for item in location_cards]
            if len(location_card_ids) != len(set(location_card_ids)):
                cross_errors.append("Duplicerade platskorts-id:n.")
            objective_cards = sum(
                item["count"] for item in location_cards if item["kind"] == "objective"
            )
            deck = loaded["locations"]["location_deck"]
            if objective_cards != deck["objective_count"]:
                cross_errors.append("Platslekens objective_count matchar inte målplatskorten.")
            if sum(item["count"] for item in location_cards) != deck["draw_count"]:
                cross_errors.append("Platslekens draw_count matchar inte antalet platskort.")

        if "road_markers" in loaded:
            marker_data = loaded["road_markers"]
            physical_markers = sum(
                item["count"] for item in marker_data["markers"]
                if item.get("purpose") not in {"scenario_connection_activation", "scenario_connection_closure"}
            )
            if physical_markers != marker_data["marker_set"]["count"]:
                cross_errors.append("Antalet vägmarkörer matchar inte marker_set.count.")
            result_counts = {
                result: sum(item["count"] for item in marker_data["markers"] if item["result"] == result)
                for result in ("open", "blocked", "travel_event")
            }
            if result_counts["blocked"] < 1 or result_counts["travel_event"] < 1:
                cross_errors.append("Vägmarkörspoolen behöver blockerad och färdhändelse.")

        if "travel_events" in loaded:
            travel_ids = [item["id"] for item in loaded["travel_events"]["cards"]]
            if len(travel_ids) != len(set(travel_ids)):
                cross_errors.append("Duplicerade färdhändelse-id:n.")

        if "scenarios" in loaded:
            scenario_ids = [s["id"] for s in loaded["scenarios"]["scenarios"]]
            if len(scenario_ids) != len(set(scenario_ids)):
                cross_errors.append("Duplicerade scenario-id:n.")
            board_location_ids = {loc["id"] for loc in loaded["board"]["locations"]}
            board_connection_ids = {c["id"] for c in loaded["board"]["connections"]}
            resource_ids = {r["id"] for r in loaded["game"]["resources"]}
            location_decks = {
                loaded["locations"]["location_deck"]["id"]: loaded["locations"]["location_deck"],
                loaded["okenrelaet_locations"]["location_deck"]["id"]: loaded["okenrelaet_locations"]["location_deck"],
            }
            road_set_id = loaded["road_markers"]["marker_set"]["id"]
            for scenario in loaded["scenarios"]["scenarios"]:
                setup = scenario["setup"]
                for location in (
                    setup["fixed_locations"]
                    + setup["location_slots"]
                    + [setup["starting_location"]]
                ):
                    if location not in board_location_ids:
                        cross_errors.append(
                            f"Scenario {scenario['id']} refererar okänd plats: {location}"
                        )
                for connection in setup["hidden_roads"]:
                    if connection not in board_connection_ids:
                        cross_errors.append(
                            f"Scenario {scenario['id']} refererar okänd väg: {connection}"
                        )
                for resource in scenario["starting_resources"]:
                    if resource not in resource_ids:
                        cross_errors.append(
                            f"Scenario {scenario['id']} refererar okänd startresurs: {resource}"
                        )
                if setup["location_deck"] not in location_decks:
                    cross_errors.append(f"Scenario {scenario['id']} har okänd platslek.")
                if setup["road_marker_set"] != road_set_id:
                    cross_errors.append(f"Scenario {scenario['id']} har okänd vägmarkörspool.")
                if setup["location_deck"] in location_decks and len(setup["location_slots"]) != location_decks[setup["location_deck"]]["draw_count"]:
                    cross_errors.append(f"Scenario {scenario['id']} har fel antal platsplatser.")
                marker_capacity = loaded["road_markers"]["marker_set"]["count"]
                if len(setup["hidden_roads"]) > marker_capacity:
                    cross_errors.append(
                        f"Scenario {scenario['id']} kräver fler dolda vägbrickor "
                        f"({len(setup['hidden_roads'])}) än poolen innehåller ({marker_capacity})."
                    )
                board_hidden_ids = {
                    connection["id"]
                    for connection in loaded["board"]["connections"]
                    if connection.get("category") == "hidden"
                }
                unknown_hidden = set(setup["hidden_roads"]) - board_hidden_ids
                if unknown_hidden:
                    cross_errors.append(
                        f"Scenario {scenario['id']} refererar okända D-vägar: "
                        f"{', '.join(sorted(unknown_hidden))}."
                    )
                if len(setup["hidden_roads"]) != len(set(setup["hidden_roads"])):
                    cross_errors.append(
                        f"Scenario {scenario['id']} innehåller dubblerade D-vägar."
                    )
                scenario_required = scenario["victory"].get(
                    "objective_cards_required",
                    scenario["victory"].get("objectives_required"),
                )
                game_required = loaded["game"]["objectives"].get(
                    "required_objective_cards",
                    loaded["game"]["objectives"].get("required_objective_tokens"),
                )
                if game_required != "scenario_defined" and scenario_required != game_required:
                    cross_errors.append(
                        f"Scenario {scenario['id']} har annat målantal än game.yaml."
                    )
        if "characters" in loaded:
            character_ids = [c["id"] for c in loaded["characters"]["characters"]]
            if len(character_ids) != len(set(character_ids)):
                cross_errors.append("Duplicerade karaktärs-id:n.")
            if len(character_ids) != loaded["characters"]["selection"]["pool_size"]:
                cross_errors.append("Karaktärspoolens storlek matchar inte antalet karaktärer.")
            default_capacity = loaded["inventory"]["inventory"]["default_capacity"]
            if loaded["characters"]["defaults"]["backpack_capacity"] != default_capacity:
                cross_errors.append("Standardkapacitet skiljer sig mellan characters.yaml och inventory.yaml.")

        if "equipment" in loaded:
            equipment_ids = [c["id"] for c in loaded["equipment"]["equipment"]]
            if len(equipment_ids) != len(set(equipment_ids)):
                cross_errors.append("Duplicerade utrustnings-id:n.")
            for item in loaded["equipment"]["equipment"]:
                if item["kind"] == "consumable" and "use" not in item:
                    cross_errors.append(f"Engångsutrustningen {item['id']} saknar use.")
                if item["kind"] == "permanent" and "passive" not in item:
                    cross_errors.append(f"Permanent utrustning {item['id']} saknar passive.")

        if "objectives" in loaded:
            objective_ids = [c["id"] for c in loaded["objectives"]["objectives"]]
            if len(objective_ids) != len(set(objective_ids)):
                cross_errors.append("Duplicerade målobjekts-id:n.")
            physical_objectives = sum(c["count"] for c in loaded["objectives"]["objectives"])
            game_required = loaded["game"]["objectives"]["required_objective_cards"]
            if game_required != "scenario_defined" and physical_objectives != game_required:
                cross_errors.append("Antalet målkort matchar inte spelets vinstkrav.")
            for objective in loaded["objectives"]["objectives"]:
                expected_slots = loaded["game"]["objectives"]["slots_each"]
                if expected_slots != "printed_on_card" and objective["slots"] != expected_slots:
                    cross_errors.append(f"Målobjektet {objective['id']} har fel ryggsäcksstorlek.")
                if objective["usable"]:
                    cross_errors.append(f"Målobjektet {objective['id']} får inte vara användbart.")

        if "rules" in loaded:
            phases = sorted(loaded["rules"]["round"]["phases"], key=lambda p: p["order"])
            phase_ids = [phase["id"] for phase in phases]
            if phase_ids != ["player_phase", "upkeep_phase", "endurance_phase"]:
                cross_errors.append(
                    "Rundordningen måste vara Spelarfas, Underhåll, Uthållighetsfas."
                )
            player_phase = next(p for p in phases if p["id"] == "player_phase")
            if player_phase.get("actor_order") != "fixed_clockwise":
                cross_errors.append("Spelarfasen måste använda fast medsols aktiveringsordning.")
            endurance_phase = next(p for p in phases if p["id"] == "endurance_phase")
            if not any(
                step.get("action") == "lose_endurance"
                for step in endurance_phase["steps"]
            ):
                cross_errors.append("Uthållighet måste förloras i Uthållighetsfasen i slutet av rundan.")

        forbidden_terms = ("resurs", "resurser", "föremål", "föremålet")
        player_facing_texts = []
        if "locations" in loaded:
            player_facing_texts.extend(
                card["display"]["body"] for card in loaded["locations"]["locations"]
            )
        if "travel_events" in loaded:
            player_facing_texts.extend(
                card["display"]["body"] for card in loaded["travel_events"]["cards"]
            )
        if "equipment" in loaded:
            player_facing_texts.extend(item["text"] for item in loaded["equipment"]["equipment"])
        if "objectives" in loaded:
            player_facing_texts.extend(item["text"] for item in loaded["objectives"]["objectives"])
        for content in player_facing_texts:
            lowered = content.lower()
            for term in forbidden_terms:
                if term in lowered:
                    cross_errors.append(
                        f"Förbjuden äldre spelterm i spelarinnehåll: '{term}' i '{content}'"
                    )
        if "simulation" in loaded:
            simulation = loaded["simulation"]
            scenario_ids = {s["id"] for s in loaded["scenarios"]["scenarios"]}
            if simulation["simulation"]["scenario_id"] not in scenario_ids:
                cross_errors.append("simulation.yaml refererar ett okänt scenario.")
            strategy_ids = [s["id"] for s in simulation["strategies"]]
            if len(strategy_ids) != len(set(strategy_ids)):
                cross_errors.append("Duplicerade strategi-id:n i simulation.yaml.")
            character_ids = {c["id"] for c in loaded["characters"]["characters"]}
            for strategy in simulation["strategies"]:
                for character_id in strategy["character_priority"]:
                    if character_id not in character_ids:
                        cross_errors.append(
                            f"Strategin {strategy['id']} refererar okänd karaktär: {character_id}"
                        )
        if "cooperation_ablation" in loaded:
            study_data = loaded["cooperation_ablation"]
            strategy_ids = {s["id"] for s in loaded["simulation"]["strategies"]}
            for strategy_id in study_data["study"]["strategies"]:
                if strategy_id not in strategy_ids:
                    cross_errors.append(
                        f"Ablationsstudien refererar okänd strategi: {strategy_id}"
                    )
            mode_ids = [mode["id"] for mode in study_data["modes"]]
            if len(mode_ids) != len(set(mode_ids)):
                cross_errors.append("Duplicerade samarbetsläge-id:n.")
            expected_modes = {
                "individual", "route_coordination",
                "full_cooperation", "free_transfer"
            }
            if set(mode_ids) != expected_modes:
                cross_errors.append("Ablationsstudien saknar ett obligatoriskt samarbetsläge.")
        if "base_profiles" in loaded and "scenarios" in loaded:
            base_by_id = {
                profile["id"]: profile
                for profile in loaded["base_profiles"]["base_profiles"]
            }
            index_by_id = {
                scenario["id"]: scenario
                for scenario in loaded["scenarios"]["scenarios"]
            }

            for scenario_id, indexed in index_by_id.items():
                pack_path = root / indexed["scenario_pack"]
                if not pack_path.exists():
                    cross_errors.append(
                        f"Scenario {scenario_id} saknar paketfil: {indexed['scenario_pack']}"
                    )
                    continue

                try:
                    pack = load_yaml(pack_path)["scenario_pack"]
                except Exception as exc:
                    cross_errors.append(
                        f"Scenario {scenario_id} kunde inte laddas: {exc}"
                    )
                    continue

                if pack["id"] != scenario_id:
                    cross_errors.append(
                        f"Scenarioindexets id {scenario_id} matchar inte paketets id {pack['id']}."
                    )
                if pack["base_profile"] not in base_by_id:
                    cross_errors.append(
                        f"Scenario {scenario_id} refererar okänd basprofil: {pack['base_profile']}"
                    )
                    continue

                profile = base_by_id[pack["base_profile"]]
                if indexed["base_profile"] != pack["base_profile"]:
                    cross_errors.append(
                        f"Scenario {scenario_id} har olika basprofil i index och paket."
                    )

                sources = pack["content"]["sources"]
                composition = pack["content"]["deck_composition"]
                required_sources = {"locations", "objectives"}
                if composition["equipment"] in {"scenario_only", "base_plus_scenario"}:
                    required_sources.add("equipment")
                if composition["travel_events"] in {"scenario_only", "base_plus_scenario"}:
                    required_sources.add("travel_events")
                if composition["tokens"] in {"scenario_only", "base_plus_scenario"}:
                    required_sources.add("tokens")

                for source_name in required_sources:
                    if source_name not in sources:
                        cross_errors.append(
                            f"Scenario {scenario_id} saknar källa för {source_name}."
                        )
                    elif not (root / sources[source_name]).exists():
                        cross_errors.append(
                            f"Scenario {scenario_id} saknar filen {sources[source_name]}."
                        )

                for source_name, source_path in profile["sources"].items():
                    if not (root / source_path).exists():
                        cross_errors.append(
                            f"Basprofil {profile['id']} saknar filen {source_path}."
                        )

                location_data = load_yaml(root / sources["locations"])
                objective_data = load_yaml(root / sources["objectives"])
                sets = pack["content"]["scenario_sets"]
                if sets["locations"] != location_data["location_deck"]["id"]:
                    cross_errors.append(
                        f"Scenario {scenario_id}: platslekens id matchar inte scenario_sets."
                    )
                if sets["objectives"] != objective_data["deck"]["id"]:
                    cross_errors.append(
                        f"Scenario {scenario_id}: mållekens id matchar inte scenario_sets."
                    )

                objective_ids = {
                    item["id"] for item in objective_data["objectives"]
                }
                for objective_id in pack["mission"]["objective_ids"]:
                    if objective_id not in objective_ids:
                        cross_errors.append(
                            f"Scenario {scenario_id} refererar okänt mål: {objective_id}"
                        )

                completion = pack["mission"]["completion"]
                if completion["required"] != pack["mission"]["required_objectives"]:
                    cross_errors.append(
                        f"Scenario {scenario_id}: completion.required skiljer sig från required_objectives."
                    )
                if completion["required"] != len(pack["mission"]["objective_ids"]):
                    cross_errors.append(
                        f"Scenario {scenario_id}: antal mål-id:n matchar inte completion.required."
                    )

                if completion["type"] == "place_items_at_tagged_locations":
                    target_tag = completion["target_location_tag"]
                    tagged = [
                        loc for loc in location_data["locations"]
                        if target_tag in loc.get("tags", [])
                    ]
                    if len(tagged) < completion["required"]:
                        cross_errors.append(
                            f"Scenario {scenario_id} har för få platser med taggen {target_tag}."
                        )
                    token_source = sources.get("tokens")
                    if token_source:
                        token_data = load_yaml(root / token_source)
                        token_ids = {
                            token["id"] for token in token_data.get("tokens", [])
                        }
                        if completion["place_token"] not in token_ids:
                            cross_errors.append(
                                f"Scenario {scenario_id} refererar okänd scenariomarkör: "
                                f"{completion['place_token']}"
                            )

                if completion["type"] == "deliver_items":
                    board_locations = {
                        location["id"] for location in loaded["board"]["locations"]
                    }
                    if completion["destination_location"] not in board_locations:
                        cross_errors.append(
                            f"Scenario {scenario_id} har okänd måldestination: "
                            f"{completion['destination_location']}"
                        )

        errors.extend(cross_errors)
        warnings.extend(cross_warnings)

    for warning in warnings:
        print(f"VARNING: {warning}")

    for error in errors:
        print(f"FEL: {error}", file=sys.stderr)

    if errors or (args.strict and warnings):
        print(
            f"Validering misslyckades: {len(errors)} fel, {len(warnings)} varningar.",
            file=sys.stderr,
        )
        return 1

    print(f"Validering godkänd: {len(pairs)} YAML-filer, {len(warnings)} varningar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
