export type SourceBlock = {
  id: string;
  page: number;
  text: string;
  section?: string | null;
  kind?: string | null;
  bbox?: { l: number; t: number; r: number; b: number; origin: string } | null;
};

export type SummaryPoint = {
  id: string;
  text: string;
  sourceIds: string[];
};

export type SummarySection = {
  title: string;
  points: SummaryPoint[];
};

export type SummaryAudit = {
  method: string;
  promptVersion?: string;
  retrieval?: string;
  processedBlocks?: number;
  totalBlocks?: number;
  modelCalls?: number;
  complete?: boolean;
  warnings?: string[];
  coverageRatio?: number;
};

export type Analysis = {
  audit?: SummaryAudit;
  headline: string;
  introduction: string;
  sections: SummarySection[];
  keyTerms: { term: string; explanation: string }[];
  mode: "ai" | "local" | "demo";
  limited: boolean;
};

export type StoredDocument = {
  id: string;
  name: string;
  size: number;
  type: "pdf" | "txt";
  createdAt: number;
  pageCount: number;
  blocks: SourceBlock[];
  binary?: ArrayBuffer;
  analysis?: Analysis;
};

export type Answer = {
  text: string;
  sourceIds: string[];
  mode: "ai" | "local";
};
