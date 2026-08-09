# Modellkonsolidering v1.9

## Resultat

Två scenarier har använts för att skilja baskomponenter från scenarioutökningar.

## Basuppsättning

Följande är generella och ligger kvar i basprofilen:

- spelbräde och fasta platser
- karaktärer
- vägmarkörerna Öppen, Hinder och Händelse
- verktyg, skada, runda, okänd plats och uthållighet
- Medicinväska
- Kartscanner
- Extra förnödenheter
- Klätterrep
- Verktygsbälte
- Stor ryggsäck
- grundläggande färdhändelser

## Scenarioutökningar

Följande deklareras per expedition:

- story och uppdragsbriefing
- platskort
- målobjekt eller reservmoduler
- uppdragets slutförandemodell
- scenariounik utrustning
- scenariounika färdhändelser
- scenariomarkörer och scenariohandlingar

## Generell uppdragsmodell

Scenarier använder `mission.completion`.

### Leverera föremål

```yaml
completion:
  type: deliver_items
  required: 3
  item_source: objectives
  destination_location: base_camp
```

### Placera föremål vid märkta platser

```yaml
completion:
  type: place_items_at_tagged_locations
  required: 3
  item_source: objectives
  target_location_tag: relay
  action_id: install_module
  action_cost: 1
  consume_item: true
  place_token: status_repaired
```

Simulatorn och validatorn tolkar samma modell.

## Kortlekskomposition

Varje scenario deklarerar för varje komponenttyp:

- `base_only`
- `scenario_only`
- `base_plus_scenario`

Det gör det tydligt vilka kort som alltid används och vilka som blandas in eller ersätter basmaterial.

## Designregel för framtida scenarier

En ny expedition ska i första hand kunna läggas till genom en ny katalog under
`data/scenarios/`. Motorn ska bara ändras när en genuint ny generell
uppdragsmodell införs, inte för ett specifikt scenarionamn.
