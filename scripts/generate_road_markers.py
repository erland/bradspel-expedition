#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml
from jinja2 import Environment,FileSystemLoader,StrictUndefined
def load(p): return yaml.safe_load(p.read_text(encoding="utf-8"))
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
 a=p.parse_args();root=a.root.resolve()
 data=load(root/"data/road-markers.yaml"); lay=load(root/"data/layouts/road-marker.yaml")
 env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,autoescape=False)
 tpl=env.get_template("templates/tokens/single-sided-road-marker.svg.j2")
 colors={"open":"#56785b","blocked":"#934f49","travel_event":"#5d6f86","connection_open":"#3f7f5f","connection_closed":"#7a4a45"}
 out=root/"output/components/road-markers";out.mkdir(parents=True,exist_ok=True)
 for old in out.glob("*.svg"):old.unlink()
 n=0
 for marker in data["markers"]:
  for i in range(1,marker["count"]+1):
   svg=tpl.render(w=lay["layout"]["width_mm"],h=lay["layout"]["height_mm"],
      radius=lay["layout"]["corner_radius_mm"],font=lay["style"]["font_family"],
      symbol_size=lay["style"]["symbol_size"],label_size=lay["style"]["label_size"],
      color=colors[marker["result"]],symbol=marker["symbol"],name=marker["name"])
   path=out/f"{marker['id']}-{i:02d}.svg";path.write_text(svg,encoding="utf-8");n+=1
 print(f"Genererade {n} enkelsidiga vägmarkörer.")
 return 0
if __name__=="__main__":raise SystemExit(main())
