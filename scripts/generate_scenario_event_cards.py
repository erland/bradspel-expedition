#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, textwrap
from pathlib import Path
from types import SimpleNamespace
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))
def wrap(text,width=36,max_lines=6):
    lines=textwrap.wrap(text,width=width,break_long_words=False,break_on_hyphens=False)
    return [html.escape(x) for x in lines[:max_lines]]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args(); root=a.root.resolve()
    env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,autoescape=False,
                    trim_blocks=True,lstrip_blocks=True)
    tpl=env.get_template("templates/cards/inventory-card.svg.j2")
    out=root/"output/components/scenario-events"; out.mkdir(parents=True,exist_ok=True)
    for old in out.glob("*.svg"): old.unlink()
    count=0
    for source, accent, env_label in [
        ("data/scenario-events/polar-station.yaml","#58758a","STATION NORDANVIND"),
        ("data/scenario-events/desert.yaml","#a97843","ÖKENRELÄET"),
    ]:
        deck=load(root/source)["scenario_event_deck"]
        for card in deck["cards"]:
            svg=tpl.render(width=63,height=88,title=card["name"],category="SCENARIOHÄNDELSE",
                symbol=card["symbol"],accent=accent,
                stat_lines=[env_label,"Lös omedelbart"],
                body_lines=wrap(card["text"]),body_start=61,
                footer="Kassera efter att effekten lösts")
            path=out/f"{card['id']}.svg"; path.write_text(svg,encoding="utf-8"); count+=1
    print(f"Genererade {count} scenariohändelsekort.")
    return 0
if __name__=="__main__": raise SystemExit(main())
