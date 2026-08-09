# Dynamiska förbindelser – nuläge efter [PLAN] Prompt 1

## Syfte

Detta dokument beskriver den första, beteendeneutrala grunden för scenariostyrda förbindelser.

## Genomfört

- Alla kartförbindelser använder nu gemensamma fält:
  - `category`
  - `default_state`
  - `printed_style`
- Befintliga öppna vägar är `fixed/open`.
- Befintliga dolda vägar är `hidden/hidden`.
- Fyra framtida scenariovägar har lagts till:
  - V1: Plats 3–Förrådet
  - V2: Plats 5–Förrådet
  - V3: Plats 6–Förrådet
  - V4: Plats 3–Plats 5
- De nya vägarna är `scenario/closed`.
- Stängda scenariovägar ignoreras av nuvarande simulator och brädgenerator.
- JSON Schema och tvärfilsvalidator har utökats.

## Avgränsning

Den här versionen implementerar inte:

- runtime-state för förbindelser
- scenarioöverskrivningar
- progression events
- öppning av vägar under spel
- visuell rendering av potentiella vägar
- Öppen-markörer
- balansändringar

## Auktoritativa filer

- `data/board.yaml`
- `schemas/board.schema.json`
- `scripts/validate_project.py`

## Nästa steg

[PLAN] Prompt 2 ska införa runtime-state och pathfinding-stöd så att en stängd väg kan öppnas kontrollerat under ett test utan att scenarioprogression ännu krävs.
