"use client";

import { useState, useEffect, use, useRef } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { SectionTabs } from "@/components/method-cards/SectionTabs";
import type { SectionTab } from "@/components/method-cards/SectionTabs";

const THINKING_MODEL_SECTIONS: SectionTab[] = [
  { id: "name", label: "思维模型名称" },
  { id: "description", label: "模型描述" },
  { id: "evidence", label: "证据来源" },
  { id: "reasoning_chain", label: "典型推理链" },
  { id: "applicable_scenarios", label: "适用场景" },
  { id: "unsuitable_scenarios", label: "不适用场景" },
  { id: "transfer_template", label: "迁移模板" },
  { id: "example_transfer", label: "示例迁移" },
  { id: "relationships", label: "模型间关系" },
  { id: "evidence_level", label: "证据等级" },
];

/* ---------- Reasoning Chain Flow Diagram ---------- */

const CHAIN_NODES = [
  {
    step: 1,
    label: "现象/缺口",
    subtitle: "Observed phenomenon or gap",
    description: "定位系统中表现异常的环节或未被满足的需求缺口",
    color: "from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-300",
    accent: "rgb(34, 211, 238)",
  },
  {
    step: 2,
    label: "问题重构",
    subtitle: "Problem reframing",
    description: "将表象重新定义为一个可操作的结构化问题",
    color:
      "from-teal-500/20 to-emerald-500/10 border-teal-500/30 text-teal-300",
    accent: "rgb(45, 212, 191)",
  },
  {
    step: 3,
    label: "关键假设",
    subtitle: "Key hypothesis",
    description: "提出可验证的核心假设，指导方法设计方向",
    color:
      "from-emerald-500/20 to-green-500/10 border-emerald-500/30 text-emerald-300",
    accent: "rgb(52, 211, 153)",
  },
  {
    step: 4,
    label: "方法机制",
    subtitle: "Method mechanism",
    description: "设计具有明确功能边界的创新模块或算法",
    color:
      "from-amber-500/20 to-yellow-500/10 border-amber-500/30 text-amber-300",
    accent: "rgb(251, 191, 36)",
  },
  {
    step: 5,
    label: "实验验证",
    subtitle: "Experimental validation",
    description: "消融实验证明瓶颈改进带来的边际增益",
    color:
      "from-orange-500/20 to-red-500/10 border-orange-500/30 text-orange-300",
    accent: "rgb(251, 146, 60)",
  },
  {
    step: 6,
    label: "贡献表述",
    subtitle: "Contribution statement",
    description: "揭示了XX系统中的XX瓶颈，提出了XX模块实现性能突破",
    color:
      "from-[var(--color-gold-dim)]/20 to-[var(--color-gold)]/10 border-[var(--color-gold-dim)]/30 text-[var(--color-gold)]",
    accent: "var(--color-gold)",
  },
];

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line
        x1="12"
        y1="4"
        x2="12"
        y2="40"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <polyline
        points="6,32 12,40 18,32"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ReasoningChainFlow() {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={containerRef} className="py-8 px-2">
      <div className="flex flex-col items-center gap-0">
        {CHAIN_NODES.map((node, index) => (
          <div key={node.step} className="flex flex-col items-center">
            {/* Node */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{
                duration: 0.5,
                delay: index * 0.15,
                ease: "easeOut",
              }}
              className={`
                relative w-full max-w-md rounded-xl border bg-gradient-to-r
                ${node.color}
                p-4 backdrop-blur-sm
              `}
            >
              {/* Step number */}
              <span
                className="absolute -top-2.5 -left-2.5 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2"
                style={{
                  backgroundColor: "var(--bg-base)",
                  borderColor: node.accent,
                  color: node.accent,
                }}
              >
                {node.step}
              </span>

              {/* Title */}
              <h4 className="text-sm font-semibold mb-0.5">{node.label}</h4>

              {/* Subtitle */}
              <p className="text-[0.65rem] font-mono opacity-60 mb-1.5">
                {node.subtitle}
              </p>

              {/* Description */}
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                {node.description}
              </p>
            </motion.div>

            {/* Arrow connector */}
            {index < CHAIN_NODES.length - 1 && (
              <motion.div
                initial={{ opacity: 0, scaleY: 0 }}
                whileInView={{ opacity: 1, scaleY: 1 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{
                  duration: 0.4,
                  delay: index * 0.15 + 0.25,
                  ease: "easeOut",
                }}
                className="text-[var(--color-gold-dim)]/50"
                style={{ transformOrigin: "top" }}
              >
                <ArrowIcon className="w-5 h-10" />
              </motion.div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- Page Component ---------- */

interface ThinkingModelFrontmatter {
  title?: string;
  evidence_level?: string;
  source_papers?: string[];
  page_id?: string;
  page_type?: string;
  confidence?: string;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

interface ThinkingModelData {
  frontmatter: ThinkingModelFrontmatter;
  body: string;
  sections: Record<string, string>;
}

export default function ThinkingModelDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<ThinkingModelData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState(
    THINKING_MODEL_SECTIONS[0].id
  );

  useEffect(() => {
    fetchData();
  }, [id]);

  async function fetchData() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/thinking-models/${id}`
      );
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error("思维模型未找到");
        }
        throw new Error(`请求失败 (${res.status})`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "加载思维模型时发生错误"
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
            <div className="h-4 w-24 bg-[var(--bg-elevated)] rounded mb-6" />
            <div className="h-8 w-80 bg-[var(--bg-elevated)] rounded mb-3" />
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
              href="/wiki/thinking-models"
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
            >
              ← 思维模型
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
              Model ID: {id}
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

  // Empty state
  if (!data) {
    return (
      <div className="min-h-screen bg-[var(--bg-base)]">
        <div className="max-w-4xl mx-auto px-6 py-12">
          <div className="mb-8">
            <Link
              href="/wiki/thinking-models"
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
            >
              ← 思维模型
            </Link>
          </div>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-[var(--text-secondary)]">
              该思维模型数据为空
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
  const availableSections = THINKING_MODEL_SECTIONS.filter(
    (s) => data.sections?.[s.id]
  );
  const useSections = availableSections.length > 0;
  const tabsToRender = useSections ? availableSections : [];

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/wiki/thinking-models"
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
            思维模型
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
            {fm.updated_at && (
              <span className="text-xs px-2 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)]">
                updated: {String(fm.updated_at)}
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
            activeSection === "reasoning_chain" ? (
              // Reasoning chain: show flow diagram + text content
              <div>
                <ReasoningChainFlow />
                {data.sections?.reasoning_chain && (
                  <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
                    <h3 className="text-sm font-semibold text-[var(--text-tertiary)] mb-3 uppercase tracking-wider">
                      详细推理
                    </h3>
                    <MarkdownRenderer
                      content={data.sections.reasoning_chain}
                    />
                  </div>
                )}
              </div>
            ) : data.sections?.[activeSection] ? (
              <MarkdownRenderer content={data.sections[activeSection]} />
            ) : (
              <p className="text-[var(--text-tertiary)] italic">
                该章节暂无内容
              </p>
            )
          ) : (
            <MarkdownRenderer content={data.body} />
          )}
        </div>
      </div>
    </div>
  );
}
