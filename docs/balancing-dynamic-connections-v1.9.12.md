# Balansunderlag – dynamiska förbindelser v1.9.12

## Status

Hypotesunderlag från simulatorn. Inte ett fysiskt speltest och inte en slutlig balanscertifiering.

## Station Nordanvind

En liten teknisk matris med 40 spel per cell och slumpmässig tie-breaker visade:

| Uthållighet | Ingen progression | V1 efter mål 1, V2 efter mål 2 |
|---:|---:|---:|
| 13 | 72,5 % | 92,5 % |
| 12 | 60,0 % | 65,0 % |
| 11 | 55,0 % | 52,5 % |
| 10 | 50,0 % | 50,0 % |
| 9 | 2,5 % | 27,5 % |

Urvalet är litet och resultaten är inte monotona. Det visar att simulatorn är känslig för seed, agent och tidig måluppfyllelse. Profilen 11/9/8 väljs därför som **första fysisk testprofil**, inte som fastslagen slutbalans.

## Ökenreläet

Den lilla matrisen visade mycket låg vinstgrad även utan dynamiska vägar. V4 efter första reläet gav liten eller ingen förbättring. Därför behålls scenariots befintliga uthållighetsprofil tills regelmotorn och ett fysiskt test har verifierat reläflödet.

## Designbeslut

- Station Nordanvind testar stark progression kombinerad med lägre uthållighet.
- Ökenreläet testar scenariotypisk tvärförbindelse utan samtidig uthållighetssänkning.
- Kontrollspel utan progression ska genomföras.
- Ingen slutlig svårighetsprofil deklareras före fysisk testning.
