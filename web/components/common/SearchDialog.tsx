"use client";

import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import * as Dialog from "@radix-ui/react-dialog";
import { motion } from "framer-motion";
import { Search, X, FileText, BookOpen, Brain, Globe } from "lucide-react";
import {
  type SearchableItem,
  type SearchResultType,
  useSearchUI,
  createSearchIndex,
  groupResults,
  getSnippet,
  getHighlightedSegments,
  fetchSearchableItems,
} from "@/lib/search-index";

/* ─── Per-type display config ─── */

interface TypeDisplayConfig {
  label: string;
  labelSingular: string;
  icon: React.ReactNode;
  badgeClass: string;
}

const TYPE_CONFIG: Record<SearchResultType, TypeDisplayConfig> = {
  paper: {
    label: "Papers",
    labelSingular: "Paper",
    icon: <FileText className="w-3.5 h-3.5" />,
    badgeClass:
      "bg-blue-500/10 text-blue-400 border-blue-500/25",
  },
  method: {
    label: "Methods",
    labelSingular: "Method",
    icon: <BookOpen className="w-3.5 h-3.5" />,
    badgeClass:
      "bg-emerald-500/10 text-emerald-400 border-emerald-500/25",
  },
  model: {
    label: "Thinking Models",
    labelSingular: "Model",
    icon: <Brain className="w-3.5 h-3.5" />,
    badgeClass:
      "bg-purple-500/10 text-purple-400 border-purple-500/25",
  },
  wiki: {
    label: "Wiki Pages",
    labelSingular: "Page",
    icon: <Globe className="w-3.5 h-3.5" />,
    badgeClass:
      "bg-amber-500/10 text-amber-400 border-amber-500/25",
  },
};

const TYPE_ORDER: SearchResultType[] = ["paper", "method", "model", "wiki"];

/* ─── Normalize a raw item from a fallback API response ─── */

function normalizeSearchResult(raw: Record<string, unknown>): SearchableItem | null {
  const id = raw.id;
  if (id == null) return null;

  const typeRaw = raw.type;
  const type: SearchResultType =
    typeof typeRaw === "string" &&
    TYPE_ORDER.includes(typeRaw as SearchResultType)
      ? (typeRaw as SearchResultType)
      : "paper";

  const strId = String(id);
  const title = String(raw.title ?? "");
  const content = String(raw.content ?? raw.snippet ?? raw.abstract ?? "");

  let href = String(raw.href ?? "");
  if (!href) {
    href = buildFallbackHref(type, strId);
  }

  const evidenceCount =
    typeof raw.evidenceCount === "number"
      ? raw.evidenceCount
      : Array.isArray(raw.evidence_ids)
        ? raw.evidence_ids.length
        : 0;

  return { id: strId, title, content, type, href, evidenceCount };
}

function buildFallbackHref(type: SearchResultType, id: string): string {
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

/* ─── Component ─── */

export function SearchDialog() {
  const router = useRouter();
  const { isOpen, open, close } = useSearchUI();

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const miniSearchRef = useRef<ReturnType<typeof createSearchIndex> | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const indexBuiltRef = useRef(false);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchableItem[]>([]);
  const [isIndexReady, setIsIndexReady] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);

  /* ── Global keyboard shortcut: Cmd+K / Ctrl+K ── */

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        const state = useSearchUI.getState();
        if (state.isOpen) state.close();
        else state.open();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  /* ── Build client-side MiniSearch index on first open ── */

  useEffect(() => {
    if (!isOpen || indexBuiltRef.current) return;
    indexBuiltRef.current = true;
    setIsIndexing(true);

    const index = createSearchIndex();
    miniSearchRef.current = index;

    fetchSearchableItems()
      .then((items) => {
        if (items.length > 0) {
          index.addAll(items);
        }
        setIsIndexReady(true);
      })
      .catch(() => {
        setIsIndexReady(true);
      })
      .finally(() => {
        setIsIndexing(false);
      });
  }, [isOpen]);

  /* ── Reset search state when dialog opens ── */

  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setResults([]);
      setSelectedIndex(0);
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  }, [isOpen]);

  /* ── Debounced search (200ms) ── */

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const q = query.trim();
    if (!q) {
      setResults([]);
      setSelectedIndex(0);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      const canSearchLocal =
        miniSearchRef.current !== null && isIndexReady;

      if (canSearchLocal) {
        const raw = miniSearchRef.current!.search(q, {
          prefix: true,
          fuzzy: 0.2,
        });
        const items: SearchableItem[] = raw.map((r) => ({
          id: r.id,
          title: ((r as Record<string, unknown>).title as string) ?? "",
          content: ((r as Record<string, unknown>).content as string) ?? "",
          type: ((r as Record<string, unknown>).type as SearchResultType) ?? "paper",
          href: ((r as Record<string, unknown>).href as string) ?? "",
          evidenceCount:
            ((r as Record<string, unknown>).evidenceCount as number) ?? 0,
        }));
        setResults(items);
        setSelectedIndex(0);
      } else {
        /* Fallback: fetch from /api/search?q= */
        try {
          const res = await fetch(
            `/api/search?q=${encodeURIComponent(q)}`,
            { signal: AbortSignal.timeout(5000) }
          );
          if (res.ok) {
            const data: unknown = await res.json();
            const rawItems: unknown[] = Array.isArray(data)
              ? data
              : Array.isArray((data as Record<string, unknown>)?.results)
                ? ((data as Record<string, unknown>).results as unknown[])
                : Array.isArray((data as Record<string, unknown>)?.items)
                  ? ((data as Record<string, unknown>).items as unknown[])
                  : [];

            const items: SearchableItem[] = [];
            for (const r of rawItems) {
              if (r != null && typeof r === "object") {
                const normalized = normalizeSearchResult(
                  r as Record<string, unknown>
                );
                if (normalized) items.push(normalized);
              }
            }

            setResults(items);
            setSelectedIndex(0);
          }
        } catch {
          /* Silent fallback failure — stay empty */
        }
      }
    }, 200);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, isIndexReady]);

  /* ── Keyboard navigation within results ── */

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const total = results.length;
      if (total === 0) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % total);
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + total) % total);
          break;
        case "Enter":
          e.preventDefault();
          const item = results[selectedIndex];
          if (item) {
            close();
            router.push(item.href);
          }
          break;
      }
    },
    [results, selectedIndex, close, router]
  );

  /* ── Scroll selected result into view ── */

  useEffect(() => {
    if (!listRef.current) return;
    const el = listRef.current.querySelector<HTMLElement>(
      `[data-index="${selectedIndex}"]`
    );
    el?.scrollIntoView({ block: "nearest" });
  }, [selectedIndex]);

  /* ── Group results by type for rendering ── */

  const groupedResults = useMemo(() => {
    const groups = groupResults(results);
    const entries: { type: SearchResultType; items: SearchableItem[] }[] = [];
    for (const type of TYPE_ORDER) {
      const items = groups.get(type);
      if (items && items.length > 0) {
        entries.push({ type, items });
      }
    }
    return entries;
  }, [results]);

  /* ── Derived booleans ── */

  const hasQuery = query.trim().length > 0;
  const hasResults = results.length > 0;
  const isEmptyQuery = !hasQuery;
  const showLoading = isIndexing && !isIndexReady;
  const showSearchSpinner = hasQuery && !isIndexReady && !isIndexing;
  const showNoResults = hasQuery && !hasResults && !isIndexing && isIndexReady;
  const showEmptyState = isEmptyQuery && !showLoading;

  /* ── Navigate to result ── */

  const navigateTo = useCallback(
    (item: SearchableItem) => {
      close();
      router.push(item.href);
    },
    [close, router]
  );

  /* ── Render ── */

  return (
    <Dialog.Root
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) close();
      }}
    >
      <Dialog.Portal>
        {/* ── Overlay / Backdrop ── */}
        <Dialog.Overlay asChild>
          <motion.div
            className="fixed inset-0 z-50 bg-[#0A0A0F]/80 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
          />
        </Dialog.Overlay>

        {/* ── Dialog Panel ── */}
        <Dialog.Content asChild>
          <motion.div
            className="fixed inset-0 z-50 flex items-start justify-center pt-[12vh] outline-none"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            onKeyDown={handleKeyDown}
          >
            <Dialog.Title className="sr-only">Search Scholar Wiki</Dialog.Title>
            <Dialog.Description className="sr-only">
              Search across papers, methods, thinking models, and wiki pages
            </Dialog.Description>
            <div className="w-full max-w-2xl mx-4 card-floating overflow-hidden">
              {/* ── Search Input Row ── */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-subtle)]">
                <Search className="w-5 h-5 text-[var(--text-tertiary)] flex-shrink-0" />

                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search papers, methods, thinking models..."
                  className="flex-1 bg-transparent text-base sm:text-lg text-[var(--text-primary)] placeholder-[var(--text-tertiary)] outline-none border-none"
                />

                {/* Clear button (visible when query is non-empty) */}
                {hasQuery && (
                  <button
                    onClick={() => setQuery("")}
                    className="p-1 rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-colors"
                    aria-label="Clear search"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}

                {/* Close button */}
                <Dialog.Close asChild>
                  <button
                    className="p-[5px] rounded-md text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-colors"
                    aria-label="Close search"
                  >
                    <X className="w-[18px] h-[18px]" />
                  </button>
                </Dialog.Close>
              </div>

              {/* ── Results Area ── */}
              <div
                ref={listRef}
                className="max-h-[55vh] overflow-y-auto overscroll-contain py-1"
              >
                {/* Loading shimmer (building index) */}
                {showLoading && (
                  <div className="px-5 py-6 space-y-3">
                    <div className="h-2.5 bg-[var(--bg-hover)] rounded animate-pulse w-3/5" />
                    <div className="h-2 bg-[var(--bg-hover)] rounded animate-pulse w-full" />
                    <div className="h-2 bg-[var(--bg-hover)] rounded animate-pulse w-4/5" />
                  </div>
                )}

                {/* Loading shimmer (search fallback) */}
                {showSearchSpinner && (
                  <div className="px-5 py-6 space-y-3">
                    <div className="h-2.5 bg-[var(--bg-hover)] rounded animate-pulse w-2/5" />
                    <div className="h-2 bg-[var(--bg-hover)] rounded animate-pulse w-4/5" />
                    <div className="h-2 bg-[var(--bg-hover)] rounded animate-pulse w-3/5" />
                  </div>
                )}

                {/* Empty state: no query typed yet */}
                {showEmptyState && (
                  <div className="flex flex-col items-center gap-3 py-12 text-center">
                    <div className="w-10 h-10 rounded-full bg-[var(--bg-hover)] flex items-center justify-center">
                      <Search className="w-5 h-5 text-[var(--text-tertiary)] opacity-50" />
                    </div>
                    <p className="text-sm text-[var(--text-tertiary)]">
                      Search papers, methods, thinking models...
                    </p>
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 text-[11px] font-mono rounded-md bg-[var(--bg-hover)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                      ⌘K
                    </span>
                  </div>
                )}

                {/* Empty results: query did not match anything */}
                {showNoResults && (
                  <div className="flex flex-col items-center gap-2 py-12 text-center">
                    <p className="text-sm text-[var(--text-tertiary)]">
                      No results for{" "}
                      <span className="text-[var(--text-secondary)] font-medium">
                        &ldquo;{query}&rdquo;
                      </span>
                    </p>
                    <p className="text-xs text-[var(--text-tertiary)] opacity-50">
                      Try different keywords or browse the wiki
                    </p>
                  </div>
                )}

                {/* Grouped result list */}
                {hasResults &&
                  groupedResults.map(({ type, items }) => (
                    <div key={type}>
                      {/* Group header */}
                      <div className="flex items-center gap-2 px-5 py-1.5 mt-1">
                        <span className="text-[var(--text-tertiary)]">
                          {TYPE_CONFIG[type].icon}
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--text-tertiary)]">
                          {TYPE_CONFIG[type].label}
                        </span>
                        <span className="text-[10px] text-[var(--text-tertiary)] opacity-30">
                          {items.length}
                        </span>
                      </div>

                      {/* Result items */}
                      {items.map((item) => {
                        const globalIdx = results.indexOf(item);
                        const isSelected = globalIdx === selectedIndex;
                        const snippet = getSnippet(item.content, query);
                        const titleSegments = getHighlightedSegments(
                          item.title,
                          query
                        );

                        return (
                          <button
                            key={item.id}
                            data-index={globalIdx}
                            onClick={() => navigateTo(item)}
                            className={[
                              "w-full text-left px-5 py-2.5 transition-colors duration-75 border-l-2",
                              isSelected
                                ? "border-[var(--color-gold)]"
                                : "border-transparent hover:bg-[var(--bg-hover)]",
                            ].join(" ")}
                            style={
                              isSelected
                                ? { backgroundColor: "rgba(201, 168, 76, 0.08)" }
                                : undefined
                            }
                          >
                            {/* Title row */}
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className="text-sm font-medium text-[var(--text-primary)] truncate">
                                {titleSegments.map((seg, i) =>
                                  seg.isHighlight ? (
                                    <mark
                                      key={i}
                                      className="bg-[var(--color-gold)]/20 text-[var(--color-gold-bright)] rounded-sm px-0.5 not-italic"
                                    >
                                      {seg.text}
                                    </mark>
                                  ) : (
                                    <span key={i}>{seg.text}</span>
                                  )
                                )}
                              </span>

                              {/* Type badge */}
                              <span
                                className={[
                                  "flex-shrink-0 text-[10px] font-medium px-1.5 py-[1px] rounded border",
                                  TYPE_CONFIG[type].badgeClass,
                                ].join(" ")}
                              >
                                {TYPE_CONFIG[type].labelSingular}
                              </span>

                              {/* Evidence count */}
                              {item.evidenceCount > 0 && (
                                <span className="flex-shrink-0 text-[10px] text-[var(--text-tertiary)]">
                                  {item.evidenceCount} evid.
                                </span>
                              )}
                            </div>

                            {/* Snippet */}
                            {snippet && (
                              <p className="text-xs text-[var(--text-tertiary)] leading-relaxed line-clamp-1">
                                {renderHighlightedSnippet(snippet, query)}
                              </p>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  ))}

                {/* Bottom keyboard shortcut hint */}
                {hasResults && (
                  <div className="flex items-center justify-center gap-4 py-2.5 border-t border-[var(--border-subtle)] mt-1">
                    <span className="flex items-center gap-1 text-[10px] text-[var(--text-tertiary)]">
                      <kbd className="px-1 py-[1px] rounded bg-[var(--bg-hover)] border border-[var(--border-subtle)] font-mono text-[10px]">
                        ↑↓
                      </kbd>
                      navigate
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-[var(--text-tertiary)]">
                      <kbd className="px-1 py-[1px] rounded bg-[var(--bg-hover)] border border-[var(--border-subtle)] font-mono text-[10px]">
                        ↵
                      </kbd>
                      open
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-[var(--text-tertiary)]">
                      <kbd className="px-1 py-[1px] rounded bg-[var(--bg-hover)] border border-[var(--border-subtle)] font-mono text-[10px]">
                        esc
                      </kbd>
                      close
                    </span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

/* ─── Render snippet with highlighted query terms ─── */

function renderHighlightedSnippet(
  snippet: string,
  query: string
): React.ReactNode {
  if (!query.trim()) {
    return <>{snippet}</>;
  }

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escaped})`, "gi");
  const parts = snippet.split(regex);

  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <mark
            key={i}
            className="bg-[var(--color-gold)]/20 text-[var(--color-gold-bright)] rounded-sm px-0.5 not-italic"
          >
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}
