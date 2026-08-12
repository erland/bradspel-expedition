## v1.9.62 – Källrent repository

- `output/` och `release/` är nu uttryckligen genererade artefaktkataloger och ska inte versionshanteras.
- Ny `.gitignore` ignorerar buildoutput, lokala releaser, cachefiler och tillfälliga distributionskataloger.
- README skiljer tydligt mellan kanoniska källor, preview-artifakter och GitHub Releases.
- Ett rent checkout utan `output/` och `release/` ska kunna valideras och byggas fullt via befintliga script och GitHub Actions.

## v1.9.61 – GitHub Actions och reproducerbar publicering

- `.github/workflows/` ligger i projektroten bredvid `README.md`.
- Ny CI-validering kontrollerar schema/YAML, tester, versionssynk och buildkonfiguration.
- Preview-workflow bygger alla aktiva printfiler och publicerar PDF:er samt buildrapport som GitHub Artifact.
- Release-workflow körs på `v*`-tagg, kräver matchande projektversion och publicerar verifierat printpaket på GitHub Releases.
- Nytt `scripts/package_release.py` skapar versionsren distribution och `RELEASE_MANIFEST.json` med SHA-256.
- `assemble_print_package` verifieras nu via versionsoberoende output-glob i stället för ett hårdkodat gammalt versionsfilnamn.

# Changelog

## v1.9.61
- Ersatte den smala 2xA4-layouten med ett A3-stort spelbräde delat på två liggande A4.
- Båda sidorna använder nu samma bakgrundsfärg från en gemensam A3-SVG.
- Behöll platsrutor, transit-/vägrutor, Basläger och Förråd i exakt samma fysiska storlek.
- Ökade endast avstånden mellan komponenterna genom nya koordinater.
- Flyttade skarven till en horisontell korridor mellan nodgrupperna.
- Kompakt A4-version behålls oförändrad.
- Rensade äldre release- och outputfiler före build.


## v1.9.50 - Fysiskt speltest: tydlighet och större spelplan

- Lade till fyra handlingsmarkörer för att visa återstående handlingar under en aktivering.
- Förtydligade Kontrollera spelstatus med milstolpar, scenariohändelser och vinstkontroll.
- Händelsevägar byts till Öppen efter att färdhändelsen lösts.
- Utökade det gemensamma vägmarkeringsarket med fler Hinder- och Händelse-markörer utan att ändra något scenarios valda sammansättning.
- Enhetlig Ö-symbol används för öppna vägar; separat öppen-variant togs bort.
- Förtydligade Klätterrepets timing och att platskortseffekter normalt bara löses vid utforskning.
- Rättade kompaktbrädet till äkta A4 och lade till en primär tvåsidig 2xA4-spelplan med större avstånd mellan komponenterna.
- Skadereglerna är oförändrade; observationen följs upp i kommande speltest.

# v1.9.49 – Adaptiv genvägsagent

- Lade till agenten `adaptive_agent`.
- Agenten jämför säker väg med väg som får använda dolda genvägar.
- Dold väg väljs endast när den beräknade besparingen är minst två handlingar.
- Tröskel och riskpremie är konfigurerbara i agentprofilen.
- Lade till mätvärdet `adaptive_hidden_choices` i simulatorresultat och agentjämförelser.
- Lade till regressionstester för val, avstående och resultatexport.

# v1.9.48 – Transitnoder

- Lade till T1–T4 på vägarna 1–3, 2–5, 3–6 och 5–6.
- Flyttade plats 3 och 5 uppåt för bättre fysisk layout.
- Delade berörda vägar i två segment med gemensamt `route_id`.
- Lade till separat komponentfamilj och printark för transitbrickor.
- Förberedde simulatorn för blockerade transitnoder och entiteter på transitnoder.
- Lade till validering och tester.

# Changelog

## v1.9.47 – Omfattningsmodell och tydligare printfiler

- Införde tre uttryckliga omfattningsnivåer: `core`, `environment` och `scenario`.
- Flyttade Ökenreläets återanvändbara utrustning och färdhändelser till `data/environments/desert/`.
- Märkte kortlekar och komponentkällor med `scope.level` och vid behov `scope.id`.
- Delade scenariohändelserna i en komplett PDF per scenario.
- Införde scenarionamn först i scenariospecifika PDF-filer.
- Märkte gemensamma vägbrickor, karaktärskort, utrustning och färdhändelser som gemensamma printfiler.
- Behöll målobjekt och platskort som scenariospecifika.
- Uppdaterade printpaketets manifest och namn till aktuell version.
- Äldre releaser och inaktuell output tas inte med i distributionszippen.

## v1.9.46 – Tydligare scenarioark och enhetliga milstolpar

- Radbryter långa rader i Förberedelser, inklusive Dolda vägbrickor.
- Skriver ut `karaktärer` och `uthållighet` och använder `verktyg` i stället för `startverktyg`.
- Flyttar fördelning av verktyg och placering i Baslägret till regelboken.
- Byter scenarioarkens rubriker till `Egen hög` och `Blanda med övriga`.
- Tar bort antal efter kortgrupper när samtliga kort redan listas.
- Formulerar milstolpar som att en namngiven scenariohändelse inträffar.
- Gör vägöppningarna till riktiga scenariohändelser; flera händelser kan inträffa vid samma milstolpe i listordning.
- Breddar radbrytningen i Vinst-rutan.
- Utökar regressionstesterna för scenarioark och samtidiga scenariohändelser.
- Inga balansvärden har ändrats.

## v1.9.45 – Scenarioarkets dolda vägkomponenter

- Gjorde Förberedelser-rutan två textrader högre.
- Lade till raden `Dolda vägbrickor` med antal öppna, hinder och händelser.
- Behöll separat rad med scenariots D-vägar.
- Lade scenario-specifik `hidden_road_marker_pool` i register och scenariokällor.
- Uppdaterade regelboken med generell blandnings- och placeringsprocedur.
- Uppdaterade simulatorn till att dra från scenariots specificerade pool.
- Lade till regressionstester för datasync, fysisk bricktäckning, regeltext och scenarioark.

## v1.9.44 – Scenariovalda dolda vägar

- Konverterade väg 1–4 och 2–4 till permanenta D5 och D6.
- Alla D1–D6 visar öppen väg på brädet när ingen bricka placeras.
- Station Nordanvind placerar dolda vägbrickor på D1, D2, D3, D5 och D6.
- Ökenreläet placerar dolda vägbrickor på D1, D2, D3 och D4.
- Utökade den fysiska vägbrickepoolen till 3 öppna, 2 hinder och 1 händelse.
- Scenarioarksgeneratorn använder scenariofilens D-lista; ingen text om övriga vägar krävs.
- Lade till tester för D-id:n, scenarioselektion, källsynk och fysisk bricktäckning.

## v1.9.43 – Tydligare sessionsrapporter

- Lade till `scripts/generate_session_report.py`.
- Sessionsrapporter använder riktiga handlingsnamn från regelkällan.
- `målobjekt` ersätter tematiskt varierande termer som `fynd` i simulatorrapporten.
- Utforskning, dragna kort och utlösta scenariohändelser presenteras i spelordning.
- Läsbar Markdown och teknisk JSON-rålogg genereras separat.
- Drag utan platsbyte kan markeras som möjlig agentineffektivitet.
- Tre regressionstester skyddar rapportformat och händelseordning.
- Inga balansvärden ändrades.

## v1.9.42 – Synkroniserat scenarioregister

- Ökenreläets värden i `data/scenarios.yaml` har uppdaterats till 12 / 10 / 9.
- Simulatorn använder nu automatiskt samma startuthållighet som scenarioarket och scenariofilen.
- Nytt test verifierar att `data/scenarios.yaml` matchar respektive scenarios källfil.
- Inga andra balans- eller regeländringar.

## v1.9.41 – Ökenreläet: +2 startuthållighet

- Startuthålligheten i Ökenreläet har ökats:
  - 2 karaktärer: 10 → 12
  - 3 karaktärer: 8 → 10
  - 4 karaktärer: 7 → 9
- Ändringen är preliminär och ska verifieras i praktiskt speltest.
- Scenarioarket genereras om med de nya värdena.
- Äldre releasekataloger och tidigare genererad output tas bort före paketering.
- Inga andra balansvärden har ändrats.

## v1.9.40 – Korrigerad överföringsheuristik

- Kapacitetsbaserade överföringar utan mål har tagits bort.
- Målobjekt överförs endast till en närmare destination eller tydligt bättre bärare.
- Verktyg och Medicinväska överförs endast vid konkret behov.
- Fram-och-tillbaka-överföringar blockeras under nästa runda.
- Högst en strategisk överföring tillåts per aktivering.
- Överföringsorsak och historik loggas.
- Fem riktade tester har lagts till eller uppdaterats.
- Seed-matchad jämförelse: 30 seeds × 3 strategier × 2 versioner.
- Station Nordanvind med två karaktärer gav 50–60 % vinst för de tre uppdaterade agenterna.
- Genomsnittliga överföringar sjönk från 24,57–30,73 till 0,13–0,20 per spel.
- Inga scenarioregler eller balansvärden ändrades.

## v1.9.39 – Layoutsäkerhet

- Tvåradiga kortrubriker har flyttats ned för att inte överlappa kategorifältet.
- Symbolområdet flyttas ned på kort med tvåradig rubrik.
- Rubrikbrytning använder en viktad uppskattning av faktisk glyphbredd.
- A6-referensens SLUT-ruta har gjorts högre och delats upp i två textlinjer.
- Layouttester har lagts till för långa platsnamn och A6-rutan.
- `release/` rensas och innehåller endast aktuell version.
- `output/` rensas helt före slutlig build.
- Inga regler eller balansvärden har ändrats.

## v1.9.38 – Nybörjarflöde och första spelrundan

- A6-referensens Utforska-text har korrigerats.
- Platskort förbereds som en dold, id-sorterad rad.
- Regelboken beskriver exakt hur utrustningslek, färdhändelselek, målobjektslek och scenariohändelser förbereds.
- Scenarioarken anger vilka kort som blandas in och vilka som läggs separat.
- Skillnaden mellan att lämna och aktivera målobjekt förklaras.
- Station Nordanvind rekommenderas som första scenario.
- Ett steg-för-steg-exempel på första rundan har lagts till.
- Oväder anger uttryckligen uthållighetsförlust.
- `Kassera` används konsekvent på engångsutrustning.
- Kuriren använder termen `föremål`.
- Karaktärskort använder kategorin `Karaktärsförmåga`.
- Ökenreläets scenariohändelse `Sandstorm` har bytt namn till `Sandstormsvåg`.
- Startverktyg visas för alla spelarantal och delas ut i aktiveringsordning.
- Inga balansvärden har ändrats.

## v1.9.37 – Simulatorns regelbegränsningar

- Förhindrar handlingar vars kostnad överstiger återstående handlingar.
- Stoppar aktiveringen omedelbart när expeditionen förlorar.
- Prioriterar omedelbar förlust om vinst och förlust skulle inträffa samtidigt.
- Läser målobjektens ryggsäcksstorlek från målobjekts-YAML.
- Gör den generella Överföra-handlingen tillgänglig för målobjekt, verktyg och utrustning.
- Låter Medicinväskan läka en annan karaktär på samma plats.
- Modellerar `betala verktyg eller ta skada` som ett faktiskt agentval.
- Aktiverar Vattenreserv vid uthållighetsförlust från färdhändelse.
- Aktiverar Diagnosverktyg när ett målobjekt aktiveras.
- Lägger till åtta riktade simulatorregelkontrakt.
- Inga scenariobalansvärden har ändrats.

## v1.9.36 – Semantisk konsistenskontroll

- YAML, scenariofiler, regelbok, A6-referens och kortkällor har jämförts.
- Spelarvänd terminologi använder konsekvent **Scenariohändelse**.
- Handlingen benämns konsekvent **Aktivera målobjekt**.
- Förlust genom uthållighet beskrivs fysiskt som att expeditionen får slut på uthållighet eller att sista markören tas bort.
- Den inaktuella policyn för separata reparationsmarkörer har tagits bort.
- Inga mekanik- eller balansvärden har ändrats.

## v1.9.35 – Referens- och regelbokskorrigering

- Handlingen **Aktivera målobjekt** har lagts till på A6-referensarket.
- Den separata raden om kassationen har tagits bort från avsnittet **Ryggsäck och föremål**.
- Kassation av engångsutrustning beskrivs fortsatt under **Använd utrustning** och på respektive kort.
- Inga spelregler eller balansvärden har ändrats.
- `output/` rensas före slutlig build.

## v1.9.34 – Kortstandard och synlig spelstatus

- Långa platsnamn bryts automatiskt över två rader inom säkerhetszonen.
- Basläger och Förråd visar tydligt att deras effekter kräver respektive handling.
- Platskortens nederkant använder konsekventa, spelarvänliga funktionskategorier.
- Alla färdhändelsekort använder huvudtypen **Färdhändelse**.
- Alla målobjektskort använder huvudtypen **Målobjekt**.
- Ökenreläets reservmoduler anger att de aktiveras på en reläplats.
- Separata reparationsmarkörer och deras genererade utskriftsark har tagits bort.
- Aktiverad reläplats visas genom målobjektskortets placering och vridning.
- **Använd utrustning** och **Aktivera målobjekt** behålls som separata handlingar.
- `output/` rensas helt före ny build så bara aktuell output återstår.

## v1.9.33 – Tydlig utrustningsaktivering

- Ingenjören använder termen **handling** i stället för handlingspoäng.
- Teknikern hänvisar konsekvent till **engångsutrustning**.
- Utrustningskort anger om användningen kräver 1 handling eller ingen handling.
- Klätterrep används frivilligt när en färdhändelse löses och kasseras först när effekten används.
- Grundregeln för engångsutrustning är att kortet kasseras först när dess effekt faktiskt används.
- Regelbok, snabbstart, A6-referens, simulator och regel-täckningsmatris har synkats.
- Ingen balansändring har gjorts.

## v1.9.32 – Tydliga reläplatser i Ökenreläet

- De tre giltiga destinationerna benämns konsekvent **reläplatser**.
- Måltext och vinstvillkor använder **aktivera målobjekt** i stället för installera/reparera.
- Alla tre relevanta platskort visar etiketten **Reläplats** och instruktionen att ett målobjekt kan aktiveras där.
- Resursplatser använder de etablerade termerna **målobjekt** och **extra utrustning**.
- Interna id:n och simulatorlogik är oförändrade; ingen balansändring har gjorts.

## v1.9.31 – Scenarioark som tilläggsblad

- Tog bort standardrutan för Förlust från scenarioarken.
- Gjorde Vinst till en låg helbreddsruta längst ned.
- Ökade höjden för komponentrutan och Mål och progression.
- Bytte rubrik till `Lägg till för detta scenario`.
- Tog bort bashändelser och grundutrustning från scenarioarkens listor.
- Bytte `Scenarioutrustning` till `Extra utrustning`.
- Behöll `Extra färdhändelser` som parallellt begrepp.
- Uppdaterade regelbok och snabbstart med ansvarsfördelningen mellan basuppsättning och scenariotillägg.
- Inga spelregler eller balansvärden har ändrats.

## v1.9.30 – Scenarioarkens informationshierarki

- Slagit ihop Vinst och Förlust till en kompakt gemensam ruta.
- Ökat utrymmet för Mål och progression.
- Breddat komponentrutan och bytt rubrik till `Använd dessa kort och lekar`.
- Tagit bort synlig text om basprofil.
- Listar konkreta målobjekt direkt.
- Delar tydligt upp bashändelser, extra färdhändelser och scenariohändelser.
- Förhindrar klippning av vinst- och förlustvillkor.
- Inga spelregler eller balansvärden har ändrats.

## v1.9.29 – Korrigerad Markdown-rendering i PDF

- PDF-generatorn tolkar nu `**fetstil**`, `*kursiv*` och `` `kod` ``.
- Rubriker och punktlistor renderas utan synliga Markdown-markörer.
- Regelbok och övriga Markdown-baserade dokument har byggts om.
- Inga spelregler, komponentdata eller balansvärden har ändrats.


## v1.9.28 – Fysisk status och komponentplacering

### Ändrat
- Platsbrickor har dold baksida och utforskad framsida.
- Separata Okänd-markörer har tagits bort ur tokenkällan.
- Baslägerkort och Förrådskort har lagts till.
- Föremålsplacering vid platskort och karaktärskort är nu en kärnregel.
- `Aktivera målobjekt` ersätter den längre handlingsbenämningen.
- Dold väg avslöjas uttryckligen som del av `Flytta`.
- Spelarvänd terminologi använder `Scenariohändelse`; `Milstolpe` är triggern.
- Grundregler och snabbstart har uppdaterats.

### Tekniskt
- Regelschema och effektvokabulär omfattar den fysiska statusmodellen.
- Platsbrickegeneratorn skapar 12 fram- och 12 baksidor samt en tvåsidig PDF.
- Tokenantal och buildförväntningar har synkats.
- Inga balansvärden har ändrats.


## v1.9.27 – Nybörjarvänlig grundregelbok

- Grundregelboken har skrivits om i inlärningsordning.
- Scenarioark, kort, platsbrickor och vägmarkörer förklaras som ett sammanhängande system.
- Setup, rundordning och samtliga handlingar har fått stegvisa instruktioner.
- Exempelrunda och FAQ har lagts till.
- `docs/quickstart.md` är inte längre en platshållare.
- Inga spelregler eller balansvärden har ändrats.

# Changelog

## v1.9.26 – Regel-täckningsmatris

### Tillagt
- Strukturerad regelmatris i `data/rule-coverage.yaml`.
- Mänskligt läsbar rapport i `docs/rule-coverage-matrix.md`.
- JSON Schema för matrisen.
- Tre automatiska integritetstester för regelmatrisen.
- Strict-build-validering av regelmatrisens schema.

### Dokumenterat
- Fullt, delvis och icke-automatiserat regelstöd.
- Kopplingar mellan regelbok, YAML, spelmotor, simulator och tester.
- Prioriterade luckor för framtida testutbyggnad.

### Oförändrat
- Inga spelregler, scenarier, balansvärden eller printkomponenter har ändrats.

## Tidigare ändringar


## v1.9.25 – Simulator alignment

### Tillagt
- Scenarioeventdata i `GameResult`: antal event, kort-id, rundor, uthållighetsdelta och vägändringar.
- Detaljerad `scenario_event_log` i råa simuleringsresultat.
- `--scenario-events on off` i den seed-matchade experimentrunnern.
- Sammanfattningsmått för eventfrekvens och eventens uthållighetspåverkan.
- Tre simulatoralignment-tester.

### Ändrat
- Standardrapporter och CSV-export inkluderar scenarioeventmått.
- Dynamiska förbindelseexperiment grupperar resultat efter scenarioevent på/av.
- Ingen spelregel, balansprofil eller fysisk komponent har ändrats.

## Tidigare ändringar

## v1.9.24 – Arkitekturlås

- Låste scenarioeventens trigger- och effektvokabulär.
- Låste miljöleksformat `format_version: 1` med severity, tags och strukturerade effekter.
- Formaliserade fast upplösningsordning.
- Lade till `docs/scenario-event-architecture.md`.
- Formaliserade `place_matching_location_tile` som presentationslager.
- Rättade regelboksnumrering och vägkortstexter.
- Tog bort scenariobundna destinationsfooters från målobjektsgeneratorerna.
- Utökade schema och valideringsunderlag.

## v1.9.23 – Scenariomilstolpar och omedelbara scenarioevent, iteration 1

- Tog bort rundbaserade stormar, rundspårskälla och fysisk rundmarkör.
- Ersatte `relay_installed` med den generella triggern `objective_activated`.
- Lade till fasta milstolpar för hittade, slutförda och aktiverade mål.
- Lade till två miljöspecifika scenarioeventkort för Polarstation och två för Ökenmiljö.
- Begränsade första effektmodellen till omedelbar uthållighetsändring och direkt vägstatusändring.
- Lade till scenarioeventkortark, schema, motorstöd, tester, regeltext, A6-påminnelse och scenarioarksinformation.
- Scenarioevent löses direkt och behöver inte kommas ihåg efteråt.

## v1.9.22 - Platsbrickor, första prototyp

- Ändrade Plats 1-6 på spelbrädet från runda noder till fyrkantiga 30 x 30 mm brickplatser.
- Lade till datadriven SVG-mall för enkelsidiga platsbrickor.
- Lade till 12 platsbrickor: sex för Station Nordanvind och sex för Ökenreläet.
- Platsbrickorna visar endast platsnamn, scenario och ett kort id.
- Platskorten visar samma id på framsidan.
- Lade till `location-tiles-a4-01.pdf` i build och komplett printpaket.
- Ingen baksida eller dold brickidentitet används i denna första version.
- Spelregler, scenarioflöde och balans är oförändrade.


## v1.9.21 – komponentlika vägstatusrutor och renare spelbräde

- spelbrädets D- och V-rutor matchar nu road markers-komponenternas 16 × 16 mm layout
- väg-id visas i övre högra hörnet utan att ersätta statusnamnet
- vägstatusförklaringar har tagits bort ur brädets legend
- rubrik, undertitel, rundspår och teknisk footer har tagits bort
- kartgeometri, scenariofunktion och balans är oförändrade

## [1.9.20] – 2026-07-16

- gett de fyra centrala specialvägarna spelar-id D1-D4
- ersatt tryckt frågetecken på D-vägar med Öppen-status och väg-id
- gjort D-vägar öppna i grundmodellen; scenario-setup avgör vilka som täcks av dolda markörer
- ersatt V-vägarnas neutrala id-ruta med tryckt Stängd-status och väg-id
- utökat road-markers-arket med 8 Öppen väg-markörer och 8 Stängd väg-markörer
- behållit fyra dolda utfallsmarkörer för D1-D4
- uppdaterat schema, regelbok, scenarioarksgenerator, brädgenerator och buildmanifest
- regenererat spelbräde, scenarioark, road-markers-PDF och komplett printpaket

## v1.9.19

- Lade till datadriven korsningsdefinition för V4 över V3.
- Brädgeneratorn ritar en liten bro på V4 och låter V3 passera visuellt under.
- Uppdaterade schema för `crossings` och byggde om spelbräde/printoutput.

## [1.9.18] – 2026-07-16
- flyttat V4-rutan åt höger för visuell balans mot V3-rutan
- lyft V3:s nedersta horisontella segment från y=238 mm till y=229 mm
- behållit V1, V2 och V4:s övriga linjedragning
- regenererat spelbräde, printpaket och releaseunderlag

## [1.9.17] – 2026-07-16
- dragit V1 horisontellt från vänster sida av Plats 3 och in horisontellt till vänster sida av Förrådet
- dragit V2 som spegelvänd motsvarighet på höger sida av Plats 5 och Förrådet
- dragit V3 från ovansidan av Plats 6 via en yttre vänsterkorridor och in vertikalt till Förrådets undersida
- lämnat V4 oförändrad
- regenererat spelbräde, printpaket och releaseunderlag

## [1.9.16] – 2026-07-16
- ersatt mjuka bågar för V1–V4 med vinklade, dubbelriktade anslutningskorridorer
- dragit potentiella vägar utanför platsnoder och ordinarie vägstruktur
- förstorat markörytorna från 14 × 14 mm till 16 × 16 mm
- utökat board-schemat med `path_points` för datadrivna polylinjer
- regenererat spelbräde, printpaket och releaseunderlag

# Changelog

## [1.9.15] – 2026-07-16

### Ändrat

- dragit V1–V4 som tydligare bågar utanför platsnoderna
- förstorat markörytan för potentiella vägar till 14 × 14 mm
- bytt scenariokortets innehållsruta till `KORT OCH LEKAR`
- lagt till namnlistor för platskort och målobjektskort på båda scenarioarken
- visat Ökenreläets kort som `MÅLOBJEKT · RESERVMODUL ×3`
- angett grundläggande respektive scenariospecifika händelselekar på scenarioarken
- normaliserat kartlegendens term från `Blockerad koppling` till `Dold vägmarkör`
- regenererat spelbräde, scenarioark och komplett printoutput
- förberett versionsren release v1.9.15

## [1.9.14] – 2026-07-16

### Scenariostyrd målarkitektur

- flyttat måldestination, slutförandedefinition, målantal och progression till scenario-YAML och scenarioark
- gjort målobjektskortens text scenariogenerisk; korten behåller ryggsäcksstorlek
- lagt generella regler för plocka upp, överföra, lämna och installera mål i grundregelboken
- tagit bort Ökenreläets scenariospecifika installationsavsnitt ur grundregelboken
- uppdaterat scenarioarkens sektion till `Mål och progression`
- standardiserat installation till 1 handling och lämning till 0 handlingar i grundreglerna
- uppdaterat simulator, schema och tvärfilsvalidering
- lagt kontroll som stoppar destinationer och installationsinstruktioner på målobjektskort
- regenererat printoutput och förberett release v1.9.14

## [1.9.13] – 2026-07-16

### Konsistenskorrigering

- gjort startuthållighet scenariostyrd i grundregelboken
- gjort grundregelbokens vinstvillkor scenariogeneriskt
- rättat numrering i förberedelser och uthållighetsfas
- normaliserat terminologin för dolda vägar och potentiella scenariovägar
- rättat A6-referensens uthållighetsfas och slutvillkor
- uppdaterat A6-referensens versionsmärkning till v1.9.13
- rättat singularformen `Ryggsäck: 1 plats` i Ökenreläets kortgenerator
- inaktiverat den äldre tekniska prototypkortspipelinen i aktiv build
- uppdaterat printpaketets manifestversion
- förberett en korrigerad release v1.9.13

## [1.9.12] – 2026-07-16

### [PLAN] Prompt 6 – scenariointegration, playtest och release

- aktiverat V1 efter första och V2 efter andra levererade målobjektet i Station Nordanvind
- satt Station Nordanvinds första fysiska testprofil till 11/9/8 uthållighet
- aktiverat V4 efter första och V2 efter andra installerade reläet i Ökenreläet
- behållit Ökenreläets uthållighet som kontroll tills fysisk verifiering
- lagt till playtestguide för dynamiska förbindelser
- lagt till dokumenterat simulator- och balansunderlag
- uppdaterat README och PROJECT_STATUS
- förberett versionsren release v1.9.12

## [1.9.11] – 2026-07-16

### [PLAN] Prompt 5 – spelbräde, markörer och regelmaterial

- renderat V1-V4 som svagt streckade potentiella vägar med spelarvänliga väg-id:n
- utökat spelbrädets legend med symbol för stängd potentiell väg
- lagt till tre Öppen väg-markörer för scenarioaktiverade förbindelser
- uppdaterat vägmarkörsarket och dess produktionsinstruktion
- uppdaterat A6-referenskortet med V1-V4 och Öppen-markör
- lagt till regelavsnitt om potentiella scenariovägar
- rättat regelbokens standarduthållighet till 13 / 11 / 10 och tagit bort äldre startverktyg
- lämnat huvudscenariernas progression och balans oförändrade

Alla betydande ändringar i projektet dokumenteras här.

## [1.9.10] – 2026-07-16

### [PLAN] Prompt 4 – simulatorstöd och balansunderlag

- lagt till mätning av dynamiska vägpassager och öppningsrundor per spel
- utökat simuleringsresultat med progressionsevent och connection-metadata
- lagt till agentvärdering för `choose_connection` baserad på publik runtime-information
- infört tie-breaker-lägena `left`, `right` och `random` för lika långa utforskningsvägar
- lagt till `simulation/run_dynamic_connection_experiments.py`
- experimentrunnern stödjer seed-matchade varianter, flera uthållighetsnivåer och båda scenarierna
- genererar rådata och sammanfattning som CSV, JSON och Markdown
- lagt till tre simulatorrelaterade tester; totalt 15 tester godkända
- kört en rökmatrix med 840 spel; resultatet är endast teknisk verifiering, inte balansunderlag
- lämnat huvudscenariernas progression, uthållighet och printlayout oförändrade

## [1.9.9] – 2026-07-16

### [PLAN] Prompt 3 – progression events och scenariohändelser

- lagt till valfri `progression_events` i scenariopaketens schema
- implementerat triggers för `objective_completed`, specifikt `objective_id`, `relay_installed` och `custom_event`
- implementerat effekterna `open_connection`, `seal_connection` och `choose_connection`
- stödjer flera vägändringar från samma händelse
- lagt till runtime-logg och skydd mot att samma progressionsevent utlöses flera gånger
- kopplat progression till både levererade målobjekt och installerade relämoduler
- lagt till integrationstester utan att aktivera progression i huvudscenarierna
- lämnat balans, spelbräde och printoutput oförändrade

## [1.9.8] – 2026-07-16

### [PLAN] Prompt 2 – runtime-state och pathfinding

- infört `connection_states` som gemensamt runtime-tillstånd för alla förbindelser
- behållit `road_state` som bakåtkompatibelt alias för befintlig doldvägslogik
- låtit adjacency innehålla all kartgeometri medan pathfinding filtrerar på aktuellt tillstånd
- lagt till `get_connection_state`, `set_connection_state`, `is_connection_traversable`, `open_connection` och `seal_connection`
- uppdaterat slumpmässig rörelse så att stängda och förseglade vägar inte väljs
- lagt till `GameEngine.create_game` för tester och framtida scenarioevents
- lagt till automatiska runtime- och pathfindingtester
- bekräftat att V1–V4 förblir stängda i befintliga scenarier

### Avgränsning

- inga `progression_events` är ännu införda
- scenarier öppnar ännu inga vägar automatiskt
- V1–V4 renderas ännu inte i printoutput
- ingen balansprofil har ändrats

## [1.9.7] – 2026-07-16

### [PLAN] Prompt 1 – dynamiska förbindelser

- generaliserat kartans förbindelser med `category`, `default_state` och `printed_style`
- migrerat befintliga öppna och dolda vägar till den gemensamma modellen
- lagt till V1–V4 som stängda scenariovägar
- utökat JSON Schema och tvärfilsvalidering
- lagt till kontroller för unika etiketter, dubbla odirektionella vägar och tillståndskonsistens
- säkerställt att stängda scenariovägar inte påverkar nuvarande simulator eller genererad spelplan
- dokumenterat nuläge och avgränsning i `docs/design/dynamic-connections-current-state.md`

### Avgränsning

- inga vägar kan ännu öppnas under spel
- inga progression events eller scenarioöverskrivningar är införda
- V1–V4 renderas ännu inte på spelbrädet
- ingen uthållighets- eller balansprofil har ändrats

## [1.9.6] – 2026-07-15

### Balans

- Station Nordanvinds standarduthållighet ändrad till 13 / 11 / 10 för 2 / 3 / 4 karaktärer
- startverktyg ändrat till 0 för samtliga spelarantal
- setupen styrs nu enbart av uthållighetsvärdet

### Underlag

Ändringen bygger på större fokuserade simuleringar i v1.9.5. Resultaten ska
fortfarande verifieras i fysiska speltest.

## [1.9.5] – 2026-07-15

### Simulator coverage

- implementerat Kartscanner, Vattenreserv och Diagnosverktyg
- implementerat Spejaren, Kuriren och Teknikern
- datastyrt utrustnings- och installationskostnader
- generaliserat överföring av mål, verktyg och utrustning
- infört dra-och-välj för karaktärer
- gjort scenariopaketen auktoritativa för vinstvillkor
- infört maskinläsbart täckningsregister
- strict build misslyckas vid saknad aktiv simulatoreffekt

## [1.9.4] – 2026-07-15

### Konsoliderat

- generell `mission.completion` för leverans- och installationsuppdrag
- explicit `deck_composition` för bas- och scenariokort
- formell policy för baskomponenter och scenarioutökningar
- simulatorn använder uppdragsmodellen i stället för scenariounika typnamn
- validatorn upptäcker och kontrollerar scenarier via scenarioindexet
- validering av målkort, destinationer, platstaggar och scenariomarkörer

### Dokumenterat

- vilka kort och komponenter som hör till basuppsättningen
- vilka komponenter som är scenarioutökningar
- krav för framtida scenarier

### Slutfört

- v1.9 Del 1–4 är genomförda

## [1.9.3] – 2026-07-15

### Tillagt

- `scripts/run_scenario_comparison.py`
- explicit scenarioval i den gemensamma agentmotorn
- automatiska körningar för alla scenarier och spelarantal
- gemensam seedserie mellan scenarier och agenter
- sammanfattning per agent och strukturerad agentgrupp
- Markdown-, JSON- och CSV-rapporter
- rådata för varje simulerat spel
- scenariojämförelse som eget buildmål

### Avgränsning

Del 4 – konsolidering av bas- och scenariomodellen återstår.

## [1.9.2] - 2026-07-15

### Tillagt
- Scenario 02 Ökenreläet
- sex ökenplatser och tre reservmoduler
- Vattenreserv och Diagnosverktyg
- Sandstorm, Extrem hetta och Navigationsfel
- tre Reparerad-markörer
- Installera modul som scenariounik handling
- simulatorstöd för mål som installeras ute på kartan
- A5-scenariokort och tre nya A4-komponentark

### Avgränsning
Del 3 och Del 4 återstår.
## [1.9.0] – 2026-07-15

### Arkitektur

- flyttat grundutrustning till `data/base/equipment.yaml`
- flyttat grundläggande färdhändelser till `data/base/travel-events.yaml`
- flyttat Station Nordanvind till `data/scenarios/station-nordanvind/`
- scenariopaket och basprofil deklarerar nu exakta källfiler
- simulatorn laddar scenario- och baskällor dynamiskt
- validatorn verifierar källor, set-id:n och katalogstruktur

### Namnändringar

- Signalboj heter nu Kartscanner
- Nödbatteri heter nu Extra förnödenheter

### Avgränsning

Versionen omfattar v1.9 Del 1. Scenario 02 och jämförande scenariosimulering
återstår till följande delar.

## [1.8.1] – 2026-07-15

### Korrigerat

- tvåkaraktärslägets startverktyg tillämpas nu i simulatorn
- agentmotorn skapar setup med rätt karaktärsantal från början
- 3–4-karaktärslägen använder därmed rätt startuthållighet
- samarbetsstudien skriver inte längre om `simulation.yaml` under körning

### Tillagt

- scenariostyrd laddning via scenarioindex och scenariopaket
- kontroll av basprofil, platsset och målset
- scenario- och setupmetadata i JSON- och CSV-rapporter
- deterministisk placering av startverktyg
- regressionskontroll mot v1.8 med neutraliserad setupbonus

### Regressionsresultat

När startverktyget sattes till 0 gav v1.8 och v1.8.1 identiska utfall för samma
seeds på samtliga jämförda spelmått. Mekaniska skillnader efter korrigeringen är
därmed avsedda setupskillnader.

## [1.8.0] - 2026-07-15

### Tillagt

- basprofilmodellen i `data/base-profiles.yaml`
- scenariopaketet `data/scenarios/station-nordanvind/scenario.yaml`
- schemas för basprofiler och scenariopaket
- A5-mall för scenariokort
- generator för Station Nordanvind
- A4-utskriftsark med skärmarkeringar
- A5- och A4-PDF för scenariot
- korsvalidering av basprofil, scenarioindex, platslek och mållek

### Ändrat

- Första expeditionen heter nu Station Nordanvind
- platsleken och målleken är namngivna efter scenariot
- Rasgruvan heter Rasade servicegångar
- regelbok och monteringsguide hänvisar till scenariokortet
- printpaketet innehåller scenariots A4-utskriftsark

## [1.7.1] – 2026-07-15

### Ändrat

- vägmarkörernas etiketter är nu `Öppen`, `Hinder` och `Händelse`
- `Öppen` ersätter `Fri` för att tydliggöra att vanlig förflyttningshandling fortfarande krävs
- regler och referenskort använder `Ta bort Hinder`
- Ingenjörens förmåga använder samma terminologi
- aktiva dokument och printpaket versionshöjda till v1.7.1

### Rensat

- äldre regelböcker och versionerade monterings-/playtestdokument
- den inaktuella vikbara vägmarkörsmallen
- äldre preflightfiler, previews och annan inaktuell genererad output
- hela outputträdet byggdes om från aktuella källor

## [1.7.0] – 2026-07-15

### Ändrat

- ersatt vikbara vägmarkörer med enkelsidiga markörer
- satt vägmarkörernas mått till 16 × 16 mm
- satt spelbrädets vägmarkörsytor till 16 × 16 mm
- uppdaterat generator, SVG-mall, A4-ark och monteringsguide
- dold information hanteras genom att den otryckta sidan ligger uppåt

## [1.6.0] – 2026-07-15

### Balanserat

- ändrat normal uthållighetsprofil från 12/10/8 till 10/8/7
- behållit ett startverktyg för två karaktärer
- behållit noll startverktyg för tre och fyra karaktärer

### Simuleringsunderlag

Med 30 körningar per strategi gav den nya profilen ungefär:

- 50,0 % vinst för två karaktärer
- 47,5 % vinst för tre karaktärer
- 57,5 % vinst för fyra karaktärer

Resultaten avser strukturerade simulatoragenter och ska verifieras fysiskt.

### Uppdaterat

- scenario-YAML
- regelbok och playtestdokument
- referenskortets versionsinformation
- projektstatus och README
- build- och printpaketsvägar

## [1.5.0] – 2026-07-15

### Ändrat

- ersatt hotspåret med en nedräknande uthållighetspool
- tagit bort hotindikatorn från spelbrädet
- ersatt hotmarkören med tolv uthållighetsmarkörer
- ändrat Hotfas till Uthållighetsfas
- ändrat hotökningar till förlust av uthållighet
- ändrat Extra förnödenheter till att återställa uthållighet
- infört setupskalning 12/10/8 för 2/3/4 karaktärer
- infört ett startverktyg för två karaktärer
- uppdaterat simulatorer och rapportmått till uthållighet
- uppdaterat regelbok, A6-referens, tokenark och printpaket

### Balanssignal

Första simuleringarna visar att 12/10/8 sannolikt är för generöst. Värdena är markerade som testprofil och ska kalibreras vidare.

## [1.4.0] – 2026-07-15

### Tillagt

- `engine/game_engine.py`
- `agents/base.py`
- `agents/standard.py`
- `simulation/run_agent_comparison.py`
- fem separata agenttyper
- agentjämförelse med gemensam spelmotor och samma seeds
- `docs/simulator-architecture.md`
- rapporter för 2, 3 och 4 karaktärer

### Arkitektur

Alla agenttyper använder samma regelimplementation, spelplan, kortpooler och YAML-data. Endast agenternas beslutsprofiler skiljer.

### Begränsning

Spelmotorn kapslar tills vidare den äldre simulatorns regelimplementation. Full action/state-uppdelning återstår.

## [1.3.0] – 2026-07-15

### Tillagt

- `data/cooperation-ablation.yaml`
- `schemas/cooperation-ablation.schema.json`
- `scripts/run_cooperation_ablation.py`
- fyra samarbetslägen
- kontrollerade jämförelser med samma seeds
- profiler för 2, 3 och 4 karaktärer
- mätning av ruttkoordination, överföringar och överföringskostnad
- `docs/cooperation-ablation.md`
- ablationsrapporter i JSON, CSV och Markdown
- build- och validatorintegration

### Designprincip

Ablationerna ändrar en samarbetsnivå åt gången för att skilja värdet av gemensam planering från värdet av fysisk överföring.

## [1.2.0] – 2026-07-14

### Tillagt

- `data/simulation.yaml`
- `schemas/simulation.schema.json`
- `scripts/simulate_game.py`
- fem agentstrategier
- seedstyrda Monte Carlo-körningar
- statistik för vinst, rundor, uthållighet, mål, skada, vägar, verktyg, kapacitet och utrustning
- JSON-, CSV- och Markdown-rapporter
- `docs/simulator.md`
- simulatorsteg i den gemensamma builden

### Rättat

- scenariots stormeffekt refererade fortfarande till borttagen Proviant
- stormen förbrukar nu endast 1 ytterligare uthållighet

### Designprincip

Simuleringar är hypoteser och jämförelseverktyg, inte facit eller ersättning för fysiska speltest.

## [1.1.0] - 2026-07-14

### Konsoliderat

- spelterminologin mellan regler, YAML och kort
- rundordningen till Spelarfas, Underhåll, Uthållighetsfas
- fast aktiveringsordning med visuell kortvridning
- uthållighetsförlust till slutet av rundan
- korttypsrubriker på Plats och Färdhändelse
- A6-referenskortets textpassning och innehåll

### Terminologi

- `Verktyg` är enda generella markören.
- `Utrustning` är kort med användning eller passiv effekt.
- `Målobjekt` är transportkort och kan inte användas.
- `Buret innehåll` omfattar verktyg, utrustning och målobjekt.
- äldre speltermer `resurs` och `föremål` tillåts inte i aktiv spelarinriktad korttext.

### Validering

- kontrollerar fasordning
- kontrollerar fast medsols aktiveringsordning
- kontrollerar att uthållighet förloras i slutlig Uthållighetsfas
- kontrollerar förbjuden äldre terminologi i aktiv korttext

## [1.0.0] – 2026-07-14

### Tillagt

- åtta asymmetriska karaktärer
- personlig ryggsäckskapacitet
- `data/characters.yaml`
- `data/equipment.yaml`
- `data/objectives.yaml`
- `data/inventory.yaml`
- schemas för samtliga nya datatyper
- sex utrustningskort
- tre separata målobjektskort
- generator och A4-ark för karaktärskort
- generator och A4-ark för utrustning och mål
- v1.0-regelbok, monteringsguide och playtestguide

### Ändrat

- verktyg är nu den enda generella resursen
- proviant, medicin och kunskap har tagits bort som resursmarkörer
- hälsa hanteras per karaktär
- målobjekt tar två ryggsäcksplatser
- utrustning tar normalt en plats
- `Använd föremål` gäller endast användbar utrustning
- målobjekt kan inte användas
- platskort drar separata mål- eller utrustningskort
- Förrådet innehåller fyra verktyg för den nya prototypen
- tokenantalet minskat och fokuserats
- printpaketet uppdaterat med nya kortark

### Designbeslut

- inga stora spelarmattor i första versionen
- inga Tetrisformer i ryggsäcken
- inventarier läggs öppet bredvid vanliga 63 × 88 mm-karaktärskort
- kapacitet räknas som ett enkelt antal platser
- målobjekt är transportuppdrag, inte föremål med effekter

### Ej genomfört

- fysisk utskrift
- fysisk solo-omgång
- fysisk samarbetsomgång

## [0.9.0] – 2026-07-14

### Omdesign

- Basläger och Förråd är nu fasta platser.
- Förrådet innehåller tre garanterade verktyg.
- Sex övriga platser är numrerade och dolda.
- Tre av sex platskort innehåller målobjekt.
- Ledtrådssystemet ingår inte i grundspelet.
- Alla platser är nåbara via öppna huvudvägar.
- Fyra okända genvägar använder dolda vägmarkörer.
- Vägutfall: två öppna, en blockerad och en färdhändelse.
- Färdhändelser ersätter termen farokort.

### Tillagt

- `data/locations.yaml`
- `data/road-markers.yaml`
- `data/travel-events.yaml`
- schemas för de tre nya datatyperna
- omarbetad nodkarta med fasta och numrerade platser
- sex platskort
- sex färdhändelsekort
- fyra vikbara vägmarkörer
- generatorer och A4-ark för de nya komponenterna
- v0.9-regelbok och monteringsguide
- komplett v0.9-printpaket

### Ändrat

- projektversion höjd till 0.9.0
- scenario-, regel- och referensdata uppdaterade
- boardgeneratorn visar okända genvägar
- buildmanifestet bygger och verifierar nya komponenttyper

### Ej genomfört

- fysisk utskrift
- fysisk solo-omgång
- fysisk samarbetsomgång

## [0.8.0] – 2026-07-14

### Tillagt

- `data/scenarios.yaml`
- `schemas/scenarios.schema.json`
- sex Okänd-markörer
- totalt 35 markörer
- testregler för utforskning, mål, blockerad väg och hotfas
- `docs/rulebook-playtest-v0.8.md`
- `docs/assembly-guide-v0.8.md`
- `docs/playtest-guide.md`
- `docs/playtest-form-v0.8.md`
- uppdaterad `docs/playtest-log.md`
- `scripts/generate_playtest_docs.py`
- `scripts/assemble_print_package.py`
- PDF-regelbok, monteringsguide och testformulär
- sammanslaget komplett printpaket
- digital solo-regelgenomgång
- digital samarbetsgenomgång

### Ändrat

- projektversion höjd till 0.8.0
- tokenantal höjt från 29 till 35
- builden utökad med måltypen `prototype`
- validatorn utökad för scenarioreferenser
- requirements kompletterade med ReportLab och pypdf
- README och projektstatus uppdaterade

### Designbeslut

- första fysiska testet använder deterministisk hotfas
- ingen tärning används
- tre målobjekt placeras på fasta platser
- okända platser markeras med fysiska frågetecken
- digitala genomgångar behandlas som hypoteser, inte fysiska speltest

### Ej genomfört

- fysisk utskrift och montering
- fysisk solo-omgång
- fysisk samarbetsomgång

## [0.7.0] – 2026-07-14

### Tillagt

- manifeststyrd `scripts/build_all.py`
- byggsteg i `data/project.yaml`
- deklarerade outputs och output-globbar
- säker output-rensning
- målbaserad build med `--target`
- `--clean`, `--no-clean` och `--strict`
- SHA-256 för källor och genererad output
- buildtid och status per steg
- `output/build-manifest.json`
- `output/build-report.md`
- `output/build-log.txt`
- `docs/build-system.md`

### Ändrat

- projektversion höjd till 0.7.0
- `project.schema.json` utökad för buildmanifestet
- gemensam build är inte längre en hårdkodad skriptlista
- projektstatus och README uppdaterade

### Designbeslut

- `project.yaml` är källa för buildordning och aktiverade mål
- builden avbryts vid första fel
- manifest och rapport skrivs även vid misslyckad build
- källor och output får checksummor för reproducerbarhet
- PDF-rendering hålls som separat verifieringssteg

## [0.6.0] - 2026-07-14

### Tillagt

- `data/tokens.yaml`
- `data/layouts/token-standard.yaml`
- `data/print-layouts/tokens-a4.yaml`
- schemas för tokens, layout och printlayout
- `templates/tokens/square-token.svg.j2`
- `scripts/generate_tokens.py`
- `scripts/build_token_sheet.py`
- `scripts/export_token_pdf.py`
- 29 genererade token-SVG
- A4-tokenark som SVG och PDF
- `docs/tokens.md`

### Ändrat

- tokenkomponenten aktiverad
- projektversion höjd till 0.6.0
- validatorn utökad med token-set, resurser, spår och målantal
- `build_all.py` bygger nu kort, bräde, referenskort och tokens
- status-, pipeline- och produktionsdokumentation uppdaterad

### Designbeslut

- fyrkantiga tokens används för enkel hemmaklippning
- ink-friendly layout är standard
- tre målmarkörer matchar vinstvillkoret
- skade- och blockeradmarkörer inkluderas tills speltest visar om de behövs

## [0.5.0] - 2026-07-14

### Tillagt

- `data/reference-cards.yaml`
- `data/layouts/reference-a6.yaml`
- `data/print-layouts/reference-a4.yaml`
- schemas för referenskort, layout och printlayout
- `templates/reference/a6-reference.svg.j2`
- `scripts/generate_reference_cards.py`
- `scripts/build_reference_sheets.py`
- `scripts/export_reference_pdf.py`
- A6-SVG och A6-PDF
- A4 4-up SVG och PDF
- `docs/reference-card.md`

### Ändrat

- referenskortskomponenten aktiverad
- projektversion höjd till 0.5.0
- validatorn utökad med ruleset-, template- och sektionskontroller
- `build_all.py` bygger nu kort, bräde och referenskort
- status-, pipeline- och produktionsdokumentation uppdaterad

### Designbeslut

- faser, handlingar och slutvillkor genereras från `rules.yaml`
- presentationsdata hålls separat från regelkällan
- symbolförklaringar härleds från spel- och bräddata

## [0.4.0] - 2026-07-14

### Tillagt

- `data/board.yaml`
- `data/layouts/board-standard.yaml`
- `data/print-layouts/board-a4.yaml`
- `schemas/board.schema.json`
- `schemas/board-layout.schema.json`
- `templates/boards/node-map.svg.j2`
- `scripts/generate_board.py`
- `scripts/export_board_pdf.py`
- åtta platser och nio kopplingar
- uthållighetspool och rundspår
- `docs/board-design.md`
- genererad bräd-SVG och A4-PDF

### Ändrat

- brädkomponenten aktiverad i `project.yaml`
- projektversion höjd till 0.4.0
- validatorn utökad med brädets referenser och koordinater
- `build_all.py` bygger nu både kort och spelbräde
- pipeline-, produktions- och statusdokumentation uppdaterad

### Kända begränsningar

- ingen automatisk layoutkollision
- ingen färdig spelregel för blockerad koppling
- ingen speltestad kartbalans

## [0.3.0] - 2026-07-14

### Tillagt

- `data/cards.yaml` med tre testkort
- `data/layouts/card-standard.yaml`
- `data/print-layouts/cards-a4.yaml`
- `schemas/cards.schema.json`
- `schemas/card-layout.schema.json`
- `schemas/print-layout.schema.json`
- SVG-ikoner för sökning, storm och medicin
- `templates/cards/standard.svg.j2`
- `scripts/generate_cards.py`
- `scripts/build_card_sheets.py`
- `scripts/export_pdf.py`
- `scripts/build_all.py`
- `docs/pipeline.md`
- genererade kort-SVG
- A4-SVG och PDF
- build-manifest

### Ändrat

- kortkomponenten aktiverad i `project.yaml`
- projektversion höjd till 0.3.0
- validatorn utökad för kort, layouts, ikoner och korteffekter
- requirements kompletterade med Jinja2 och CairoSVG
- projektstatus och produktionsguide uppdaterade

### Kända begränsningar

- enkel approximativ textpassning
- inga kortbaksidor eller PNG-bakgrunder
- ett enda A4-ark och kortformat

## [0.2.0] – 2026-07-14

### Tillagt

- `data/project.yaml`
- `schemas/project.schema.json`
- `schemas/game.schema.json`
- `schemas/rules.schema.json`
- `scripts/validate_project.py`
- `requirements.txt`
- Semantisk tvärfilsvalidering
- Kontroll av resurser, spår, målobjekt och antal handlingar
- Kontroll av aktiverade och avstängda komponentkällor

### Ändrat

- Maskin-id:n normaliserade till ASCII för stabil schema- och scriptkompatibilitet.

- Projektstatus uppdaterad till Fas 2
- README kompletterad med valideringsinstruktion
- Schema- och scriptsdokumentation uppdaterad
- Projektversion höjd till 0.2.0

### Designbeslut

- JSON Schema hanterar filstruktur och lokala datakrav.
- Python-valideraren hanterar referenser och regler mellan filer.
- Datamodellen hålls avsiktligt begränsad tills kortpipelinen ger konkreta behov.

## [0.1.0] – 2026-07-14

### Tillagt

- Grundläggande projektstruktur
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/design-brief.md`
- `docs/game-overview.md`
- `data/game.yaml`
- `data/rules.yaml`
- Grundmappar för data, schemas, templates, assets, scripts och output

### Designbeslut

- Kooperativt spel för 1–4 spelare
- Solo stöds genom samma kärnregler
- Rekommenderad soloform är två karaktärer
- Nodbaserat A4-spelbräde
- Två handlingar per karaktär och runda
- Tre målobjekt krävs för vinst
- Hotspår används som primär förlusttimer
- Första komponentbudgeten hålls liten

### Ej genomfört ännu

- Kortpipeline
- Spelbrädesgenerator
- A6-referenskort
- Tokengenerator
- PDF-export
- Simulering
- Full regelbok