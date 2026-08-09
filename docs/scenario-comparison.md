# Scenariojämförelse v1.9 – Del 3

## Syfte

Verktyget kör alla aktiva scenarier med:

- samma gemensamma spelmotor
- samma agenttyper
- samma spelarantal
- samma seedserie
- respektive scenarios egna kortset och vinstvillkor

## Körning

```bash
python scripts/run_scenario_comparison.py   --root .   --runs 30   --seed 139000
```

Ett scenario kan väljas separat:

```bash
python scripts/run_scenario_comparison.py   --root .   --scenario okenrelaet
```

## Output

```text
output/simulation/scenario-comparison/
  summary.json
  scenario-comparison.csv
  runs.csv
  scenario-comparison-report.md
```

`mission_progress` betyder återförda målobjekt i Station Nordanvind och
reparerade relästationer i Ökenreläet.

## Tolkning

Jämförelsen visar om scenariernas svårighet, tempo och strategiska profiler
skiljer sig. Den är ett designverktyg och ersätter inte fysisk speltestning.
