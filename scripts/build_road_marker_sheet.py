#!/usr/bin/env python3
from __future__ import annotations
import argparse,re
from pathlib import Path
import cairosvg
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
 a=p.parse_args();root=a.root.resolve()
 files=sorted((root/"output/components/road-markers").glob("*.svg"))
 chunks=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">','<rect width="100%" height="100%" fill="#fff"/>']
 for i,path in enumerate(files):
  col=i%8;row=i//8;x=10+col*25;y=22+row*27
  inner=path.read_text(encoding="utf-8")
  inner=re.sub(r"^.*?<svg[^>]*>","",inner,count=1,flags=re.S);inner=re.sub(r"</svg>\s*$","",inner,count=1,flags=re.S)
  chunks.append(f'<g transform="translate({x},{y})">{inner}</g>')
 chunks.append('<text x="10" y="118" font-family="DejaVu Sans" font-size="3.5">Dolda vägmarkörer läggs med baksidan upp på de D-vägar som scenariot anger.</text>')
 chunks.append('<text x="10" y="124" font-family="DejaVu Sans" font-size="3.5">Öppen/Stängd väg-markörer används för att ändra en tryckt vägstatus.</text>')
 chunks.append("</svg>")
 svg=root/"output/print/svg/gemensamma-vagbrickor-a4-01.svg";svg.parent.mkdir(parents=True,exist_ok=True);svg.write_text("\n".join(chunks),encoding="utf-8")
 pdf=root/"output/print/pdf/gemensamma-vagbrickor-a4-01.pdf";pdf.parent.mkdir(parents=True,exist_ok=True)
 cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),output_width=210/25.4*72,output_height=297/25.4*72)
 print(f"Skapade {svg.relative_to(root)} och {pdf.relative_to(root)}")
 return 0
if __name__=="__main__":raise SystemExit(main())
