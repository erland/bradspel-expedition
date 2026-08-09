# Vinnande spelsession – Station Nordanvind

> Detta är en återgivning av en faktisk deterministisk simulatorkörning. Tankarna är simulatoragentens beslutsmotiveringar, inte ord från en verklig spelare.

## Testdata

- Version: **Expedition v1.9.42**
- Scenario: **Station Nordanvind**
- Karaktärer: **Bäraren och Läkaren**
- Strategi: **Närmaste okända plats**
- Seed: **600000**
- Startuthållighet: **11**
- Resultat: **Vinst i runda 7**
- Uthållighet vid vinst: **1**
- Återförda fynd: **3 av 3**

## Hur agenten prioriterar

1. Utforska den närmaste okända platsen.
2. Ta ett verktyg tidigt när strategin bedömer att det behövs.
3. När ett fynd bärs, återvänd direkt mot Baslägret.
4. Lämna fyndet omedelbart när Baslägret nås.
5. Fortsätt utforska tills tre fynd har återförts.

## Spelsession, drag för drag

## Runda 1

**Rundstart:** Runda 1 börjar med 11 uthållighet.

### Bäraren

Bäraren börjar på Basläger med 0 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Bäraren flyttar Basläger → Förråd.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 1.
- **Handling:** Bäraren tar ett verktyg och har nu 1.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 1.
**Aktiveringen slutar:** Bäraren avslutar på Förråd. Uthållighet: 11.

### Läkaren

Läkaren börjar på Basläger med 0 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Basläger → Förråd.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 1.
- **Handling:** Läkaren tar ett verktyg och har nu 1.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 1.
**Aktiveringen slutar:** Läkaren avslutar på Förråd. Uthållighet: 11.

## Runda 2

**Underhåll:** Rundslutet har minskat uthålligheten till 10.
**Rundstart:** Runda 2 börjar med 10 uthållighet.

### Bäraren

Bäraren börjar på Förråd med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Bäraren flyttar Förråd → Plats 1.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 1.
- **Scenariohändelse:** Scenariohändelsen **Stormfront** löses ut: uthållighet -1.
- **Kort/utforskning:** Fyndkortet **Medicinskt prov** dras och bärs direkt.
- **Kort/utforskning:** Bäraren utforskar Plats 1 och vänder **Rasade servicegångar**: uthållighet 10 → 9; skada 0 → 1; ett fynd hittas.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
**Aktiveringen slutar:** Bäraren avslutar på Plats 1. Uthållighet: 9.

### Läkaren

Läkaren börjar på Förråd med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Förråd → Plats 2.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 2.
- **Kort/utforskning:** Läkaren utforskar Plats 2 och vänder **Stormzonen**: uthållighet 9 → 7.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
**Aktiveringen slutar:** Läkaren avslutar på Plats 2. Uthållighet: 7.

## Runda 3

**Underhåll:** Rundslutet har minskat uthålligheten till 6.
**Rundstart:** Runda 3 börjar med 6 uthållighet.

### Bäraren

Bäraren börjar på Plats 1 med 1 verktyg, 1 fynd och 2 hälsa.
- **Handling:** Bäraren flyttar Plats 1 → Förråd.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Handling:** Bäraren flyttar Förråd → Basläger.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Milstolpe:** Bäraren lämnar **Medicinskt prov** i Baslägret. Progress: 1/3.
  - *Agentens tanke:* Fyndet har nått destinationen och lämnas omedelbart.
**Aktiveringen slutar:** Bäraren avslutar på Basläger. Uthållighet: 6.

### Läkaren

Läkaren börjar på Plats 2 med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Plats 2 → Plats 4.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 4.
- **Handling:** Läkaren flyttar Plats 4 → Plats 1.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 4.
**Aktiveringen slutar:** Läkaren avslutar på Plats 1. Uthållighet: 6.

## Runda 4

**Underhåll:** Rundslutet har minskat uthålligheten till 5.
**Rundstart:** Runda 4 börjar med 5 uthållighet.

### Bäraren

Bäraren börjar på Basläger med 1 verktyg, 0 fynd och 2 hälsa.
- **Handling:** Bäraren flyttar Basläger → Förråd.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 3.
- **Handling:** Bäraren flyttar Förråd → Plats 3.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 3.
**Aktiveringen slutar:** Bäraren avslutar på Plats 3. Uthållighet: 5.

### Läkaren

Läkaren börjar på Plats 1 med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Plats 1 → Plats 3.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 3.
- **Kort/utforskning:** Fyndkortet **Forskningsserver** dras och bärs direkt.
- **Kort/utforskning:** Läkaren utforskar Plats 3 och vänder **Övergivet laboratorium**: uthållighet 5 → 4; ett fynd hittas.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
**Aktiveringen slutar:** Läkaren avslutar på Plats 3. Uthållighet: 4.

## Runda 5

**Underhåll:** Rundslutet har minskat uthålligheten till 3.
**Rundstart:** Runda 5 börjar med 3 uthållighet.

### Bäraren

Bäraren börjar på Plats 3 med 1 verktyg, 0 fynd och 2 hälsa.
- **Handling:** Bäraren flyttar Plats 3 → Plats 6.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 6.
- **Kort/utforskning:** Utrustningen **Verktygsbälte** dras och tas upp direkt.
- **Kort/utforskning:** Bäraren utforskar Plats 6 och vänder **Fältsjukhuset**: skada 1 → 0.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
**Aktiveringen slutar:** Bäraren avslutar på Plats 6. Uthållighet: 3.

### Läkaren

Läkaren börjar på Plats 3 med 1 verktyg, 1 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Plats 3 → Förråd.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Handling:** Läkaren flyttar Förråd → Basläger.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Scenariohändelse:** Scenariohändelsen **Isras** löses ut: kartläget förändras.
- **Milstolpe:** Läkaren lämnar **Forskningsserver** i Baslägret. Progress: 2/3.
  - *Agentens tanke:* Fyndet har nått destinationen och lämnas omedelbart.
**Aktiveringen slutar:** Läkaren avslutar på Basläger. Uthållighet: 3.

## Runda 6

**Underhåll:** Rundslutet har minskat uthålligheten till 2.
**Rundstart:** Runda 6 börjar med 2 uthållighet.

### Bäraren

Bäraren börjar på Plats 6 med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Bäraren flyttar Plats 6 → Plats 5.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 5.
- **Kort/utforskning:** Fyndkortet **Satellitkärna** dras och bärs direkt.
- **Kort/utforskning:** Bäraren utforskar Plats 5 och vänder **Signaltornet**: ett fynd hittas.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
**Aktiveringen slutar:** Bäraren avslutar på Plats 5. Uthållighet: 2.

### Läkaren

Läkaren börjar på Basläger med 1 verktyg, 0 fynd och 3 hälsa.
- **Handling:** Läkaren flyttar Basläger → Förråd.
  - *Agentens tanke:* Platsen är okänd och utforskas för att hitta expeditionsfynd.
- **Handling:** Läkaren flyttar Förråd → Basläger.
  - *Agentens tanke:* Strategin går mot närmaste okända plats: Plats 4.
**Aktiveringen slutar:** Läkaren avslutar på Basläger. Uthållighet: 2.

## Runda 7

**Underhåll:** Rundslutet har minskat uthålligheten till 1.
**Rundstart:** Runda 7 börjar med 1 uthållighet.

### Bäraren

Bäraren börjar på Plats 5 med 1 verktyg, 1 fynd och 3 hälsa.
- **Handling:** Bäraren flyttar Plats 5 → Förråd.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Handling:** Bäraren flyttar Förråd → Basläger.
  - *Agentens tanke:* Karaktären bär ett fynd och prioriterar återfärd till Baslägret.
- **Milstolpe:** Bäraren lämnar **Satellitkärna** i Baslägret. Progress: 3/3.
  - *Agentens tanke:* Fyndet har nått destinationen och lämnas omedelbart.
**Aktiveringen slutar:** Bäraren avslutar på Basläger. Uthållighet: 1.

## Slutresultat

Bäraren återvänder med det tredje fyndet i runda 7. Gruppen vinner med endast 1 uthållighet kvar.

- Förflyttningar: **19**
- Verktyg tagna: **2**
- Utforskningar: **5**
- Återförda fynd: **3**
- Scenariohändelser: **Stormfront** och **Isras**

## Designobservationer

- De två karaktärerna delar upp utforskningen och hittar tidigt olika vägar ut från Förrådet.
- Bäraren utnyttjar sin roll väl genom att transportera två av de tre fynden.
- Läkaren hittar och återför Forskningsservern utan att behöva använda sin läkeförmåga.
- Partiet vinns med mycket liten uthållighetsmarginal, vilket visar att tidsbudgeten är pressad men möjlig.
- Simulatorn gör en ineffektiv kort förflyttning med Läkaren i runda 6; trots det vinns partiet. Detta är relevant vid tolkning av resultatet.

## Teknisk notering

`data/scenarios.yaml` och Ökenreläets scenariofil är i v1.9.42 synkroniserade till 12 / 10 / 9 startuthållighet. Ett regressionstest kontrollerar nu att scenarioregistret och scenariokällorna fortsätter att matcha.
