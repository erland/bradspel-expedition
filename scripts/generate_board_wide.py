#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy
from pathlib import Path
from typing import Any
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()

    board = copy.deepcopy(load_yaml(root / "data/board.yaml"))
    layout_data = copy.deepcopy(load_yaml(root / "data/layouts/board-standard.yaml"))

    # Primary large board: A3 portrait, exported as two landscape A4 pages.
    board["board"]["width_mm"] = 297
    board["board"]["height_mm"] = 420
    board["board"]["orientation"] = "portrait"
    layout_data["layout"]["width_mm"] = 297
    layout_data["layout"]["height_mm"] = 420
    layout_data["style"]["title_x"] = 148.5

    # Preserve all physical component sizes. Only spread their coordinates.
    # The horizontal seam between the two landscape A4 pages is at y=210 mm.
    # This transform leaves a clear seam corridor between T1/T2 and location 1/2.
    def large_x(value: float) -> float:
        return 12.0 + float(value) * 1.3

    def large_y(value: float) -> float:
        return float(value) * 1.35 - 10.0

    for loc in board["locations"]:
        loc["x"] = large_x(loc["x"])
        loc["y"] = large_y(loc["y"])

    for conn in board["connections"]:
        if "label_x" in conn:
            conn["label_x"] = large_x(conn["label_x"])
        if "label_y" in conn:
            conn["label_y"] = large_y(conn["label_y"])
        if "control_x" in conn:
            conn["control_x"] = large_x(conn["control_x"])
        if "control_y" in conn:
            conn["control_y"] = large_y(conn["control_y"])
        if "path_points" in conn:
            conn["path_points"] = [
                [large_x(x), large_y(y)] for x, y in conn["path_points"]
            ]

    if "legend" in board:
        board["legend"]["x"] = large_x(board["legend"]["x"])
        board["legend"]["y"] = large_y(board["legend"]["y"])

    for crossing in board.get("crossings", []):
        crossing["x"] = large_x(crossing["x"])
        crossing["y"] = large_y(crossing["y"])

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
        points = (
            " ".join(f"{point[0]},{point[1]}" for point in path_points)
            if path_points else None
        )
        connection_views.append({
            **connection,
            "x1": source["x"], "y1": source["y"],
            "x2": target["x"], "y2": target["y"],
            "mx": connection.get("label_x", (source["x"] + target["x"]) / 2),
            "my": connection.get("label_y", (source["y"] + target["y"]) / 2),
            "polyline_points": points,
        })

    location_views = [
        {
            **loc,
            "type_style": type_by_id[loc["type"]],
            "resource_label": resource_names.get(loc.get("resource"), ""),
        }
        for loc in board["locations"]
    ]
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
    svg = env.get_template(layout["template"]).render(
        board=board, layout=layout, palette=palette, style=style, render=render,
        connection_views=connection_views, location_views=location_views,
        track_values=track_values,
    )

    out = root / "output/components/boards/expedition-board-2xa4.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"Skapade A3-bräd-SVG för 2xA4: {out.relative_to(root)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
