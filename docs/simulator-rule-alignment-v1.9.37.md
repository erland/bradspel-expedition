# Simulatorns regelanpassning v1.9.37

## Syfte

Säkerställa att simulatoragenten använder samma centrala kostnader, kapaciteter,
valmöjligheter och förlusttidpunkter som en mänsklig spelare.

## Implementerade regelkontrakt

1. En handling genomförs inte om kostnaden överstiger återstående handlingar.
2. Förlust kontrolleras efter effekter och stoppar resterande aktivering.
3. Målobjektens storlek hämtas från respektive YAML-kort.
4. Överföra tillåter alla föremål; Kuriren ändrar kostnaden, inte reglerna.
5. Medicinväskan får välja en skadad karaktär på samma plats.
6. Valet mellan verktyg och skada görs av agentstrategin.
7. Kostnadsfri utrustning används vid den trigger som står på kortet.
8. Automatiska tester verifierar dessa kontrakt.

## Fortsatt begränsning

Simulatorn har perfekt bokföring och en definierad heuristik. Den simulerar därför
en regellydig agent, inte mänskliga misstag, diskussioner eller bordsläsbarhet.
