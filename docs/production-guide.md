# Produktionsguide

## Kortark

- papper: A4, stående
- kortstorlek: 63 × 88 mm
- layout: 3 × 3 möjliga kortplatser
- aktuell version använder 3 kort
- skärmärken ingår
- säker sidmarginal: 10 mm
- enkelsidig utskrift
- skala: 100 %, faktisk storlek
- avaktivera skrivarens "anpassa till sida"

## Rekommenderat prototypsätt

1. Skriv ut PDF-filen på vanligt papper.
2. Kontrollmät ett kort till 63 × 88 mm.
3. Klipp längs skärmärkena.
4. Lägg kortet framför ett vanligt spelkort i en sleeve.
5. Testa läsbarhet vid bordet innan fler kort skapas.

## Källor och output

Källor:

- `data/cards.yaml`
- `data/layouts/card-standard.yaml`
- `data/print-layouts/cards-a4.yaml`
- `templates/cards/standard.svg.j2`
- `assets/icons/*.svg`

Genererad output:

- `output/components/cards/*.svg`
- `output/print/svg/cards-a4-01.svg`
- `output/print/pdf/cards-a4-01.pdf`


## Spelbräde

- format: A4, stående
- utskrift: enkelsidig
- skala: 100 %
- rekommenderat papper: 160-250 g/m² eller vanligt papper monterat på kartong
- laminering är valfri
- uthållighet- och rundspår kan markeras med kub, mynt eller pappersmarkör

Kontrollera särskilt att text i noderna är läsbar från normal sittposition.


## A6-referenskort

Två utskriftsalternativ finns:

- `reference-a6.pdf` för enskild A6-utskrift
- `reference-a4-4up.pdf` med fyra A6-kort på ett A4

Skriv ut i 100 % skala. A4-versionen innehåller skärmärken och passar när varje spelare ska få ett eget kort.


## Tokenark

- format: A4, stående
- utskrift: enkelsidig
- skala: 100 %
- skärmärken ingår
- montera gärna arket på tunn kartong innan utskärning
- fyrkantiga tokens kan klippas med sax eller pappersskärare
- laminera hela arket före utskärning om extra hållbarhet behövs

Skriv först ut en testsida och kontrollmät en resursmarkör till 22 mm.
