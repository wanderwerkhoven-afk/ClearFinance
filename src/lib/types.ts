export type SourceBlock = {
  id: string;
  page: number;
  text: string;
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

export type Analysis = {
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
