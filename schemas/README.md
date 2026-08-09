# Schemas

Projektet använder JSON Schema draft 2020-12.

## Aktiva schemas

- `project.schema.json`
- `game.schema.json`
- `rules.schema.json`

Schemas kontrollerar struktur, obligatoriska fält, grundtyper, id-format och flera enum-värden.

`validate_project.py` kompletterar schemas med tvärfilsvalidering, exempelvis:

- projekt-id matchar spel-id
- resurser och spår som refereras finns
- antal handlingar matchar mellan `game.yaml` och `rules.yaml`
- antal målobjekt matchar mellan filer
- intervall och startvärden är rimliga
- aktiverade komponentkällor finns

Schemas för kort, bräde, referenskort och tokens införs när respektive datamodell skapas.
