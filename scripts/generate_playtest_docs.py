#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=14, leading=17, spaceBefore=8, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, spaceBefore=6, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.2, leading=12, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="SmallCustom", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8, leading=10
    ))
    return styles


def inline_markdown(text: str) -> str:
    """Convert the small inline Markdown subset used by the project to ReportLab XML."""
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Code first so emphasis markers inside code are not interpreted.
    code_parts: list[str] = []
    def stash_code(match: re.Match[str]) -> str:
        code_parts.append(match.group(1))
        return f"@@CODE{len(code_parts) - 1}@@"

    escaped = re.sub(r"`([^`]+)`", stash_code, escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<i>\1</i>", escaped)

    for index, code in enumerate(code_parts):
        escaped = escaped.replace(
            f"@@CODE{index}@@",
            f'<font name="Courier">{code}</font>',
        )
    return escaped


def md_to_story(md_text: str, styles):
    story = []
    in_code = False
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 3 * mm))
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f'<font name="Courier">{escaped}</font>', styles["SmallCustom"]))
        elif line == "---":
            story.append(Spacer(1, 2 * mm))
        elif line.startswith("# "):
            story.append(Paragraph(inline_markdown(line[2:]), styles["TitleCustom"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline_markdown(line[3:]), styles["H1Custom"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline_markdown(line[4:]), styles["H2Custom"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + inline_markdown(line[2:]), styles["BodyCustom"]))
        elif re.match(r"^\d+\.\s+", line):
            story.append(Paragraph(inline_markdown(line), styles["BodyCustom"]))
        else:
            story.append(Paragraph(inline_markdown(line), styles["BodyCustom"]))
    return story


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    styles = build_styles()

    jobs = [
        ("docs/rulebook-playtest-v1.9.md", "output/print/pdf/rulebook-playtest-v1.9.pdf"),
        ("docs/assembly-guide-v1.9.md", "output/print/pdf/assembly-guide-v1.9.pdf"),
        ("docs/playtest-guide-v1.9.md", "output/print/pdf/playtest-guide-v1.9.pdf"),
        ("docs/playtest-form-v1.9.md", "output/print/pdf/playtest-forms-v1.9.pdf"),
    ]
    for source_rel, output_rel in jobs:
        source = root / source_rel
        output = root / output_rel
        output.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output), pagesize=A4,
            rightMargin=14 * mm, leftMargin=14 * mm,
            topMargin=14 * mm, bottomMargin=14 * mm,
            title=output.name,
        )
        doc.build(md_to_story(source.read_text(encoding="utf-8"), styles))
        print(f"Skapade dokument-PDF: {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
