#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, re, textwrap
from pathlib import Path
import cairosvg, yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pypdf import PdfReader, PdfWriter

def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def inner_svg(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^.*?<svg[^>]*>", "", text, count=1, flags=re.S)
    return re.sub(r"</svg>\s*$", "", text, count=1, flags=re.S)

def wrap_name(name: str, width: int = 15) -> list[str]:
    return [html.escape(x) for x in textwrap.wrap(name, width=width, break_long_words=False, break_on_hyphens=False)[:2]]

def cut_marks(x: float, y: float, w: float, h: float) -> list[str]:
    s = 'stroke="#333" stroke-width="0.2"'
    return [
        f'<path d="M{x-2.5},{y}H{x} M{x},{y-2.5}V{y}" {s}/>',
        f'<path d="M{x+w},{y}H{x+w+2.5} M{x+w},{y-2.5}V{y}" {s}/>',
        f'<path d="M{x-2.5},{y+h}H{x} M{x},{y+h}V{y+h+2.5}" {s}/>',
        f'<path d="M{x+w},{y+h}H{x+w+2.5} M{x+w},{y+h}V{y+h+2.5}" {s}/>',
    ]

def hidden_svg(width, height, radius, fill, stroke, font, scenario_name):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">
<rect x="0.25" y="0.25" width="{width-0.5}" height="{height-0.5}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>
<rect x="1.4" y="1.4" width="{width-2.8}" height="{height-2.8}" rx="{radius-0.3}" fill="none" stroke="{stroke}" stroke-width="0.25" stroke-dasharray="1.5,1"/>
<text x="{width/2}" y="{height/2+1.8}" text-anchor="middle" font-family="{font}" font-size="9" font-weight="700" fill="{stroke}">?</text>
<text x="{width/2}" y="{height-2.2}" text-anchor="middle" font-family="{font}" font-size="2" fill="{stroke}">{html.escape(scenario_name)}</text>
</svg>'''

def sheet_svg(rows, title, subtitle, layout):
    w, h = layout["width_mm"], layout["height_mm"]
    gap, start_x, row_ys = layout["gap_mm"], layout["margin_x_mm"], layout["row_y_mm"]
    sheet=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">',
           '<rect width="210" height="297" fill="#fff"/>',
           f'<text x="105" y="13" text-anchor="middle" font-family="DejaVu Sans" font-size="5" font-weight="700">{title}</text>',
           f'<text x="105" y="19" text-anchor="middle" font-family="DejaVu Sans" font-size="2.6">{subtitle}</text>']
    for row_index,(scenario_name,files) in enumerate(rows):
        y=row_ys[row_index]
        sheet.append(f'<text x="{start_x}" y="{y-5}" font-family="DejaVu Sans" font-size="3.1" font-weight="700">{html.escape(scenario_name)}</text>')
        for i,file in enumerate(files):
            x=start_x+i*(w+gap)
            sheet.append(f'<g transform="translate({x},{y})">{inner_svg(file)}</g>')
            sheet.extend(cut_marks(x,y,w,h))
    sheet.append('</svg>')
    return "\n".join(sheet)

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args(); root=args.root.resolve()
    config=load(root/"data/layouts/location-tile.yaml")
    layout,style,palette=config["layout"],config["style"],config["palette"]
    env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,autoescape=False,trim_blocks=True,lstrip_blocks=True)
    template=env.get_template(layout["template"])
    sources=[
      ("station-nordanvind","Station Nordanvind","station",root/"data/scenarios/station-nordanvind/locations.yaml"),
      ("okenrelaet","Ökenreläet","desert",root/"data/scenarios/okenrelaet/locations.yaml")]
    out_dir=root/"output/components/location-tiles"; out_dir.mkdir(parents=True,exist_ok=True)
    for old in out_dir.glob("*.svg"): old.unlink()
    front_rows=[]; back_rows=[]
    for scenario_id,scenario_name,theme,source in sources:
        front_files=[]; back_files=[]
        for card in load(source)["locations"]:
            name_lines=wrap_name(card["name"])
            front=template.render(width=layout["width_mm"],height=layout["height_mm"],radius=layout["corner_radius_mm"],
              fill=palette[theme],stroke=palette[f"{theme}_stroke"],ink=palette["ink"],muted=palette["muted"],
              font=style["font_family"],id_size=style["id_font_size"],name_size=style["name_font_size"],
              scenario_size=style["scenario_font_size"],display_id=card["display_id"],name_lines=name_lines,
              name_start=12.2 if len(name_lines)==2 else 14.3,scenario_name=scenario_name)
            front_path=out_dir/f"{scenario_id}-{card['display_id'].lower()}-{card['id']}-front.svg"
            back_path=out_dir/f"{scenario_id}-{card['display_id'].lower()}-{card['id']}-back.svg"
            front_path.write_text(front,encoding="utf-8")
            back_path.write_text(hidden_svg(layout["width_mm"],layout["height_mm"],layout["corner_radius_mm"],
                palette[theme],palette[f"{theme}_stroke"],style["font_family"],scenario_name),encoding="utf-8")
            front_files.append(front_path); back_files.append(back_path)
        front_rows.append((scenario_name,front_files)); back_rows.append((scenario_name,list(reversed(back_files))))
    svg_dir=root/"output/print/svg"; pdf_dir=root/"output/print/pdf"
    svg_dir.mkdir(parents=True,exist_ok=True); pdf_dir.mkdir(parents=True,exist_ok=True)
    front_svg=svg_dir/"location-tiles-front-a4-01.svg"; back_svg=svg_dir/"location-tiles-back-a4-01.svg"
    front_svg.write_text(sheet_svg(front_rows,"PLATSBRICKOR – FRAMSIDA","Utforskad sida: namn och id uppåt",layout),encoding="utf-8")
    back_svg.write_text(sheet_svg(back_rows,"PLATSBRICKOR – BAKSIDA","Dold sida: skriv ut dubbelsidigt, vänd på kortsidan",layout),encoding="utf-8")
    front_pdf=pdf_dir/"_location-tiles-front.pdf"; back_pdf=pdf_dir/"_location-tiles-back.pdf"
    cairosvg.svg2pdf(url=str(front_svg),write_to=str(front_pdf),output_width=210/25.4*72,output_height=297/25.4*72)
    cairosvg.svg2pdf(url=str(back_svg),write_to=str(back_pdf),output_width=210/25.4*72,output_height=297/25.4*72)
    writer=PdfWriter()
    for f in [front_pdf,back_pdf]:
        for page in PdfReader(str(f)).pages: writer.add_page(page)
    with open(pdf_dir/"location-tiles-a4-01.pdf","wb") as out: writer.write(out)
    front_pdf.unlink(); back_pdf.unlink()
    print("Genererade dubbelsidiga platsbrickor: 12 framsidor, 12 baksidor och 2-sidig PDF.")
    return 0
if __name__=="__main__": raise SystemExit(main())
