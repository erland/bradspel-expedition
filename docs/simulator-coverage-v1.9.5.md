# Simulator coverage v1.9.5

## Implementerat

- Kartscanner: dolda vägar kan granskas och kunskapen påverkar ruttval.
- Vattenreserv: reducerar nästa uthållighetsförlust från en färdhändelse med 1.
- Diagnosverktyg: reducerar nästa installationskostnad.
- Spejaren: granskar en angränsande dold väg en gång per runda.
- Kuriren: överför mål, verktyg och utrustning utan handling en gång per aktivering.
- Teknikern: använder första rationella engångsutrustningen per runda utan handling.
- Klättraren, Ingenjören, Läkaren, Bäraren och Veteranen är fortsatt modellerade.
- Utrustningens `cost_actions` och scenariots `action_cost` styr handlingsekonomin.
- Karaktärer dras enligt 4/5/6-kortsregeln och väljs därefter av agenten.
- Överföring stödjer målobjekt, verktyg och utrustning.

## Automatisk täckningskontroll

`data/simulation-coverage.yaml` är simulatorns stödkontrakt.
`scripts/check_simulation_coverage.py` söker igenom aktiva kort, förmågor och
uppdragstyper. Builden misslyckas om något aktivt id saknar deklarerat stöd.

## Avsiktliga approximationer

- Agenter använder kort rationellt i stället för att simulera mänsklig tvekan.
- Kartkunskap är perfekt ihågkommen.
- Kuriren flyttar så mycket som ryms när överföringen bedöms nyttig.
- Teknikern använder sin gratiseffekt på första rationella engångsutrustningen.

Dessa är hypoteser och ska verifieras genom fysisk speltestning.
