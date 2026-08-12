# Expedition

## Scenarioark och milstolpar i v1.9.50

Scenarioarken har tydligare förberedelser, konsekventa benämningar och mindre upprepad grundregeltext. Vägöppningar hanteras nu som scenariohändelser, så flera händelser kan inträffa vid samma milstolpe i angiven ordning.

## Scenarioark som tilläggsblad i v1.9.45

Scenarioarken visar nu endast det som läggs till för det aktuella scenariot. Grundutrustning och bashändelser förklaras i regelboken. Komponentenheten listar konkreta platskort, målobjekt, extra utrustning, extra färdhändelser och scenariohändelser. Standardrutan för Förlust är borttagen och Vinst visas som en låg helbreddsruta längst ned.

## Scenarioarkens informationshierarki i v1.9.30

Scenarioarken har fått en kompakt gemensam ruta för vinst och förlust, större yta för mål och progression samt en bredare och mer konkret komponentlista. Intern termen `basprofil` visas inte längre. Konkreta målobjekt, bashändelser, extra färdhändelser och scenariohändelser listas separat.

## Fysisk status och komponentplacering i v1.9.29

Platsbrickor är nu dubbelsidiga och ersätter separata Okänd-markörer. Basläger och Förråd har egna platskort. Föremål placeras vid platskort eller karaktärskort för att visa var de finns, och målobjekt vrids 90 grader när de aktiveras. Regelboken beskriver vägar efter status: öppen, dold, hinder eller stängd.


## Regel-täckningsmatris i v1.9.27

`docs/rule-coverage-matrix.md` och `data/rule-coverage.yaml` kopplar nu varje kartlagd regel till YAML-källa, motorfunktion, simulatorstöd och automatiska tester. Matrisen skiljer full täckning från delvis stöd, presentationslager och sådant som kräver fysisk kontroll.


Ett kooperativt print-and-play-äventyr för 1–4 spelare.

## Simulator alignment i v1.9.25

Simulatorn exporterar nu scenariohändelse per spel och kan köra seed-matchade jämförelser med scenariohändelse aktiva eller avstängda. Detta gör det möjligt att isolera eventkortens påverkan på vinstgrad, rundor, uthållighet och vägstatus utan att ändra spelreglerna.


## Status

Version 1.9.62 – tydligare scenarioark och enhetliga milstolpar.

Projektet innehåller nu:

- projektstruktur
- spelbrief
- spelöversikt
- första strukturerade speldata
- första strukturerade regler
- projektmanifest i `data/project.yaml`
- JSON Schema för projekt, spel och regler
- körbar tvärfilsvalidering
- projektstatus
- changelog

Genererad print-output och en versionsren release finns. Nästa steg är fysisk A/B-playtest och därefter blindtest.



## v1.9.25 – arkitekturlås

- Trigger-, effekt- och miljöleksformat är låsta i `docs/scenario-event-architecture.md`.
- Scenariohändelse använder endast omedelbara effekter i arkitekturversion 1.
- Platsbrickor är formaliserade som presentationslager.
- Kvarvarande konsistensfel i kort- och regeltext är rättade.

## v1.9.23 – komponentlika vägstatusrutor och renare bräde

- D1-D4 och V1-V4 använder samma 16 × 16 mm grundlayout som de fysiska road markers-brickorna.
- Väg-id visas diskret i markörrutans övre högra hörn.
- Vägstatusar har tagits bort ur brädets legend eftersom rutorna och brickorna använder samma visuella språk.
- Rubrik, undertitel, rundspår och teknisk footer har tagits bort från spelbrädet.
- Kartgeometri, scenarioregler och balans är oförändrade.

## v1.9.20 – enhetligt vägstatussystem

- De fyra centrala specialvägarna har id D1-D4 och visar Öppen-status på brädet.
- Scenarioarket anger exakt vilka D-vägar som täcks av dolda vägmarkörer.
- V1-V4 visar Stängd-status på brädet och täcks med Öppen väg-markör när de aktiveras.
- Road-markers-arket innehåller 4 dolda utfallsmarkörer, 8 Öppen väg-markörer och 8 Stängd väg-markörer.
- Stängd väg-markör är förberedd för framtida scenarier men används inte i de två nuvarande.

## v1.9.19 – tydlig planskild korsning

- V4 visas med en liten bro där den korsar V3.
- V3 passerar visuellt under bron utan anslutningspunkt.
- Korsningen är datadriven via `data/board.yaml` och genereras från källan.


## v1.9.18 – finjusterad placering av V3 och V4

- V4-rutan har flyttats tydligt åt höger för bättre visuell balans mot V3.
- V3:s nedersta horisontella segment har lyfts för större avstånd till Baslägret.
- V1, V2 och V4:s linjedragning är i övrigt oförändrad.

## v1.9.17 – finjusterad dragning av potentiella vägar

- V1 ansluter horisontellt till vänster sida av Plats 3 och Förrådet.
- V2 speglar V1 på höger sida av Plats 5 och Förrådet.
- V3 går från ovansidan av Plats 6 via en yttre vänsterkorridor till undersidan av Förrådet.
- V4 är oförändrad.

## v1.9.16 – tydligare kart- och scenarioinformation

- V1–V4 ritas som tydligare yttre bågar för att inte konkurrera med platsnoderna.
- Markörytan för öppnade potentiella vägar är förstorad till 14 × 14 mm.
- Scenarioarken listar namn på använda platskort och målobjektskort.
- Ökenreläets reservmoduler visas konsekvent som målobjekt: `Reservmodul ×3`.
- Scenarioarken anger vilka händelselekar som används; A6-kortet förklarar fortsatt den generella händelseproceduren.

## v1.9.14 – scenariostyrd målarkitektur

- målobjektskorten visar endast identitet, korttext och ryggsäcksstorlek
- grundregelboken beskriver plocka upp, överföra, lämna och aktivera målobjekt
- scenarioarken anger destination, slutförande, målantal och progression
- spelmotor och simulator använder samma scenarioägda mission-definition
- valideringen stoppar scenariologik i målobjektskortens text

## v1.9.13 – konsistenskorrigering

- grundregelboken hämtar startuthållighet och vinstvillkor från scenarioarket
- A6-referensen visar korrekt uthållighetsfas och scenariogeneriskt slutvillkor
- regelbokens numrering och vägterminologi är rättad
- singularformen `1 plats` används på Ökenreläets utrustningskort
- äldre tekniska prototypkort byggs inte längre till printoutput eller release

## [PLAN] Prompt 6 – scenariointegration och playtest

- Station Nordanvind öppnar V1 efter första leveransen och V2 efter den andra.
- Station Nordanvinds första fysiska testprofil är 11/9/8 uthållighet.
- Ökenreläet öppnar V4 efter första reläet och V2 efter det andra.
- Ökenreläets uthållighet lämnas oförändrad tills reläflödet verifierats fysiskt.
- Separat playtestguide och balansunderlag finns i `docs/`.
- En versionsren release skapas i `release/v1.9.12/`.

## [PLAN] Prompt 5 – fysisk representation

- V1–V4 renderas som svagt streckade potentiella vägar på spelbrädet
- stängda potentiella vägar har ingen markör vid setup
- tre Öppen väg-markörer ingår på vägmarkörsarket
- regelbok och A6-referens förklarar hur scenariovägar aktiveras
- huvudscenarierna öppnar ännu inga V-vägar; progression och balans låses i Prompt 6

## [PLAN] Prompt 4 – simulatorstöd

- dynamiska vägöppningar loggas per spel
- användning och öppningsrunda registreras per förbindelse
- agenten kan välja en väg utifrån aktuell kartnytta
- vänster-, höger- och slumpmässig tie-breaker stöds
- `simulation/run_dynamic_connection_experiments.py` skapar seed-matchade jämförelser
- experimentmatrisen kan variera scenario, uthållighet, vägprogression och tie-breaker
- genererade rapporter ligger i `output/simulation/dynamic-connections/`

## Spelöversikt

I Expedition utforskar spelarna en okänd plats, samlar tre målobjekt och försöker återvända till baslägret innan hotspåret når sitt slut.

Spelet är:

- kooperativt
- för 1–4 spelare
- cirka 25–40 minuter
- avsett för A4 print-and-play
- byggt kring strukturerade YAML-källor

## Viktiga filer

- `docs/design-brief.md` – designmål och avgränsningar
- `docs/game-overview.md` – spelidén i spelbar form
- `data/game.yaml` – strukturerad spelmetadata
- `data/rules.yaml` – strukturerad regelmodell
- `PROJECT_STATUS.md` – nuläge och nästa steg
- `CHANGELOG.md` – versionshistorik

## Projektprincip

Källor ligger i `docs/`, `data/`, `templates/` och `scripts/`.

Genererade filer ska senare ligga i `output/`.

PDF, PNG och genererad SVG ska inte vara enda sanningen för projektet.


## Validering

Installera beroenden och kör:

```bash
python -m pip install -r requirements.txt
python scripts/validate_project.py
```

Valideringen kombinerar JSON Schema med kontroller mellan YAML-filerna.


## Gemensam build

Installera beroenden och bygg hela projektet:

```bash
python -m pip install -r requirements.txt
python scripts/build_all.py
```

Builden styrs från `data/project.yaml` och skapar:

- samtliga komponent-SVG
- samtliga print-PDF
- `output/build-manifest.json`
- `output/build-report.md`
- `output/build-log.txt`

Se `docs/build-system.md` för full dokumentation.


## Första fysiska prototypen

Det kompletta utskriftspaketet finns i:

```text
output/print-package/expedition-v0.8-complete-print-pack.pdf
```

Paketet innehåller regler, monteringsguide, spelbräde, kort, tokens, referenskort, playtestguide och formulär.

Den tekniska preflighten och två digitala regelgenomgångar är genomförda. Fysisk utskrift, montering och bordstest kan inte genomföras i denna miljö och återstår därför.


## Omdesign v0.9

Den aktuella spelversionen använder:

- fasta Basläger och Förråd
- sex dolda platskort kopplade till plats 1–6
- tre dolda målobjekt
- fyra okända genvägar
- vikbara vägmarkörer med öppen, blockerad eller färdhändelse
- en liten lek med sex färdhändelser

Det kompletta printpaketet skapas som:

```text
output/print-package/expedition-v0.9-complete-print-pack.pdf
```


## Karaktärer och ryggsäck v1.0

Version 1.0 lägger till åtta valbara karaktärer. Varje karaktär har hälsa, ryggsäckskapacitet och en enkel förmåga.

Utrustning och målobjekt är separata kort:

- utrustning kan användas eller ge en passiv effekt
- målobjekt tar två platser och kan inte användas
- verktyg är den enda kvarvarande generella resursmarkören

Det kompletta printpaketet byggs till:

```text
output/print-package/expedition-v1.0-complete-print-pack.pdf
```


## Konsolidering v1.1

Version 1.1 lägger inte till nya mekaniker. Den gör den befintliga prototypen konsekvent:

- uthållighet minskar i slutet av rundan
- karaktärerna agerar i fast ordning
- alla kort visar sin korttyp
- referenskortet har kortare och säkrare layout
- regler och kort använder samma begrepp


## Designsimulator

Kör:

```bash
python scripts/simulate_game.py
```

Simulatorn jämför fem strategier med reproducerbara seeds och skapar rapporter i `output/simulation/`.

Se `docs/simulator.md`.


## Samarbetsstudie

Kör:

```bash
python scripts/run_cooperation_ablation.py
```

Studien jämför individuellt agerande, samordnade destinationer, fullt samarbete och gratis överföring för 2–4 karaktärer.


## Agentarkitektur

Kör jämförelsen:

```bash
python simulation/run_agent_comparison.py --runs 100
```

Alla agenter använder samma spelmotor och speldata.


## Uthållighet

Spelet använder nu en fysisk pool av uthållighetsmarkörer i stället för ett hotspår. Poolens startstorlek bestäms vid setup och kan därför användas för enkel svårighetsskalning utan separata spelregler.


## Normal uthållighetsprofil v1.6

| Karaktärer | Uthållighet | Startverktyg |
|---:|---:|---:|
| 2 | 10 | 1 |
| 3 | 8 | 0 |
| 4 | 7 | 0 |

Profilen gav ungefär 50 %, 47,5 % respektive 57,5 % vinst för strukturerade simulatoragenter och är nu projektets rekommenderade fysiska testprofil.


## Enkelsidiga vägmarkörer

Vägmarkörerna är 16 × 16 mm och passar direkt på brädets 16 × 16 mm stora markörsytor. Lägg dem med den otryckta sidan uppåt och vänd vid första användning.


## Vägmarkörer v1.7.1

Markörerna är 16 × 16 mm och läggs med den otryckta sidan uppåt.

- `Öppen`: vägen kan användas med den vanliga handlingen Flytta.
- `Hinder`: karaktären stannar; Hindret kan tas bort med ett verktyg.
- `Händelse`: dra ett färdhändelsekort och fortsätt därefter rörelsen.


## Scenariomodell v1.8

- `data/base-profiles.yaml` definierar basuppsättningen.
- `data/scenarios.yaml` är scenarioindex och innehåller den simulerbara setupen.
- `data/scenarios/station-nordanvind/scenario.yaml` innehåller story, uppdrag och scenariounikt innehåll.
- A5-kortet genereras från scenariopaketet.


## Simulator v1.8.1

Simulatorn laddar valt scenario, dess basprofil och deklarerade innehållsset.
Startuthållighet och startverktyg tillämpas innan spelomgången skapas och loggas
i varje körning.


## Scenarioplattform v1.9

Basuppsättningen ligger i `data/base/`. Varje expedition ligger i en egen katalog
under `data/scenarios/`. Simulator, validator och generatorer följer deklarerade
källor i stället för globala hårdkodade kortfiler.


## Scenario 02 - Ökenreläet
Hitta tre reservmoduler och aktivera ett målobjekt vid var och en av de tre reläplatserna. Scenariot testar mål som används ute på kartan i stället för att återföras till Baslägret.


## Scenariojämförelse

`scripts/run_scenario_comparison.py` kör Station Nordanvind och Ökenreläet
med samma agenttyper, spelarantal och seeds. Rapporter skrivs till
`output/simulation/scenario-comparison/`.


## Konsoliderad scenariomodell

Scenarier deklarerar nu både uppdragets slutförandemodell och hur bas- och scenariokort kombineras. Se `docs/model-consolidation-v1.9.md` och `data/base/component-policy.yaml`.


## Simulator coverage

Aktiva effekter, förmågor och uppdragstyper kontrolleras automatiskt mot `data/simulation-coverage.yaml`.


## Station Nordanvind – standardsetup

```yaml
endurance_by_character_count:
  "2": 13
  "3": 11
  "4": 10

starting_tools_by_character_count:
  "2": 0
  "3": 0
  "4": 0
```


## Dynamiska förbindelser – Prompt 3

Spelmotorn stödjer nu datadrivna `progression_events` för att öppna eller försegla scenariovägar efter slutförda mål eller aktiverade reläplatser. Huvudscenarierna använder ännu inte funktionen; balans och printlayout är oförändrade.

## Platsbrickor i v1.9.23

- Spelbrädets Plats 1-6 är 30 x 30 mm fyrkantiga brickplatser.
- Varje scenario har sex enkelsidiga platsbrickor med namn och synligt kort-id.
- Samma id visas på platskortets framsida för enkel matchning.
- Platskortens regler och effekter ligger fortsatt bredvid spelbrädet.

## Källor, output och releases

Repositoryt ska vara **källdrivet**. Följande kataloger är kanoniska och ska versionshanteras:

- `data/` – speldata och konfiguration
- `schemas/` – valideringsscheman
- `templates/` – layoutmallar
- `scripts/` – generatorer, validering och paketering
- `assets/` – källgrafik
- `docs/` – regel- och projektdokumentation
- `agents/`, `engine/`, `simulation/`, `tests/` – simulator- och testkällor
- `.github/` – CI/CD-workflows

Följande är **genererade artefakter** och ska inte checkas in:

- `output/` – lokal buildoutput, preview-PDF:er, buildmanifest och simulatorresultat
- `release/` – lokalt skapade releasepaket
- `release-dist/`, `dist/`, `build/` – tillfälliga distributionskataloger

`output/` och `release/` kan därför saknas helt i ett rent checkout. Skripten skapar katalogerna när de behövs.

Preview-filer hämtas från GitHub Actions-artifakter. Riktiga versionerade printfiler hämtas från GitHub Releases. PDF, SVG och andra genererade filer ska alltid kunna återskapas från källorna.


## GitHub Actions

Projektet har tre CI/CD-flöden i `.github/workflows/`:

- `01-validate.yml` kör strikt källvalidering och hela testsuiten på pull requests, push till `main` och manuellt.
- `02-build-preview.yml` bygger om alla aktiva printfiler och laddar upp PDF:er, komplett printpaket och buildrapport som en tillfällig GitHub Artifact.
- `03-release.yml` körs på taggar `v*`, kräver att taggen matchar `data/project.yaml`, bygger om allt från källor och publicerar ett verifierat print-releasepaket på GitHub Releases.

Lokalt motsvaras flödena av:

```bash
python -m pip install -r requirements.txt pytest
python scripts/ci_validate.py --root .
python scripts/build_all.py --root . --clean --strict
python scripts/ci_validate.py --root . --built --skip-tests
python scripts/package_release.py --root . --output-dir release-dist --expected-version 1.9.61
```

GitHub Actions bygger från källorna och behandlar `output/` som genererad arbetsoutput.

