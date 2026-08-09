# A6-referenskort

## Syfte

Referenskortet ska göra det möjligt att spela utan att slå upp grundflödet i regelboken.

Det innehåller:

- rundans tre faser
- sex grundhandlingar
- centrala symboler
- vinst- och förlustvillkor

## Källor

Spelvärden hämtas från:

- `data/rules.yaml`
- `data/game.yaml`
- `data/board.yaml`

Presentation styrs av:

- `data/reference-cards.yaml`
- `data/layouts/reference-a6.yaml`
- `templates/reference/a6-reference.svg.j2`

## Output

- en A6-SVG
- en A6-PDF
- ett A4-ark med fyra identiska A6-kort
- A4-PDF med skärmärken

## Designprincip

Referenskortet får inte bli en separat regelkälla. Om en handling, fas eller slutregel ändras ska kortet byggas om från regeldata.

## Dynamiska förbindelser

Referenskortet visar att V1-V4 är stängda streckade vägar tills en Öppen väg-markör placeras enligt scenariot.


## Vägstatus

- D1-D4 visar Öppen väg. Lägg dold markör endast där scenarioarket anger det.
- V1-V4 visar Stängd väg. Lägg Öppen väg-markör när scenariot öppnar vägen.
- Stängd väg-markörer är förberedda för framtida scenarier.
