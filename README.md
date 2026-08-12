# Expedition

Ett kooperativt print-and-play-äventyr för 1–4 spelare.

Projektet är källdrivet: speldata, regler, mallar, script och dokumentation versionshanteras i Git. Preview-PDF:er skapas av GitHub Actions och riktiga printfiler publiceras via GitHub Releases.

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

## Platsbrickor i tidigare version

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


### Versionspolicy

Den aktuella projektversionen finns på **ett ställe**: `data/project.yaml` → `project.project_version`.

Git-taggen för en release (`vX.Y.Z`) måste matcha detta värde. Buildmanifest, printpaket, releasefilnamn och release-manifest får sin version automatiskt från `data/project.yaml`. Aktiva regler, referenskort och källdokument ska därför normalt inte innehålla patchversionsnummer i rubriker eller filnamn.

Historiska poster i `CHANGELOG.md`, `docs/playtest-log.md` och frysta analys-/sessionsrapporter får behålla versionsnummer eftersom de beskriver ett specifikt historiskt tillstånd.


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
python scripts/package_release.py --root . --output-dir release-dist
```

GitHub Actions bygger från källorna och behandlar `output/` som genererad arbetsoutput.

