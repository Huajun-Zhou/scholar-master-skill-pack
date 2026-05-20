"use client";

import React, { useMemo } from "react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { EvidenceSidebar } from "@/components/papers/EvidenceSidebar";
import type { PaperData, EvidenceEntry } from "@/lib/types";
import Link from "next/link";

interface PaperCardDetailProps {
  paper: PaperData;
}

/** Extract structured evidence entries from the paper body text. */
function extractEvidenceFromBody(body: string): EvidenceEntry[] {
  const pattern = /\[EVID-([A-Z]+)-([A-Za-z0-9_]+)-([A-Z])-([a-z0-9]+)\]/g;
  const seen = new Set<string>();
  const entries: EvidenceEntry[] = [];
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(body)) !== null) {
    const [, paperPrefix, category, level, shortId] = match;
    const fullId = `EVID-${paperPrefix}-${category}-${level}-${shortId}`;
    if (!seen.has(fullId)) {
      seen.add(fullId);
      entries.push({
        evidence_id: fullId,
        level: level as "A" | "B" | "C",
        section: category,
      });
    }
  }

  return entries;
}

function VenueBadge({ venue }: { venue: string }) {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[0.65rem] font-medium bg-[var(--bg-elevated)] border border-[var(--border-default)] text-[var(--text-secondary)]">
      <svg
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="opacity-60"
      >
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      </svg>
      {venue}
    </span>
  );
}

function RelationLink({ relation }: { relation: { paper_id: string; title: string; year: number | null } }) {
  return (
    <Link
      href={`/wiki/papers/${relation.paper_id}`}
      className="group flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:bg-[var(--bg-hover)] transition-all"
    >
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-[var(--text-primary)] group-hover:text-[var(--color-gold)] transition-colors line-clamp-2 leading-snug">
          {relation.title}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <code className="text-[0.6rem] font-mono text-[var(--text-tertiary)]">
            {relation.paper_id.slice(-8)}
          </code>
          {relation.year && (
            <span className="text-[0.6rem] text-[var(--text-tertiary)]">
              {relation.year}
            </span>
          )}
        </div>
      </div>
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="flex-shrink-0 mt-1 text-[var(--text-tertiary)] group-hover:text-[var(--color-gold)] transition-colors"
      >
        <path d="M5 12h14" />
        <path d="m12 5 7 7-7 7" />
      </svg>
    </Link>
  );
}

function PaperRelationsSection({
  relations,
}: {
  relations: NonNullable<PaperData["paper_relations"]>;
}) {
  const hasAny =
    (relations.predecessors && relations.predecessors.length > 0) ||
    (relations.successors && relations.successors.length > 0) ||
    (relations.related && relations.related.length > 0);

  if (!hasAny) return null;

  return (
    <section className="mt-10 pt-8 border-t border-[var(--border-subtle)]">
      <h2 className="text-lg font-serif font-semibold text-[var(--text-primary)] mb-5">
        Paper Relations
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {relations.predecessors && relations.predecessors.length > 0 && (
          <div>
            <h3 className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)] mb-2.5 flex items-center gap-1.5">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M19 12H5" />
                <path d="m12 19-7-7 7-7" />
              </svg>
              Predecessors
            </h3>
            <div className="space-y-2">
              {relations.predecessors.map((rel) => (
                <RelationLink key={rel.paper_id} relation={rel} />
              ))}
            </div>
          </div>
        )}

        {relations.successors && relations.successors.length > 0 && (
          <div>
            <h3 className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)] mb-2.5 flex items-center gap-1.5">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
              Successors
            </h3>
            <div className="space-y-2">
              {relations.successors.map((rel) => (
                <RelationLink key={rel.paper_id} relation={rel} />
              ))}
            </div>
          </div>
        )}

        {relations.related && relations.related.length > 0 && (
          <div>
            <h3 className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)] mb-2.5 flex items-center gap-1.5">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              Related
            </h3>
            <div className="space-y-2">
              {relations.related.map((rel) => (
                <RelationLink key={rel.paper_id} relation={rel} />
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export function PaperCardDetail({ paper }: PaperCardDetailProps) {
  // Extract structured evidence entries from the body
  const evidenceFromBody = useMemo(
    () => extractEvidenceFromBody(paper.body),
    [paper.body]
  );

  // Merge with any explicit evidence_ids from API
  const allEvidenceIds = useMemo(() => {
    const ids = new Set<string>();
    // Add API-provided IDs first
    paper.evidence_ids?.forEach((id) => ids.add(id));
    // Add body-extracted IDs
    evidenceFromBody.forEach((e) => ids.add(e.evidence_id));
    return Array.from(ids);
  }, [paper.evidence_ids, evidenceFromBody]);

  // Parse frontmatter for extra metadata
  const fm = paper.frontmatter || {};
  const paperIdShort = paper.paper_id?.slice(-8) || "";

  return (
    <div className="flex flex-col lg:flex-row gap-0 lg:gap-0 min-h-screen">
      {/* Main content area (65%) */}
      <div className="flex-1 lg:w-[65%] min-w-0">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 lg:py-10">
          {/* Header metadata */}
          <div className="mb-8">
            {/* Paper ID */}
            <div className="flex items-center gap-2 mb-3">
              <code className="text-[0.65rem] font-mono text-[var(--text-tertiary)] bg-[var(--bg-elevated)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">
                {paperIdShort}
              </code>
              {paper.year && (
                <span className="text-[0.65rem] text-[var(--text-secondary)]">
                  {paper.year}
                </span>
              )}
            </div>

            {/* Title */}
            <h1 className="text-2xl sm:text-3xl font-serif font-semibold text-[var(--text-primary)] leading-tight mb-4">
              {paper.title}
            </h1>

            {/* Authors */}
            {paper.authors && paper.authors.length > 0 && (
              <p className="text-sm text-[var(--text-secondary)] mb-3">
                {paper.authors.join(", ")}
              </p>
            )}

            {/* Venue badge */}
            <div className="flex flex-wrap items-center gap-2">
              {paper.venue && <VenueBadge venue={paper.venue} />}
              {(fm as Record<string, string>).status && (
                <span className="text-[0.65rem] px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                  {(fm as Record<string, string>).status}
                </span>
              )}
              {(fm as Record<string, string>).evidence_level && (
                <span className="text-[0.65rem] px-2 py-0.5 rounded bg-[var(--color-evidence-a-bg)] text-[var(--color-evidence-a)] border border-[var(--color-evidence-a-border)] font-mono">
                  evidence: {(fm as Record<string, string>).evidence_level}
                </span>
              )}
            </div>
          </div>

          {/* Abstract (if available) */}
          {paper.abstract && (
            <div className="mb-8 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-tertiary)] mb-2">
                Abstract
              </h2>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                {paper.abstract}
              </p>
            </div>
          )}

          {/* Paper body */}
          <div className="bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-xl p-5 sm:p-8">
            <MarkdownRenderer content={paper.body} />
          </div>

          {/* Source papers */}
          {paper.source_papers && paper.source_papers.length > 0 && (
            <div className="mt-6 p-4 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
              <h3 className="text-[0.65rem] font-semibold uppercase tracking-wider text-[var(--text-tertiary)] mb-2">
                Source Papers
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {paper.source_papers.map((pid: string) => (
                  <Link
                    key={pid}
                    href={`/wiki/papers/${pid}`}
                    className="text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:text-[var(--color-gold)] transition-colors"
                  >
                    {pid}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Paper relations */}
          {paper.paper_relations && (
            <PaperRelationsSection relations={paper.paper_relations} />
          )}

          {/* Back link */}
          <div className="mt-10 pt-6 border-t border-[var(--border-subtle)]">
            <Link
              href="/wiki/papers"
              className="inline-flex items-center gap-1.5 text-xs text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M19 12H5" />
                <path d="m12 19-7-7 7-7" />
              </svg>
              Back to all paper cards
            </Link>
          </div>
        </div>
      </div>

      {/* Evidence sidebar (35%) — hidden on mobile, shown inline on mobile below content */}
      <div className="hidden lg:block lg:w-[35%] min-w-[300px] max-w-[420px] border-l border-[var(--border-subtle)]">
        <div className="sticky top-0 h-screen overflow-hidden bg-[var(--bg-surface)]">
          <EvidenceSidebar
            evidenceIds={allEvidenceIds}
            evidenceData={evidenceFromBody}
            paperId={paper.paper_id}
          />
        </div>
      </div>

      {/* Mobile evidence section — rendered below the main content */}
      <div className="lg:hidden border-t border-[var(--border-subtle)] bg-[var(--bg-surface)]">
        <div className="max-h-[50vh] overflow-y-auto">
          <EvidenceSidebar
            evidenceIds={allEvidenceIds}
            evidenceData={evidenceFromBody}
            paperId={paper.paper_id}
          />
        </div>
      </div>
    </div>
  );
}
