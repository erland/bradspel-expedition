#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
import cairosvg,yaml

def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))
def marks(x,y,w,h,l=2.5):
    s='stroke="#333" stroke-width="0.2"'
    return [f'<path d="M{x-l},{y} H{x} M{x},{y-l} V{y}" {s}/>',
            f'<path d="M{x+w},{y} H{x+w+l} M{x+w},{y-l} V{y}" {s}/>',
            f'<path d="M{x-l},{y+h} H{x} M{x},{y+h} V{y+h+l}" {s}/>',
            f'<path d="M{x+w},{y+h} H{x+w+l} M{x+w},{y+h} V{y+h+l}" {s}/>']
def build(root, scenario_id, source):
    deck=load(root/source)["scenario_event_deck"]
    ids=[card["id"] for card in deck["cards"]]
    files=[root/f"output/components/scenario-events/{cid}.svg" for cid in ids]
    missing=[str(p.relative_to(root)) for p in files if not p.exists()]
    if missing: raise FileNotFoundError("Saknade scenariohändelser: "+", ".join(missing))
    chunks=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
            '<rect width="100%" height="100%" fill="#fff"/>',
            f'<text x="10" y="7" font-family="sans-serif" font-size="4" font-weight="700">{deck["name"].upper()}</text>']
    positions=[(8,12),(74,12),(8,104),(74,104)]
    for path,(x,y) in zip(files,positions):
        inner=path.read_text(encoding="utf-8")
        inner=re.sub(r"^.*?<svg[^>]*>","",inner,count=1,flags=re.S)
        inner=re.sub(r"</svg>\s*$","",inner,count=1,flags=re.S)
        chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
        chunks.extend(marks(x,y,63,88))
    chunks.append("</svg>")
    name=f"{scenario_id}-scenariohandelser-a4-01"
    svg=root/f"output/print/svg/{name}.svg"; pdf=root/f"output/print/pdf/{name}.pdf"
    svg.parent.mkdir(parents=True,exist_ok=True); pdf.parent.mkdir(parents=True,exist_ok=True)
    svg.write_text("\n".join(chunks),encoding="utf-8")
    cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),output_width=210/25.4*72,output_height=297/25.4*72)
    print(f"Skapade {svg.relative_to(root)} och {pdf.relative_to(root)} med {len(files)} kort.")
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args();root=a.root.resolve()
    build(root,"station-nordanvind","data/scenario-events/polar-station.yaml")
    build(root,"okenrelaet","data/scenario-events/desert.yaml")
    return 0
if __name__=="__main__": raise SystemExit(main())
