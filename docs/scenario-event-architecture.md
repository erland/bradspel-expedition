# Scenariohändelsearkitektur v1

Status: Låst för Expedition v1.9.24.

## Syfte

Scenariohändelse ska skapa omedelbara, tydliga förändringar utan fler-runders minnesregler. Miljön ger kortens tema; scenariot bestämmer vilka fasta kort som triggas vid vilka milstolpar.

## Låsta triggers

- `objective_found`
- `objective_completed`
- `objective_activated`
- `location_explored`
- `all_objectives_completed`

Alla milstolpar är engångstriggers (`once: true`).

## Låsta eventeffekter i version 1

- `modify_endurance`
- `open_connection`
- `close_connection`

Nya effekter införs endast när ett konkret scenario behöver dem och efter schema-, motor-, simulator- och regeluppdatering.

## Upplösningsordning

1. Slutför aktuell handling.
2. Uppdatera spelstatus.
3. Lös progressionseffekter.
4. Kontrollera scenariomilstolpar.
5. Lös scenariohändelseet omedelbart och kassera kortet.
6. Kontrollera vinst och förlust.

## Miljölekar

Varje miljölek har:

- stabilt id
- `format_version: 1`
- miljö
- kort med unikt id
- allvarlighetsgrad
- effektfamilj
- interna taggar
- spelartext
- strukturerade effekter

Iteration 1 använder endast fasta kort (`mode: fixed`). Slumpad och dold dragning är avsiktligt uppskjuten.

## Kortlayout

Spelarsidan visar:

1. miljö
2. symbol
3. kortnamn
4. omedelbar effekttext
5. kort-id

Allvarlighetsgrad och taggar är designdata och behöver inte visas.

## Designregler

- Kortet ska alltid kunna lösas när dess milstolpe inträffar.
- Kortet ska inte kräva att ett målobjekt, hinder eller viss utrustning redan är tillgängligt, om detta inte garanteras av triggern.
- Ingen effekt får gälla “nästa gång” eller “under kommande rundor” i arkitekturversion 1.
- Bestående kartförändringar måste visas med fysisk markör.
- Korttext och strukturerad effekt ska beskriva samma resultat.

## Platsbrickor

Platsbrickan är ett presentationslager. Det utforskade platskortets id används för att välja rätt bricka. Spelstatus ägs fortsatt av platskort/YAML.
