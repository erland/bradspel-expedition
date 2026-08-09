#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
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

    data = load_yaml(root / "data/tokens.yaml")
    layout_data = load_yaml(root / "data/layouts/token-standard.yaml")
    layout = layout_data["layout"]
    style = layout_data["style"]
    palette = layout_data["palette"]

    env = Environment(
        loader=FileSystemLoader(root),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(layout["template"])

    out_dir = root / "output/components/tokens"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.svg"):
        old.unlink()

    generated = []
    for token in data["tokens"]:
        svg = template.render(
            token=SimpleNamespace(**token),
            layout=SimpleNamespace(**layout),
            style=SimpleNamespace(**style),
            palette=SimpleNamespace(**palette),
        )
        for copy_no in range(1, token["count"] + 1):
            suffix = f"-{copy_no:02d}"
            path = out_dir / f"{token['id']}{suffix}.svg"
            path.write_text(svg, encoding="utf-8")
            generated.append(path)

    print(f"Genererade {len(generated)} token-SVG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
