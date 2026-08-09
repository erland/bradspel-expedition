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
        (root / "data/print-layouts/reference-a4.yaml").read_text(encoding="utf-8")
    )["print_layout"]

    single_svg = root / cfg["source_svg"]
    sheet_svg = root / cfg["output_svg"]
    single_pdf = root / cfg["single_pdf"]
    sheet_pdf = root / cfg["output_pdf"]

    for path in [single_svg, sheet_svg]:
        if not path.exists():
            raise FileNotFoundError(f"SVG saknas: {path}")

    single_pdf.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2pdf(
        url=str(single_svg),
        write_to=str(single_pdf),
        output_width=105 / 25.4 * 72,
        output_height=148 / 25.4 * 72,
    )
    cairosvg.svg2pdf(
        url=str(sheet_svg),
        write_to=str(sheet_pdf),
        output_width=210 / 25.4 * 72,
        output_height=297 / 25.4 * 72,
    )
    print(f"Skapade A6-PDF: {single_pdf.relative_to(root)}")
    print(f"Skapade A4 4-up PDF: {sheet_pdf.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
