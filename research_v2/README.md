# ClearFinance — Case B: evaluatie per hiërarchische laag

**De samenvattingspipeline is het testinstrument; de evaluatiemodule is het product.**

## Werkende één-commando-demo

Vanaf de repository-root:

```bash
python -m pip install -r research_v2/requirements.txt
python -m research_v2.demo
python -m pytest -q research_v2/tests
```

Open daarna lokaal `research_v2/output/demo/index.html`. De run produceert ook `run.json` met bron, tussenlagen, lineage, evaluaties, foutinjectie en ROUGE-baselines. **Dit is een uitgevoerde extractieve baseline zonder LLM**, niet een AI-samenvatting. Fouten zijn traceerbaar naar de bronpagina.

## Eigen PDF verwerken

```bash
python -m research_v2.demo --input pad/naar/jaarverslag.pdf --old 50 --new 55
```

Dit kan alleen als de tussenlaag daadwerkelijk een claim met het getal `50` bevat. Als dat niet zo is, volgt een expliciete fout in plaats van een kunstmatige succesvolle meting. De parser gebruikt lokaal PyMuPDF en bewaart paginanummers en tekstblokken. Complexe financiële tabellen worden nog **niet betrouwbaar als gestructureerde cellen** geparseerd. OCR ontbreekt.

Alternatief voor alleen tussenlagen zonder foutinjectie:

```bash
python -m research_v2.cli --input research_v2/fixtures/synthetic_report.json
```

## Optionele lokale generatieve LLM-test

```bash
ollama pull qwen2.5:7b
python -m research_v2.demo --mode ollama --model qwen2.5:7b
```

Het model draait uitsluitend op localhost; geen externe AI-API. Dit vereist een geïnstalleerde Ollama-server en voldoende RAM. Let op: met vrije tekst is het **niet gegarandeerd** dat een samenvattingslaag het injecteerbare getal behoudt. Voor de vergelijkbare foutinjectietest gebruiken we daarom eerst de extractieve baseline.

## Huidige metingen

- Per laag zijn claims, source IDs, origin IDs en compressieratio opgeslagen.
- Cijfercheck signaleert **kandidaat-afwijkingen**, geen gevalideerde tegenspraak.
- De demo maakt een bekende numerieke fout in één tussenlaag en vergelijkt de getalcontrole met ROUGE.
- NLI-claims, local/global semantic faithfulness, drift, gewogen kernpuntdekking en BERTScore zijn **nog niet geïmplementeerd**.
- Hierarchical merging is in deze baseline selecteren van bronclaims, geen LLM-synthese. De daadwerkelijke NLP-pipeline moet later met een lokaal model worden gevalideerd.

De oude website op `main` blijft intact. Deze code staat op de branch `research-rebuild`. De formele Tech Methods-repository hoort volgens de projectvoorwaarden op GitLab; deze GitHub-branch moet daarvoor gespiegeld of gemigreerd worden.

## Gecontroleerde demo-output op GitHub

De GitHub Actions workflow draait alle tests en voert de demonstratie daadwerkelijk uit. In de run `Research rebuild validation` staat onder **Artifacts** het bestand `clearfinance-evaluation-demo`: hierin zitten `index.html` (interactieve browserweergave zonder AI) en `run.json` (traceerbare data). Download de ZIP, pak hem uit en open `index.html` lokaal. De gegenereerde HTML is een statisch verslag met uitklapbare codevrije visuele secties, niet de huidige GitHub Pages-app.

De Ollama-contracttests gebruiken een gesimuleerde lokale HTTP-server, niet een echt geladen Qwen-model. Dit valideert de API-aanroep, seed, tokens en brontoewijzing maar **niet** de kwaliteit van de AI-uitvoer.
