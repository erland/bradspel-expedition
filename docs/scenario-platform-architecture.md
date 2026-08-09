# Scenarioarkitektur v1.9

## Syfte

Projektet skiljer nu mellan basuppsättning och scenariopaket.

```text
data/
  base/
    equipment.yaml
    travel-events.yaml

  scenarios/
    station-nordanvind/
      scenario.yaml
      locations.yaml
      objectives.yaml
```

## Basprofil

`data/base-profiles.yaml` anger gemensamma regler och källfiler:

- grundutrustning
- grundläggande färdhändelser
- karaktärer
- vägmarkörer
- tokens

## Scenariopaket

Varje scenario har en egen katalog. `scenario.yaml` deklarerar:

- story och uppdrag
- basprofil
- plats- och målset
- exakta källfiler
- setup
- specialregler
- vinst och förlust

## Laddningsflöde

```text
simulation.yaml
  -> scenarios.yaml
  -> scenarios/<scenario>/scenario.yaml
  -> base-profiles.yaml
  -> scenario- och baskällor
```

Simulatorn och validatorn använder samma referenser. Ett scenario kan därför
inte tyst köras med fel plats-, mål-, utrustnings- eller färdhändelsefiler.

## Nästa steg

Scenario 02 kan läggas i en ny katalog utan att Station Nordanvinds filer ändras.
Scenariounik utrustning och färdhändelser kan då läggas bredvid scenariofilen.
