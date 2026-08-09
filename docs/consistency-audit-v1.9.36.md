# Konsistenskontroll v1.9.36

## Omfattning

Kontrollen jämförde:

- grundregler i `data/rules.yaml`
- båda scenariofilerna och deras kortdata
- regelboken
- A6-referensen
- platskort, färdhändelser, målobjekt och utrustningskort
- simulatorns spelarvända feltexter
- regel-täckningsmatris och komponentpolicy

## Korrigerat

- `Scenarioevent` ersatt med spelarvända termen `Scenariohändelse`.
- `Installera/aktivera mål` ersatt med `Aktivera målobjekt`.
- Förlusttext använder slut på uthållighet eller sista uthållighetsmarkören.
- Inaktuell policy för separata reparationsmarkörer borttagen.
- A6-referens, scenario-YAML, regelbok och kortkällor använder samma centrala terminologi.

## Verifiering

- YAML-filer: 36
- YAML-varningar: 0
- Tester: 27 godkända
- Strict build: godkänd
- Simulatortäckning: 17 effekter, 8 förmågor, 2 uppdragstyper
- Balansändringar: inga

## Kvarvarande träffar

{
  "scenarioevent": [
    [
      "docs/simulator-alignment-v1.9.25.md",
      5,
      "Simulatorn ska använda scenarioeventarkitekturen från v1.9.24 och samtidigt göra eventens balanspåverkan mätbar."
    ],
    [
      "docs/simulator-alignment-v1.9.25.md",
      30,
      "Samma seeds används för båda lägena. Skillnaden mellan cellerna kan därför användas som hypotes om scenarioeventens påverkan."
    ],
    [
      "docs/simulator-alignment-v1.9.25.md",
      35,
      "- Endast fasta omedelbara scenarioevent från arkitekturversion 1 stöds."
    ],
    [
      "docs/design/dynamic-connections-prompt2-report.md",
      39,
      "Nästa steg ansvarar för datadrivna scenarioevents och automatisk öppning."
    ]
  ]
}
