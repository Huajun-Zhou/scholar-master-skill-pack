import MiniSearch from "minisearch";
import { create } from "zustand";

/* ─── Types ─── */

export type SearchResultType = "paper" | "method" | "model" | "wiki";

export interface SearchableItem {
  id: string;
  title: string;
  content: string;
  type: SearchResultType;
  href: string;
  evidenceCount: number;
}

/* ─── Zustand store for search dialog UI state ─── */

interface SearchUIState {
  isOpen: boolean;
  open: () => void;
  close: () => void;
}

export const useSearchUI = create<SearchUIState>((set) => ({
  isOpen: false,
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
}));

/* ─── MiniSearch factory ─── */

export function createSearchIndex(): MiniSearch<SearchableItem> {
  return new MiniSearch<SearchableItem>({
    fields: ["title", "content"],
    storeFields: ["title", "content", "type", "href", "evidenceCount"],
    searchOptions: {
      boost: { title: 3 },
      prefix: true,
      fuzzy: 0.2,
    },
    extractField: (doc, fieldName) => {
      const value = doc[fieldName as keyof SearchableItem];
      return value != null ? String(value) : "";
    },
  });
}

/* ─── Group results by type in a consistent order ─── */

const TYPE_ORDER: SearchResultType[] = ["paper", "method", "model", "wiki"];

export function groupResults(
  results: SearchableItem[]
): Map<SearchResultType, SearchableItem[]> {
  const groups = new Map<SearchResultType, SearchableItem[]>();
  for (const type of TYPE_ORDER) {
    groups.set(type, []);
  }
  for (const item of results) {
    const group = groups.get(item.type);
    if (group) group.push(item);
  }
  return groups;
}

/* ─── Snippet extraction (context around match) ─── */

export function getSnippet(content: string, query: string, maxLen = 160): string {
  if (!query.trim() || !content) {
    if (!content) return "";
    return content.length > maxLen ? content.slice(0, maxLen) + "..." : content;
  }

  const lowerContent = content.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const matchIdx = lowerContent.indexOf(lowerQuery);

  if (matchIdx === -1) {
    return content.length > maxLen ? content.slice(0, maxLen) + "..." : content;
  }

  const start = Math.max(0, matchIdx - 50);
  const end = Math.min(content.length, matchIdx + query.length + 80);
  const prefix = start > 0 ? "..." : "";
  const suffix = end < content.length ? "..." : "";
  return prefix + content.slice(start, end) + suffix;
}

/* ─── Get segments for rendering highlighted matches ─── */

export interface HighlightSegment {
  text: string;
  isHighlight: boolean;
}

export function getHighlightedSegments(
  text: string,
  query: string
): HighlightSegment[] {
  if (!query.trim() || !text) {
    return [{ text, isHighlight: false }];
  }

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escaped})`, "gi");
  const parts = text.split(regex);

  return parts.map((part) => ({
    text: part,
    isHighlight: part.toLowerCase() === query.toLowerCase(),
  }));
}

/* ─── API data fetching to build the client-side index ─── */

export interface SearchEndpoint {
  url: string;
  type: SearchResultType;
  idField: string;
  titleField: string;
  contentField: string;
}

const DEFAULT_ENDPOINTS: SearchEndpoint[] = [
  {
    url: "http://localhost:8000/api/papers",
    type: "paper",
    idField: "paper_id",
    titleField: "title",
    contentField: "abstract",
  },
  {
    url: "http://localhost:8000/api/methods",
    type: "method",
    idField: "id",
    titleField: "title",
    contentField: "content",
  },
  {
    url: "http://localhost:8000/api/thinking-models",
    type: "model",
    idField: "id",
    titleField: "title",
    contentField: "content",
  },
  {
    url: "http://localhost:8000/api/wiki",
    type: "wiki",
    idField: "id",
    titleField: "title",
    contentField: "body",
  },
];

function extractArray(data: unknown): unknown[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object") {
    for (const key of ["items", "data", "results", "pages"]) {
      const val = (data as Record<string, unknown>)[key];
      if (Array.isArray(val)) return val;
    }
  }
  return [];
}

function buildHref(type: SearchResultType, id: string): string {
  switch (type) {
    case "paper":
      return `/wiki/papers/${encodeURIComponent(id)}`;
    case "method":
      return `/wiki/methods/${encodeURIComponent(id)}`;
    case "model":
      return `/wiki/thinking-models/${encodeURIComponent(id)}`;
    case "wiki":
      return `/wiki/${encodeURIComponent(id)}`;
  }
}

export async function fetchSearchableItems(
  endpoints?: SearchEndpoint[]
): Promise<SearchableItem[]> {
  const targets = endpoints ?? DEFAULT_ENDPOINTS;
  const results: SearchableItem[] = [];

  await Promise.allSettled(
    targets.map(async (ep) => {
      try {
        const res = await fetch(ep.url, { signal: AbortSignal.timeout(5000) });
        if (!res.ok) return;

        const raw: unknown = await res.json();
        const items = extractArray(raw);

        for (const item of items) {
          if (!item || typeof item !== "object") continue;

          const obj = item as Record<string, unknown>;
          const id = obj[ep.idField] ?? obj.id;
          if (id == null) continue;

          const strId = String(id);
          const title = String(obj[ep.titleField] ?? obj.title ?? "");
          const content = String(
            obj[ep.contentField] ??
              obj.abstract ??
              obj.body ??
              obj.content ??
              obj.description ??
              ""
          );

          const evidenceIds = obj.evidence_ids;
          const evidenceCount = Array.isArray(evidenceIds)
            ? evidenceIds.length
            : typeof obj.evidenceCount === "number"
              ? obj.evidenceCount
              : 0;

          results.push({
            id: `${ep.type}:${strId}`,
            title,
            content,
            type: ep.type,
            href: buildHref(ep.type, strId),
            evidenceCount,
          });
        }
      } catch {
        /* Individual endpoint failures are non-fatal */
      }
    })
  );

  return results;
}
