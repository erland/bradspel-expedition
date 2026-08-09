# Gemensamt buildsystem

## Syfte

`build_all.py` är projektets gemensamma byggingång.

Det läser `data/project.yaml` och utför endast aktiverade byggmål och steg.

## Grundkommando

```bash
python scripts/build_all.py
```

## Alternativ

Tvinga rensning:

```bash
python scripts/build_all.py --clean
```

Hoppa över rensning:

```bash
python scripts/build_all.py --no-clean
```

Strikt validering:

```bash
python scripts/build_all.py --strict
```

Bygg ett eller flera specifika mål:

```bash
python scripts/build_all.py --target validate --target cards
```

## Byggordning

1. validera projektet
2. generera kort-SVG
3. skapa kortark och PDF
4. generera bräd-SVG och PDF
5. generera referenskort, A4-ark och PDF
6. generera tokens, tokenark och PDF
7. verifiera förväntade outputfiler
8. skapa build-manifest
9. skapa mänskligt läsbar buildrapport
10. spara samlad buildlogg

## Manifeststyrning

Varje steg i `data/project.yaml` anger:

- stabilt steg-id
- byggmål
- Python-skript
- om steget är aktiverat
- förväntade outputfiler
- eventuella output-globbar
- förväntat antal globträffar

Det gör att `build_all.py` inte behöver känna till en specifik komponenttyp.

## Rensning

Endast sökvägar i `build.clean_paths` får rensas.

Skriptet kontrollerar att varje rensningssökväg ligger under projektroten.

Källfiler i `data/`, `templates/`, `assets/`, `docs/`, `schemas/` och `scripts/` rensas aldrig.

## Build-manifest

`output/build-manifest.json` innehåller:

- projektversion
- start- och sluttid
- buildstatus
- Python- och plattformsinformation
- valda byggmål
- rensade sökvägar
- SHA-256 för källfiler
- resultat och tid för varje byggsteg
- verifierade outputfiler
- SHA-256 för output
- varningar och fel

## Buildrapport och logg

- `output/build-report.md` är en kort mänskligt läsbar sammanfattning.
- `output/build-log.txt` innehåller stdout och stderr från varje steg.

## Felhantering

Builden avbryts vid första misslyckade steg.

Manifest, rapport och logg skrivs även när builden misslyckas, så att felet går att felsöka.
