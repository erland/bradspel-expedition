#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import textwrap
from pathlib import Path
from types import SimpleNamespace

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def wrap(text: str, width: int, maximum: int | None = None) -> list[str]:
    lines = textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if maximum and len(lines) > maximum:
        lines = lines[:maximum]
        lines[-1] = lines[-1].rstrip(".") + "..."
    return [html.escape(line) for line in lines]


def bullets(items: list[str], width: int, maximum: int) -> list[str]:
    output: list[str] = []
    for item in items:
        for index, line in enumerate(wrap(item, width)):
            output.append(("• " if index == 0 else "  ") + line)
            if len(output) >= maximum:
                return output
    return output


def item_names(path: Path, key: str) -> list[str]:
    data = load(path)
    return [str(item["name"]) for item in data.get(key, [])]


def deck_count(path: Path, key: str) -> int:
    data = load(path)
    return sum(int(item.get("count", 1)) for item in data.get(key, []))


def compact_group(title: str, names: list[str], width: int = 49) -> list[str]:
    lines = [title]
    joined = " · ".join(names)
    lines.extend(textwrap.wrap(joined, width=width, break_long_words=False, break_on_hyphens=False))
    return lines


def wrapped_bullet(text: str, width: int = 40) -> list[str]:
    wrapped = textwrap.wrap(
        text,
        width=width,
        initial_indent="• ",
        subsequent_indent="  ",
        break_long_words=False,
        break_on_hyphens=False,
    )
    return wrapped or ["•"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    root = parser.parse_args().root.resolve()

    layout = load(root / "data/layouts/scenario-a5.yaml")
    board_data = load(root / "data/board.yaml")
    road_label_by_id = {c["id"]: c.get("label", c["id"]) for c in board_data["connections"]}
    env = Environment(
        loader=FileSystemLoader(root),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    output_dir = root / "output/components/scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob("*-a5.svg"):
        old.unlink()

    for scenario_file in sorted((root / "data/scenarios").glob("*/scenario.yaml")):
        data = load(scenario_file)["scenario_pack"]
        setup = data["setup"]
        card_counts = data["content"]["scenario_cards"]
        sources = data["content"]["sources"]
        base_sources = data["content"].get("base_sources", {})

        intro = wrap(data["story"]["introduction"], 82, 6)
        briefing = wrap(data["story"]["briefing"], 78, 3)

        marker_pool = setup["hidden_road_marker_pool"]
        setup_items = [
            f"2 karaktärer: {setup['endurance_by_character_count']['2']} uthållighet · "
            f"{setup['starting_tools_by_character_count']['2']} verktyg",
            f"3 karaktärer: {setup['endurance_by_character_count']['3']} uthållighet · "
            f"{setup['starting_tools_by_character_count']['3']} verktyg",
            f"4 karaktärer: {setup['endurance_by_character_count']['4']} uthållighet · "
            f"{setup['starting_tools_by_character_count']['4']} verktyg",
            f"{setup['location_slots']} platskort + matchande platsbrickor",
            f"Dolda vägbrickor: {marker_pool['open']} öppna, "
            f"{marker_pool['blocked']} hinder, {marker_pool['travel_event']} händelse",
            f"Dolda vägar: {', '.join(road_label_by_id[r] for r in setup.get('hidden_roads', []))}",
            f"{setup['supply_depot_tools']} verktyg vid Förrådet",
        ]
        setup_lines = [
            line
            for item in setup_items
            for line in wrapped_bullet(item, width=46)
        ]

        location_path = root / sources["locations"]
        objective_path = root / sources["objectives"]
        location_names = item_names(location_path, "locations")
        objective_names = item_names(objective_path, "objectives")
        objective_deck = load(objective_path).get("deck", {})
        objective_deck_name = str(objective_deck.get("name", "")).lower()

        content_lines: list[str] = []
        content_lines.extend(
            compact_group("PLATSKORT · DOLD RAD", location_names, width=51)
        )
        content_lines.extend(
            compact_group("MÅLOBJEKT · EGEN HÖG", objective_names, width=51)
        )


        scenario_travel_names: list[str] = []
        scenario_travel_count = int(card_counts.get("travel_events", 0))
        if scenario_travel_count and sources.get("travel_events"):
            scenario_travel_names = item_names(root / sources["travel_events"], "cards")

        if scenario_travel_names:
            content_lines.extend(
                compact_group(
                    "FÄRDHÄNDELSER · BLANDA MED ÖVRIGA",
                    scenario_travel_names,
                    width=51,
                )
            )

        scenario_event_cfg = data.get("scenario_events")
        if scenario_event_cfg:
            event_deck = load(root / scenario_event_cfg["source"])["scenario_event_deck"]
            event_by_id = {card["id"]: card["name"] for card in event_deck["cards"]}
            milestone_names = [
                event_by_id[item["resolve"]["card_id"]]
                for item in scenario_event_cfg.get("milestones", [])
            ]
            content_lines.extend(
                compact_group(
                    "SCENARIOHÄNDELSER · EGEN HÖG",
                    milestone_names,
                    width=51,
                )
            )

        equipment_count = int(card_counts.get("equipment", 0))
        if equipment_count and sources.get("equipment"):
            equipment_names = item_names(root / sources["equipment"], "equipment")
            content_lines.extend(
                compact_group(
                    "UTRUSTNING · BLANDA MED ÖVRIGA",
                    equipment_names,
                    width=51,
                )
            )

        # Keep the A5 section readable and deterministic.
        content_lines = content_lines[:14]

        svg = env.get_template(data["presentation"]["template"]).render(
            scenario=SimpleNamespace(**data),
            palette=SimpleNamespace(**layout["palette"]),
            style=SimpleNamespace(**layout["style"]),
            intro_lines=intro,
            briefing_lines=briefing,
            briefing_y=38 + len(intro) * 4.1 + 3.2,
            setup_lines=[html.escape(line) for line in setup_lines],
            content_lines=[html.escape(line) for line in content_lines],
            special_lines=bullets(
                data["mission"]["player_instructions"] + [
                    m["label"]
                    for m in data.get("scenario_events", {}).get("milestones", [])
                ],
                90,
                8,
            ),
            victory_items=[
                [html.escape(line) for line in wrap(item, 50, 2)]
                for item in data["victory"]
            ],
        )

        path = output_dir / f"{data['id'].replace('_', '-')}-a5.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"Skapade A5-scenariokort: {path.relative_to(root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
