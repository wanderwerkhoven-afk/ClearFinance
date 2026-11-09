import OpenAI from "openai";
import type { SourceBlock } from "./types";

export function validBlocks(value: unknown): SourceBlock[] {
  if (!Array.isArray(value)) return [];
  return value.slice(0, 600).filter((b): b is SourceBlock =>
    typeof b?.id === "string" && /^p\d+-b\d+$|^demo-[a-z0-9]+$/.test(b.id) &&
    typeof b?.page === "number" && Number.isInteger(b.page) && b.page > 0 && b.page < 10000 &&
    typeof b?.text === "string" && b.text.length > 0 && b.text.length <= 1200
  );
}

export function aiClient(): OpenAI | null {
  if (!process.env.OPENAI_API_KEY) return null;
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY, timeout: 45_000, maxRetries: 1 });
}

export const model = () => process.env.OPENAI_MODEL || "gpt-4.1-mini";

export function documentEvidence(blocks: SourceBlock[]): string {
  return blocks.map(b => `[${b.id} | pagina ${b.page}] ${b.text}`).join("\n\n");
}

export function checkSourceIds(candidate: unknown, blocks: SourceBlock[]): string[] {
  const ids = new Set(blocks.map(b => b.id));
  return Array.isArray(candidate) ? candidate.filter((x): x is string => typeof x === "string" && ids.has(x)).slice(0, 5) : [];
}

export function pickBlocks(blocks: SourceBlock[], maxChars = 52_000): { selected: SourceBlock[]; limited: boolean } {
  const total = blocks.reduce((n, b) => n + b.text.length, 0);
  if (total < maxChars) return { selected: blocks, limited: false };
  const interesting = /(risic|rente|kosten|resultaat|verlies|omzet|winst|verplicht|schuld|looptijd|garant|voorwaarden|liquiditeit|kapitaal|dividend|rentabiliteit|balans|aansprak|jaarrekening)/i;
  const ranked = blocks.map((b, i) => ({b, i, priority: (i < 12 ? 8 : 0) + (i >= blocks.length - 10 ? 4 : 0) + (interesting.test(b.text) ? 5 : 0) + (i % 17 === 0 ? 2 : 0)})).sort((a,b) => b.priority - a.priority || a.i - b.i);
  const chosen: SourceBlock[] = [];
  let used = 0;
  for (const { b } of ranked) {
    if (used + b.text.length > maxChars) continue;
    chosen.push(b); used += b.text.length;
  }
  return { selected: chosen.sort((a,b) => blocks.indexOf(a) - blocks.indexOf(b)), limited: true };
}
