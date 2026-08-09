# Markörer och tokenark

## Syfte

Tokenkomponenten representerar:

- fyra resurstyper
- tre målobjekt
- skada
- blockerade kopplingar

## Källor

- `data/tokens.yaml`
- `data/layouts/token-standard.yaml`
- `data/print-layouts/tokens-a4.yaml`
- `templates/tokens/square-token.svg.j2`

## Produktion

Alla tokens är fyrkantiga för enkel klippning.

Storlekar:

- resurser: 22 mm
- målobjekt: 24 mm
- spårmarkörer: 20 mm
- statusmarkörer: 18 mm

Första versionen är ink-friendly och använder ljusa tonplattor i stället för heltäckande mörka bakgrunder.

## Output

- en SVG per fysisk token
- ett A4-tokenark som SVG
- ett A4-tokenark som PDF

## Designrisk

Skademarkörerna kan vara onödiga om hälsa senare spåras på spelarmattor. De behålls i v0.6 för att stödja första fysiska prototypen.
