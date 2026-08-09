#!/usr/bin/env python3
import argparse,re
from pathlib import Path
def marks(x,y,w,h):
 s='stroke="#333" stroke-width="0.2"';return [f'<path d="M{x-3},{y}H{x} M{x},{y-3}V{y}" {s}/>',f'<path d="M{x+w},{y}H{x+w+3} M{x+w},{y-3}V{y}" {s}/>',f'<path d="M{x-3},{y+h}H{x} M{x},{y+h}V{y+h+3}" {s}/>',f'<path d="M{x+w},{y+h}H{x+w+3} M{x+w},{y+h}V{y+h+3}" {s}/>']
def main():
 a=argparse.ArgumentParser();a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);root=a.parse_args().root.resolve()
 for source in sorted((root/"output/components/scenarios").glob("*-a5.svg")):
  inner=source.read_text();inner=re.sub(r"^.*?<svg[^>]*>","",inner,count=1,flags=re.S);inner=re.sub(r"</svg>\s*$","",inner,count=1,flags=re.S)
  x,y=31,20;c=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">','<rect width="210" height="297" fill="#fff"/>',f'<g transform="translate({x},{y})">{inner}</g>']+marks(x,y,148,210)+['</svg>']
  out=root/f"output/print/svg/{source.stem.replace('-a5','')}-scenarioark-a4.svg";out.parent.mkdir(parents=True,exist_ok=True);out.write_text("\n".join(c))
  print(f"Skapade {out.relative_to(root)}")
 return 0
if __name__=="__main__":raise SystemExit(main())
