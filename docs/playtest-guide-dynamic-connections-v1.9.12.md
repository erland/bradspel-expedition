# Playtestguide – dynamiska förbindelser v1.9.12

## Syfte

Verifiera om scenariostyrda vägöppningar förbättrar progressionen och minskar repetitiv transport utan att göra scenarierna triviala.

Simuleringarna är hypotesunderlag. Fysisk spelupplevelse, regelklarhet och faktisk speltid måste mätas vid bordet.

## Testprofil A – Station Nordanvind

- 2 karaktärer
- 11 uthållighet
- 0 startverktyg
- första återförda målobjektet öppnar V1
- andra återförda målobjektet öppnar V2

### Mät

- total speltid och antal rundor
- runda då mål 1 och mål 2 levereras
- runda då V1 respektive V2 först används
- antal passager över V1 och V2
- om spelarna prioriterar en viss gren eftersom öppningsordningen är känd
- om sista två rundorna fortfarande känns spända
- om transporten känns mindre repetitiv än utan dynamiska vägar

## Testprofil B – Station Nordanvind kontroll

Spela samma setup med 13 uthållighet och utan progressionsevent.

Syftet är att jämföra den nya progressionen mot tidigare standardläge, inte bara bedöma den isolerat.

## Testprofil C – Ökenreläet

- använd scenariots befintliga uthållighetsprofil
- första reparerade relästationen öppnar V4
- andra reparerade relästationen öppnar V2

### Mät

- om V4 skapar verkliga vägval mellan kartans sidor
- om V2 används efter andra reläet
- om reläordningen påverkas av kända framtida vägöppningar
- om den andra öppningen sker för sent för att vara relevant

## Observationer

Notera särskilt:

1. Om spelarna kommer ihåg att lägga ut Öppen-markören.
2. Om V-id:n går att hitta snabbt på brädet.
3. Om öppningsordningen skapar ett taktiskt val eller en självklar lösning.
4. Om positiva framsteg skapar en för stark snöboll.
5. Om uthållighet 11 för två karaktärer känns pressad men rimlig.

## Beslut efter test

Ändra högst tre saker. Prioritera i denna ordning:

1. regelklarhet
2. trigger-timing
3. vilken väg som öppnas
4. uthållighet
5. grafisk presentation

Ändra inte målantalet samtidigt som uthållighet och vägprogression justeras.
