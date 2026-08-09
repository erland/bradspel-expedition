#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def svg_inner(path: Path) -> list[ET.Element]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    return list(root)


def crop_marks(x: float, y: float, w: float, h: float, length: float) -> list[str]:
    s = []
    style = 'stroke="#333" stroke-width="0.2"'
    # top-left, top-right, bottom-left, bottom-right
    s += [
        f'<path d="M{x-length},{y} H{x} M{x},{y-length} V{y}" {style}/>',
        f'<path d="M{x+w},{y} H{x+w+length} M{x+w},{y-length} V{y}" {style}/>',
        f'<path d="M{x-length},{y+h} H{x} M{x},{y+h} V{y+h+length}" {style}/>',
        f'<path d="M{x+w},{y+h} H{x+w+length} M{x+w},{y+h} V{y+h+length}" {style}/>',
    ]
    return s


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    card_layout = load_yaml(root / "data/layouts/card-standard.yaml")["layout"]
    print_layout = load_yaml(root / "data/print-layouts/cards-a4.yaml")["print_layout"]

    cards = sorted((root / print_layout["source_directory"]).glob("*.svg"))
    if not cards:
        raise RuntimeError("Inga genererade kort-SVG hittades.")

    width = print_layout["width_mm"]
    height = print_layout["height_mm"]
    card_w = card_layout["width_mm"]
    card_h = card_layout["height_mm"]
    cols = print_layout["columns"]
    rows = print_layout["rows"]
    capacity = cols * rows
    if len(cards) > capacity:
        raise RuntimeError(
            f"{len(cards)} kort ryms inte på ett ark med kapacitet {capacity}."
        )

    chunks = [
        f'<svg xmlns="{SVG_NS}" width="{width}mm" height="{height}mm" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    for index, card_path in enumerate(cards):
        col = index % cols
        row = index // cols
        x = print_layout["margin_left_mm"] + col * (card_w + print_layout["gap_x_mm"])
        y = print_layout["margin_top_mm"] + row * (card_h + print_layout["gap_y_mm"])
        inner = card_path.read_text(encoding="utf-8")
        inner = re.sub(r"^.*?<svg[^>]*>", "", inner, count=1, flags=re.S)
        inner = re.sub(r"</svg>\s*$", "", inner, count=1, flags=re.S)
        chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
        if print_layout.get("crop_marks", False):
            chunks.extend(crop_marks(
                x, y, card_w, card_h,
                print_layout.get("crop_mark_length_mm", 2.5)
            ))

    chunks.append("</svg>")
    output_path = root / print_layout["output_svg"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Skapade A4-SVG: {output_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
