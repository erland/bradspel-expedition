#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, textwrap
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def wrap(value, width=32, max_lines=5):
    lines = textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…"
    return [html.escape(x) for x in lines]



def estimated_text_width(value):
    """Approximerad rubrikbredd i relativa glyph-enheter."""
    wide = set("MWÅÄÖQGmwåäö")
    narrow = set("Iil1.,:;!'| ")
    total = 0.0
    for char in value:
        if char in wide:
            total += 1.35
        elif char in narrow:
            total += 0.55
        else:
            total += 1.0
    return total

def title_layout(value):
    """Säker rubriklayout för 57 mm-kort."""
    max_single_width = 17.5
    if estimated_text_width(value) <= max_single_width:
        return {
            "lines": [html.escape(value)],
            "size": 4.4,
            "title_y": 15.0,
            "symbol_y": 34.0,
        }

    words = value.split()
    best = None
    for split_at in range(1, len(words)):
        first = " ".join(words[:split_at])
        second = " ".join(words[split_at:])
        score = max(estimated_text_width(first), estimated_text_width(second))
        if best is None or score < best[0]:
            best = (score, first, second)

    if best is None:
        lines = textwrap.wrap(
            value, width=18, break_long_words=False, break_on_hyphens=False
        )[:2]
    else:
        lines = [best[1], best[2]]

    widest = max(estimated_text_width(line) for line in lines)
    size = 3.8 if widest <= 20 else 3.5
    return {
        "lines": [html.escape(line) for line in lines],
        "size": size,
        "title_y": 17.4,
        "symbol_y": 35.8,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args=p.parse_args(); root=args.root.resolve()
    layout=load(root/"data/layouts/component-card.yaml")
    env=Environment(loader=FileSystemLoader(root), undefined=StrictUndefined,
                    autoescape=False, trim_blocks=True, lstrip_blocks=True)
    tpl=env.get_template("templates/cards/component-card.svg.j2")
    out=root/"output/components/scenario-cards"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"): old.unlink()

    items=[]
    loc=load(root/"data/scenarios/station-nordanvind/locations.yaml")
    for card in loc["locations"]:
        items.append({
            "id":card["id"], "title":card["display"]["title"],
            "body":card["display"]["body"], "footer":card["display"]["footer"],
            "symbol":card["symbol"], "accent":layout["palette"][card["kind"]],
            "count":card["count"], "category":"location", "type_label":"PLATS", "display_id": card["display_id"],
        })
    fixed=load(root/"data/base/fixed-locations.yaml")
    for card in fixed["locations"]:
        items.append({
            "id":card["id"], "title":card["display"]["title"],
            "body":card["display"]["body"], "footer":card["display"]["footer"],
            "symbol":card["symbol"], "accent":layout["palette"].get(card["kind"], layout["palette"]["resource"]),
            "count":card["count"], "category":"location", "type_label":"FAST PLATS", "display_id": card["display_id"],
        })

    travel=load(root/"data/base/travel-events.yaml")
    travel_symbols={
        "travel_rockfall":"-1","travel_bad_visibility":"!",
        "travel_lost_pack":"R","travel_bad_weather":"!",
        "travel_detour":"↔","travel_calm_passage":"✓",
    }
    for card in travel["cards"]:
        items.append({
            "id":card["id"], "title":card["display"]["title"],
            "body":card["display"]["body"], "footer":card["display"]["footer"],
            "symbol":travel_symbols.get(card["id"], "!"),
            "accent":layout["palette"]["travel"],
            "count":card["count"], "category":"travel", "type_label":"FÄRDHÄNDELSE", "display_id": "",
        })

    l=layout["layout"]; f=layout["fields"]; r=layout["render"]; pal=layout["palette"]
    generated=[]
    for item in items:
        svg=tpl.render(
            width=l["width_mm"], height=l["height_mm"], radius=l["corner_radius_mm"],
            paper=pal["paper"], ink=pal["ink"], muted=pal["muted"],
            accent=item["accent"], font=r["font_family"],
            title_lines=title_layout(item["title"])["lines"], category=item["type_label"], symbol=item["symbol"],
            body_lines=wrap(item["body"]), footer=item["footer"], display_id=item["display_id"],
            title_y=title_layout(item["title"])["title_y"], title_size=title_layout(item["title"])["size"],
            symbol_y=title_layout(item["title"])["symbol_y"], symbol_size=f["symbol_size"],
            body_y=f["body_y"], body_size=f["body_size"],
            footer_y=f["footer_y"], footer_size=f["footer_size"],
        )
        for copy in range(1,item["count"]+1):
            path=out/f"{item['category']}-{item['id']}-{copy:02d}.svg"
            path.write_text(svg, encoding="utf-8"); generated.append(path)
    print(f"Genererade {len(generated)} scenario-kort-SVG.")
    return 0
if __name__=="__main__": raise SystemExit(main())
