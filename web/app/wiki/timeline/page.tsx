"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { PageTransition } from "@/components/common/PageTransition";

/* ------------------------------------------------------------------ */
/*  Types                                                             */
/* ------------------------------------------------------------------ */

interface PaperSummary {
  paper_id: string;
  page_id: string;
  title: string;
  year: number | null;
  authors: string[];
  venue: string;
  status: string;
  evidence_level: string;
  evidence_ids: string[];
  confidence: string;
  char_count: number;
  file: string;
  path: string;
}

interface PapersResponse {
  papers: PaperSummary[];
  total: number;
}

/* ------------------------------------------------------------------ */
/*  Research area classification (paper_id -> area)                   */
/* ------------------------------------------------------------------ */

const RESEARCH_AREA: Record<string, string> = {
  PAPER_BC534646: "Privacy-Preserving ML",
  PAPER_0A8C55F0: "UAV Edge Computing",
  PAPER_9955C321: "Privacy-Preserving ML",
  PAPER_09026E9B: "IIoT Security",
  PAPER_B1C0C91E: "GNN Security",
  PAPER_141EDBB3: "UAV Security",
  PAPER_513EB8C3: "IIoT Blockchain",
  PAPER_F530EB8C: "GNN Security",
  PAPER_34285F47: "GNN Security",
  PAPER_96645819: "IIoT Security",
  PAPER_E155CF85: "UAV Security",
  PAPER_B4EA5A99: "Privacy-Preserving ML",
  PAPER_00BA0203: "Privacy-Preserving ML",
  PAPER_8E699870: "UAV Security",
  PAPER_627CFA0B: "Privacy-Preserving ML",
};

const AREA_COLORS: Record<string, { border: string; bg: string }> = {
  "Privacy-Preserving ML": {
    border: "rgba(196, 78, 82, 0.25)",
    bg: "rgba(196, 78, 82, 0.08)",
  },
  "UAV Edge Computing": {
    border: "rgba(91, 155, 181, 0.25)",
    bg: "rgba(91, 155, 181, 0.08)",
  },
  "IIoT Security": {
    border: "rgba(93, 155, 126, 0.25)",
    bg: "rgba(93, 155, 126, 0.08)",
  },
  "GNN Security": {
    border: "rgba(176, 138, 93, 0.25)",
    bg: "rgba(176, 138, 93, 0.08)",
  },
  "UAV Security": {
    border: "rgba(139, 126, 181, 0.25)",
    bg: "rgba(139, 126, 181, 0.08)",
  },
  "IIoT Blockchain": {
    border: "rgba(76, 154, 110, 0.25)",
    bg: "rgba(76, 154, 110, 0.08)",
  },
};

const RESEARCH_AREAS = Object.keys(AREA_COLORS);
const DOT_COLORS = [
  "bg-[rgba(196,78,82,0.6)]",
  "bg-[rgba(91,155,181,0.6)]",
  "bg-[rgba(93,155,126,0.6)]",
  "bg-[rgba(176,138,93,0.6)]",
  "bg-[rgba(139,126,181,0.6)]",
  "bg-[rgba(76,154,110,0.6)]",
  "bg-[rgba(160,105,75,0.6)]",
];

function getResearchArea(paper_id: string): string {
  // Extract the paper ID key (e.g., "PAPER_XXXX" from any format)
  const match = paper_id.match(/(PAPER_\w+)/);
  const key = match ? match[1] : paper_id;
  return RESEARCH_AREA[key] ?? "General";
}

function getColor(area: string) {
  return AREA_COLORS[area] ?? { border: "rgba(255,255,255,0.1)", bg: "transparent" };
}

function getVenueShort(venue: string): string {
  if (!venue) return "";
  // Extract a short venue abbreviation
  const clean = venue.replace(/,\s*Vol\.\s*\d+.*$/, "").replace(/,\s*\d{4}.*$/, "");
  if (clean.length > 30) return clean.slice(0, 27) + "...";
  return clean;
}

/* ------------------------------------------------------------------ */
/*  Main Page                                                         */
/* ------------------------------------------------------------------ */

export default function TimelinePage() {
  const router = useRouter();
  const [data, setData] = useState<PapersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchPapers() {
      try {
        const res = await fetch("/api/papers");
        if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
        const arr = await res.json();
        const papers = Array.isArray(arr) ? arr : (arr.papers || []);
        const normalized: PapersResponse = {
          papers,
          total: papers.length,
        };
        if (!cancelled) setData(normalized);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchPapers();
    return () => { cancelled = true; };
  }, []);

  const byYear = useMemo(() => {
    if (!data?.papers) return new Map<number, PaperSummary[]>();
    const map = new Map<number, PaperSummary[]>();
    for (const p of data.papers) {
      const y = p.year ?? 0;
      if (!map.has(y)) map.set(y, []);
      map.get(y)!.push(p);
    }
    // Sort years descending
    const sorted = new Map<number, PaperSummary[]>();
    for (const y of [...map.keys()].sort((a, b) => b - a)) {
      sorted.set(y, map.get(y)!);
    }
    return sorted;
  }, [data]);

  const years = useMemo(() => [...byYear.keys()], [byYear]);

  const stats = useMemo(() => {
    if (!data?.papers) return null;
    const total = data.papers.length;
    const minYear = Math.min(...data.papers.map((p) => p.year ?? 0));
    const maxYear = Math.max(...data.papers.map((p) => p.year ?? 0));
    // Top venue
    const venueCount = new Map<string, number>();
    for (const p of data.papers) {
      const v = p.venue.trim();
      if (!v) continue;
      const short = getVenueShort(v);
      venueCount.set(short, (venueCount.get(short) ?? 0) + 1);
    }
    const topVenue = [...venueCount.entries()].sort((a, b) => b[1] - a[1])[0];
    return { total, minYear, maxYear, topVenue };
  }, [data]);

  /* ---- Loading state ---- */
  if (loading) {
    return (
      <PageTransition>
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-6 h-6 rounded-full border-2 border-[var(--color-gold)]/30 border-t-[var(--color-gold)] animate-spin" />
            <p className="text-xs text-[var(--text-tertiary)]">Loading papers...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  /* ---- Error state ---- */
  if (error || !data) {
    return (
      <PageTransition>
        <div className="min-h-[60vh] flex items-center justify-center">
          <div className="text-center">
            <p className="text-sm text-[var(--text-tertiary)] mb-2">
              Failed to load paper data.
            </p>
            <p className="text-xs text-[var(--text-tertiary)]">
              {error ?? "No data available"}
            </p>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-[var(--bg-base)]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
          {/* ---- Header ---- */}
          <div className="mb-8">
            <h1 className="text-2xl sm:text-3xl font-serif font-semibold text-[var(--text-primary)]">
              Research Timeline
            </h1>
            <p className="text-sm text-[var(--text-secondary)] mt-1">
              {data.total} papers &middot; {stats ? `${stats.minYear}–${stats.maxYear}` : ""}
            </p>
          </div>

          {/* ---- Stats row ---- */}
          {stats && (
            <div className="flex flex-wrap gap-3 mb-8">
              <StatBadge label="Total Papers" value={String(stats.total)} />
              <StatBadge
                label="Year Range"
                value={`${stats.minYear}–${stats.maxYear}`}
              />
              {stats.topVenue && (
                <StatBadge
                  label="Top Venue"
                  value={`${stats.topVenue[0]} (${stats.topVenue[1]})`}
                />
              )}
              <div className="flex items-center gap-2 ml-auto">
                <span className="text-[0.6rem] text-[var(--text-tertiary)] uppercase tracking-wider">
                  Areas:
                </span>
                <div className="flex gap-1.5">
                  {RESEARCH_AREAS.map((area, i) => (
                    <span
                      key={area}
                      className="group relative"
                      title={area}
                    >
                      <span className={`block w-2.5 h-2.5 rounded-full ${DOT_COLORS[i]}`} />
                      <span className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2 py-1 rounded bg-[var(--bg-elevated)] border border-[var(--border-subtle)] text-[0.55rem] text-[var(--text-secondary)] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                        {area}
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ---- Desktop: Horizontal Timeline ---- */}
          <div className="hidden md:block overflow-x-auto pb-4 -mx-4 sm:-mx-6">
            <div className="inline-flex gap-6 px-4 sm:px-6 min-w-[700px]">
              {years.map((year) => (
                <YearColumn
                  key={year}
                  year={year}
                  papers={byYear.get(year)!}
                  isCurrent={year === 2026}
                  router={router}
                />
              ))}
            </div>
          </div>

          {/* ---- Mobile: Vertical List ---- */}
          <div className="block md:hidden">
            <div className="space-y-8">
              {years.map((year) => (
                <YearSection
                  key={year}
                  year={year}
                  papers={byYear.get(year)!}
                  isCurrent={year === 2026}
                  router={router}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function StatBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-3 py-1.5 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
      <p className="text-[0.55rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
        {label}
      </p>
      <p className="text-xs font-medium text-[var(--text-primary)] mt-0.5">
        {value}
      </p>
    </div>
  );
}

/* ---- Year Column (Desktop) ---- */

function YearColumn({
  year,
  papers,
  isCurrent,
  router,
}: {
  year: number;
  papers: PaperSummary[];
  isCurrent: boolean;
  router: ReturnType<typeof useRouter>;
}) {
  return (
    <div className="flex flex-col flex-1 min-w-[180px] max-w-[260px]">
      {/* Year header */}
      <div className="relative flex items-center gap-2 pb-4 mb-5 border-b border-[var(--border-subtle)]">
        <span className="text-lg font-serif font-semibold text-[var(--text-primary)]">
          {year}
        </span>
        <span className="text-[0.65rem] text-[var(--text-tertiary)] font-mono">
          {papers.length}
        </span>
        {isCurrent && (
          <span className="absolute left-0 -bottom-[1px] w-full h-0.5 bg-[var(--color-gold)] rounded-full" />
        )}
      </div>

      {/* Cards */}
      <div className="flex flex-col gap-2.5">
        {papers.map((paper, idx) => (
          <PaperCard
            key={paper.paper_id}
            paper={paper}
            router={router}
            index={idx}
          />
        ))}
      </div>
    </div>
  );
}

/* ---- Year Section (Mobile) ---- */

function YearSection({
  year,
  papers,
  isCurrent,
  router,
}: {
  year: number;
  papers: PaperSummary[];
  isCurrent: boolean;
  router: ReturnType<typeof useRouter>;
}) {
  return (
    <div>
      <div className="flex items-center gap-2 pb-3 mb-4 border-b border-[var(--border-subtle)]">
        <span className="text-lg font-serif font-semibold text-[var(--text-primary)]">
          {year}
        </span>
        <span className="text-[0.65rem] text-[var(--text-tertiary)] font-mono">
          {papers.length} papers
        </span>
        {isCurrent && (
          <span className="ml-2 w-2 h-2 rounded-full bg-[var(--color-gold)] animate-pulse-subtle" />
        )}
      </div>
      <div className="space-y-2.5">
        {papers.map((paper, idx) => (
          <PaperCard
            key={paper.paper_id}
            paper={paper}
            router={router}
            index={idx}
          />
        ))}
      </div>
    </div>
  );
}

/* ---- Paper Card ---- */

function PaperCard({
  paper,
  router,
  index,
}: {
  paper: PaperSummary;
  router: ReturnType<typeof useRouter>;
  index: number;
}) {
  const area = getResearchArea(paper.paper_id);
  const color = getColor(area);
  const shortId = paper.paper_id.slice(-8);
  const venueShort = getVenueShort(paper.venue);

  return (
    <motion.button
      onClick={() => router.push(`/wiki/papers/${paper.paper_id}`)}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04, ease: "easeOut" }}
      whileHover={{ y: -2 }}
      className={`
        w-full text-left rounded-lg p-3
        bg-[var(--bg-surface)] border
        hover:border-[var(--color-gold)]/40
        transition-colors duration-200
        cursor-pointer group
      `}
      style={{
        borderLeft: `3px solid ${color.border}`,
      }}
    >
      {/* Title */}
      <h3 className="text-xs font-medium leading-snug text-[var(--text-primary)] group-hover:text-[var(--color-gold)] transition-colors line-clamp-2 mb-1.5">
        {paper.title}
      </h3>

      {/* Meta row */}
      <div className="flex items-center gap-2 text-[0.6rem] text-[var(--text-tertiary)]">
        <span className="font-mono">{shortId}</span>
        {venueShort && (
          <span className="truncate max-w-[120px]">{venueShort}</span>
        )}
      </div>

      {/* Research area pill */}
      <div className="mt-1.5">
        <span
          className="inline-block text-[0.55rem] px-1.5 py-0.5 rounded-full font-mono"
          style={{
            color: color.border.replace("0.25", "0.9"),
            background: color.bg,
          }}
        >
          {area}
        </span>
      </div>
    </motion.button>
  );
}
