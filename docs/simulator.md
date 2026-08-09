# Designsimulator

## Syfte

Simulatorn testar spelmodellens matematiska och logistiska struktur. Den jämför strategier, uppskattar lösbarhet och söker efter återkommande flaskhalsar.

Den simulerar inte spelglädje, läsbarhet, mänsklig kommunikation, alfa-spelare eller fysisk komponentfriktion.

## Kommando

```bash
python scripts/simulate_game.py
```

Färre körningar:

```bash
python scripts/simulate_game.py --runs 100
```

En strategi:

```bash
python scripts/simulate_game.py --strategy aggressive
```

Reproducerbar körning:

```bash
python scripts/simulate_game.py --seed 12000
```

## Datakällor

Simulatorn läser bland annat:

- `board.yaml`
- `scenarios.yaml`
- `locations.yaml`
- `road-markers.yaml`
- `travel-events.yaml`
- `characters.yaml`
- `equipment.yaml`
- `objectives.yaml`
- `simulation.yaml`

Regeltolkning, grafalgoritmer och agentbeslut implementeras i Python.

## Strategier

- Slumpmässig baslinje
- Närmaste okända plats
- Försiktig expedition
- Aggressiv måljakt
- Logistisk expedition

## Output

- `summary.json`
- `strategy-comparison.csv`
- `runs.csv`
- `simulation-report.md`

## Viktiga approximationer

- två karaktärer per omgång
- perfekt regelkunskap och öppen information
- fasta strategiska prioriteringar
- mål lämnas automatiskt i Baslägret
- vissa karaktärsförmågor approximeras konservativt
- beslut och kommunikation tar ingen verklig tid

Resultaten ska behandlas som hypoteser. Relativa skillnader mellan strategier är mer användbara än en enskild exakt vinstprocent.


## Scenariostyrning v1.8.1

Simulatorn väljer scenario via `data/simulation.yaml` och följer därefter:

1. scenarioindexet i `data/scenarios.yaml`
2. scenariopaketets YAML
3. scenariots basprofil
4. deklarerade plats- och målset
5. setupvärden för valt karaktärsantal

Varje körning loggar scenario-id, basprofil, platsset, målset, antal karaktärer,
startuthållighet och startverktyg.

Tvåkaraktärslägets startverktyg läggs deterministiskt i den första
karaktärens ryggsäck i aktiveringsordningen. Detta är en reproducerbar
simulatorrepresentation av regeln att gruppen får placera verktyget i valfri
ryggsäck.
