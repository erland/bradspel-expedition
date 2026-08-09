#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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

    token_data = load_yaml(root / "data/tokens.yaml")
    cfg = load_yaml(root / "data/print-layouts/tokens-a4.yaml")["print_layout"]

    token_by_prefix = {token["id"]: token for token in token_data["tokens"]}
    files = sorted((root / cfg["source_directory"]).glob("*.svg"))
    if not files:
        raise RuntimeError("Inga genererade token-SVG hittades.")

    width = cfg["width_mm"]
    height = cfg["height_mm"]
    x = cfg["margin_left_mm"]
    y = cfg["margin_top_mm"]
    row_height = 0

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    for path in files:
        token_id = re.sub(r"-\d\d$", "", path.stem)
        token = token_by_prefix[token_id]
        size = token["size_mm"]

        if x + size > width - cfg["margin_left_mm"]:
            x = cfg["margin_left_mm"]
            y += row_height + cfg["gap_y_mm"]
            row_height = 0

        if y + size > height - cfg["margin_top_mm"]:
            raise RuntimeError("Alla tokens ryms inte på ett A4-ark.")

        inner = path.read_text(encoding="utf-8")
        inner = re.sub(r"^.*?<svg[^>]*>", "", inner, count=1, flags=re.S)
        inner = re.sub(r"</svg>\s*$", "", inner, count=1, flags=re.S)

        chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
        if cfg["crop_marks"]:
            chunks.extend(crop_marks(
                x, y, size, size, cfg["crop_mark_length_mm"]
            ))

        x += size + cfg["gap_x_mm"]
        row_height = max(row_height, size)

    chunks.append("</svg>")
    out = root / cfg["output_svg"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Skapade tokenark-SVG: {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
