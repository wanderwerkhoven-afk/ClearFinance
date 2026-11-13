import type { Analysis, SourceBlock } from "./types";
let worker: Worker | null = null;
let running = false;
let request = 0;
export function browserAiSupported(): boolean {
  return typeof window !== "undefined" && typeof Worker !== "undefined" &&
    Boolean((navigator as Navigator & {gpu?: unknown}).gpu);
}
export function cancelBrowserAnalysis() {
  worker?.terminate(); worker = null; running = false;
}
export function analyzeInBrowser(blocks: SourceBlock[], onProgress: (text: string, progress: number | null) => void): Promise<Analysis> {
  if (!browserAiSupported()) return Promise.reject(new Error("WebGPU ontbreekt. Gebruik Chrome of Edge op een geschikt apparaat."));
  if (running) return Promise.reject(new Error("Er loopt al een AI-analyse."));
  if (!worker) worker = new Worker((process.env.NEXT_PUBLIC_BASE_PATH ?? "") + "/browser-ai.worker.mjs", { type:"module" });
  running = true;
  const current = worker;
  const id = ++request;
  return new Promise((resolve,reject)=>{
    const cleanup=()=>{current.removeEventListener("message",message);current.removeEventListener("error",fail);running=false;};
    const fail=(event:ErrorEvent)=>{cleanup();cancelBrowserAnalysis();reject(new Error(event.message||"Browsermodel kan niet worden gestart."));};
    const message=(event:MessageEvent)=>{
      const info=event.data;
      if(info?.id!==id)return;
      if(info.type==="progress"){onProgress(String(info.text||"AI werkt"),typeof info.progress==="number"?info.progress:null);return;}
      cleanup();
      if(info.type==="result")resolve(info.analysis as Analysis);
      else reject(new Error(String(info.message||"AI-analyse mislukt.")));
    };
    current.addEventListener("message",message);
    current.addEventListener("error",fail);
    current.postMessage({type:"analyze",id,blocks});
  });
}
