#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, re, textwrap
from pathlib import Path
from types import SimpleNamespace
import cairosvg, yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load(p): return yaml.safe_load(p.read_text(encoding="utf-8"))
def wrap(t,w=34,n=6):
    x=textwrap.wrap(t,width=w,break_long_words=False,break_on_hyphens=False)
    return [html.escape(v) for v in x[:n]]
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
def inner(p):
    x=p.read_text(encoding="utf-8")
    x=re.sub(r"^.*?<svg[^>]*>","",x,count=1,flags=re.S)
    return re.sub(r"</svg>\s*$","",x,count=1,flags=re.S)
def marks(x,y,w,h):
    s='stroke="#333" stroke-width="0.2"'
    return [f'<path d="M{x-2.5},{y}H{x} M{x},{y-2.5}V{y}" {s}/>',
    f'<path d="M{x+w},{y}H{x+w+2.5} M{x+w},{y-2.5}V{y}" {s}/>',
    f'<path d="M{x-2.5},{y+h}H{x} M{x},{y+h}V{y+h+2.5}" {s}/>',
    f'<path d="M{x+w},{y+h}H{x+w+2.5} M{x+w},{y+h}V{y+h+2.5}" {s}/>']
def sheet(root, files, name, w=63,h=88):
    c=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">','<rect width="210" height="297" fill="#fff"/>']
    for i,p in enumerate(files):
        x=8+(i%3)*66.5;y=10+(i//3)*92
        c.append(f'<g transform="translate({x},{y})">{inner(p)}</g>');c+=marks(x,y,w,h)
    c.append('</svg>')
    svg=root/f"output/print/svg/{name}.svg";pdf=root/f"output/print/pdf/{name}.pdf"
    svg.parent.mkdir(parents=True,exist_ok=True);pdf.parent.mkdir(parents=True,exist_ok=True)
    svg.write_text("\n".join(c),encoding="utf-8")
    cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),output_width=210/25.4*72,output_height=297/25.4*72)
def main():
    a=argparse.ArgumentParser();a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);root=a.parse_args().root.resolve()
    env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,autoescape=False,trim_blocks=True,lstrip_blocks=True)
    comp=env.get_template("templates/cards/component-card.svg.j2");inv=env.get_template("templates/cards/inventory-card.svg.j2")
    layout=load(root/"data/layouts/component-card.yaml"); pal=layout["palette"];l=layout["layout"];f=layout["fields"];r=layout["render"]
    d=root/"data/scenarios/okenrelaet"; envd=root/"data/environments/desert"; out=root/"output/components/okenrelaet";out.mkdir(parents=True,exist_ok=True)
    for p in out.glob("*.svg"):p.unlink()
    cards=[]
    for c in load(d/"locations.yaml")["locations"]:
        cards.append(("scenario",c["id"],comp.render(width=l["width_mm"],height=l["height_mm"],radius=l["corner_radius_mm"],paper=pal["paper"],ink=pal["ink"],muted=pal["muted"],accent=pal[c["kind"]],font=r["font_family"],title_lines=title_layout(c["display"]["title"])["lines"],category="PLATS",symbol=c["symbol"],body_lines=wrap(c["display"]["body"],32,5),footer=c["display"]["footer"],display_id=c["display_id"],title_y=title_layout(c["display"]["title"])["title_y"],title_size=title_layout(c["display"]["title"])["size"],symbol_y=title_layout(c["display"]["title"])["symbol_y"],symbol_size=f["symbol_size"],body_y=f["body_y"],body_size=f["body_size"],footer_y=f["footer_y"],footer_size=f["footer_size"])))
    for c in load(envd/"travel-events.yaml")["cards"]:
        cards.append(("scenario",c["id"],comp.render(width=l["width_mm"],height=l["height_mm"],radius=l["corner_radius_mm"],paper=pal["paper"],ink=pal["ink"],muted=pal["muted"],accent=pal["travel"],font=r["font_family"],title_lines=title_layout(c["display"]["title"])["lines"],category="FÄRDHÄNDELSE",symbol="!",body_lines=wrap(c["display"]["body"],32,5),footer=c["display"]["footer"],display_id="",title_y=title_layout(c["display"]["title"])["title_y"],title_size=title_layout(c["display"]["title"])["size"],symbol_y=title_layout(c["display"]["title"])["symbol_y"],symbol_size=f["symbol_size"],body_y=f["body_y"],body_size=f["body_size"],footer_y=f["footer_y"],footer_size=f["footer_size"])))
    invcards=[]
    for source,cat,accent,footer in [(d/"objectives.yaml","MÅLOBJEKT","#a6782f","Reservmodul"),(envd/"equipment.yaml","UTRUSTNING","#5d6f86","Extra utrustning")]:
        key="objectives" if "objectives" in source.name else "equipment"
        for c in load(source)[key]:
            invcards.append((c["id"],inv.render(width=63,height=88,title=c["name"],category=cat,symbol=c["symbol"],accent=accent,stat_lines=[f"Ryggsäck: {c['slots']} " + ("plats" if c["slots"] == 1 else "platser")],body_lines=wrap(c["text"],37,7),body_start=57,footer=footer)))
    scenfiles=[]
    for _,cid,svg in cards:
        p=out/f"scenario-{cid}.svg";p.write_text(svg,encoding="utf-8");scenfiles.append(p)
    invfiles=[]
    for cid,svg in invcards:
        p=out/f"inventory-{cid}.svg";p.write_text(svg,encoding="utf-8");invfiles.append(p)
    sheet(root,scenfiles,"okenrelaet-platskort-och-okenmiljo-fardhandelser-a4-01")
    sheet(root,invfiles,"okenrelaet-malobjekt-och-okenmiljo-utrustning-a4-01")
    print(f"Genererade Ökenreläets {len(cards)+len(invcards)} kort och två A4-ark.")
    return 0
if __name__=="__main__": raise SystemExit(main())
