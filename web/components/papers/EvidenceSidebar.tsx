"use client";

import { useState, useMemo, useCallback } from "react";

interface EvidenceEntry {
  evidence_id: string;
  level: "A" | "B" | "C";
  page?: string;
  section?: string;
  claim_type?: string;
}

interface EvidenceSidebarProps {
  evidenceIds: string[];
  evidenceData?: EvidenceEntry[];
  paperId: string;
}

function parseEvidenceId(raw: string): {
  paperPrefix: string;
  category: string;
  level: string;
  shortId: string;
} {
  // Expected format: EVID-<PAPER>-<CATEGORY>-<LEVEL>-<ID>
  // e.g., EVID-CVPR2024-OBS-A-a1b2c3
  const parts = raw.replace("EVID-", "").split("-");
  if (parts.length >= 4) {
    return {
      paperPrefix: parts[0],
      category: parts[1],
      level: parts[2],
      shortId: parts.slice(3).join("-"),
    };
  }
  return {
    paperPrefix: "",
    category: "",
    level: "",
    shortId: raw.slice(-8),
  };
}

function getLevelColor(level: string): string {
  switch (level) {
    case "A":
      return "text-[var(--color-evidence-a)] bg-[var(--color-evidence-a-bg)] border-[var(--color-evidence-a-border)]";
    case "B":
      return "text-[var(--color-evidence-b)] bg-[var(--color-evidence-b-bg)] border-[var(--color-evidence-b-border)]";
    case "C":
      return "text-[var(--color-evidence-c)] bg-[var(--color-evidence-c-bg)] border-[var(--color-evidence-c-border)]";
    default:
      return "text-[var(--text-secondary)] bg-[var(--bg-elevated)] border-[var(--border-default)]";
  }
}

export function EvidenceSidebar({
  evidenceIds,
  evidenceData,
  paperId,
}: EvidenceSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeEvidence, setActiveEvidence] = useState<string | null>(null);

  // Merge explicit evidence data with parsed IDs
  const entries = useMemo<EvidenceEntry[]>(() => {
    if (evidenceData && evidenceData.length > 0) {
      return evidenceData;
    }
    // Derive from raw ID strings
    return evidenceIds.map((rawId) => {
      const parsed = parseEvidenceId(rawId);
      return {
        evidence_id: rawId,
        level: (parsed.level as "A" | "B" | "C") || "B",
        section: parsed.category,
      };
    });
  }, [evidenceIds, evidenceData]);

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return entries;
    const q = searchQuery.toLowerCase();
    return entries.filter(
      (e) =>
        e.evidence_id.toLowerCase().includes(q) ||
        (e.section && e.section.toLowerCase().includes(q)) ||
        (e.claim_type && e.claim_type.toLowerCase().includes(q)) ||
        (e.page && e.page.toLowerCase().includes(q))
    );
  }, [entries, searchQuery]);

  const handleEvidenceClick = useCallback((evidenceId: string) => {
    setActiveEvidence(evidenceId);
    // Try to find the element in the main content and scroll to it
    const el = document.getElementById(evidenceId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("ring-2", "ring-[var(--color-gold)]/50", "rounded-lg");
      setTimeout(() => {
        el.classList.remove("ring-2", "ring-[var(--color-gold)]/50", "rounded-lg");
      }, 2000);
    }
  }, []);

  const getLevelCounts = () => {
    const counts = { A: 0, B: 0, C: 0 };
    entries.forEach((e) => {
      if (e.level in counts) counts[e.level]++;
    });
    return counts;
  };

  const levelCounts = getLevelCounts();

  return (
    <aside className="w-full h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border-subtle)]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Evidence Table
          </h3>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-[var(--color-evidence-a-bg)] text-[var(--color-evidence-a)] border border-[var(--color-evidence-a-border)]">
            {entries.length} EVIDs
          </span>
        </div>

        {/* Level breakdown */}
        <div className="flex gap-2 mb-3">
          {(["A", "B", "C"] as const).map((level) => (
            <span
              key={level}
              className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[0.6rem] font-mono font-semibold ${getLevelColor(level)}`}
            >
              {level}
              <span className="opacity-60">{levelCounts[level]}</span>
            </span>
          ))}
        </div>

        {/* Search / filter */}
        <div className="relative">
          <svg
            className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[var(--text-tertiary)] pointer-events-none"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter evidence..."
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--color-gold)]/40 focus:ring-1 focus:ring-[var(--color-gold)]/20 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
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
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Evidence list */}
      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-xs text-[var(--text-tertiary)]">
              {searchQuery
                ? "No matching evidence found."
                : "No evidence entries available."}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-[var(--border-subtle)]">
            {filtered.map((entry) => {
              const parsed = parseEvidenceId(entry.evidence_id);
              const isActive = activeEvidence === entry.evidence_id;

              return (
                <button
                  key={entry.evidence_id}
                  onClick={() => handleEvidenceClick(entry.evidence_id)}
                  className={`
                    w-full text-left px-4 py-2.5 transition-all duration-150
                    hover:bg-[var(--bg-hover)]
                    ${isActive ? "bg-[var(--bg-hover)]" : ""}
                  `}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`px-1 py-0.5 rounded text-[0.55rem] font-mono font-semibold border ${getLevelColor(entry.level)}`}
                    >
                      {entry.level}
                    </span>
                    <code className="text-[0.65rem] font-mono text-[var(--color-gold)] truncate">
                      {parsed.shortId}
                    </code>
                  </div>
                  <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[0.6rem] text-[var(--text-tertiary)]">
                    {entry.page && (
                      <span>
                        Page{" "}
                        <code className="font-mono text-[var(--text-secondary)]">
                          {entry.page}
                        </code>
                      </span>
                    )}
                    {entry.section && (
                      <span>
                        Section{" "}
                        <code className="font-mono text-[var(--text-secondary)]">
                          {entry.section}
                        </code>
                      </span>
                    )}
                    {entry.claim_type && (
                      <span className="px-1 rounded bg-[var(--bg-elevated)]">
                        {entry.claim_type}
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-[var(--border-subtle)]">
        <p className="text-[0.55rem] text-[var(--text-tertiary)] text-center">
          Click an evidence ID to highlight it in the paper body
        </p>
      </div>
    </aside>
  );
}
