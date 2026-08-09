#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def crop_marks(x: float, y: float, w: float, h: float, length: float) -> list[str]:
    style = 'stroke="#333" stroke-width="0.2"'
    return [
        f'<path d="M{x-length},{y} H{x} M{x},{y-length} V{y}" {style}/>',
        f'<path d="M{x+w},{y} H{x+w+length} M{x+w},{y-length} V{y}" {style}/>',
        f'<path d="M{x-length},{y+h} H{x} M{x},{y+h} V{y+h+length}" {style}/>',
        f'<path d="M{x+w},{y+h} H{x+w+length} M{x+w},{y+h} V{y+h+length}" {style}/>',
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    cfg = yaml.safe_load(
        (root / "data/print-layouts/reference-a4.yaml").read_text(encoding="utf-8")
    )["print_layout"]
    layout = yaml.safe_load(
        (root / "data/layouts/reference-a6.yaml").read_text(encoding="utf-8")
    )["layout"]

    source = root / cfg["source_svg"]
    if not source.exists():
        raise FileNotFoundError(f"Referenskort saknas: {source}")

    inner = source.read_text(encoding="utf-8")
    inner = re.sub(r"^.*?<svg[^>]*>", "", inner, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, count=1, flags=re.S)

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{cfg["width_mm"]}mm" '
        f'height="{cfg["height_mm"]}mm" viewBox="0 0 {cfg["width_mm"]} {cfg["height_mm"]}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for row in range(cfg["rows"]):
        for col in range(cfg["columns"]):
            x = cfg["margin_left_mm"] + col * (layout["width_mm"] + cfg["gap_x_mm"])
            y = cfg["margin_top_mm"] + row * (layout["height_mm"] + cfg["gap_y_mm"])
            chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
            if cfg["crop_marks"]:
                chunks.extend(crop_marks(
                    x, y, layout["width_mm"], layout["height_mm"],
                    cfg["crop_mark_length_mm"]
                ))
    chunks.append("</svg>")

    output = root / cfg["output_svg"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Skapade A4 4-up SVG: {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
