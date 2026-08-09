# Samarbets-ablationsstudie

## Syfte

Studien isolerar fyra nivåer av samarbete med samma speldata, strategier och seeds:

1. individuellt agerande
2. samordnade destinationer utan överföring
3. fullt samarbete med normal överföringskostnad
4. fullt samarbete med gratis överföring

Det gör det möjligt att skilja på värdet av gemensam planering och värdet av faktisk överlämning.

## Kommando

```bash
python scripts/run_cooperation_ablation.py
```

Större studie:

```bash
python scripts/run_cooperation_ablation.py --runs 100
```

## Mätvärden

- vinstgrad
- rundor och slutligt uthållighet
- hemtransporterade mål
- dubblerade destinationer
- samordnade måltilldelningar
- överföringar
- handlingar som används för överföring
- gratis överföringar
- kapacitetsproblem
- lämnade saker

## Tolkning

- `route_coordination - individual` mäter värdet av att dela upp utforskningen.
- `full_cooperation - individual` mäter den samlade effekten av planering och överföring.
- `free_transfer - full_cooperation` mäter hur mycket överföringens handlingskostnad bromsar samarbetet.

Resultaten är hypoteser. Den enkla mötes- och överföringsagenten kan underskatta mänskligt samarbete.
