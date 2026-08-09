# Byggpipeline - kort

## Kedja

```text
data/cards.yaml
+ data/layouts/card-standard.yaml
+ templates/cards/standard.svg.j2
+ assets/icons/*.svg
→ scripts/generate_cards.py
→ output/components/cards/*.svg
→ scripts/build_card_sheets.py
→ output/print/svg/cards-a4-01.svg
→ scripts/export_pdf.py
→ output/print/pdf/cards-a4-01.pdf
```

## Bygg allt

```bash
python -m pip install -r requirements.txt
python scripts/build_all.py
```

## Ansvar

- `cards.yaml` beskriver kortens speldata och visningstext.
- `card-standard.yaml` beskriver mått, färger och textpositioner.
- SVG-templaten beskriver lager och fast grafisk struktur.
- `cards-a4.yaml` beskriver placering på A4.
- filer i `output/` är genererade och ska inte handredigeras.

## Begränsningar i v0.3

- textpassning använder en enkel teckenbaserad uppskattning
- endast ett kortformat
- endast ett A4-ark
- inga kortbaksidor
- inga PNG-bakgrunder
- inga automatiska flersidesark


## Kedja - spelbräde

```text
data/board.yaml
+ data/layouts/board-standard.yaml
+ templates/boards/node-map.svg.j2
→ scripts/generate_board.py
→ output/components/boards/expedition-board-01.svg
→ scripts/export_board_pdf.py
→ output/print/pdf/board-a4-01.pdf
```

Brädet använder samma princip som korten: gameplay-data, presentationsdata och output hålls separerade.


## Kedja - A6-referenskort

```text
data/rules.yaml
+ data/game.yaml
+ data/board.yaml
+ data/reference-cards.yaml
+ data/layouts/reference-a6.yaml
+ templates/reference/a6-reference.svg.j2
→ scripts/generate_reference_cards.py
→ output/components/reference/core-turn-reference-a6.svg
→ scripts/build_reference_sheets.py
→ output/print/svg/reference-a4-4up.svg
→ scripts/export_reference_pdf.py
→ output/print/pdf/reference-a6.pdf
→ output/print/pdf/reference-a4-4up.pdf
```


## Kedja - markörer

```text
data/tokens.yaml
+ data/layouts/token-standard.yaml
+ templates/tokens/square-token.svg.j2
→ scripts/generate_tokens.py
→ output/components/tokens/*.svg
→ scripts/build_token_sheet.py
→ output/print/svg/tokens-a4-01.svg
→ scripts/export_token_pdf.py
→ output/print/pdf/tokens-a4-01.pdf
```
