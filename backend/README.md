# ClearFinance — kosteloze lokale AI-backend

**Status:** werkende onderzoeksbasis; niet geschikt voor openbaar bankgebruik. Alle tools hieronder zijn gratis/open source, maar je eigen computer en stroom zijn nodig.

## Start

Installeer Python 3.12 en [Ollama](https://ollama.com/). In de repository:

```bash
ollama pull qwen2.5:3b
ollama serve
```

Open een tweede terminal:

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Een derde terminal voor de bestaande interface:

```bash
# repository root
# create .env.local with NEXT_PUBLIC_AI_API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open http://localhost:3000. Upload een PDF met tekstlaag en bekijk de samenvatting. Het model wordt lokaal via Ollama aangeroepen.

**Zonder Ollama**: de API valt terug op expliciet als `local` aangeduide letterlijke passages; er is dan geen echte AI-samenvatting.

## Tests

```bash
PYTHONPATH=backend pytest -q backend/tests
```

## Veiligheid

- De API heeft geen authenticatie, gebruikersscheiding of productiegeschikte beveiliging.
- Host alleen op `127.0.0.1`; niet publiek bereikbaar maken.
- SQLite-bestand `backend/data/clearfinance.sqlite3` bevat tekst van documenten die expliciet via /api/documents worden opgeslagen. De huidige UI gebruikt die opslagroute nog niet.
- GitHub Pages blijft voorlopig alleen de publieke *design-demo*. Voor een live AI-demo gebruik je de frontend lokaal of bouw je eerst een beveiligde HTTPS-API met authenticatie.
- Upload geen vertrouwelijke klantdocumenten.
