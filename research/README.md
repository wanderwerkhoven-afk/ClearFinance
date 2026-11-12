# ClearFinance — reproduceerbare AI-experimenten

Dit is het ML-onderzoeksspoor voor de Master Applied AI. **Geen prestaties of modelgewichten worden verzonnen.**

## Retrieval: benchmark
Maak een JSONL-bestand met per regel:
```json
{"document_id":"public-doc-001","question":"Hoe lang staat de rente vast?","relevant_ids":["p1-b1"],"blocks":[{"id":"p1-b1","page":1,"text":"De rente staat tien jaar vast."}]}
```

```bash
PYTHONPATH=backend python research/evaluate_retrieval.py path/to/gold.jsonl
```

Resultaat: Recall@1/5 en MRR, plus aantal vragen. Testset handmatig labelen en **per document gescheiden houden** van trainingsdata. BM25 is de nul/baseline.

## Verificatiemodel: TF-IDF baseline
Maak een CSV met kolommen `document_id,premise,hypothesis,label` en labels `entailment`, `contradiction`, `neutral`. Iedere hypothese is een vereenvoudigde samenvattingsclaim en de premise een originele bronpassage.

```bash
pip install -r research/requirements.txt
python research/train_verifier.py path/to/claims.csv
```

De code splitst eerst op document-ID in train, validatie en test. Fit van de vectorizer vindt uitsluitend op trainingsdata plaats. Uitvoer toont macro F1, classification report en confusion matrix op de testset. De baseline is geen transformer-NLI-model: het is juist een reproduceerbaar startpunt om latere fine-tuning eerlijk mee te vergelijken. Vereist meerdere documenten en voldoende voorbeelden per klasse.

## Vervolg voor de onderzoeksfase
1. Ground-truth laten beoordelen door twee annotatoren; inconsistenties bespreken.
2. Semantische retrieval vergelijken op exact dezelfde testset.
3. Transformer-NLI-model fine-tunen en document-gescheiden evalueren.
4. Significantieduiding en foutanalyse, ook financiële cijfers en ontkenningen.
5. Gebruikersbegrip meten met vooraf vastgelegde toetsvragen.

**Gebruik uitsluitend publieke, fictieve of aantoonbaar toegestane data.**
