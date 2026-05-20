import Link from "next/link";

const WORKFLOW_CARDS = [
  {
    href: "/studio/design",
    title: "学者委员会",
    description: "4 角色 × 3 轮辩论。Methodologist 提案 → Evidence Inspector ∥ Skeptic Reviewer 并行挑战 → 回应修订 → 最终报告。",
    icon: "⚖",
    agentCount: 4,
    color: "amber",
    badge: "推荐",
  },
  {
    href: "/studio/ask",
    title: "学者问答",
    description: "向 Scholar Skill 提问，获取 A/B/C 三级证据的严谨回答。",
    icon: "?",
    agentCount: 4,
    color: "emerald",
  },
  {
    href: "/studio/critique",
    title: "论文审查",
    description: "按陈志远教授的安全实证标准审查论文，产出 Must Fix / Should Fix 分类建议。",
    icon: "◇",
    agentCount: 6,
    color: "sky",
  },
];

export default function StudioPage() {
  return (
    <div className="max-w-4xl mx-auto py-12">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-zinc-100 mb-3">研究工作室</h1>
        <p className="text-zinc-400 max-w-xl mx-auto">
          选择工作流类型，AutoGen 多智能体系统将基于陈志远教授 15 篇公开论文的知识库，
          为你执行完整的科研辅助流程
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {WORKFLOW_CARDS.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="group bg-zinc-900 border border-zinc-800 rounded-xl p-6
                       hover:border-amber-500/30 hover:bg-zinc-800/50
                       transition-all duration-200 relative"
          >
            {card.badge && (
              <span className="absolute top-3 right-3 px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full border border-amber-500/30">
                {card.badge}
              </span>
            )}
            <span className="text-3xl">{card.icon}</span>
            <h2 className="text-lg font-semibold text-zinc-100 mt-4 mb-2">
              {card.title}
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed">{card.description}</p>
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-zinc-800">
              <span className="text-xs text-zinc-500">{card.agentCount} agents</span>
              <span className="text-xs text-amber-400 ml-auto group-hover:translate-x-1 transition-transform">
                进入 →
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
