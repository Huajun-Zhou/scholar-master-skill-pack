import Link from "next/link";
import { listAllPapers } from "@/lib/wiki-server";

interface PaperSummary {
  paper_id: string;
  title: string;
  year: number | null;
  authors: string[];
  venue: string;
}

export default function PapersPage() {
  const papers = listAllPapers() as unknown as PaperSummary[];
  const byYear: Record<string, PaperSummary[]> = {};
  for (const p of papers) {
    const y = String(p.year || "Unknown");
    if (!byYear[y]) byYear[y] = [];
    byYear[y].push(p);
  }

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="mb-10">
          <Link href="/wiki" className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors">
            ← Wiki
          </Link>
          <h1 className="text-3xl font-serif font-semibold mt-4 mb-2">Paper Cards</h1>
          <p className="text-[var(--text-secondary)]">{papers.length} 篇结构化论文卡片</p>
        </div>
        {Object.entries(byYear)
          .sort(([a], [b]) => (b === "Unknown" ? -1 : a === "Unknown" ? 1 : Number(b) - Number(a)))
          .map(([yearStr, yearPapers]) => (
            <div key={yearStr} className="mb-10">
              <h2 className="text-xl font-serif font-semibold mb-4 text-[var(--color-gold)]">{yearStr}</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {yearPapers.map((paper) => (
                  <Link key={paper.paper_id} href={`/wiki/papers/${paper.paper_id}`}
                    className="block p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:bg-[var(--bg-hover)] transition-all group">
                    <h3 className="text-sm font-medium leading-snug mb-2 group-hover:text-[var(--color-gold)] transition-colors line-clamp-2">{paper.title}</h3>
                    <div className="flex flex-wrap items-center gap-2 text-[0.65rem] text-[var(--text-tertiary)]">
                      <span className="font-mono">{paper.paper_id.slice(-8)}</span>
                      {paper.venue && <span className="truncate max-w-[140px]">{paper.venue.slice(0, 30)}</span>}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
