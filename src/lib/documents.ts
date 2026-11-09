import { del, get, set } from "idb-keyval";
import type { SourceBlock, StoredDocument } from "./types";

const INDEX_KEY = "cf:documents";
const docKey = (id: string) => `cf:doc:${id}`;

export async function getDocuments(): Promise<StoredDocument[]> {
  const ids = (await get<string[]>(INDEX_KEY)) ?? [];
  const docs = await Promise.all(ids.map(id => get<StoredDocument>(docKey(id))));
  return docs.filter((doc): doc is StoredDocument => Boolean(doc));
}

export async function saveDocument(doc: StoredDocument): Promise<void> {
  const ids = (await get<string[]>(INDEX_KEY)) ?? [];
  await set(docKey(doc.id), doc);
  if (!ids.includes(doc.id)) await set(INDEX_KEY, [doc.id, ...ids]);
}

export async function removeDocument(id: string): Promise<void> {
  const ids = (await get<string[]>(INDEX_KEY)) ?? [];
  await del(docKey(id));
  await set(INDEX_KEY, ids.filter(candidate => candidate !== id));
}

function blockify(pages: string[]): SourceBlock[] {
  const blocks: SourceBlock[] = [];
  pages.forEach((text, pageIndex) => {
    const paragraphs = text.replace(/\r/g, "").split(/\n{2,}/).map(x => x.trim()).filter(Boolean);
    for (const paragraph of paragraphs) {
      const words = paragraph.split(/\s+/);
      for (let i = 0; i < words.length; i += 75) {
        const value = words.slice(i, i + 75).join(" ").trim();
        if (value.length > 12) blocks.push({ id: `p${pageIndex + 1}-b${blocks.length + 1}`, page: pageIndex + 1, text: value });
      }
    }
  });
  return blocks;
}

export async function importDocument(file: File): Promise<StoredDocument> {
  const name = file.name;
  const isPdf = name.toLowerCase().endsWith(".pdf");
  const isTxt = name.toLowerCase().endsWith(".txt");
  if (!isPdf && !isTxt) throw new Error("Gebruik een PDF- of TXT-bestand.");
  if (file.size > 18 * 1024 * 1024) throw new Error("Maximale bestandsgrootte: 18 MB.");
  const binary = await file.arrayBuffer();
  let pages: string[] = [];
  if (isPdf) {
    const pdfjs = await import("pdfjs-dist");
    pdfjs.GlobalWorkerOptions.workerSrc = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/pdf.worker.min.mjs`;
    const pdf = await pdfjs.getDocument({ data: new Uint8Array(binary.slice(0)) }).promise;
    if (pdf.numPages > 150) throw new Error("Maximaal 150 pagina's per document in deze MVP.");
    for (let i = 1; i <= pdf.numPages; i++) {
      const content = await (await pdf.getPage(i)).getTextContent();
      let pageText = "";
      let prevY: number | null = null;
      for (const item of content.items) {
        if (!("str" in item)) continue;
        const y = item.transform[5];
        const newline = prevY !== null && Math.abs(y - prevY) > 7;
        pageText += `${newline ? "\n\n" : " "}${item.str}`;
        prevY = y;
      }
      pages.push(pageText.trim());
    }
    await pdf.destroy();
  } else {
    pages = [new TextDecoder().decode(binary)];
  }
  const blocks = blockify(pages);
  if (!blocks.length) throw new Error("Geen selecteerbare tekst gevonden. Gescande PDF's vereisen eerst OCR.");
  return {
    id: crypto.randomUUID(), name, size: file.size, type: isPdf ? "pdf" : "txt",
    createdAt: Date.now(), pageCount: pages.length, blocks, binary: isPdf ? binary : undefined,
  };
}

const wordSet = (text: string) => new Set((text.toLowerCase().match(/[a-zà-ž0-9]{3,}/g) ?? []).filter(w => !["een", "het", "van", "voor", "met", "dat", "deze", "zijn", "wordt", "door", "over", "niet", "waar", "heeft", "this", "from", "there", "which"].includes(w)));

export function findRelevantBlocks(blocks: SourceBlock[], question: string, limit = 8): SourceBlock[] {
  const words = wordSet(question);
  return blocks.map((block, index) => {
    const haystack = wordSet(block.text);
    const overlap = [...words].filter(word => haystack.has(word)).length;
    return { block, score: overlap / Math.sqrt(Math.max(haystack.size, 1)) + overlap * 0.04 - index * 0.000001 };
  }).sort((a, b) => b.score - a.score).slice(0, limit).map(x => x.block);
}

export function generateLocalAnalysis(blocks: SourceBlock[]): import("./types").Analysis {
  const prioritized = [...blocks].map((block, index) => ({
    block, score: (/(risic|rente|kosten|resultaat|verlies|omzet|verplicht|schuld|looptijd|garant|voorwaarden|belangrijk|liquiditeit|kapitaal)/i.test(block.text) ? 3 : 0) + (index < 4 ? 2 : 0) - index / Math.max(1, blocks.length),
  })).sort((a,b) => b.score - a.score).slice(0, 6).sort((a,b) => a.block.page - b.block.page);
  return {
    headline: "Documentoverzicht",
    introduction: "Dit is een lokaal, letterlijk fragmentenoverzicht. Configureer een AI-sleutel voor een begrijpelijke samenvatting in gewone taal.",
    sections: [{ title: "Mogelijk relevante passages", points: prioritized.map((v, i) => ({ id: `local-${i}`, text: v.block.text.slice(0, 340), sourceIds: [v.block.id] })) }],
    keyTerms: [], mode: "local", limited: false,
  };
}
