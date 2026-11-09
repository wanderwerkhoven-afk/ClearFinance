import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const src = join(process.cwd(), "node_modules", "pdfjs-dist", "build", "pdf.worker.min.mjs");
const dest = join(process.cwd(), "public", "pdf.worker.min.mjs");
if (!existsSync(src)) throw new Error("PDF.js worker ontbreekt: installeer eerst dependencies.");
mkdirSync(join(process.cwd(), "public"), { recursive: true });
copyFileSync(src, dest);
console.log("PDF.js worker beschikbaar in public/.");
