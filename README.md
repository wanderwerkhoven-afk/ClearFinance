# ClearFinance AI

Een cleane, interactieve **GitHub Pages-designpreview** van een AI-documentworkspace voor begrijpelijke juridische en financiële documenten. Gebouwd met Next.js, TypeScript en PDF.js.

## Wat werkt er?

- Documentendashboard, zoeken, toevoegen en verwijderen.
- PDF- en TXT-upload via bestandskiezer of drag-and-drop.
- PDF-tekstextractie per pagina met traceerbare bronpassages.
- Lokale opslag van bestanden en bronoverzichten in IndexedDB.
- Klikbare bronverwijzingen, paginanavigatie en gemarkeerde PDF-tekst.
- Een lokale zoekfunctie die bij vragen passende bronpassages teruggeeft.
- Een fictief hypotheekdocument met vooraf gemaakte, interactieve samenvatting.
- TXT-export van de getoonde samenvatting of bronpassages.

**Dit is een designprototype, geen werkende AI-analyseservice.** Nieuwe uploads tonen momenteel letterlijke fragmenten. De vragenfunctie geeft bronpassages terug, geen door een LLM gegenereerd antwoord. Het ingebouwde fictieve document toont hoe de toekomstige AI-ervaring eruit kan zien.

## GitHub Pages

De GitHub Actions-workflow `.github/workflows/deploy-pages.yml` bouwt bij iedere push naar `main` een statische Next.js-export en publiceert de map `out/`.

1. Ga in de repository naar **Settings → Pages**.
2. Kies bij **Build and deployment → Source** voor **GitHub Actions**.
3. Controleer de workflow onder **Actions → Publish ClearFinance to GitHub Pages**.
4. Na een succesvolle deployment is de app bereikbaar op <https://wanderwerkhoven-afk.github.io/ClearFinance/>.

De build gebruikt `basePath: /ClearFinance` en zorgt dat de PDF.js-worker onder datzelfde pad bereikbaar is.

## Lokaal ontwikkelen

Vereist: Node.js 20.9+ (aanbevolen Node.js 24).

```bash
npm install
npm run dev
```

Open <http://localhost:3000>.

```bash
npm run typecheck
npm run build
```

Om de GitHub Pages-build lokaal te reproduceren:

```bash
GITHUB_PAGES=true NEXT_PUBLIC_BASE_PATH=/ClearFinance npm run build
```

## Later de AI-backend aansluiten

De eerdere Next.js-API-routes voor gestructureerde documentanalyse en documentvragen zijn bewaard in `server-reference/`. Ze draaien **niet** op GitHub Pages. Een toekomstige, apart gehoste backend kan op een beveiligde manier worden gekoppeld via `NEXT_PUBLIC_AI_API_BASE_URL`.

Een OpenAI API-sleutel hoort uitsluitend op de backend, **nooit** in de frontend of een `NEXT_PUBLIC_*` variabele. Een backend heeft ook authenticatie, rate limiting, loggingbeleid en privacybescherming nodig voor werkelijk gebruik.

## Grenzen en veiligheid

- PDF's met tekstlaag en TXT worden ondersteund; gescande PDF's vereisen OCR. DOCX volgt later.
- Maximaal 18 MB en 150 PDF-pagina's. Lange documenten vragen om uitgebreide indexering in een latere versie.
- Geen accountbeheer, centrale documentopslag, audittrail, beveiligingsonderzoek of productiegeschikte bankbeveiliging.
- Documenten blijven in de huidige versie lokaal in de browser; er is geen externe AI-backend verbonden.
- De fictieve samenvatting is slechts illustratief, niet financieel of juridisch advies.
- **Gebruik geen echte vertrouwelijke klant- of bankdocumenten** zonder voorafgaande beveiligings- en privacybeoordeling.

## Vervolg

1. De designpreview testen met potentiële gebruikers.
2. De begrijpelijkheid van het samenvattingsformat en de broninteractie evalueren.
3. OCR/DOCX en semantische retrieval toevoegen.
4. Een beveiligde AI-backend bouwen en antwoorden op juistheid en brononderbouwing evalueren.
