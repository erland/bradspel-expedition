#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def load(p): return yaml.safe_load(p.read_text(encoding="utf-8"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    args=ap.parse_args(); root=args.root.resolve()
    reg=load(root/"data/simulation-coverage.yaml")["coverage"]
    supported=set(reg["effect_handlers"]["full"])|set(reg["effect_handlers"]["passive"])
    abilities=set(reg["character_abilities"]["full"])
    completions=set(reg["mission_completion"]["full"])

    used_effects=set()
    equipment_files=[root/"data/base/equipment.yaml"]
    equipment_files += sorted((root/"data/scenarios").glob("*/equipment.yaml"))
    for p in equipment_files:
        data=load(p)
        for card in data.get("equipment",[]):
            for effect in card.get("use",{}).get("effect",[]):
                used_effects.add(effect["action"])
            passive=card.get("passive",{}).get("effect")
            if passive: used_effects.add(passive)

    for p in sorted((root/"data/scenarios").glob("*/locations.yaml")):
        for card in load(p).get("locations",[]):
            for effect in card.get("on_reveal",[]):
                used_effects.add(effect["action"])
    for p in [root/"data/base/travel-events.yaml",*sorted((root/"data/scenarios").glob("*/travel-events.yaml"))]:
        if not p.exists(): continue
        for card in load(p).get("cards",[]):
            for effect in card.get("effect",[]):
                used_effects.add(effect["action"])

    used_abilities={c["ability"]["effect"] for c in load(root/"data/characters.yaml")["characters"]}
    used_completions={
        load(p)["scenario_pack"]["mission"]["completion"]["type"]
        for p in (root/"data/scenarios").glob("*/scenario.yaml")
    }
    missing_effects=sorted(used_effects-supported)
    missing_abilities=sorted(used_abilities-abilities)
    missing_completions=sorted(used_completions-completions)
    report={
      "status":"passed" if not (missing_effects or missing_abilities or missing_completions) else "failed",
      "used_effects":sorted(used_effects),
      "supported_effects":sorted(supported),
      "used_character_abilities":sorted(used_abilities),
      "supported_character_abilities":sorted(abilities),
      "used_completion_types":sorted(used_completions),
      "supported_completion_types":sorted(completions),
      "missing_effects":missing_effects,
      "missing_character_abilities":missing_abilities,
      "missing_completion_types":missing_completions,
      "documented_approximations":reg["documented_approximations"],
    }
    out=root/"output/simulation-coverage-report.json";out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=["# Simulatortäckning","",f"Status: **{report['status']}**","",
        f"- Aktiva korteffekter: {len(used_effects)} / {len(used_effects)-len(missing_effects)} stödda",
        f"- Aktiva karaktärsförmågor: {len(used_abilities)} / {len(used_abilities)-len(missing_abilities)} stödda",
        f"- Uppdragstyper: {len(used_completions)} / {len(used_completions)-len(missing_completions)} stödda",""]
    if missing_effects: md += ["## Saknade korteffekter",""]+[f"- `{x}`" for x in missing_effects]
    if missing_abilities: md += ["","## Saknade förmågor",""]+[f"- `{x}`" for x in missing_abilities]
    if missing_completions: md += ["","## Saknade uppdragstyper",""]+[f"- `{x}`" for x in missing_completions]
    (root/"output/simulation-coverage-report.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    if report["status"]!="passed":
        raise SystemExit(1)
    print(f"Simulatortäckning godkänd: {len(used_effects)} effekter, {len(used_abilities)} förmågor, {len(used_completions)} uppdragstyper.")
    return 0
if __name__=="__main__": raise SystemExit(main())
