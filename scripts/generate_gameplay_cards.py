#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, textwrap
from pathlib import Path
from types import SimpleNamespace
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))

def wrap(text, width=37, max_lines=7):
    lines=textwrap.wrap(text,width=width,break_long_words=False,break_on_hyphens=False)
    if len(lines)>max_lines:
        lines=lines[:max_lines]; lines[-1]=lines[-1][:-1]+"…"
    return [html.escape(line) for line in lines]

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args();root=a.root.resolve()
    env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,
                    autoescape=False,trim_blocks=True,lstrip_blocks=True)
    tpl=env.get_template("templates/cards/inventory-card.svg.j2")
    out=root/"output/components/gameplay-cards";out.mkdir(parents=True,exist_ok=True)
    for old in out.glob("*.svg"):old.unlink()
    cards=[]
    chars=load(root/"data/characters.yaml")
    for c in chars["characters"]:
        cards.append(dict(group="characters",id=c["id"],title=c["name"],category="KARAKTÄR",
            symbol=c["symbol"],accent="#56785b",
            stats=[f"Hälsa: {c['health']}",f"Ryggsäck: {c['backpack_capacity']} platser"],
            body=c["ability"]["text"],footer="Karaktärsförmåga",count=1))
    eq=load(root/"data/base/equipment.yaml")
    for c in eq["equipment"]:
        kind="Engångsutrustning" if c["kind"]=="consumable" else "Permanent utrustning"
        cards.append(dict(group="core-equipment",id=c["id"],title=c["name"],category="UTRUSTNING",
            symbol=c["symbol"],accent="#5d6f86",
            stats=[f"Ryggsäck: {c['slots']} plats",kind],
            body=c["text"],footer="Kan användas som utrustning" if c["kind"]=="consumable" else "Passiv effekt",
            count=c["count"]))
    obj=load(root/"data/scenarios/station-nordanvind/objectives.yaml")
    for c in obj["objectives"]:
        cards.append(dict(group="station-objectives",id=c["id"],title=c["name"],category="MÅLOBJEKT",
            symbol=c["symbol"],accent="#a6782f",
            stats=[f"Ryggsäck: {c['slots']} platser","Kan inte användas"],
            body=c["text"],footer="",count=c["count"]))
    n=0
    for c in cards:
        svg=tpl.render(width=63,height=88,title=c["title"],category=c["category"],
            symbol=c["symbol"],accent=c["accent"],stat_lines=c["stats"],
            body_lines=wrap(c["body"]),body_start=61 if len(c["stats"])==2 else 57,
            footer=c["footer"])
        for i in range(1,c["count"]+1):
            path=out/f"{c['group']}-{c['id']}-{i:02d}.svg"
            path.write_text(svg,encoding="utf-8");n+=1
    print(f"Genererade {n} karaktärs-, utrustnings- och målkort.")
    return 0
if __name__=="__main__":raise SystemExit(main())
