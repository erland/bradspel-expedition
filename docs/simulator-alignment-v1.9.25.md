# Simulator alignment v1.9.25

## Syfte

Simulatorn ska använda scenarioeventarkitekturen från v1.9.24 och samtidigt göra eventens balanspåverkan mätbar.

## Resultatmodell

Varje `GameResult` innehåller:

- `scenario_events_resolved`
- `scenario_event_cards`
- `scenario_event_rounds`
- `scenario_event_endurance_delta`
- `connections_closed_by_events`
- `connections_opened_by_events`
- `scenario_event_log`

Den detaljerade loggen innehåller milstolpe, kort-id, trigger, runda, uthållighetsdelta och berörda förbindelser.

## Seed-matchad isolering

`simulation/run_dynamic_connection_experiments.py` stöder:

```bash
python simulation/run_dynamic_connection_experiments.py \
  --scenario-events on off
```

Samma seeds används för båda lägena. Skillnaden mellan cellerna kan därför användas som hypotes om scenarioeventens påverkan.

## Begränsningar

- Resultaten är simuleringshypoteser, inte fysiska speltest.
- Endast fasta omedelbara scenarioevent från arkitekturversion 1 stöds.
- Slumpade miljölekar och severity-urval ingår inte.
- Platsbrickor simuleras inte eftersom de är presentationslager.
- Fysiska markörer simuleras som underliggande vägstatus.
