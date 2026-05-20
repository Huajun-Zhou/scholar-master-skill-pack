export interface PaperRelation {
  paper_id: string;
  title: string;
  year: number | null;
}

export interface PaperRelations {
  predecessors?: PaperRelation[];
  successors?: PaperRelation[];
  related?: PaperRelation[];
}

export interface PaperData {
  paper_id: string;
  title: string;
  authors: string[];
  venue: string;
  year: number | null;
  abstract?: string;
  body: string;
  frontmatter: Record<string, unknown>;
  evidence_ids: string[];
  source_papers: string[];
  paper_relations?: PaperRelations;
}

export type EvidenceLevel = "A" | "B" | "C";

export interface EvidenceEntry {
  evidence_id: string;
  level: EvidenceLevel;
  page?: string;
  section?: string;
  claim_type?: string;
}
