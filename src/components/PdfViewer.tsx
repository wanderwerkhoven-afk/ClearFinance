"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, FileText, ScanSearch } from "lucide-react";
import type { SourceBlock, StoredDocument } from "@/lib/types";

type Highlight = { x: number; y: number; width: number; height: number };

function normalize(value: string) {
  return value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9€%]+/g, " ").trim().replace(/\s+/g, " ");
}

export default function PdfViewer({ doc, selected, page, onPageChange }: {
  doc: StoredDocument; selected: SourceBlock | null; page: number; onPageChange: (p: number) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [renderError, setRenderError] = useState("");

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(280, entry.contentRect.width - 56)));
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (doc.type !== "pdf" || !doc.binary || !canvasRef.current) return;
    let cancelled = false;
    let renderTask: { cancel: () => void; promise: Promise<void> } | undefined;
    let pdf: Awaited<ReturnType<typeof import("pdfjs-dist")["getDocument"]>["promise"]> | undefined;

    async function run() {
      try {
        setRenderError(""); setHighlights([]);
        const pdfjs = await import("pdfjs-dist");
        pdfjs.GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs";
        pdf = await pdfjs.getDocument({ data: new Uint8Array(doc.binary!.slice(0)) }).promise;
        const pdfPage = await pdf.getPage(page);
        const viewport0 = pdfPage.getViewport({ scale: 1 });
        const viewport = pdfPage.getViewport({ scale: width / viewport0.width });
        const canvas = canvasRef.current;
        if (!canvas || cancelled) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        canvas.height = Math.floor(viewport.height * ratio);
        canvas.width = Math.floor(viewport.width * ratio);
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;
        renderTask = pdfPage.render({ canvas, canvasContext: ctx, viewport, transform: ratio === 1 ? undefined : [ratio, 0, 0, ratio, 0, 0] });
        await renderTask.promise;
        if (cancelled) return;
        if (selected?.page === page) {
          const content = await pdfPage.getTextContent();
          const items = content.items.filter((item): item is typeof item & {str: string; transform: number[]; width: number; height: number} => "str" in item);
          const itemText = items.map(i => normalize(i.str));
          const joined = itemText.join(" ");
          const query = normalize(selected.text);
          let start = joined.indexOf(query);
          let length = query.length;
          if (start < 0) {
            const leading = query.split(" ").slice(0, 7).join(" ");
            start = joined.indexOf(leading);
            length = start < 0 ? 0 : Math.min(query.length, joined.length - start);
          }
          if (start >= 0 && length > 0) {
            let cursor = 0;
            const found: Highlight[] = [];
            for (let i = 0; i < items.length; i++) {
              const text = itemText[i];
              const itemStart = cursor;
              const itemEnd = itemStart + text.length;
              cursor = itemEnd + 1;
              if (itemEnd < start || itemStart > start + length || !text) continue;
              const transform = pdfjs.Util.transform(viewport.transform, items[i].transform);
              const height = Math.max(8, Math.abs(items[i].height * viewport.scale));
              found.push({ x: transform[4], y: transform[5] - height, width: Math.max(5, items[i].width * viewport.scale), height: height + 3 });
            }
            if (!cancelled) setHighlights(found);
          }
        }
      } catch (error) {
        if (!cancelled && !(error instanceof Error && error.name === "RenderingCancelledException")) setRenderError("PDF-pagina kon niet worden weergegeven.");
      }
    }
    run();
    return () => { cancelled = true; renderTask?.cancel(); void pdf?.destroy(); };
  }, [doc, page, width, selected]);

  return <div className="source-viewer">
    <div className="source-toolbar">
      <div className="source-title"><FileText size={17}/><span>Origineel document</span></div>
      <div className="source-page-nav">
        <button aria-label="Vorige pagina" onClick={() => onPageChange(Math.max(1, page - 1))} disabled={page <= 1}><ChevronLeft size={17}/></button>
        <span>{page} <span className="muted">/ {doc.pageCount}</span></span>
        <button aria-label="Volgende pagina" onClick={() => onPageChange(Math.min(doc.pageCount, page + 1))} disabled={page >= doc.pageCount}><ChevronRight size={17}/></button>
      </div>
    </div>
    <div className="source-scroll" ref={containerRef}>
      {selected && <div className="source-context"><ScanSearch size={15}/><span>Bronpassage op pagina {selected.page} geselecteerd</span></div>}
      {doc.type === "pdf" && doc.binary ? <div className="pdf-page-wrap">
        <div className="pdf-page" style={{width: "fit-content"}}>
          <canvas ref={canvasRef} aria-label={`PDF pagina ${page}`}/>
          {highlights.map((h, i) => <span key={i} className="pdf-highlight" style={{left:h.x, top:h.y, width:h.width, height:h.height}}/>)}
        </div>
        {renderError && <div className="error-note">{renderError}</div>}
      </div> : <div className="text-document-page">
        <div className="doc-paper-kicker">{doc.id === "demo" ? "FICTIEF VOORBEELDDOCUMENT" : "TEKSTDOCUMENT"}</div>
        <h2>{doc.name.replace(/\.[^.]+$/, "")}</h2>
        {doc.blocks.filter(b => b.page === page).map(b => <p key={b.id} className={selected?.id === b.id ? "text-highlight" : ""}>{b.text}</p>)}
        <div className="page-number">{page}</div>
      </div>}
    </div>
    <div className="source-footnote">Klik op een bron bij een kernpunt om de passage terug te vinden.</div>
  </div>;
}
