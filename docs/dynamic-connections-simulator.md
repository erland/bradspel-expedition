# Simulatorstöd för dynamiska förbindelser

Version: 1.9.10

## Syfte

Detta stöd gör det möjligt att jämföra scenariostyrda förbindelser med samma seedserie och samma agentprofiler.

Resultaten är designhypoteser och ersätter inte fysiska speltester.

## Experimentrunner

```bash
python simulation/run_dynamic_connection_experiments.py --runs 100
```

Viktiga parametrar:

```text
--scenario station_nordanvind
--endurance 13 12 11 10 9
--variants none v1_after_1 v1_then_v2 choose_after_1
--tie-breakers left right random
--seed 49000
```

## Standardvarianter

- `none`
- `v1_after_1`
- `v2_after_1`
- `v1_then_v2`
- `choose_after_1`
- `choose_after_1_and_2`
- `v4_after_relay_1`

## Mätvärden

- vinstgrad
- rundor
- rörelsehandlingar
- slutlig uthållighet
- antal progressionsevent
- öppningsrunda per väg
- passager per dynamisk väg
- andel spel som använder en dynamisk väg

## Tie-breakers

`left` använder stigande nod-id som deterministisk sekundär prioritet.

`right` använder omvänd ordning.

`random` skapar en seedad slumpordning och är reproducerbar.

## Begränsningar

Agentens val är en approximation. Den använder offentlig kartstatus, karaktärernas positioner, outforskade platser, kända mål på marken och uppdragsmål. Den modellerar inte mänsklig diskussion eller berättelsepreferenser.

Den inkluderade rökkörningen använder endast två körningar per agent och cell. Den verifierar pipeline och rapportformat, men ska inte användas för balansbeslut.
