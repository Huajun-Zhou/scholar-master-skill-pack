import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import Link from "next/link";
import { getWikiIndex } from "@/lib/wiki-server";

export const dynamic = "force-dynamic";

export default function WikiPage() {
  const data = getWikiIndex();

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-10">
          <Link
            href="/chat"
            className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
          >
            ← 返回对话
          </Link>
          <h1 className="text-3xl font-serif font-semibold mt-4 mb-2">
            Scholar Wiki
          </h1>
          <p className="text-[var(--text-secondary)]">
            陈志远教授学术知识库 — 15 篇论文 · 7 个方法卡片 · 6 个思维模型
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <QuickCard
            href="/wiki/papers"
            title="论文卡片"
            desc="15 篇结构化 Paper Card"
            accent="gold"
          />
          <QuickCard
            href="/wiki/methods"
            title="方法卡片"
            desc="7 张完整 Method Card"
            accent="silver"
          />
          <QuickCard
            href="/wiki/thinking-models"
            title="思维模型"
            desc="6 个 Thinking Model"
            accent="bronze"
          />
          <QuickCard
            href="/wiki/timeline"
            title="研究时间线"
            desc="2025-2026 论文年表"
            accent="blue"
          />
        </div>

        <div className="mt-12">
          <h2 className="text-xl font-serif font-semibold mb-4">快速链接</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[
              ["研究问题", "research_questions"],
              ["术语表", "glossary"],
              ["开放问题", "open_questions"],
              ["局限性", "limitations"],
              ["矛盾候选", "contradictions"],
              ["证据标准", "synthesis/evidence_standards"],
              ["问题定义模式", "synthesis/problem_framing_patterns"],
              ["方法演化", "synthesis/method_evolution"],
              ["研究主线", "synthesis/research_lines"],
              ["研究范式", "research_paradigm"],
              ["研究手册", "synthesis/research_playbook"],
            ].map(([label, slug]) => (
              <Link
                key={slug}
                href={`/wiki/${slug}`}
                className="block p-3 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-subtle)] hover:border-[var(--color-gold)]/30 hover:bg-[var(--bg-hover)] transition-all text-sm"
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickCard({
  href,
  title,
  desc,
  accent,
}: {
  href: string;
  title: string;
  desc: string;
  accent: "gold" | "silver" | "bronze" | "blue";
}) {
  const accentColors = {
    gold: "border-l-[var(--color-evidence-a)]",
    silver: "border-l-[var(--color-evidence-b)]",
    bronze: "border-l-[var(--color-evidence-c)]",
    blue: "border-l-[var(--color-blue)]",
  };

  return (
    <Link
      href={href}
      className={`block p-5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)] border-l-2 ${accentColors[accent]} hover:bg-[var(--bg-hover)] hover:border-l-[var(--color-gold)] transition-all`}
    >
      <h3 className="font-serif font-semibold text-lg mb-1">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)]">{desc}</p>
    </Link>
  );
}
