#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil
from pathlib import Path
from pypdf import PdfReader,PdfWriter
import yaml

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    root=parser.parse_args().root.resolve()
    version=yaml.safe_load((root/"data/project.yaml").read_text(encoding="utf-8"))["project"]["project_version"]
    package_dir=root/"output/print-package"
    if package_dir.exists(): shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    files=[
      "output/print/pdf/rulebook-playtest-v1.9.pdf",
      "output/print/pdf/assembly-guide-v1.9.pdf",
      "output/print/pdf/station-nordanvind-scenarioark-a4.pdf",
      "output/print/pdf/station-nordanvind-platskort-a4-01.pdf",
      "output/print/pdf/station-nordanvind-malobjekt-a4-01.pdf",
      "output/print/pdf/station-nordanvind-scenariohandelser-a4-01.pdf",
      "output/print/pdf/okenrelaet-scenarioark-a4.pdf",
      "output/print/pdf/okenrelaet-platskort-och-okenmiljo-fardhandelser-a4-01.pdf",
      "output/print/pdf/okenrelaet-malobjekt-och-okenmiljo-utrustning-a4-01.pdf",
      "output/print/pdf/okenrelaet-scenariohandelser-a4-01.pdf",
      "output/print/pdf/spelplan-2xa4.pdf",
      "output/print/pdf/spelplan-a4-kompakt.pdf",
      "output/print/pdf/location-tiles-a4-01.pdf",
      "output/print/pdf/gemensamma-fardhandelser-a4-01.pdf",
      "output/print/pdf/gemensamma-vagbrickor-a4-01.pdf",
      "output/print/pdf/gemensamma-transitbrickor-a4-01.pdf",
      "output/print/pdf/gemensamma-karaktarskort-a4-01.pdf",
      "output/print/pdf/gemensam-utrustning-a4-01.pdf",
      "output/print/pdf/tokens-a4-01.pdf",
      "output/print/pdf/reference-a4-4up.pdf",
      "output/print/pdf/playtest-guide-v1.9.pdf",
      "output/print/pdf/playtest-forms-v1.9.pdf",
    ]
    writer=PdfWriter(); manifest_files=[]
    for relative in files:
        source=root/relative
        if not source.exists(): raise FileNotFoundError(f"Printpaket saknar: {relative}")
        destination=package_dir/source.name
        shutil.copy2(source,destination)
        reader=PdfReader(str(source))
        for page in reader.pages: writer.add_page(page)
        manifest_files.append({"source":relative,"package_file":str(destination.relative_to(root)),"pages":len(reader.pages)})
    combined=package_dir/f"expedition-v{version}-komplett-printpaket.pdf"
    with combined.open("wb") as handle: writer.write(handle)
    manifest={"version":version,"status":"ready_for_physical_print","physical_test_completed":False,
              "files":manifest_files,"combined_pdf":str(combined.relative_to(root)),
              "scope_levels":["core","environment","scenario"],
              "notes":["Skriv ut i 100 procent eller faktisk storlek.","Fysisk montering och bordstest återstår."]}
    (package_dir/"PRINT_PACKAGE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Skapade komplett printpaket: {combined.relative_to(root)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
