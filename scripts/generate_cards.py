#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import textwrap
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def wrap_text(value: str, width_mm: float, font_size_mm: float, max_lines: int) -> list[str]:
    # Approximation for prototypes: average glyph width ~= 0.52 * font size.
    chars = max(8, int(width_mm / (font_size_mm * 0.52)))
    lines = textwrap.wrap(
        value,
        width=chars,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        lines[-1] = (last[:-1] + "…") if len(last) > 1 else "…"
    return [html.escape(line) for line in lines]


def icon_inner_svg(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(">")
    end = text.rfind("</svg>")
    if start < 0 or end < 0:
        raise ValueError(f"Ogiltig SVG-ikon: {path}")
    return text[start + 1:end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    cards_data = load_yaml(root / "data/cards.yaml")
    layout_data = load_yaml(root / "data/layouts/card-standard.yaml")
    layout = layout_data["layout"]
    fields = layout_data["fields"]
    palette = layout_data["palette"]
    render = layout_data["render"]

    env = Environment(
        loader=FileSystemLoader(root),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(layout["template"])
    output_dir = root / "output/components/cards"
    output_dir.mkdir(parents=True, exist_ok=True)

    for old in output_dir.glob("*.svg"):
        old.unlink()

    generated = []
    for card in cards_data["cards"]:
        icon_path = root / "assets/icons" / f"{card['icon']}.svg"
        if not icon_path.exists():
            raise FileNotFoundError(f"Ikon saknas: {icon_path}")

        accent = palette[card["type"]]
        svg = template.render(
            card=card,
            data_version=cards_data["version"],
            layout=layout,
            fields=fields,
            palette=palette,
            render=render,
            accent=accent,
            icon_svg=icon_inner_svg(icon_path),
            title_lines=wrap_text(
                card["display"]["title"],
                fields["title"]["width"],
                fields["title"]["font_size"],
                fields["title"]["max_lines"],
            ),
            body_lines=wrap_text(
                card["display"]["body"],
                fields["body"]["width"],
                fields["body"]["font_size"],
                fields["body"]["max_lines"],
            ),
            flavor_lines=wrap_text(
                card["display"]["flavor"],
                fields["flavor"]["width"],
                fields["flavor"]["font_size"],
                fields["flavor"]["max_lines"],
            ),
        )
        for copy_no in range(1, card["count"] + 1):
            suffix = f"-{copy_no:02d}" if card["count"] > 1 else ""
            path = output_dir / f"{card['id']}{suffix}.svg"
            path.write_text(svg, encoding="utf-8")
            generated.append(path)

    print(f"Genererade {len(generated)} kort-SVG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
