# Playtestlogg

## Test 001 - digital solo-regelgenomgång

### Version

v0.8.0

### Testtyp

Digital, deterministisk regelgenomgång. Inte ett fysiskt speltest.

### Testmål

Kontrollera om scenariot har en möjlig handlingssekvens och om resurser, mål, uthållighet och återresa kan lösas utan att uppfinna regler.

### Antaganden

- två karaktärer
- optimala, helt koordinerade val
- inga oförutsedda kort utöver storm på runda 3 och 6
- inga fysiska läsbarhets- eller monteringsproblem

### Resultat

En möjlig väg finns före uthållighet 10. Signaltornet används för att samla kunskap flera gånger, varefter gruppen kan säkra de tre fasta målobjekten och återvända till Baslägret.

### Observationer

- Scenariot är lösbart på regelplanet.
- Kunskap riskerar att bli en flaskhals med upprepad Samla-handling.
- Den blockerade vägen skapar ett faktiskt användningsområde för verktyg.
- Två karaktärer ger tillräcklig handlingsmängd men kan skapa optimeringsadministration.
- Den deterministiska uthållighetkurvan ger en hård tidsgräns vid början av runda 8.

### Beslut

1. Behåll deterministisk uthållighetfas i första fysiska testet.
2. Mät hur ofta Samla används på Signaltornet.
3. Ändra inte uthållighetvärden innan ett fysiskt solo-test genomförts.

## Test 002 - digital samarbetsgenomgång

### Version

v0.8.0

### Testtyp

Digital rollfördelningsgenomgång för två spelare. Inte ett fysiskt speltest.

### Testmål

Kontrollera att två karaktärer kan dela upp vägar och att Hjälpa har en möjlig funktion.

### Resultat

Karaktärerna kan dela upp sig mellan norra och östra grenen, men behöver samordna kunskap och verktyg. Hjälpa blir relevant om resurser hamnar på fel karaktär eller om skada behöver läkas.

### Observationer

- Samarbetsbehov finns, men helt öppen information kan uppmuntra en dominant spelare.
- Resursöverföring kräver att karaktärerna möts, vilket kan kosta mycket transport.
- Fysiskt test måste mäta väntetid och faktisk diskussion; detta kan inte avgöras digitalt.

### Beslut

1. Behåll fri aktiveringsordning.
2. Observera alfa-spelarproblemet specifikt.
3. Ändra inte Hjälpa förrän spelarna faktiskt försökt använda handlingen.


## Fysiskt solotest - två karaktärer, v1.9.49
- Handlingsföljden var lätt att tappa bort när en handling ledde till kortdragning.
- Kontrollera spelstatus behöver uttryckligen nämna milstolpar och scenariohändelser.
- Skada upplevdes som lågprioriterad. Ingen regeländring görs ännu; fortsatt observation krävs.
- Händelsevägar bör bli Öppna efter att färdhändelsen lösts.
- Kompaktbrädet är användbart i prototypstadiet men för trångt för bekväm hantering. Primärt testformat blir 2xA4.
