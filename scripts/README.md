# Scripts

## Aktivt

### `validate_project.py`

Validerar:

- `data/project.yaml`
- `data/game.yaml`
- `data/rules.yaml`
- tvärreferenser mellan filerna

Kör från projektroten:

```bash
python scripts/validate_project.py
```

Strikt läge, där även varningar ger felkod:

```bash
python scripts/validate_project.py --strict
```

Installera beroenden:

```bash
python -m pip install -r requirements.txt
```

## Planerade skript

- `generate_cards.py`
- `generate_board.py`
- `generate_reference_cards.py`
- `generate_tokens.py`
- `build_print_sheets.py`
- `export_pdf.py`
- `build_all.py`
