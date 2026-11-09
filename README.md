# ClearFinance AI

Een cleane documentworkspace voor het begrijpelijk maken van financiële en juridische documenten. Gebouwd als een eerste werkende MVP in Next.js, TypeScript en PDF.js.

## Wat werkt er?

- Overzicht van je documenten, zoeken, toevoegen en verwijderen.
- PDF- en TXT-upload via bestandskiezer of drag-and-drop.
- Uitlezen van PDF-tekst per pagina en opsplitsen in bronpassages.
- Opslag van bestanden en analyses in **IndexedDB van de huidige browser**.
- AI-samenvatting in begrijpelijk Nederlands, met bron-ID's per kernpunt.
- Klikbare bronverwijzingen, paginanavigatie en markering van teruggevonden PDF-tekst.
- Vragen stellen over een geselecteerd document, met passagegebaseerde antwoorden.
- Fictief hypotheekvoorbeelddocument om alles direct te bekijken.
- TXT-export van de samenvatting.

Zonder API-sleutel blijft de app bruikbaar voor uploaden, bewaren, lezen en bronnen zoeken. De app toont dan **letterlijke fragmenten**, geen AI-samenvatting. Ook de chat geeft dan alleen passende bronfragmenten terug. Dit staat expliciet in de interface.

## Lokaal starten

Vereist: Node.js 20.9+ (aanbevolen Node.js 24).

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open daarna <http://localhost:3000>. Om AI-analyse en chat te activeren, vul in `.env.local` de server-side sleutel in:

```env
OPENAI_API_KEY=je_eigen_api_sleutel
OPENAI_MODEL=gpt-4.1-mini
```

**Plaats de sleutel nooit in browsercode of een publieke GitHub-repository.** De server gebruikt de OpenAI Responses API met `store: false`.

Controleer de productiebuild:

```bash
npm run typecheck
npm run build
```

## GitHub en Vercel

1. Maak op GitHub een nieuwe (bij voorkeur privé) repository, bijvoorbeeld `clearfinance-ai`.
2. Push deze projectmap naar `main` of naar een ontwikkelbranch.
3. Importeer de GitHub-repository in Vercel als Next.js-project.
4. Voeg de environment variables `OPENAI_API_KEY` en optioneel `OPENAI_MODEL` toe **in Vercel**.
5. Deploy. `npm install` kopieert de benodigde PDF.js-worker naar `public/`.

### Grenzen van deze MVP

- PDF met tekstlaag en TXT; gescande PDF's hebben OCR nodig. Word/DOCX staat voor een latere versie gepland.
- Maximaal 18 MB en 150 PDF-pagina's. Bij zeer lange documenten wordt een selectie van bronpassages aan de AI gegeven; de app waarschuwt daarvoor.
- De analyse is **niet juridisch of financieel gevalideerd**. Het feit dat een bron-ID bestaat, bewijst nog niet dat een modelclaim volledig door die bron wordt gedragen.
- Geen accountbeheer, rollen, server-side versleutelde documentopslag, audittrail, rate limiting, antiviruscontrole, DPIA of productieklare bankbeveiliging.
- Het originele bestand blijft lokaal. Voor AI-analyse worden documentpassages naar de geconfigureerde modelprovider verstuurd. Gebruik **geen echte vertrouwelijke klant- of bankdocumenten** zonder voorafgaande privacy-, beveiligings- en contractuele beoordeling.
- Externe modelverzoeken kosten mogelijk geld. Een publiek bereikbare deployment met API-sleutel vereist authenticatie, rate limiting en budgetlimieten voordat je die openstelt.

## Architectuur (MVP)

```text
Browser
  ├─ PDF.js: tekst per pagina + PDF-weergave
  ├─ IndexedDB: documenten en analyse
  ├─ Dashboard & split-screen
  └─ /api/analyze, /api/ask
           │
           └─ Next.js server route → OpenAI Responses API
                  ↳ gestructureerde antwoorden met bron-ID's
```

Het ophalen van relevante passages voor de chat gebeurt voorlopig op basis van woordoverlap. Dit is nog geen semantische vector-RAG-architectuur; daarvoor is een latere versie met embeddings en evaluatie van retrievalkwaliteit wenselijk.

## Logische vervolgstappen

1. GitHub-repository aanmaken en een beveiligde testdeployment instellen.
2. Auth + database + beveiligde blobstorage toevoegen voor meerdere gebruikers.
3. OCR/DOCX, volledige documentindexering en semantische retrieval toevoegen.
4. Bronclaim-validatie, risicodetectie en testset met menselijke beoordeling opzetten.
5. Gebruikersonderzoek: leesbaarheid en begrip meten bij de doelgroep.
