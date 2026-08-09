# [PLAN] Prompt 2 – runtime-state och pathfinding

## Genomfört

- Alla förbindelser får ett aktuellt runtime-tillstånd från `default_state`.
- Scenarioets befintliga `hidden_roads` skriver över motsvarande tillstånd till `hidden`.
- Adjacency innehåller hela den fysiska geometrin.
- Pathfinding och slumpmässig rörelse använder bara traverserbara vägar.
- `closed` och `sealed` är inte traverserbara.
- `open`, `hidden` och reparerbart `blocked` kan hanteras av befintlig rörelselogik.
- V1–V4 kan öppnas manuellt via motor-API men inget scenario gör detta ännu.

## API

- `get_connection_state(connection_id)`
- `set_connection_state(connection_id, state)`
- `is_connection_traversable(connection_id)`
- `open_connection(connection_id)`
- `seal_connection(connection_id)`

## Bakåtkompatibilitet

`road_state` är ett alias till `connection_states`. Befintlig kod för dolda och
blockerade vägar fortsätter därför att fungera under migrationen.

## Tester

`tests/test_dynamic_connections_runtime.py` verifierar:

1. V1–V4 börjar stängda.
2. Stängd V1 används inte av pathfinding.
3. Manuellt öppnad V1 används direkt.
4. Öppning är idempotent.
5. Förseglad väg kan inte öppnas.
6. Ogiltig tillståndsövergång avvisas.

## Avgränsning

Nästa steg ansvarar för datadrivna scenarioevents och automatisk öppning.
