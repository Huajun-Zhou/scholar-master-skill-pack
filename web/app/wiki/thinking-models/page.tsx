import Link from "next/link";

const THINKING_MODELS = [
  {
    id: "threat-model-driven-security",
    name: "威胁模型驱动的安全设计",
    paperCount: 6,
    description: "定义威胁→安全需求形式化→方案设计→安全证明",
    type: "B 综合归纳",
  },
  {
    id: "hybrid-security-composition",
    name: "混合安全原语组合",
    paperCount: 3,
    description: "分析瓶颈→选择互补原语→设计切换协议→效率+安全",
    type: "B 综合归纳",
  },
  {
    id: "split-architecture-privacy",
    name: "拆分架构隐私保护",
    paperCount: 3,
    description: "确定拆分点→结构拆分→低敏感中间表示传输→隐私天然保护",
    type: "B 综合归纳",
  },
  {
    id: "lightweight-by-design",
    name: "设计即轻量安全",
    paperCount: 2,
    description: "资源约束分析→最小化安全运算→形式化验证→基准优化",
    type: "B 综合归纳",
  },
  {
    id: "physics-data-cps-safety",
    name: "物理+数据融合CPS安全",
    paperCount: 2,
    description: "物理建模→DL异常检测→动态融合→鲁棒安全检测",
    type: "B 综合归纳",
  },
  {
    id: "graph-as-security-lens",
    name: "图即安全透镜",
    paperCount: 3,
    description: "对象图结构化→GNN模式学习→攻防两端验证→跨域迁移",
    type: "B 综合归纳",
  },
];

const MODEL_COLORS = [
  "border-l-[var(--color-evidence-a)]",
  "border-l-[var(--color-evidence-b)]",
  "border-l-[var(--color-gold)]",
  "border-l-[var(--color-blue)]",
  "border-l-[var(--color-green)]",
  "border-l-[var(--color-evidence-c)]",
];

export default async function ThinkingModelsGalleryPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="mb-10">
          <Link
            href="/wiki"
            className="text-sm text-[var(--text-tertiary)] hover:text-[var(--color-gold)] transition-colors"
          >
            ← Wiki
          </Link>
          <h1 className="text-3xl font-serif font-semibold mt-4 mb-2">
            思维模型
          </h1>
          <p className="text-[var(--text-secondary)]">
            {THINKING_MODELS.length} 个可操作科研思维模型 · 从陈志远教授论文中提炼
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {THINKING_MODELS.map((model, index) => (
            <Link
              key={model.id}
              href={`/wiki/thinking-models/${model.id}`}
              className={`
                group relative block p-5 rounded-xl bg-[var(--bg-surface)]
                border border-[var(--border-subtle)] border-l-2
                ${MODEL_COLORS[index % MODEL_COLORS.length]}
                hover:bg-[var(--bg-hover)] hover:border-l-[var(--color-gold)]
                transition-all duration-200
              `}
            >
              {/* Paper count badge */}
              <span className="absolute top-3 right-3 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--bg-elevated)] border border-[var(--border-subtle)] text-[0.6rem] font-mono text-[var(--text-tertiary)]">
                <svg
                  className="w-3 h-3"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
                {model.paperCount}
              </span>

              {/* Type badge */}
              <span className="inline-block text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--color-evidence-b)] border border-[var(--border-subtle)] mb-3">
                {model.type}
              </span>

              <h3 className="text-base font-serif font-semibold mb-2 pr-10 group-hover:text-[var(--color-gold)] transition-colors">
                {model.name}
              </h3>

              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                {model.description}
              </p>
            </Link>
          ))}
        </div>

        {/* Model relationship preview */}
        <div className="mt-12 p-5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">
            模型关系层次
          </h3>
          <div className="space-y-2 text-sm text-[var(--text-tertiary)]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--color-gold)]" />
              <span>顶层方法论：威胁模型驱动的安全设计</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--color-evidence-b)]" />
              <span>设计策略层：拆分架构隐私保护 · 混合安全原语组合 · 设计即轻量安全</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--color-blue)]" />
              <span>应用层：物理+数据融合CPS安全</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[var(--color-evidence-c)]" />
              <span>分析工具层：图即安全透镜</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
