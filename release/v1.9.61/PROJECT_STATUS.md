## v1.9.61 – CI/CD för validering, preview och release

- GitHub Actions är infört med tre separata workflows.
- Projektversionen är synkroniserad mellan `data/project.yaml` och `PROJECT_MANIFEST.json`.
- CI bygger alltid printfiler från källor och verifierar printpaketets manifest efter build.
- GitHub Release skapas endast från en tagg som exakt matchar projektversionen.

# Project status

## v1.9.61 - 2xA4-spelplan i liggande format
- Primär stor spelplan: A3-område (297 x 420 mm).
- Utskrift: två liggande A4-sidor (297 x 210 mm), övre och nedre.
- Komponentstorlekar är oförändrade; endast koordinater och avstånd har justerats.
- Skarven går horisontellt mellan nodgrupper.
- Kompakt A4-version finns kvar för snabb prototyp.
- Skadereglerna är oförändrade.

# Projektstatus

## v1.9.50 – Adaptiv genvägsagent

- Simulatorn innehåller nu en adaptiv agent som inte alltid använder eller alltid undviker dolda vägar.
- Agenten jämför aktuell säker rutt med rutt via dolda vägar och väljer genvägen när den sparar minst två handlingar.
- Beslutet är en simulatorhypotes och ska jämföras med mänskliga speltest.
- Transitnoderna och övriga spelregler är oförändrade.
- Nästa lämpliga steg är en seed-matchad jämförelse mellan adaptiv, försiktig och riskbenägen agent.

## v1.9.48 – Tydligare scenarioark och enhetliga milstolpar

- Scenarioarkens Förberedelser använder automatisk radbrytning och fullständiga ord.
- Verktygsfördelning och gemensam start i Baslägret förklaras endast i regelboken.
- Scenariotillägg använder `Egen hög` och `Blanda med övriga` utan redundanta antal.
- Vägöppningar är scenariohändelsekort och delar milstolpssystem med övriga scenariohändelser.
- Flera scenariohändelser vid samma milstolpe genomförs i den ordning de listas.
- Vinsttexten använder bredare radbrytning.
- Inga balansvärden har ändrats.
- Nästa steg är fysisk kontroll av A5/A4-scenarioark och scenariohändelsearket.

## v1.9.45 – Scenarioark som tilläggsblad

- Standardrutan för Förlust är borttagen från scenarioarken.
- Vinst visas i en låg helbreddsruta längst ned med kolumnindelning.
- Komponentenheten heter `Lägg till för detta scenario` och har större höjd.
- Grundutrustning och bashändelser listas inte längre på scenarioarken.
- Scenariospecifika kort listas som `Extra utrustning` och `Extra färdhändelser`.
- Scenariohändelser listas separat.
- Regelboken förklarar att grundutrustning och bashändelser alltid förbereds före scenariotilläggen.
- Inga balansvärden har ändrats.

## v1.9.30 – Scenarioarkens informationshierarki

- Vinst och förlust visas i en gemensam kompakt ruta.
- Mål och progression har fått större vertikal yta.
- Komponentenheten heter `Använd dessa kort och lekar` och är bredare.
- Intern termen `basprofil` visas inte längre för spelaren.
- Målobjekt listas med konkreta kortnamn utan överordnad kategori.
- Bashändelser, extra färdhändelser och scenariohändelser är tydligt separerade.
- Båda scenarioarken är ombyggda och visuellt granskade.
- Inga spelregler eller balansvärden har ändrats.

## v1.9.29 – Fysisk status och komponentplacering

- Dubbelsidiga platsbrickor ersätter separata Okänd-markörer.
- Basläger och Förråd har egna öppna platskort för föremålsplacering.
- Föremål vid platskort finns på platsen; föremål vid karaktärskort finns i ryggsäcken.
- Målobjekt aktiveras med en generell handling och vrids 90 grader vid destinationens platskort.
- Dolda vägar avslöjas endast som del av handlingen Flytta.
- Regelbok och snabbstart använder Scenariohändelse som spelarvänd term; interna data-id:n är oförändrade.
- YAML, schema, generatorer och print-output är uppdaterade.
- Fysisk blindtest av dubbelsidig utskrift och bordsläsbarhet återstår.

## v1.9.27 – Regel-täckningsmatris

- 32 centrala regler är kopplade till YAML, motor, simulator och tester.
- 8 regler har full automatisk täckning.
- 21 regler är implementerade men behöver mer direkta tester eller har begränsad agentheuristik.
- 1 regel är avsiktligt presentationslager och 2 kräver fysisk kontroll.
- `data/rule-coverage.yaml` är validerad strukturerad källa.
- `docs/rule-coverage-matrix.md` är den mänskligt läsbara rapporten.
- Strict build validerar matrisens schema.
- Ingen spelregel eller balansprofil har ändrats.

## Tidigare status


## v1.9.25 – Simulator alignment

- Scenariohändelse exporteras nu i `GameResult` och simuleringsrapporter.
- Loggning omfattar kort-id, runda, uthållighetsdelta samt öppnade/stängda förbindelser.
- Dynamiska förbindelseexperiment kan köras seed-matchat med scenariohändelse `on` och `off`.
- Tre nya automatiska tester verifierar avstängning, eventlogg och resultatexport.
- Scenariohändelsearkitekturen från v1.9.24 är oförändrad.
- Fysisk playtest och blindtest återstår.

## Tidigare status

## v1.9.24 – Scenariohändelsearkitektur låst

- Triggers: `objective_found`, `objective_completed`, `objective_activated`, `location_explored`, `all_objectives_completed`.
- Eventeffekter v1: `modify_endurance`, `open_connection`, `close_connection`.
- Milstolpar är engångstriggers och fasta kort används i nuvarande scenarier.
- Upplösningsordningen progression → scenariohändelse → vinst/förlust är låst.
- Platsbrickor är presentationslager och matchas med platskortets id.
- Slumpade/dolda miljölekar och fler effekter är avsiktligt uppskjutna.
- Fysisk playtest och blindtest återstår.

## Tidigare status

# Projektstatus

## v1.9.23 – Scenariomilstolpar, iteration 1

- Rundbaserade stormeffekter och den fysiska rundmarkören har tagits bort.
- Milstolpar kan triggas av `objective_found`, `objective_completed`, `objective_activated` och senare även platsutforskning.
- `relay_installed` är ersatt av den generella triggern `objective_activated`.
- Två fasta, öppna och omedelbara scenariohändelse finns per miljö.
- Scenariohändelse löses helt när de triggas och kasseras därefter.
- Kvarvarande kartändringar visas med befintliga vägmarkörer.

## v1.9.22

Spelbrädet använder nu komponentlika 16 × 16 mm vägstatusrutor med väg-id i övre högra hörnet. Rubrik, undertitel, rundspår, vägstatuslegend och teknisk footer är borttagna. Kartgeometri och regler är oförändrade.

## Version

v1.9.20 – enhetligt vägstatussystem

## Aktiva scenarioförändringar

### Station Nordanvind

- V1 öppnas efter första återförda målobjektet.
- V2 öppnas efter andra återförda målobjektet.
- Första fysiska testprofil: 11/9/8 uthållighet för 2/3/4 karaktärer.
- Inga startverktyg.

### Ökenreläet

- V4 öppnas efter första aktiverade reläplatsen.
- V2 öppnas efter den andra aktiverade reläplatsen.
- Befintlig uthållighetsprofil behålls tills fysisk verifiering.

## Genomfört

- gett de fyra centrala specialvägarna id D1-D4
- gjort D-vägarnas tryckta grundstatus Öppen och V-vägarnas tryckta grundstatus Stängd
- lagt scenarioansvar på exakt vilka D-vägar som får dolda markörer
- utökat road-markers-arket till 4 dolda utfallsmarkörer, 8 Öppen och 8 Stängd väg-markörer
- förberett Stängd väg-markörer för framtida scenarier utan att aktivera dem i nuvarande scenarier

- flyttat V4-rutan åt höger och lyft V3:s nedersta korridor för bättre kartläsbarhet

- flyttat destination, slutförandedefinition och progression till scenario-YAML och scenarioark
- gjort målobjektskorten scenariogeneriska; ryggsäcksstorlek finns kvar på korten
- samlat överlämning, lämning och installation i grundregelboken
- uppdaterat motor, simulator, schema och validering för den nya ansvarsfördelningen

- konsistenskorrigering av regelbok, A6-referens, versionsmärkning och kortmallar
- scenariostyrd startuthållighet och scenariogeneriskt vinstvillkor i grundreglerna
- äldre tekniska prototypkort borttagna från aktiv printpipeline

- gemensam connection-modell
- runtime-state och dynamisk pathfinding
- datadrivna progression events
- simulatorrapportering och tie-breaker-varianter
- V1–V4 på brädet
- Öppen-markörer och regelmaterial
- scenariointegration för båda scenarierna
- playtestguide och balansunderlag
- versionsren release v1.9.17

## Kända risker

- Station Nordanvinds 11/9/8-profil är endast en testhypotes.
- Ökenreläets simulator visar låg vinstgrad och kan behöva regel- eller agentgranskning.
- Känd öppningsordning kan skapa en dominant utforskningsrutt.
- Två positiva upplåsningar kan ge snöbollseffekt.
- Fysisk läsbarhet och markörhantering är ännu inte blindtestade.

## Rekommenderat nästa steg

1. Fysiskt A/B-test av Station Nordanvind: v1.9.12 mot tidigare kontrollprofil.
2. Fysiskt test av Ökenreläet med fokus på V4:s faktiska nytta.
3. Uppdatera playtestloggen med runda för öppning och första användning.
4. Ändra högst tre parametrar efter testerna.

## Ändra inte ännu

- målantal
- fler potentiella vägar
- fler state-övergångar
- scenariohemligheter eller slumpmässiga öppningar
- slutlig releaseprofil för uthållighet

## Platsbrickor v1.9.22

Första prototypen använder 12 enkelsidiga platsbrickor (30 x 30 mm), sex per scenario. Brickorna visar endast namn och id. Platskortens framsidor visar samma id. Fysisk passform och bordsläsbarhet återstår att testas.

- Ökenreläets tre destinationer benämns konsekvent **reläplatser** och markeras på platskorten.

- Utrustningskort anger nu uttryckligen om användning kräver 1 handling eller ingen handling; engångsutrustning kasseras först vid faktisk användning.

- Kortstandard v1.9.45: dynamiska rubriker, enhetliga korttyper och aktiverade reläplatser utan separata reparationsmarkörer.

- Aktivera målobjekt finns nu på A6-referensarket; ryggsäckssektionen beskriver endast var föremål finns.


## v1.9.45 – Simulator med mänskliga regelbegränsningar

- Simulatorn får inte betala fler handlingar än karaktären har kvar.
- Omedelbar förlust stoppar resterande aktivering.
- Målobjektsstorlek läses från YAML.
- Överföra omfattar målobjekt, utrustning och verktyg för alla karaktärer.
- Medicinväskan kan användas på en annan karaktär på samma plats.
- Valet verktyg eller skada hanteras som ett agentval.
- Vattenreserv och Diagnosverktyg används vid sina faktiska triggers.
- Åtta nya simulatorregelkontrakt skyddar beteendet.


## v1.9.45 – Nybörjarflöde

- Regelboken leder nu från komponentuppställning till första rundan.
- Scenarioarken anger hur scenariokort ska blandas in eller läggas separat.
- Platskort läggs i en dold id-sorterad rad för enkel matchning.
- Skillnaden mellan att lämna och aktivera målobjekt är uttrycklig.
- A6-referensen beskriver Utforska korrekt.
- Kortterminologi och scenariohändelsenamn har standardiserats.


## v1.9.45 – Layoutsäkerhet

- Tvåradiga platsrubriker flyttas ned och får mer plats mellan kategorifält och symbol.
- Rubrikbrytning använder viktad teckenbredd i stället för enbart teckenantal.
- A6-referensens SLUT-ruta är högre och använder två separata informationsrader.
- Automatiska layouttester täcker kända långa platsnamn och A6-rutan.
- Äldre releasekataloger och all tidigare genererad output tas bort före paketering.


## v1.9.45 – Överföringsheuristik

- Simulatorn överför bara föremål när det finns konkret logistisk nytta.
- Målobjekt kan lämnas till en karaktär som är närmare destinationen eller tydligt bättre bärare.
- Verktyg överförs bara från överskott till en målobjektsbärare med konkret behov.
- Medicinväska överförs bara till en skadad lagkamrat när bäraren inte själv behöver den.
- Omvänd överföring blockeras under nästa runda.
- Högst en strategisk överföring görs per aktivering.
- Seed-matchad jämförelse omfattar 180 simuleringar.


## v1.9.45 – Ökenreläet: preliminär startuthållighet

- Ökenreläet får +2 startuthållighet för 2, 3 och 4 karaktärer.
- Nya värden: 12 / 10 / 9 uthållighet.
- Ändringen är ett preliminärt playtestvärde och ska verifieras i praktiskt speltest.
- Inga övriga scenario-, regel- eller komponentvärden har ändrats.


## v1.9.45 – Synkroniserat scenarioregister

- `data/scenarios.yaml` använder nu samma uthållighetsvärden som Ökenreläets scenariofil.
- Simulatorn läser därmed automatiskt 12 / 10 / 9 uthållighet för 2 / 3 / 4 karaktärer.
- Ett regressionstest säkerställer att scenarioregister och scenariokällor inte driver isär igen.
- Inga ytterligare balansvärden har ändrats.


## v1.9.45 – Sessionsrapporter

- Ny generator för läsbara Markdown-sessioner och separat rålogg i JSON.
- Rapporter använder handlingsnamnen från `data/rules.yaml`.
- Den generella regeltermen `målobjekt` används konsekvent.
- Utlösta kort och scenariohändelser presenteras efter den handling som orsakade dem.
- Råloggen sparar tekniskt handlings-id, visningsnamn och möjlig agentineffektivitet.
- Regressionstester verifierar terminologi, handlingsnamn och händelseordning.
- Inga balans- eller spelregelvärden har ändrats.


## v1.9.45 – Scenariovalda D-vägar

- Spelbrädet har nu sex permanenta D-positioner.
- Förbindelserna 1–4 och 2–4 är D5 respektive D6.
- En D-position är öppen i grundläget och blir dold endast när scenariot listar den.
- Station Nordanvind använder D1, D2, D3, D5 och D6; D4 lämnas utan bricka.
- Ökenreläet behåller D1, D2, D3 och D4 som dolda.
- Scenarioarken listar endast vilka D-positioner som ska få dolda vägbrickor.
- Den fysiska utfallspoolen är utökad till sex brickor: 3 öppna, 2 hinder och 1 händelse.
- Validering och regressionstester kontrollerar D-id:n, scenarioreferenser och brickantal.


## v1.9.45 – Scenario-specifika vägbrickor

- Förberedelserutan på scenarioarket är två textrader högre.
- Scenarioarket visar både vägbrickepool och D-positioner.
- Station Nordanvind visar 3 öppna, 2 hinder och 1 händelse samt D1, D2, D3, D5 och D6.
- Ökenreläet visar 2 öppna, 1 hinder och 1 händelse samt D1, D2, D3 och D4.
- Regelboken beskriver blandning, placering med baksidan upp och hantering av överblivna brickor.
- Simulatorn använder scenariots egen vägbrickepool i stället för hela den globala tryckpoolen.
- Validering och regressionstester kontrollerar scenariokällor, fysisk bricktäckning och scenarioarkets layoutkälla.


## v1.9.48 – komponentomfattning och filnamn

Printfiler klassificeras nu som gemensamma, miljöspecifika eller scenariospecifika. Scenariospecifika PDF-filer börjar med scenario-id. Ökenmiljön har egna återanvändbara källor för utrustning och färdhändelser. Station Nordanvind och Ökenreläet har varsin komplett scenariohändelse-PDF.


## Transitnoder v1.9.48

- T1–T4 införda som riktiga, icke utforskbara grafnoder.
- Plats 3 och 5 flyttade 7,5 mm uppåt.
- Fyra öppna sträckor består nu av två segment.
- Separata gemensamma transitbrickor har införts.
- Simulatorn har grundstöd för blockerade transitnoder och entiteter på noder.
