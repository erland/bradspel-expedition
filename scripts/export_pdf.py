#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cairosvg
import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()

    config = yaml.safe_load(
        (root / "data/print-layouts/cards-a4.yaml").read_text(encoding="utf-8")
    )["print_layout"]
    svg_path = root / config["output_svg"]
    pdf_path = root / config["output_pdf"]
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG saknas: {svg_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2pdf(
        url=str(svg_path),
        write_to=str(pdf_path),
        output_width=210 / 25.4 * 72,
        output_height=297 / 25.4 * 72,
    )
    print(f"Skapade PDF: {pdf_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
