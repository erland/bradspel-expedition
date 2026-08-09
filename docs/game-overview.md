# Spelöversikt – Expedition

## Premiss

En expedition har förlorat kontakten med omvärlden efter att ha nått en okänd och instabil plats. Gruppen måste utforska området, hitta tre nödvändiga målobjekt och återvända till baslägret innan förhållandena blir för farliga.

Temat hålls medvetet generellt i version 0.1. Det kan senare bli exempelvis:

- en främmande planet
- en glömd ö
- en frusen forskningszon
- en översvämmad ruinstad
- en förtrollad skog

## Vad spelarna gör

Spelarna styr tillsammans expeditionens karaktärer.

Varje karaktär får normalt två handlingar under spelarnas fas.

Vanliga handlingar:

- flytta till en angränsande plats
- utforska en okänd plats
- samla en resurs
- vila och återhämta sig
- hjälpa en karaktär på samma plats
- använda ett föremål

## Rundans struktur

### 1. Uthållighetsfas

- dra och lös en händelse
- justera uthållighetspåret om händelsen kräver det
- lös eventuella scenarioeffekter

### 2. Spelarfas

Varje aktiv karaktär får två handlingar.

Spelarna bestämmer i vilken ordning karaktärerna agerar.

### 3. Underhåll

- lös statusar
- kontrollera utslagna karaktärer
- kontrollera vinst och förlust
- öka rundräknaren

## Spelbräde

Första versionen använder en nodkarta.

Kartan bör innehålla:

- ett basläger
- 6–8 platser
- kopplingar mellan platser
- några okända eller blockerade vägar
- ett uthållighetspår
- eventuellt ett rundspår

Nodkartan väljs eftersom den är enkel att:

- beskriva i YAML
- generera i SVG
- skriva ut på A4
- simulera som en graf
- ändra mellan scenarier

## Resurser

### Proviant

Används för uthållighet, vila och vissa resor.

### Verktyg

Används för att hantera hinder och reparera utrustning.

### Medicin

Används för att återhämta skada.

### Kunskap

Används för att tolka ledtrådar och säkra målobjekt.

## Uthållighetspår

Uthållighetspåret går i första versionen från 0 till 10.

Uthållighet kan öka genom:

- händelser
- misslyckade utmaningar
- förseningar
- vissa platser
- brist på resurser

När uthålligheten når 10 förlorar gruppen.

## Målobjekt

Gruppen behöver hitta tre målobjekt.

I första prototypen kan de representeras av tre likadana målmarkörer.

Senare kan de få olika funktioner eller kräva olika resurser.

## Skada och utslagning

Första hypotes:

- varje karaktär har 3 hälsa
- vid 0 hälsa blir karaktären utslagen
- en utslagen karaktär kan inte agera
- andra karaktärer kan återuppliva eller stabilisera med medicin
- gruppen förlorar om alla karaktärer är utslagna

## Solo

Rekommenderat solo:

- styr två karaktärer
- använd samma regler som för två spelare
- håll all information öppen

Möjliga senare solojusteringar:

- en fri hjälp-handling per runda
- lägre startuthållighet
- extra startresurs
- en särskild solokaraktär

Dessa införs inte innan grundspelet har testats.

## Första komponentlista

- 1 A4-spelbräde
- 12 utforskningskort
- 6 händelsekort
- 6 föremåls- eller hjälpkort
- 3 målmarkörer
- 8 resursmarkörer
- 8 uthållighet- eller statusmarkörer
- 2–4 spelarpjäser
- 1 A6-referenskort
- regler

## Exempel på en runda

1. En stormhändelse höjer uthålligheten från 3 till 4.
2. Karaktär A flyttar till en okänd plats.
3. Karaktär A utforskar platsen och hittar verktyg.
4. Karaktär B samlar proviant.
5. Karaktär B flyttar närmare en plats som kan innehålla ett målobjekt.
6. Gruppen löser underhåll och kontrollerar om någon vinst eller förlust inträffat.

## Vad som ännu inte är bestämt

- exakt tema
- exakt karta
- om D6 ska användas
- hur utmaningar löses
- om varje karaktär har unik förmåga
- hur målobjekt fördelas
- exakt kortfördelning
- hur mycket uthålligheten normalt ökar per runda
