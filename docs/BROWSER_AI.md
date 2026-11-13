# Browser AI Demo — ClearFinance

## Doel

De GitHub Pages-website is de zelfstandige demo. Het model draait op de GPU van de bezoeker in een JavaScript Web Worker. **Er is geen backend- of API-sleutel nodig** voor de browserstand.

## Wat is gebouwd?

- Next.js static export op GitHub Pages, bestaande PDF.js-reader, lokale IndexedDB-documenten.
- Bij upload PDF met selecteerbare tekst of TXT: document openen, daarna de knop **Genereer met Browser AI**.
- WebLLM-runtime wordt via een versiegefixeerde CDN-module geladen. Het model is **Qwen2.5-0.5B-Instruct-q4f16_1-MLC**.
- Eerste gebruik vereist een grote modeldownload en voldoende WebGPU-/GPU-geheugen; volgende sessies kunnen de modelcache hergebruiken.
- Generatie gebeurt in een aparte worker: chunk → section → document, plus lexicale retrieval van originele passages.
- Validatie van bron-ID's; waarschuwingen voor onvolledige verwerking.
- De bestaande Python/Ollama/Docling-pipeline blijft apart beschikbaar voor onderzoeksvergelijking.

## Test de demo

1. Open https://wanderwerkhoven-afk.github.io/ClearFinance/ in een recente desktopbrowser met WebGPU en voldoende GPU-geheugen (Chrome/Edge zijn logische eerste testdoelen).
2. Upload een kort, fictief PDF- of TXT-document (bijv. 2-5 pagina's).
3. Klik **Genereer met Browser AI** in de documentwerkruimte.
4. Observeer de download-/generatiestatus. De eerste modeldownload is groot; het model blijft daarna tijdens de huidige sessie beschikbaar.
5. Controleer iedere bronverwijzing tegen de originele tekst.
6. Herhaal met een document dat een financieel risico bevat; controleer of cijfers, voorwaarden en risico's juist zijn weergegeven.
7. Test zonder WebGPU: de applicatie moet een compatibiliteitsmelding tonen en mag niet ten onrechte suggereren dat er AI draait.

## Grenzen

- Browser AI werkt alleen op hardware en browsers met WebGPU. Er is geen CPU-generatiemodus ingebouwd.
- Modelgewichten en runtime worden van externe CDN-/modelhosts **gedownload**. Geen documenttekst gaat naar ClearFinance-backend in de Pages-stand.
- De modeluitvoering gebruikt een compact 0.5B-model; kwaliteit van lange en complexe financiële samenvattingen is nog niet bewezen.
- Er is een verwerkingslimiet van 12 chunks en 600 bronblokken. Onvolledigheid moet als zodanig herkenbaar zijn.
- In browserstand gebruikt de demo PDF.js, niet Docling/OCR; gescande PDF's werken daarom niet.
- RAG is vooralsnog eenvoudige lexicale passage-retrieval. **Dit is nog geen BGE-M3 semantic retrieval.**
- Bron-ID's zijn uitsluitend verwijzingen, geen bewijs van feitelijke correctheid.
- Gebruik alleen publieke of fictieve documenten. De app is geen gevalideerde financiële advies- of bankomgeving.

## Onderzoeksaanpak

Meet eerst modelcompatibiliteit, laadtijd en kwaliteit van bronverwijzingen met fictieve documentfixtures. Daarna samenvattingskwaliteit onafhankelijk evalueren en vergelijken met Python hierarchical baseline. De officiële Rabobank-hoofdvraag blijft de betrouwbare automatische evaluatie van samenvattingen.
