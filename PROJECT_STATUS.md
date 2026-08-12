# Projektstatus

## Nuläge

Expedition är ett källdrivet print-and-play-projekt med två aktiva scenarier, datadriven spelmotor, simulator, validering, automatiska tester och reproducerbar printpipeline.

Spelplanen finns som kompakt A4 och som två liggande A4-sidor med skrivarsäker överlapp. Transitnoder, scenariohändelser, platsbrickor, vägbrickor, karaktärskort, utrustning, målobjekt och referensmaterial byggs från strukturerade källor.

GitHub Actions hanterar tre separata flöden:

- validering av källor och tester
- preview-build av allt utskrivbart material
- versionerad release av verifierat printpaket

## Versionshantering

Aktuell projektversion finns endast i `data/project.yaml` under `project.project_version`.

Git-taggen för en release ska matcha värdet i `data/project.yaml`. Buildmanifest, printpaket och releasefilnamn hämtar versionen automatiskt därifrån.

Aktiva regler, referenskort, dokumentrubriker och källfilnamn ska normalt inte innehålla patchversionsnummer. Historiska versionsreferenser hör hemma i `CHANGELOG.md`, playtestloggen och frysta analys-/sessionsrapporter.

## Repositorypolicy

Versionshanteras:

- `.github/`
- `data/`
- `schemas/`
- `templates/`
- `scripts/`
- `assets/`
- `docs/`
- `agents/`
- `engine/`
- `simulation/`
- `tests/`
- top-level dokumentation och konfiguration

Genereras och checkas inte in:

- `output/`
- `release/`
- `release-dist/`
- `dist/`
- `build/`
- cache- och temporärfiler

## Aktuella designrisker

- Skada har hittills haft låg strategisk betydelse i både simulering och första fysiska testet.
- Transitnoder och dolda vägar behöver fortsatt fysisk verifiering för att säkerställa att risk/belöning känns intuitiv.
- Tvåspelarlägets uthållighetsprofil och agentresultat är simulatorhypoteser och inte slutbalans.
- Fysisk läsbarhet, montering av 2×A4-spelplanen och blindtest återstår att verifiera vidare.

## Nästa praktiska steg

1. Fortsätt fysisk testning av Station Nordanvind med fokus på vägval, skada och handlingsflöde.
2. Kontrollera 2×A4-spelplanens skarv och skrivarmarginaler i faktisk utskrift.
3. Kör preview-build i GitHub Actions efter layout- eller regeländringar.
4. Skapa GitHub Release först när printpaketet är testutskrivet och validerat.
