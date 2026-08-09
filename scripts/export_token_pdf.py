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

    cfg = yaml.safe_load(
        (root / "data/print-layouts/tokens-a4.yaml").read_text(encoding="utf-8")
    )["print_layout"]
    svg = root / cfg["output_svg"]
    pdf = root / cfg["output_pdf"]

    if not svg.exists():
        raise FileNotFoundError(f"Tokenark-SVG saknas: {svg}")

    pdf.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2pdf(
        url=str(svg),
        write_to=str(pdf),
        output_width=210 / 25.4 * 72,
        output_height=297 / 25.4 * 72,
    )
    print(f"Skapade tokenark-PDF: {pdf.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
