#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, xml.etree.ElementTree as ET
from pathlib import Path
import cairosvg
from pypdf import PdfReader, PdfWriter

A4_LANDSCAPE_WIDTH_MM = 297
A4_LANDSCAPE_HEIGHT_MM = 210

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()

    source = root / "output/components/boards/expedition-board-2xa4.svg"
    out_svg = root / "output/print/svg"
    out_pdf = root / "output/print/pdf"
    out_svg.mkdir(parents=True, exist_ok=True)
    out_pdf.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(source)
    original = tree.getroot()
    pages = []

    # Printer-safe A3 portrait split into two landscape A4 pages.
    # A 14 mm overlap keeps seam content at least 7 mm from both page edges.
    # The omitted 7 mm at the master top and bottom is empty margin.
    for name, y in [("ovre", 7), ("nedre", 203)]:
        node = copy.deepcopy(original)
        node.set("width", f"{A4_LANDSCAPE_WIDTH_MM}mm")
        node.set("height", f"{A4_LANDSCAPE_HEIGHT_MM}mm")
        node.set("viewBox", f"0 {y} {A4_LANDSCAPE_WIDTH_MM} {A4_LANDSCAPE_HEIGHT_MM}")

        svg_path = out_svg / f"spelplan-2xa4-{name}.svg"
        ET.ElementTree(node).write(svg_path, encoding="unicode", xml_declaration=True)

        pdf_path = out_pdf / f"spelplan-2xa4-{name}.pdf"
        cairosvg.svg2pdf(
            url=str(svg_path),
            write_to=str(pdf_path),
            output_width=A4_LANDSCAPE_WIDTH_MM / 25.4 * 96,
            output_height=A4_LANDSCAPE_HEIGHT_MM / 25.4 * 96,
        )
        pages.append(pdf_path)

    writer = PdfWriter()
    for page_path in pages:
        for page in PdfReader(str(page_path)).pages:
            writer.add_page(page)

    combined = out_pdf / "spelplan-2xa4.pdf"
    with combined.open("wb") as handle:
        writer.write(handle)

    print(f"Skapade skrivarsäker 2xA4-spelplan med 14 mm överlapp: {combined.relative_to(root)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
