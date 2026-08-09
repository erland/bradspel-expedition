#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from types import SimpleNamespace
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    a=p.parse_args(); root=a.root.resolve()
    cfg=load(root/"data/reference-cards.yaml")["reference_cards"][0]
    rules=load(root/"data/rules.yaml")
    layout=load(root/"data/layouts/reference-a6.yaml")
    if cfg["source_ruleset"] != rules["ruleset"]["id"]:
        raise ValueError("Referenskortets ruleset matchar inte rules.yaml.")

    actions = [
        ("Flytta", "1: följ väg; vänd dold markör först"),
        ("Utforska", "1: vänd brickan; hitta platskortet"),
        ("Hämta verktyg", "1: vid Förrådet"),
        ("Ta bort Hinder", "1 + verktyg"),
        ("Återhämta", "1: läk 1 i Baslägret"),
        ("Överföra", "1: samma plats"),
        ("Använd utrustning", "följ kortets kostnad"),
        ("Lämna innehåll", "0 handlingar"),
        ("Plocka upp", "1: kräver plats"),
        ("Aktivera målobjekt", "1: på rätt destination"),
    ]
    rounds = [
        ("1. Spelarfas", "Fast ordning. 2 handlingar var."),
        ("2. Underhåll", "Statusar och kontrollera vinst."),
        ("3. Uthållighetsfas", "Förlora 1 uthållighet och kontrollera förlust."),
    ]
    symbols = [
        ("? Plats", "Vänd vid Utforska."),
        ("D1-D4", "Utan markör: öppen."),
        ("✓ Öppen", "Ta bort; flytta."),
        ("X Hinder", "Stanna; använd verktyg."),
        ("! Händelse", "Lös; flytta sedan."),
        ("V1-V4", "Tryckt S: stängd."),
    ]
    inventory = [
        ("Verktyg", "1 plats"),
        ("Utrustning", "antal på kortet"),
        ("Målobjekt", "antal platser står på kortet"),
    ]
    ending = [
        ("VINN", "Uppfyll scenarioarkets vinstvillkor."),
        ("FÖRLORA", "Slut på uthållighet eller alla utslagna."),
    ]

    env=Environment(loader=FileSystemLoader(root),undefined=StrictUndefined,
                    autoescape=False,trim_blocks=True,lstrip_blocks=True)
    tpl=env.get_template(cfg["template"])
    svg=tpl.render(
        card=SimpleNamespace(**cfg),
        layout=SimpleNamespace(**layout["layout"]),
        palette=SimpleNamespace(**layout["palette"]),
        style=SimpleNamespace(**layout["style"]),
        rounds=rounds, actions=actions, symbols=symbols,
        inventory=inventory, ending=ending,
    )
    out=root/"output/components/reference/core-turn-reference-a6.svg"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(svg,encoding="utf-8")
    print(f"Skapade A6-referenskort: {out.relative_to(root)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
