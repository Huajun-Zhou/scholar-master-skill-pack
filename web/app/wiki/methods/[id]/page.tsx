"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { SectionTabs } from "@/components/method-cards/SectionTabs";
import type { SectionTab } from "@/components/method-cards/SectionTabs";

const METHOD_SECTIONS: SectionTab[] = [
  { id: "definition", label: "方法定义" },
  { id: "source_papers", label: "来源论文" },
  { id: "applicable_problems", label: "适用问题" },
  { id: "core_mechanism", label: "核心机制" },
  { id: "pipeline", label: "典型流程" },
  { id: "input_conditions", label: "输入条件" },
  { id: "output_results", label: "输出结果" },
  { id: "advantages", label: "优势" },
  { id: "limitations", label: "局限" },
  { id: "transfer_plan", label: "迁移方案" },
  { id: "combinations", label: "组合使用" },
  { id: "unsuitable_scenarios", label: "不适用场景" },
];

interface MethodFrontmatter {
  title?: string;
  evidence_level?: string;
  source_papers?: string[];
  page_id?: string;
  page_type?: string;
  status?: string;
  confidence?: string;
  [key: string]: unknown;
}

interface MethodData {
  frontmatter: MethodFrontmatter;
  body: string;
  sections: Record<string, string>;
}

export default function MethodDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<MethodData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState(METHOD_SECTIONS[0].id);

  useEffect(() => {
    fetchData();
  }, [id]);

  async function fetchData() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/methods/${id}`
      );
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("方法卡片未找到");
        }
        throw new Error(`请求失败 (${res.status})`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "加载方法卡片时发生错误"
      );
    } finally {
      setLoading(false);
    }
  }

  // Loading skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)]">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="mb-8 animate-pulse-subtle">
            <div className="h-4 w-20 bg-[var(--bg-elevated)] rounded mb-6" />
            <div className="h-8 w-72 bg-[var(--bg-elevated)] rounded mb-3" />
            <div className="flex gap-2 mb-6">
              <div className="h-5 w-16 bg-[var(--bg-elevated)] rounded" />
              <div className="h-5 w-24 bg-[var(--bg-elevated)] rounded" />
            </div>
            <div className="h-10 w-full bg-[var(--bg-elevated)] rounded mb-8" />
            <div className="space-y-3">
              <div className="h-4 w-full bg-[var(--bg-elevated)] rounded" />
              <div className="h-4 w-5/6 bg-[var(--bg-elevated)] rounded" />
              <div className="h-4 w-4/6 bg-[var(--bg-elevated)] rounded" />
              <div className="h-4 w-full bg-[var(--bg-elevated)] rounded" />
              <div className="h-4 w-3/4 bg-[var(--bg-elevated)] rounded" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)]">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="mb-8">
            <Link
              href="/wiki/methods"
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
            >
              ← 方法卡片
            </Link>
          </div>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-12 h-12 rounded-full bg-[var(--color-evidence-c-bg)] border border-[var(--color-evidence-c-border)] flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6 text-[var(--color-evidence-c)]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <p className="text-[var(--text-secondary)] mb-2">{error}</p>
            <p className="text-xs text-[var(--text-tertiary)] mb-4">
              方法 ID: {id}
            </p>
            <button
              onClick={fetchData}
              className="px-4 py-2 text-sm rounded-lg bg-[var(--bg-surface)] border border-[var(--border-default)] text-[var(--color-gold)] hover:bg-[var(--bg-hover)] transition-colors"
            >
              重新加载
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty state (data loaded but no content)
  if (!data) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)]">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="mb-8">
            <Link
              href="/wiki/methods"
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
            >
              ← 方法卡片
            </Link>
          </div>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-[var(--text-secondary)]">
              该方法卡片数据为空
            </p>
          </div>
        </div>
      </div>
    );
  }

  const fm = data.frontmatter || {};
  const title = (fm.title as string) || id.replace(/-/g, " ");
  const sourcePapers = (fm.source_papers as string[]) || [];
  const evidenceLevel = fm.evidence_level as string | undefined;

  // Filter to only sections that have content
  const availableSections = METHOD_SECTIONS.filter(
    (s) => data.sections?.[s.id]
  );

  // If no sections have content, fall back to rendering the full body
  const useSections = availableSections.length > 0;
  const tabsToRender = useSections ? availableSections : [];

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/wiki/methods"
            className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors inline-flex items-center gap-1"
          >
            <svg
              className="w-3.5 h-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="19" y1="12" x2="5" y2="12" />
              <polyline points="12 19 5 12 12 5" />
            </svg>
            方法卡片
          </Link>

          <h1 className="text-3xl font-serif font-semibold mt-4 mb-3">
            {title}
          </h1>

          {/* Metadata badges */}
          <div className="flex flex-wrap items-center gap-2 mb-4">
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
            {evidenceLevel && (
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-semibold tracking-wide ${
                  evidenceLevel === "A"
                    ? "border-[var(--color-evidence-a)] text-[var(--color-evidence-a)]"
                    : evidenceLevel === "B"
                    ? "border-[var(--color-evidence-b)] text-[var(--color-evidence-b)]"
                    : "border-[var(--color-evidence-c)] text-[var(--color-evidence-c)]"
                }`}
              >
                {evidenceLevel}
              </span>
            )}
            {fm.confidence && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                confidence: {String(fm.confidence)}
              </span>
            )}
          </div>

          {/* Source papers */}
          {sourcePapers.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-[0.6rem] text-[var(--text-tertiary)] mr-1">
                source papers:
              </span>
              {sourcePapers.map((pid: string) => (
                <Link
                  key={pid}
                  href={`/wiki/papers/${pid}`}
                  className="text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:text-[var(--color-gold)] transition-colors"
                >
                  {pid}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Section tabs */}
        {useSections && (
          <SectionTabs
            sections={tabsToRender}
            activeSection={activeSection}
            onSelect={setActiveSection}
          />
        )}

        {/* Content area */}
        <div className="mt-8 bg-[var(--bg-surface)] border border-[var(--border-subtle)] rounded-xl p-6 sm:p-8 min-h-[300px] animate-fade-in">
          {useSections ? (
            // Render active section content
            data.sections?.[activeSection] ? (
              <MarkdownRenderer content={data.sections[activeSection]} />
            ) : (
              <p className="text-[var(--text-tertiary)] italic">
                该章节暂无内容
              </p>
            )
          ) : (
            // Fall back to full body if no sections available
            <MarkdownRenderer content={data.body} />
          )}
        </div>
      </div>
    </div>
  );
}
