# Simulatorarkitektur v1.4

## Struktur

```text
engine/
  game_engine.py

agents/
  base.py
  standard.py

simulation/
  run_agent_comparison.py
```

## Princip

Alla agenter använder samma spelmotor och samma YAML-data. Skillnaden mellan simuleringar ska ligga i beslutsprofilen, inte i regelimplementationen.

## Nuvarande agenter

- Slumpagent
- Utforskaragent
- Riskagent
- Försiktig agent
- Logistikagent

## Viktig begränsning

`GameEngine` kapslar den befintliga regelimplementationen i `scripts/simulate_game.py`. Arkitekturen är därför separerad, men regelmotorn är ännu inte fullständigt uppdelad i enskilda lagliga handlingar och state-transaktioner.

Detta är ett praktiskt mellansteg: vi kan jämföra agenter mot samma motor nu, utan att skriva om hela simulatorn på en gång.


## Setupkorrigering v1.8.1

`GameEngine` skickar nu karaktärsantalet till regelmotorn innan setup skapas.
Därmed används rätt uthållighet och rätt startverktyg för 2–4 karaktärer.

Motorn validerar också att scenariopaketets plats- och målset motsvarar de
laddade datakällorna. Ett scenario kan därför inte tyst simuleras med fel kortset.
