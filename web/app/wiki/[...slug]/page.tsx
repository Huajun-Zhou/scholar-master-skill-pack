import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import Link from "next/link";
import { notFound } from "next/navigation";

interface WikiPageData {
  frontmatter: Record<string, unknown>;
  body: string;
  html: string;
  evidence_ids: string[];
  source_papers: string[];
}

async function getWikiPage(slug: string[]): Promise<WikiPageData | null> {
  try {
    const path = slug.join("/");
    const res = await fetch(
      `/api/wiki/${path}`,
      { next: { revalidate: 60 } }
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function WikiSlugPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const { slug } = await params;
  const data = await getWikiPage(slug);

  if (!data) {
    notFound();
  }

  const fm = (data.frontmatter || {}) as Record<string, string | string[]>;
  const title = (fm.title as string) || slug[slug.length - 1] || "Wiki";

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="mb-8">
          <Link
            href="/wiki"
            className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
          >
            ← Wiki
          </Link>
          <h1 className="text-3xl font-serif font-semibold mt-4 mb-3">{title}</h1>

          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2 mb-6">
            {fm.page_type && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                {String(fm.page_type)}
              </span>
            )}
            {fm.status && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                {String(fm.status)}
              </span>
            )}
            {fm.evidence_level && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                evidence: {String(fm.evidence_level)}
              </span>
            )}
            {data.evidence_ids && data.evidence_ids.length > 0 && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--color-evidence-a-bg)] text-[var(--color-evidence-a)] font-mono">
                {data.evidence_ids.length} EVIDs
              </span>
            )}
          </div>

          {/* Source papers */}
          {data.source_papers && data.source_papers.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-6">
              {data.source_papers.slice(0, 10).map((pid: string) => (
                <Link
                  key={pid}
                  href={`/wiki/papers/${pid}`}
                  className="text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:text-[var(--color-gold)] transition-colors"
                >
                  {pid}
                </Link>
              ))}
              {data.source_papers.length > 10 && (
                <span className="text-[0.6rem] text-[var(--text-tertiary)]">
                  +{data.source_papers.length - 10} more
                </span>
              )}
            </div>
          )}
        </div>

        {/* Page content */}
        <div className="bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-xl p-6 sm:p-8">
          <MarkdownRenderer content={data.body} />
        </div>

        {/* Related pages */}
        {fm.related_pages && Array.isArray(fm.related_pages) && (fm.related_pages as string[]).length > 0 && (
          <div className="mt-8 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
            <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
              Related Pages
            </h3>
            <div className="flex flex-wrap gap-2">
              {(fm.related_pages as string[]).map((rp: string) => {
                const path = rp.replace(/\.\.?\//g, "").replace(/\.md$/, "");
                return (
                  <Link
                    key={rp}
                    href={`/wiki/${path}`}
                    className="text-xs px-2 py-1 rounded bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--color-gold)] border border-[var(--border-subtle)] hover:border-[var(--border-accent)] transition-colors"
                  >
                    {path.split("/").pop()?.replace(/-/g, " ") || rp}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
