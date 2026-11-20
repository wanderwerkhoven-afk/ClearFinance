# ClearFinance — Case B research rebuild

**Pipeline = testinstrument. Evaluatie per laag = onderzoeksproduct.** Deze branch is een schone onderzoeksbasis. De bestaande GitHub Pages UI en experimentele WebGPU-worker blijven op main behouden maar gelden **niet** als gevalideerde onderzoeksimplementatie.

## Offline demo zonder GPU / API-key

```bash
python -m pip install pytest
python -m research_v2.cli --input research_v2/fixtures/synthetic_report.json --out research_v2/output
python -m pytest -q research_v2/tests
```

De extractieve baseline produceert reproduceerbaar `layers.json` (bronpassages, laag 1 en alle merge-stappen) en `metrics.json` (provenance, cijferkandidaten, compressie per laag). De baseline **genereert geen vrije AI-tekst**. Dit is bedoeld om fouten in de evaluatie-code vroeg te vangen.

## Optioneel open model via lokaal Ollama

Start lokaal Ollama met `qwen2.5:7b`. Run:
```bash
python -m research_v2.cli --input research_v2/fixtures/synthetic_report.json --merger ollama --model qwen2.5:7b --seed 42 --out research_v2/output-ollama
```

Fouten bij modelstart, JSON of bron-ID-validatie worden zichtbaar; er verschijnt geen fictieve AI-output. De adapter accepteert uitsluitend localhost. Seed + temperature=0 zijn gelogd maar garanderen geen identieke uitvoer op alle hardware.

## Onderzoeksmeting: status

| Eigenschap | V0 |
|---|---|
| Hiërarchische lagen en bron-ID's | Geïmplementeerd |
| Alle tussenlagen en lineage opslaan | Geïmplementeerd |
| Exacte numerieke kandidaatcontrole | Eerste implementatie; geen gevalideerde 90% |
| ROUGE-1/2/L | Deterministische baselines beschikbaar |
| Foutinjecties | Getal, jaar, kritieke omissie |
| BERTScore | Volgt |
| Parser voor echte jaarverslagen en tabellen | Volgt; input is parser-onafhankelijke JSON |
| Lokale/global faithfulness en drift | Volgt; opgeslagen als not_evaluated |
| NLI / judge / retrieval recall@k | Volgt; geen verzonnen scores |
| Gewogen coverage en gevoelige gewichten | Volgt |
| Menselijke validatie op 150–300 claims | Volgt |

**Belangrijk:** F1 95%, F2 90%, F4 ‘critical fail’ zijn concept-acceptatiecriteria en geen gemeten resultaten. Getal-match alleen is niet hetzelfde als cijfer-, jaar- en eenheidscorrectheid in tabellen. De 5 goede/5 slechte voorbeelden hebben beperkte statistische kracht. Gebruik publieke/synthetische bronnen en documenteer licenties.

## Volgende technische stappen

1. PDF + tabellen → expliciete `{id,page,section,text,kind}`-bronblokken; audit van jaar/eenheid in een tabelrij.
2. EDA over echte publieke bankjaarverslagen.
3. Golden injectieset en ROUGE/BERTScore-baselines plus false-failure-test.
4. Claimretrieval benchmark Recall@3 op circa 50 gelabelde claims.
5. Lokaal/global NLI- of judge-label `supported/contradicted/not_found`, drift, menselijke annotatie en κ.
6. Gewogen kernpuntdekking met stakeholder-gewichtenschema en sensitiviteitsanalyse.
7. Pas daarna minimale evaluatiedemo: fouten per claim met bronpagina.

**GitLab:** Tech Methods vraagt een GitLab-repolink. Deze branch is vooralsnog op GitHub. Zorg voor de juiste repository of spiegel en vermeld de werkelijke bron.
