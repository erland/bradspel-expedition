# Spelbräde - nodkarta

## Syfte

Brädet representerar expeditionsområdet som en graf av platser och kopplingar.

Spelaren flyttar mellan anslutna platser. Platser kan vara säkra, farliga, målrelaterade eller basläger.

## Datamodell

`data/board.yaml` beskriver:

- brädets mått
- platstyper
- platser och koordinater
- kopplingar
- blockerade vägar
- resurskopplingar
- målplatser
- uthållighet- och rundspår
- legendens position

## Första karta

Kartan har åtta platser:

1. Basläger
2. Förrådet
3. Gamla bron
4. Signaltornet
5. Fältsjukhuset
6. Rasgruvan
7. Den gamla platsen
8. Väderstationen

Tre platser kan innehålla målobjekt.

En koppling är blockerad i prototypen för att testa visuell och regelmässig hantering av hinder.

## Designhypoteser

- Åtta noder ger tillräckligt vägval utan att A4-brädet blir trångt.
- Två huvudgrenar minskar risken att alla optimala vägar blir identiska.
- Tre målplatser stödjer nuvarande vinstvillkor.
- Baslägret längst ned gör återresan visuellt tydlig.
- Uthållighetspåret högst upp fungerar som central tidspress.
- Rundspåret längst ned hjälper speltest och framtida simulering.

## Kända frågor

- Ska okända platser döljas med brickor eller kort?
- Hur låses en blockerad koppling upp?
- Ska resursen på en plats kunna samlas flera gånger?
- Ska målobjekten placeras slumpmässigt?
- Är återresan till baslägret intressant eller bara transport?


## Transitnoder

T1–T4 är transitnoder på öppna vägar. Att flytta mellan en plats och en transitnod kostar en förflyttningshandling. Transitnoder kan beträdas och innehålla karaktärer eller framtida entiteter, men de kan inte utforskas och får inga platskort. En blockerad transitnod kan inte beträdas eller passeras.
