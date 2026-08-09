#!/usr/bin/env python3
import argparse
from pathlib import Path
import cairosvg
def main():
 a=argparse.ArgumentParser();a.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);root=a.parse_args().root.resolve()
 out=root/"output/print/pdf";out.mkdir(parents=True,exist_ok=True)
 for svg in sorted((root/"output/components/scenarios").glob("*-a5.svg")):
  pdf=out/f"{svg.stem.removesuffix('-a5')}-scenarioark-a5.pdf";cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),output_width=148/25.4*96,output_height=210/25.4*96)
 for svg in sorted((root/"output/print/svg").glob("*-scenarioark-a4.svg")):
  pdf=out/f"{svg.stem}.pdf";cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),output_width=210/25.4*96,output_height=297/25.4*96)
 print("Exporterade scenariokort för alla scenarier.")
 return 0
if __name__=="__main__":raise SystemExit(main())
