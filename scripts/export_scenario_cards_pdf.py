#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import cairosvg
def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args(); root=args.root.resolve()
    for name in ["station-nordanvind-platskort-a4-01","gemensamma-fardhandelser-a4-01"]:
        svg=root/f"output/print/svg/{name}.svg"
        pdf=root/f"output/print/pdf/{name}.pdf"
        cairosvg.svg2pdf(url=str(svg),write_to=str(pdf),
                        output_width=210/25.4*72,output_height=297/25.4*72)
        print(f"Skapade {pdf.relative_to(root)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
