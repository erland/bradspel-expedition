#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, math
from pathlib import Path
import yaml

def load(path): return yaml.safe_load(path.read_text(encoding="utf-8"))

def marks(x,y,w,h,l):
    s='stroke="#333" stroke-width="0.2"'
    return [
      f'<path d="M{x-l},{y} H{x} M{x},{y-l} V{y}" {s}/>',
      f'<path d="M{x+w},{y} H{x+w+l} M{x+w},{y-l} V{y}" {s}/>',
      f'<path d="M{x-l},{y+h} H{x} M{x},{y+h} V{y+h+l}" {s}/>',
      f'<path d="M{x+w},{y+h} H{x+w+l} M{x+w},{y+h} V{y+h+l}" {s}/>',
    ]

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args(); root=args.root.resolve()
    cfg=load(root/"data/print-layouts/component-cards-a4.yaml")["print_layout"]
    layout=load(root/"data/layouts/component-card.yaml")["layout"]
    files=sorted((root/"output/components/scenario-cards").glob("*.svg"))
    groups={
      "station-nordanvind-platskort":[f for f in files if f.name.startswith("location-")],
      "gemensamma-fardhandelser":[f for f in files if f.name.startswith("travel-")],
    }
    for group, cards in groups.items():
      chunks=[f'<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
              '<rect width="100%" height="100%" fill="#fff"/>']
      for i,path in enumerate(cards):
        col=i%cfg["columns"]; row=i//cfg["columns"]
        x=cfg["margin_left_mm"]+col*(layout["width_mm"]+cfg["gap_x_mm"])
        y=cfg["margin_top_mm"]+row*(layout["height_mm"]+cfg["gap_y_mm"])
        inner=path.read_text(encoding="utf-8")
        inner=re.sub(r"^.*?<svg[^>]*>","",inner,count=1,flags=re.S)
        inner=re.sub(r"</svg>\s*$","",inner,count=1,flags=re.S)
        chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
        chunks.extend(marks(x,y,layout["width_mm"],layout["height_mm"],2.5))
      chunks.append("</svg>")
      out=root/f"output/print/svg/{group}-a4-01.svg"
      out.parent.mkdir(parents=True,exist_ok=True)
      out.write_text("\n".join(chunks),encoding="utf-8")
      print(f"Skapade {out.relative_to(root)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
