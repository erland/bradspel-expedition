#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
import cairosvg

def marks(x,y,w,h,l=2.5):
    s='stroke="#333" stroke-width="0.2"'
    return [f'<path d="M{x-l},{y} H{x} M{x},{y-l} V{y}" {s}/>',
            f'<path d="M{x+w},{y} H{x+w+l} M{x+w},{y-l} V{y}" {s}/>',
            f'<path d="M{x-l},{y+h} H{x} M{x},{y+h} V{y+h+l}" {s}/>',
            f'<path d="M{x+w},{y+h} H{x+w+l} M{x+w},{y+h} V{y+h+l}" {s}/>']

def build(root,group,name):
    files=sorted((root/"output/components/gameplay-cards").glob(f"{group}-*.svg"))
    chunks=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
            '<rect width="100%" height="100%" fill="#fff"/>']
    for i,path in enumerate(files):
        col=i%3;row=i//3;x=8+col*66.5;y=10+row*92
        inner=path.read_text(encoding="utf-8")
        inner=re.sub(r"^.*?<svg[^>]*>","",inner,count=1,flags=re.S)
        inner=re.sub(r"</svg>\s*$","",inner,count=1,flags=re.S)
        chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
        chunks.extend(marks(x,y,63,88))
    chunks.append("</svg>")
    svg=root/f"output/print/svg/{name}.svg";pdf=root/f"output/print/pdf/{name}.pdf"
    svg.parent.mkdir(parents=True,exist_ok=True);pdf.parent.mkdir(parents=True,exist_ok=True)
    svg.write_text("\n".join(chunks),encoding="utf-8")
    cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),
                    output_width=210/25.4*72,output_height=297/25.4*72)
    print(f"Skapade {svg.relative_to(root)} och {pdf.relative_to(root)}")

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args();root=a.root.resolve()
    build(root,"characters","gemensamma-karaktarskort-a4-01")
    build(root,"core-equipment","gemensam-utrustning-a4-01")
    build(root,"station-objectives","station-nordanvind-malobjekt-a4-01")
    return 0
if __name__=="__main__":raise SystemExit(main())
