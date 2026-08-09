# [PLAN] Expedition – spelutveckling och byggpipeline

## Syfte

Målet är att utveckla ett nytt kooperativt print-and-play-brädspel som:

- fungerar för 1–4 spelare
- spelas tillsammans mot spelet
- kan skrivas ut med en vanlig A4-skrivare
- använder strukturerade YAML-filer som primära källor
- kan generera kort, spelbräde, A6-referenskort, markörer och andra komponenter
- bygger komponenter genom en pipeline från YAML och SVG-mallar till SVG och PDF
- på sikt kan stödja simulering, validering och flera spelvarianter

Projektet ska utvecklas stegvis. Spelbarhet prioriteras före grafisk finish och en fungerande vertikal byggkedja prioriteras före ett stort generellt ramverk.

---

## Grundprinciper

1. **Spelet är referensimplementationen**
   - Vi bygger inte ett helt generellt system i förväg.
   - Varje teknisk lösning ska först behövas av det aktuella spelet.

2. **Källa och output hålls åtskilda**
   - YAML, Markdown, SVG-mallar och skript är källor.
   - Genererade SVG-, PNG- och PDF-filer placeras i `output/`.

3. **Gameplay, presentation och produktion separeras**
   - Gameplay beskriver vad komponenter och regler gör.
   - Presentation beskriver hur komponenten ser ut.
   - Produktion beskriver hur komponenter placeras på A4 för utskrift.

4. **Små iterationer**
   - Varje milstolpe ska ge något som går att granska, bygga eller spela.
   - Vi undviker att skapa hela regelsystemet eller alla komponenttyper samtidigt.

5. **Maskinläsbara regler**
   - Regler och effekter ska uttryckas strukturerat där det är praktiskt.
   - Mänskligt läsbar regeltext får finnas parallellt.
   - Simuleringar ska använda strukturerade effekter, inte tolka fri text.

---

# Rekommenderad projektstruktur

```text
expedition/
  README.md
  PROJECT_STATUS.md
  CHANGELOG.md
  PLAN.md

  docs/
    design-brief.md
    game-overview.md
    rulebook.md
    quickstart.md
    pipeline.md
    production-guide.md
    playtest-guide.md
    playtest-log.md

  data/
    project.yaml
    game.yaml
    rules.yaml
    scenarios.yaml
    cards.yaml
    board.yaml
    tokens.yaml
    reference-cards.yaml

    layouts/
      card-standard.yaml
      board-standard.yaml
      reference-a6.yaml
      token-standard.yaml

    print-layouts/
      cards-a4.yaml
      board-a4.yaml
      reference-a4.yaml
      tokens-a4.yaml

  schemas/
    project.schema.json
    game.schema.json
    rules.schema.json
    cards.schema.json
    board.schema.json
    tokens.schema.json
    reference-cards.schema.json
    layout.schema.json
    print-layout.schema.json

  templates/
    cards/
      standard.svg.j2
    boards/
      node-map.svg.j2
    reference/
      a6-reference.svg.j2
    tokens/
      square-token.svg.j2
    print/
      a4-sheet.svg.j2

  assets/
    icons/
    backgrounds/
    illustrations/
    source/

  scripts/
    validate_project.py
    generate_cards.py
    generate_board.py
    generate_reference_cards.py
    generate_tokens.py
    build_print_sheets.py
    export_pdf.py
    build_all.py

  output/
    components/
      cards/
      boards/
      reference/
      tokens/
    print/
      svg/
      pdf/
    preview/
    build-manifest.json
```

Alla mappar behöver inte fyllas direkt. Strukturen införs gradvis.

---

# Fas 0 – Projektgrund

## Mål

Skapa en tydlig arbetsyta innan spelregler eller generatorer växer.

## Leverabler

- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `PLAN.md`
- grundmappar för `docs/`, `data/`, `templates/`, `scripts/`, `assets/` och `output/`

## Beslut

- Arbetsnamn: **Expedition**
- Format: A4 print-and-play
- Speltyp: kooperativt spel mot spelet
- Spelare: 1–4
- Solo: samma grundregler, med en eller två styrda karaktärer
- Primära källor: YAML, Markdown, SVG-mallar och Python-skript

## Klart när

Projektet kan öppnas av en ny utvecklare och strukturen är begriplig utan muntlig förklaring.

---

# Fas 1 – Spelbrief och minsta spelbara kärna

## Mål

Definiera tillräckligt av spelidén för att tekniken ska byggas mot verkliga behov.

## Frågor som ska besvaras

- Vad gör spelarna varje tur?
- Vad gör spelet varje runda?
- Hur vinner gruppen?
- Hur förlorar gruppen?
- Vilka resurser finns?
- Vilka komponenttyper krävs i första prototypen?
- Hur skiljer sig solo från fler spelare?
- Vilken speltid och svårighetsgrad eftersträvas?

## Rekommenderad första riktning

### Spelupplevelse

Ett lättillgängligt, spänt och utforskande samarbetsäventyr.

### Kärnloop

```text
Hotfas
→ spelarna utför handlingar
→ utforska eller hantera problem
→ samla resurser och målobjekt
→ underhåll
→ nästa runda
```

### Första vinstvillkor

Gruppen hittar tre målobjekt och återvänder till baslägret innan hotspåret når sitt slut.

### Första förlustvillkor

- hotspåret når max
- alla aktiva karaktärer blir utslagna

### Första komponentbudget

- 1 A4-spelbräde
- 18–24 kort
- 1 A6-referenskort per spelare eller grupp
- 12–20 fyrkantiga markörer
- lånade pjäser eller mynt
- 1 vanlig D6 vid behov

## Leverabler

- `docs/design-brief.md`
- `docs/game-overview.md`
- första `data/game.yaml`
- första `data/rules.yaml`

## Klart när

Spelet kan beskrivas på en sida och kärnloopen går att genomföra med papper och handskrivna lappar.

---

# Fas 2 – Gemensam datamodell

## Mål

Skapa en liten men stabil modell som kan användas av regler, komponenter, validering och senare simulering.

## Delar

### `data/project.yaml`

Beskriver projekt, buildmål och aktiva komponenter.

### `data/game.yaml`

Beskriver metadata, spelarantal, resurser, spår, komponentinventering och scenarier.

### `data/rules.yaml`

Beskriver:

- rundans faser
- tillgängliga handlingar
- kostnader
- krav
- effekter
- vinst
- förlust
- solojusteringar

### Effektmodell

Första versionen bör stödja ett litet vokabulär:

```text
gain_resource
lose_resource
move
draw_card
discard_card
increase_track
decrease_track
reveal_location
place_token
remove_token
damage
heal
set_flag
complete_objective
```

## Viktig begränsning

Ingen generell programmeringsmiljö eller avancerat regelspråk byggs i denna fas.

Vi inför endast effekter som det aktuella spelet behöver.

## Leverabler

- första YAML-formaten
- stabila unika id:n
- enkel JSON Schema-validering
- exempeldata för ett scenario

## Klart när

Samma regler kan användas av både en generator och ett framtida simuleringsskript utan att läsa fri svensk regeltext.

---

# Fas 3 – Första vertikala byggkedjan: kort

## Mål

Bevisa hela byggflödet med en komponenttyp.

## Kedja

```text
cards.yaml
→ validering
→ intern Python-modell
→ SVG-template
→ en SVG per kort
→ A4-printark
→ PDF
```

## Första testomfattning

- 3 kortdefinitioner
- 1 kortformat
- 1 SVG-template
- 1 A4-layout
- enkelsidiga kort
- inga PNG-bakgrunder
- SVG-lager för bakgrund, ram, ikon, titel, regeltext och metadata

## Leverabler

- `data/cards.yaml`
- `data/layouts/card-standard.yaml`
- `data/print-layouts/cards-a4.yaml`
- `templates/cards/standard.svg.j2`
- `scripts/generate_cards.py`
- `scripts/build_print_sheets.py`
- `scripts/export_pdf.py`
- genererade SVG- och PDF-filer i `output/`

## Validering

- unika kort-id:n
- giltiga korttyper
- känt ikon-id
- antal kopior större än noll
- textfält får plats eller ger tydlig varning
- outputantal matchar YAML-data

## Klart när

En ändring av titel, position eller text i YAML ger en ny korrekt SVG och PDF utan manuell SVG-redigering.

---

# Fas 4 – Spelbräde

## Mål

Återanvänd samma pipelineprincip för ett A4-spelbräde.

## Första brädmodell

En nodkarta rekommenderas framför rutnät eftersom den:

- kräver mindre regelmassa
- är lättare att anpassa till A4
- fungerar bra med utforskning
- kan beskrivas med noder och kopplingar i YAML
- är enklare att simulera som en graf

## `data/board.yaml`

Bör beskriva:

- brädets id och storlek
- platser/noder
- koordinater
- kopplingar
- startplats
- platstyper
- symboler
- spår eller pooler, till exempel uthållighet och runda
- eventuella tokenpositioner

## Lager

- grundbakgrund
- dekorativa zoner
- kopplingslinjer
- platsfält
- ikoner
- platstext
- hotspår
- utskriftsmarkeringar

## Leverabler

- `data/board.yaml`
- `data/layouts/board-standard.yaml`
- `data/print-layouts/board-a4.yaml`
- `templates/boards/node-map.svg.j2`
- `scripts/generate_board.py`
- A4-SVG och PDF

## Klart när

Noder kan flyttas, döpas om eller kopplas om i YAML och hela brädet byggs om automatiskt.

---

# Fas 5 – A6-referenskort

## Mål

Generera ett bordsvänligt referenskort från samma regeldata som spelet använder.

## Innehåll

- rundans faser
- spelarens tur
- grundhandlingar
- centrala symboler
- vinst och förlust i kortform
- solojustering vid behov

## Princip

Referenskortet ska så långt som möjligt hämta data från `rules.yaml`, men får ha en separat presentationsdefinition för ordning och kortfattad text.

## Leverabler

- `data/reference-cards.yaml`
- `data/layouts/reference-a6.yaml`
- `data/print-layouts/reference-a4.yaml`
- `templates/reference/a6-reference.svg.j2`
- `scripts/generate_reference_cards.py`
- A6-SVG
- A4-ark med fyra A6-kort
- PDF

## Klart när

En ändring av handlingarnas namn eller kostnad i regeldata kan slå igenom i referenskortet utan dubbel manuell redigering.

---

# Fas 6 – Markörer och tokenark

## Mål

Generera enkla, produktionsvänliga markörer.

## Första begränsning

- fyrkantiga markörer
- enkelsidiga
- få typer
- tydlig ikon och text eller värde
- inga avancerade konturskärningar

## Leverabler

- `data/tokens.yaml`
- `data/layouts/token-standard.yaml`
- `data/print-layouts/tokens-a4.yaml`
- `templates/tokens/square-token.svg.j2`
- `scripts/generate_tokens.py`
- A4-SVG och PDF

## Klart när

Antal, storlek, färg och symbol kan ändras i YAML och ett nytt tokenark byggs automatiskt.

---

# Fas 7 – Gemensam build och manifest

## Mål

Samla komponentgeneratorerna i en reproducerbar build.

## `scripts/build_all.py`

Föreslagen ordning:

1. läs `project.yaml`
2. validera alla aktiva YAML-filer
3. bygg komponent-SVG
4. bygg A4-printark
5. exportera PDF
6. kontrollera filer och sidantal
7. skriv `output/build-manifest.json`
8. rapportera varningar och fel

## Build-manifest

Bör innehålla:

- projektversion
- buildtid
- använda källfiler
- genererade filer
- antal komponenter
- antal A4-sidor
- eventuella varningar
- verktygs- eller scriptversion

## Klart när

Ett enda kommando bygger hela prototypen på nytt från källfiler.

---

# Fas 8 – Första fysiska prototypen

## Mål

Skriva ut och spela en komplett men enkel version.

## Printpaket

- spelbräde, A4
- kortark
- tokenark
- A6-referenskort
- kort regelblad
- produktionsguide

## Första testmål

Inte balans i detalj.

Testa endast:

- går spelet att förbereda?
- förstår spelaren vad den gör på sin tur?
- fungerar spelmotståndet?
- är vinst och förlust tydliga?
- är solo administrativt rimligt?
- går komponenterna att läsa och hantera?
- tar spelet ungefär avsedd tid?

## Mätvärden

- speltid
- antal rundor
- hotnivå vid slut
- antal använda handlingar
- antal gånger regler behöver slås upp
- vinst/förlust
- dödtid mellan spelare
- komponenter som inte används

## Klart när

En hel omgång går att spela utan att regler behöver uppfinnas under spelets gång.

---

# Fas 9 – Regelbok och regelgenerering

## Mål

Skapa en riktig regelbok utan att göra YAML till ett obehagligt författarformat.

## Rekommenderad modell

- `rules.yaml` är maskinläsbar regelkälla.
- `docs/rulebook.md` är den pedagogiska regelboken.
- vissa tabeller och faktarutor kan genereras från YAML.
- löptext, exempel och förklaringar skrivs i Markdown.

## Automatiskt genererbara delar

- komponentlista
- spelarantal
- handlingstabell
- fasöversikt
- symbolförteckning
- vinst- och förlustvillkor
- scenarioegenskaper

## Klart när

Regelboken och komponenterna använder samma namn och värden utan motsägelser.

---

# Fas 10 – Simuleringsgrund

## Mål

Bygga en enkel simulering först när en människa har kunnat spela kärnloopen.

## Första simulering

Inte en intelligent spelare.

En regelbaserad agent kan:

- välja laglig handling
- prioritera mål enligt enkel lista
- hantera resurser
- spela ett scenario många gånger
- logga resultat

## Frågor simuleringen kan undersöka

- tar hotspåret slut för snabbt?
- är vissa resurser nästan aldrig relevanta?
- når spelet ofta ett låst läge?
- varierar speltiden orimligt mycket?
- skalar svårigheten med spelarantal?
- verkar någon handling nästan alltid bäst?

## Viktigt

Simuleringens resultat är hypoteser och ska inte ersätta mänskliga speltester.

## Klart när

Simuleringen kan köra många reproducerbara omgångar och exportera sammanfattande data utan att kringgå reglerna.

---

# Fas 11 – Grafiklager och PNG-bakgrunder

## Mål

Införa mer visuell identitet efter att komponentformat och kärnloop är stabila.

## Lagerordning

```text
grundfärg
→ PNG-bakgrund eller illustration
→ SVG-toning/mask
→ dekorativ SVG-ram
→ ikoner
→ text
→ metadata
```

## Krav

- PNG-bakgrunder är utbytbara assets
- ingen regeldata bakas in i bilden
- text förblir SVG-text så länge möjligt
- ink-friendly-läge kan stänga av tunga bakgrunder
- builden ska fungera även om illustration saknas

## Klart när

Samma kort kan byggas i minst två presentationer, exempelvis standard och ink-friendly, utan ändrad gameplay-data.

---

# Fas 12 – Stabilisering och release

## Mål

Skilja arbetsoutput från ett rent utskriftspaket.

## Release

```text
release/v0.x.y/
  README.md
  RELEASE_MANIFEST.json
  docs/
  print/pdf/
  print/svg/
```

## Kontrollpunkter

- alla YAML-filer valideras
- alla id:n är unika
- komponentantal stämmer
- alla ikoner finns
- referenskort och regelbok matchar reglerna
- samtliga PDF:er går att öppna
- sidantal är rimligt
- testsida har skrivits ut
- marginaler och skärlinjer fungerar
- kända begränsningar dokumenteras
- `PROJECT_STATUS.md` och `CHANGELOG.md` är uppdaterade

---

# Föreslagen arbetsordning härifrån

## Nästa steg: iteration 1

1. Skapa projektstommen.
2. Skriva `design-brief.md`.
3. Definiera kärnloop, vinst, förlust, resurser och första komponentlista.
4. Skapa första versionen av `game.yaml` och `rules.yaml`.
5. Dokumentera vilka delar som fortfarande är designhypoteser.

## Iteration 2

1. Skapa tre testkort.
2. Definiera kortlayout i YAML.
3. Skapa första SVG-templaten.
4. Generera kort-SVG.
5. Bygga första A4-arket.
6. Exportera första PDF-filen.

## Iteration 3

1. Definiera nodkartan i YAML.
2. Generera spelbrädet.
3. Skapa hotspår och platsikoner.
4. Exportera A4-brädet till PDF.

## Iteration 4

1. Skapa A6-referenskort.
2. Skapa markörer.
3. Införa `build_all.py`.
4. Skapa en komplett utskrivbar mikroprototyp.

## Iteration 5

1. Spela första solo-genomgången.
2. Dokumentera frågor och regelhål.
3. Göra högst tre huvudändringar.
4. Bygga nästa version.

---

# Beslut som medvetet skjuts upp

- slutligt tema och grafisk stil
- PNG-illustrationer
- dubbelsidig utskrift
- avancerad textpassning
- helt generell komponentmotor
- generellt regelspråk
- avancerad AI
- kampanjstruktur
- flera spelbräden
- många karaktärer
- finbalans
- professionell release-layout

---

# Framgångskriterier för v0.1

Version 0.1 är lyckad när:

- hela spelet kan byggas från strukturerade källfiler
- minst kort, spelbräde, referenskort och markörer genereras
- samtliga delar får plats på ett rimligt antal A4-sidor
- en full solo-omgång går att spela
- 2–4 spelare kan spela med samma kärnregler
- ett enda buildkommando genererar alla printfiler
- ändringar i YAML slår igenom utan manuell redigering av genererad SVG eller PDF
- kända problem är dokumenterade för nästa iteration

---

# Rekommendation

Börja med **Fas 0 och Fas 1**, inte med mer arkitektur.

Det första tekniska målet blir därefter en mycket liten vertikal kortpipeline. När den fungerar återanvänder vi samma mönster för spelbräde, A6-referenskort och markörer.

På så sätt utvecklas spelet och byggsystemet tillsammans, utan att vi låser oss för tidigt eller bygger ett ramverk som ännu saknar verkliga behov.
