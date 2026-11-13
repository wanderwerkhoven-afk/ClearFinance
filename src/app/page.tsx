"use client";

import { ChangeEvent, DragEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft, ArrowRight, BadgeCheck, BookOpen, Check, ChevronRight, CircleHelp, Clock3,
  CloudUpload, File, FileCheck2, FilePlus2, FileSearch, FileText, FolderOpen, HelpCircle,
  Info, Landmark, LayoutGrid, Lightbulb, LoaderCircle, LockKeyhole, MessageCircle,
  MoreHorizontal, PanelRightClose, PanelRightOpen, Plus, Search, Send, ShieldCheck,
  Sparkles, Trash2, X,
} from "lucide-react";
import PdfViewer from "@/components/PdfViewer";
import { analyzeInBrowser, browserAiSupported, clearBrowserModelCache } from "@/lib/browser-ai";
import { demoDocument } from "@/lib/demo";
import { findRelevantBlocks, generateLocalAnalysis, getDocuments, importDocument, removeDocument, saveDocument } from "@/lib/documents";
import type { Answer, SourceBlock, StoredDocument } from "@/lib/types";

const formatDate = (date: number) => new Intl.DateTimeFormat("nl-NL", { day: "numeric", month: "short", year: "numeric" }).format(date);
const formatSize = (bytes: number) => bytes ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : "Voorbeeld";

function displayError(value: unknown) { return value instanceof Error ? value.message : "Er is iets misgegaan."; }

export default function Home() {
  const [docs, setDocs] = useState<StoredDocument[]>([demoDocument]);
  const [activeId, setActiveId] = useState("demo");
  const [view, setView] = useState<"library" | "workspace">("library");
  const [query, setQuery] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [showSource, setShowSource] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [chatBusy, setChatBusy] = useState(false);
  const [answers, setAnswers] = useState<Record<string, { question: string; answer: Answer }[]>>({});
  const [notice, setNotice] = useState("");
  const [browserStatus, setBrowserStatus] = useState("");
  const [browserSupported, setBrowserSupported] = useState<boolean | null>(null);
  const [clearingCache, setClearingCache] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const chatEnd = useRef<HTMLDivElement>(null);

  useEffect(() => { setBrowserSupported(browserAiSupported()); }, []);

  useEffect(() => {
    getDocuments().then(saved => setDocs([demoDocument, ...saved])).catch(() => setNotice("Lokale opslag is niet beschikbaar in deze browser."));
  }, []);

  const activeDoc = docs.find(d => d.id === activeId) ?? demoDocument;
  const selectedBlock = activeDoc.blocks.find(b => b.id === selectedSourceId) ?? null;
  const filtered = useMemo(() => docs.filter(d => d.name.toLowerCase().includes(query.toLowerCase())), [docs, query]);
  const currentAnswers = answers[activeId] ?? [];

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [currentAnswers.length]);

  function openDoc(id: string) {
    setActiveId(id); setView("workspace"); setSelectedSourceId(null); setPage(1); setShowSource(true); setNotice("");
  }

  function gotoSource(id: string) {
    const block = activeDoc.blocks.find(b => b.id === id);
    if (!block) return;
    setSelectedSourceId(id); setPage(block.page); setShowSource(true);
  }

  async function analyze(doc: StoredDocument) {
    setAnalyzingId(doc.id);
    setBrowserStatus("Browser AI voorbereiden...");
    try {
      const api = process.env.NEXT_PUBLIC_AI_API_BASE_URL?.replace(/\/$/, "");
      if (!api) {
        const analysis = await analyzeInBrowser(doc.blocks, (status, fraction) => {
          const percentage = fraction !== null ? " (" + Math.round(fraction * 100) + "%)" : "";
          setBrowserStatus(status + percentage);
        });
        const updated = { ...doc, analysis };
        await saveDocument(updated);
        setDocs(current => current.map(d => d.id === doc.id ? updated : d));
        return;
      }
      const result = await fetch(`${api}/api/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ blocks: doc.blocks }) });
      const payload = await result.json();
      const updated = { ...doc, analysis: result.ok ? { ...payload.analysis, audit: payload.audit } : generateLocalAnalysis(doc.blocks) } as StoredDocument;
      await saveDocument(updated);
      setDocs(current => current.map(d => d.id === doc.id ? updated : d));
      if (!result.ok && payload.code !== "CONFIG_REQUIRED") setNotice(payload.error || "AI-analyse is niet beschikbaar. Er is een lokaal bronnenoverzicht getoond.");
    } catch {
      const updated = { ...doc, analysis: generateLocalAnalysis(doc.blocks) };
      await saveDocument(updated);
      setDocs(current => current.map(d => d.id === doc.id ? updated : d));
      setNotice("Browser AI kon niet draaien. Er is alleen een lokaal bronnenoverzicht getoond; geen echte AI-samenvatting.");
    } finally { setAnalyzingId(null); setBrowserStatus(""); }
  }

  async function parseWithLocalBackend(file: File, fallbackBlocks: SourceBlock[]): Promise<SourceBlock[]> {
    const api = process.env.NEXT_PUBLIC_AI_API_BASE_URL?.replace(/\/$/, "");
    if (!api || !file.name.toLowerCase().endsWith(".pdf")) return fallbackBlocks;
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch(api + "/api/parse", { method: "POST", body: form });
      if (!response.ok) throw new Error("Docling-parser niet beschikbaar.");
      const payload: {blocks?: SourceBlock[]} = await response.json();
      if (!Array.isArray(payload.blocks) || !payload.blocks.length || !payload.blocks.every(
        b => typeof b.id === "string" && Number.isInteger(b.page) &&
             b.page > 0 && typeof b.text === "string" && b.text.length > 0
      )) throw new Error("Onjuiste brondata van de documentparser.");
      return payload.blocks;
    } catch {
      if (!fallbackBlocks.length) throw new Error("Document bevat geen selecteerbare tekst en Docling/OCR is niet beschikbaar.");
      setNotice("Docling is niet bereikbaar. PDF.js-tekstextractie is als fallback gebruikt.");
      return fallbackBlocks;
    }
  }

  async function importFiles(files: FileList | File[]) {
    if (!files.length) return;
    setUploading(true); setNotice("");
    try {
      for (const file of Array.from(files).slice(0, 8)) {
        const imported = await importDocument(file);
        const blocks = await parseWithLocalBackend(file, imported.blocks);
        const doc = { ...imported, blocks };
        await saveDocument(doc);
        setDocs(current => [current[0], doc, ...current.slice(1)]);
        openDoc(doc.id);
        if (process.env.NEXT_PUBLIC_AI_API_BASE_URL) await analyze(doc);
      }
    } catch (error) { setNotice(displayError(error)); }
    finally { setUploading(false); if (fileInput.current) fileInput.current.value = ""; }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) { if (event.target.files) void importFiles(event.target.files); }
  function handleDrop(event: DragEvent<HTMLElement>) { event.preventDefault(); setDragOver(false); void importFiles(event.dataTransfer.files); }

  async function deleteDoc(id: string) {
    if (id === "demo" || !window.confirm("Dit document uit deze browser verwijderen?")) return;
    await removeDocument(id);
    setDocs(current => current.filter(d => d.id !== id));
    if (activeId === id) { setActiveId("demo"); setView("library"); }
  }

  async function ask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = chatInput.trim();
    if (!question || chatBusy) return;
    setChatBusy(true); setChatInput("");
    try {
      let answer: Answer;
      const api = process.env.NEXT_PUBLIC_AI_API_BASE_URL?.replace(/\/$/, "");
      if (!api) {
        const related = findRelevantBlocks(activeDoc.blocks, question, 3);
        answer = { text: "Dit is een lokale bronzoekfunctie, geen AI-antwoord. Dit zijn de best passende passages uit het document:\n\n" + related.map(b => `• ${b.text.slice(0, 260)}`).join("\n\n"), sourceIds: related.map(b => b.id), mode: "local" };
      } else {
        const response = await fetch(`${api}/api/ask`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ question, blocks: activeDoc.blocks }) });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || "Vraag beantwoorden is niet gelukt.");
        answer = payload.answer;
      }
      setAnswers(current => ({ ...current, [activeId]: [...(current[activeId] || []), {question, answer}] }));
    } catch (error) { setNotice(displayError(error)); }
    finally { setChatBusy(false); }
  }

  function exportAnalysis() {
    if (!activeDoc.analysis) return;
    const lines = [activeDoc.name, activeDoc.analysis.headline, "", activeDoc.analysis.introduction];
    for (const section of activeDoc.analysis.sections) {
      lines.push("", section.title);
      for (const point of section.points) {
        const pages = point.sourceIds.map(id => activeDoc.blocks.find(b => b.id === id)?.page).filter(Boolean);
        lines.push(`• ${point.text} [pagina ${[...new Set(pages)].join(", ")}]`);
      }
    }
    lines.push("", "Automatische uitleg — controleer belangrijke informatie in het originele document.");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([lines.join("\n")], {type:"text/plain;charset=utf-8"}));
    link.download = `${activeDoc.name.replace(/\.[^.]+$/, "")}-samenvatting.txt`;
    link.click(); URL.revokeObjectURL(link.href);
  }

  async function clearAiDownloads() {
    if (clearingCache || analyzingId) return;
    if (!window.confirm("Het gedownloade Qwen AI-model verwijderen uit de browsercache? Je documenten en samenvattingen blijven bewaard. Bij de volgende analyse moet het model opnieuw worden gedownload.")) return;
    setClearingCache(true);
    setNotice("AI-modelcache wordt opgeruimd...");
    try {
      await clearBrowserModelCache(status => setNotice(status));
      setNotice("AI-downloads gewist. Je documenten en samenvattingen zijn behouden. Het model wordt bij de volgende analyse opnieuw gedownload.");
    } catch (error) {
      setNotice("Modelcache wissen is niet gelukt: " + displayError(error));
    } finally {
      setClearingCache(false);
    }
  }

  const canAnalyze = activeDoc.id !== "demo" && !!activeDoc.blocks.length && !analyzingId && (Boolean(process.env.NEXT_PUBLIC_AI_API_BASE_URL) || browserSupported !== false);

  return <div className="app-shell">
    <input ref={fileInput} className="visually-hidden" type="file" accept=".pdf,.txt,application/pdf,text/plain" multiple onChange={handleFileChange} />
    <aside className="sidebar">
      <button className="brand" onClick={() => setView("library")} aria-label="ClearFinance startpagina">
        <span className="brand-mark"><Landmark size={21} strokeWidth={2.1}/></span>
        <span><span className="brand-name">clearfinance<span className="brand-dot">.</span></span><span className="brand-caption">DOCUMENT INTELLIGENCE</span></span>
      </button>
      <div className="sidebar-label">WERKOMGEVING</div>
      <nav className="sidebar-nav" aria-label="Hoofdnavigatie">
        <button className={`nav-link ${view === "library" ? "active" : ""}`} onClick={() => setView("library")}><LayoutGrid size={18}/> Overzicht</button>
        <button className={`nav-link ${view === "workspace" ? "active" : ""}`} onClick={() => setView("workspace")}><FolderOpen size={18}/> Documentanalyse</button>
      </nav>
      <div className="sidebar-label second-label">DOCUMENTEN</div>
      <div className="sidebar-recent">
        {docs.slice(0, 5).map(doc => <button className={`recent-item ${view === "workspace" && activeId === doc.id ? "selected" : ""}`} key={doc.id} onClick={() => openDoc(doc.id)}><FileText size={15}/><span>{doc.name}</span></button>)}
      </div>
      <button className="sidebar-add" onClick={() => fileInput.current?.click()}><Plus size={17}/> Nieuw document</button>
      <div className="sidebar-bottom">
        <div className="privacy-message"><ShieldCheck size={18}/><span>Browser AI draait op je apparaat. Alleen modelbestanden worden gedownload; zonder optionele backend blijven je documenten lokaal.</span></div>
        <div className="profile"><div className="profile-avatar">CF</div><div><strong>Mijn werkruimte</strong><span>Browser AI · lokaal</span></div><MoreHorizontal size={17}/></div>
      </div>
    </aside>

    <main className="main-panel">
      <header className="topbar">
        <div className="breadcrumb"><span>Werkruimte</span><ChevronRight size={15}/><strong>{view === "library" ? "Overzicht" : "Documentanalyse"}</strong></div>
        <div className="top-actions"><button className="outline-button" disabled={clearingCache || !!analyzingId} onClick={() => void clearAiDownloads()} title="Alleen het lokale Qwen-model wissen; documenten blijven bewaard"><Trash2 size={15}/><span className="hide-on-mobile">{clearingCache ? "Wissen..." : "AI-downloads wissen"}</span></button><div className="top-status"><span className="status-dot"/> Browser AI · lokale inferentie</div><button className="icon-button" title="Over deze versie" onClick={() => setNotice("Browser AI draait lokaal met WebGPU en vereist een eenmalige modeldownload. Gebruik alleen fictieve of publieke testdocumenten; valideer alle financiële conclusies.")}><HelpCircle size={18}/></button><div className="top-avatar">CF</div></div>
      </header>

      {notice && <div className="notice"><Info size={16}/><span>{notice}</span><button onClick={() => setNotice("")} aria-label="Sluiten"><X size={16}/></button></div>}

      {view === "library" ? <section className="dashboard-content">
        <div className="welcome-row"><div><div className="eyebrow">JOUW FINANCIËLE DOCUMENTEN, HELDER UITGELEGD</div><h1>Begrijp wat er écht staat<span className="accent-period">.</span></h1><p>Van complexe voorwaarden tot uitgebreide jaarverslagen. Alles wat je moet weten, in begrijpelijke taal.</p></div><div className="welcome-art" aria-hidden><div className="art-card art-back"/><div className="art-card art-front"><FileCheck2 size={25}/><span/><span/><span/></div><div className="art-spark"><Sparkles size={23}/></div></div></div>
        <div className="stat-row"><div className="stat-card"><div className="stat-icon"><FileText size={18}/></div><div><strong>{docs.length - 1}</strong><span>Mijn documenten</span></div></div><div className="stat-card"><div className="stat-icon mint"><BadgeCheck size={18}/></div><div><strong>{docs.filter(d => d.id !== "demo" && d.analysis?.mode === "ai").length}</strong><span>AI-analyses</span></div></div><div className="stat-card"><div className="stat-icon cream"><LockKeyhole size={18}/></div><div><strong>Privé</strong><span>Lokale opslag</span></div></div></div>
        <div className={`upload-zone ${dragOver ? "drag-over" : ""}`} onDrop={handleDrop} onDragOver={e => {e.preventDefault();setDragOver(true);}} onDragLeave={() => setDragOver(false)}>
          <div className="upload-icon"><CloudUpload size={25}/></div><div className="upload-copy"><h3>Een nieuw document analyseren?</h3><p>Upload PDF of TXT en start daarna Browser AI. Het model draait lokaal op een WebGPU-compatibel apparaat.</p></div><button className="primary-button" onClick={() => fileInput.current?.click()} disabled={uploading}>{uploading ? <LoaderCircle className="spin" size={16}/> : <Plus size={16}/>} {uploading ? "Verwerken..." : "Document toevoegen"}</button>
        </div>
        <div className="section-header"><div><h2>Mijn documenten</h2><p>Al je bestanden overzichtelijk op één plek.</p></div><div className="search-field"><Search size={17}/><input placeholder="Zoek documenten..." value={query} onChange={e => setQuery(e.target.value)} aria-label="Zoek documenten"/></div></div>
        <div className="document-table"><div className="table-header"><span>DOCUMENT</span><span>GEÜPLOAD</span><span>STATUS</span><span></span></div>
          {filtered.length === 0 ? <div className="empty-search"><FileSearch size={23}/>Geen documenten gevonden.</div> : filtered.map(doc => <div className="document-row" key={doc.id}>
            <button className="doc-open" onClick={() => openDoc(doc.id)}><span className={`file-icon ${doc.type}`}><FileText size={21}/></span><span className="doc-name"><strong>{doc.name}</strong><small>{doc.pageCount} {doc.pageCount === 1 ? "pagina" : "pagina's"} · {formatSize(doc.size)}</small></span></button>
            <span className="doc-date"><Clock3 size={14}/>{formatDate(doc.createdAt)}</span>
            <span><span className={`doc-status ${analyzingId === doc.id ? "working" : doc.analysis?.mode === "ai" ? "complete" : "example"}`}>{analyzingId === doc.id ? "Bezig..." : doc.analysis?.mode === "ai" ? "Geanalyseerd" : doc.id === "demo" ? "Voorbeeld" : "Bronoverzicht"}</span></span>
            <div className="doc-actions"><button className="row-arrow" onClick={() => openDoc(doc.id)} aria-label={`${doc.name} openen`}><ArrowRight size={18}/></button>{doc.id !== "demo" && <button className="row-delete" onClick={() => void deleteDoc(doc.id)} title="Verwijderen"><Trash2 size={16}/></button>}</div>
          </div>)}
        </div>
        <div className="dashboard-help"><Lightbulb size={18}/><p><strong>Browser AI:</strong> {browserSupported === false ? "Deze browser ondersteunt momenteel geen WebGPU. De fictieve demo blijft beschikbaar." : "Na het uploaden kun je een AI-samenvatting genereren. Het model wordt bij de eerste analyse gedownload."}</p></div>
      </section> : <section className="workspace-content">
        <div className="workspace-header"><div className="workspace-heading"><button className="back-button" onClick={() => setView("library")} aria-label="Terug naar documenten"><ArrowLeft size={20}/></button><div><div className="eyebrow">DOCUMENTANALYSE <span className="eyebrow-divider">/</span> {activeDoc.pageCount} PAGINA&apos;S</div><h1>{activeDoc.name}</h1></div></div><div className="workspace-actions"><button className="outline-button" disabled={!canAnalyze} onClick={() => void analyze(activeDoc)}><Sparkles size={16}/><span className="hide-on-mobile">{analyzingId === activeId ? "AI werkt..." : "Genereer met Browser AI"}</span></button><button className="outline-button" onClick={() => setShowSource(v => !v)}>{showSource ? <PanelRightClose size={16}/> : <PanelRightOpen size={16}/>} <span className="hide-on-mobile">{showSource ? "Verberg bron" : "Toon bron"}</span></button><button className="outline-button" onClick={exportAnalysis} disabled={!activeDoc.analysis}><FileText size={16}/><span className="hide-on-mobile">Exporteer</span></button></div></div>
        <div className={`workspace-grid ${!showSource ? "without-source" : ""}`}>
          <div className="analysis-pane"><div className="analysis-toolbar"><div className="analysis-tab"><Sparkles size={16}/> AI-samenvatting</div><div className="analysis-mode">{activeDoc.analysis?.mode === "ai" ? <><span className="dot-green"/>AI-analyse</> : activeDoc.id === "demo" ? "Interactief voorbeeld" : "Lokale bronextractie"}</div></div>
            <div className="analysis-scroll">
              {analyzingId === activeId ? <div className="analysis-loading"><div className="loading-glyph"><LoaderCircle size={30} className="spin"/></div><h3>Browser AI analyseert je document</h3><p>{browserStatus || "Model en bronpassages voorbereiden..."}</p></div> : activeDoc.analysis ? <>
                <div className="summary-eyebrow"><span className="summary-badge"><Sparkles size={13}/> SAMENVATTING</span><span className="reading-time"><BookOpen size={14}/> 3 min leestijd</span></div>
                <h2 className="summary-title">{activeDoc.analysis.headline}</h2><p className="summary-intro">{activeDoc.analysis.introduction}</p>
                {activeDoc.analysis.audit && <div className="scope-warning"><Info size={16}/><span>Verwerking: {activeDoc.analysis.audit.processedBlocks ?? "?"} van {activeDoc.analysis.audit.totalBlocks ?? "?"} bronblokken · {activeDoc.analysis.audit.modelCalls ?? "?"} modelaanroepen · {activeDoc.analysis.audit.retrieval ?? "bronzoekfunctie"} · {activeDoc.analysis.audit.complete ? "Alle blokken verwerkt" : "Voorlopig/onvolledig resultaat"}. Een geldige bronverwijzing bewijst nog niet dat een AI-claim inhoudelijk klopt.</span></div>}
                {activeDoc.analysis.limited && <div className="scope-warning"><Info size={16}/>De verwerking is onvolledig of een samenvattingsstap is mislukt. Controleer het originele document.</div>}
                {activeDoc.analysis.mode === "local" && <div className="scope-warning"><Info size={16}/>Dit zijn letterlijke passages, nog geen door AI vereenvoudigde uitleg. Gebruik een WebGPU-compatibele browser en kies Genereer met Browser AI voor echte samenvatting.</div>}
                <div className="summary-divider"/>
                {activeDoc.analysis.sections.map((section, i) => <section className="summary-section" key={`${section.title}-${i}`}><div className="section-number">0{i + 1}</div><div className="summary-section-body"><h3>{section.title}</h3><div className="summary-points">{section.points.map(point => <div className={`summary-point ${point.sourceIds.includes(selectedSourceId || "____") ? "is-selected" : ""}`} key={point.id}>
                  <span className="point-bullet"><Check size={12}/></span><div><p>{point.text}</p><div className="source-links">{point.sourceIds.map(id => {const block = activeDoc.blocks.find(b => b.id === id); return block ? <button className={`source-link ${selectedSourceId === id ? "active" : ""}`} key={id} onClick={() => gotoSource(id)} title={`Bekijk bron: ${block.text.slice(0, 150)}`}><FileSearch size={12}/> Bron: pagina {block.page}<ArrowRight size={12}/></button> : null;})}</div></div>
                </div>)}</div></div></section>)}
                {activeDoc.analysis.keyTerms.length > 0 && <div className="glossary"><div className="glossary-heading"><Lightbulb size={17}/> Begrippen uitgelegd</div>{activeDoc.analysis.keyTerms.map(term => <div className="term" key={term.term}><strong>{term.term}</strong><span>{term.explanation}</span></div>)}</div>}
                <div className="disclaimer"><ShieldCheck size={16}/><span>Deze uitleg is automatisch gegenereerd. Controleer belangrijke bedragen, voorwaarden en beslissingen altijd in het originele document.</span></div>
              </> : <div className="analysis-empty"><FileSearch size={27}/><h3>Nog geen analyse</h3><p>Start Browser AI om met het lokale Qwen-model een hiërarchische samenvatting te maken.</p><button className="primary-button" disabled={!canAnalyze} onClick={() => void analyze(activeDoc)}>Genereer met Browser AI</button>{browserSupported === false && <p>WebGPU ontbreekt in deze browser. Gebruik een geschikte desktopbrowser.</p>}</div>}
            </div>
            <div className="chat-panel"><div className="chat-label"><MessageCircle size={17}/><span>Stel een vraag over dit document</span></div>
              {currentAnswers.length > 0 && <div className="chat-history">{currentAnswers.map((entry, i) => <div className="chat-exchange" key={i}><div className="chat-question">{entry.question}</div><div className="chat-answer"><Sparkles size={15}/><div><p>{entry.answer.text}</p><div className="source-links">{entry.answer.sourceIds.map(id => {const block = activeDoc.blocks.find(b => b.id === id); return block ? <button key={id} className="source-link" onClick={() => gotoSource(id)}>Bron p. {block.page}<ArrowRight size={11}/></button> : null;})}</div></div></div></div>)}<div ref={chatEnd}/></div>}
              <form className="chat-input-wrap" onSubmit={ask}><input value={chatInput} onChange={e => setChatInput(e.target.value)} placeholder="Bijv. Wat betekent dit voor mijn maandlasten?" aria-label="Vraag over het document" disabled={chatBusy}/><button className="send-button" disabled={!chatInput.trim() || chatBusy} type="submit" aria-label="Vraag stellen">{chatBusy ? <LoaderCircle size={18} className="spin"/> : <Send size={17}/>}</button></form>
              <div className="chat-hint">Antwoorden zijn gebaseerd op het geselecteerde document.</div>
            </div>
          </div>
          {showSource && <PdfViewer doc={activeDoc} page={page} onPageChange={setPage} selected={selectedBlock}/>}
        </div>
      </section>}
    </main>
  </div>;
}
