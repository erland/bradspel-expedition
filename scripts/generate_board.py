#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    board = load_yaml(root / "data/board.yaml")
    layout_data = load_yaml(root / "data/layouts/board-standard.yaml")
    layout = layout_data["layout"]
    palette = layout_data["palette"]
    style = layout_data["style"]
    render = layout_data["render"]

    location_by_id = {loc["id"]: loc for loc in board["locations"]}
    type_by_id = {item["id"]: item for item in board["location_types"]}
    resource_names = {
        item["id"]: item["name"]
        for item in load_yaml(root / "data/game.yaml")["resources"]
    }

    connection_views = []
    for connection in board["connections"]:
        source = location_by_id[connection["from"]]
        target = location_by_id[connection["to"]]
        path_points = connection.get("path_points")
        if path_points:
            points = " ".join(f"{point[0]},{point[1]}" for point in path_points)
        else:
            points = None
        connection_views.append({
            **connection,
            "x1": source["x"],
            "y1": source["y"],
            "x2": target["x"],
            "y2": target["y"],
            "mx": connection.get("label_x", (source["x"] + target["x"]) / 2),
            "my": connection.get("label_y", (source["y"] + target["y"]) / 2),
            "polyline_points": points,
        })

    location_views = []
    for location in board["locations"]:
        location_views.append({
            **location,
            "type_style": type_by_id[location["type"]],
            "resource_label": resource_names.get(location.get("resource"), ""),
        })

    track_values = {
        track["id"]: list(range(track["minimum"], track["maximum"] + 1))
        for track in board["tracks"]
    }

    env = Environment(
        loader=FileSystemLoader(root),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(layout["template"])
    svg = template.render(
        board=board,
        layout=layout,
        palette=palette,
        style=style,
        render=render,
        connection_views=connection_views,
        location_views=location_views,
        track_values=track_values,
    )

    output_path = root / "output/components/boards/expedition-board-02.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Skapade bräd-SVG: {output_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
