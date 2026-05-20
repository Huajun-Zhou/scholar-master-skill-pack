import Link from "next/link";

const METHODS = [
  {
    id: "federated-model-splitting",
    name: "联邦模型拆分与中间表示传输",
    paperCount: 1,
    family: "隐私保护协作学习",
    definition: "如何在垂直分区数据上实现隐私保护异常检测",
  },
  {
    id: "ldp-key-value-collection",
    name: "分段随机响应LDP键值收集",
    paperCount: 1,
    family: "隐私保护协作学习",
    definition: "如何在复合键值数据上平衡LDP隐私和统计精度",
  },
  {
    id: "hybrid-secure-computation",
    name: "混合安全计算架构",
    paperCount: 2,
    family: "混合安全计算",
    definition: "如何消除同态加密的自举瓶颈并保护LLM梯度隐私",
  },
  {
    id: "graph-learning-security-detection",
    name: "图学习安全检测",
    paperCount: 3,
    family: "图学习安全",
    definition: "如何用GNN从代码图结构中检测恶意行为和攻击",
  },
  {
    id: "uav-hybrid-fault-detection",
    name: "物理+DL混合UAV故障检测",
    paperCount: 1,
    family: "UAV安全",
    definition: "如何在UAV实时约束下检测多类型故障",
  },
  {
    id: "marl-secure-communication",
    name: "MARL驱动的安全通信优化",
    paperCount: 1,
    family: "UAV安全",
    definition: "如何在有窃听者的场景下优化多UAV安全通信",
  },
  {
    id: "lightweight-iiot-authentication",
    name: "IIoT轻量级可信认证协议",
    paperCount: 1,
    family: "IIoT可信安全",
    definition: "如何在资源受限设备上实现形式化可证明安全",
  },
];

const FAMILY_COLORS: Record<string, string> = {
  "隐私保护协作学习": "border-l-[var(--color-evidence-a)]",
  "混合安全计算": "border-l-[var(--color-evidence-b)]",
  "图学习安全": "border-l-[var(--color-evidence-c)]",
  "UAV安全": "border-l-[var(--color-gold)]",
  "IIoT可信安全": "border-l-[var(--color-blue)]",
};

function getFamilyColor(family: string): string {
  return FAMILY_COLORS[family] || "border-l-[var(--border-default)]";
}

export default async function MethodsGalleryPage() {
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
            方法卡片
          </h1>
          <p className="text-[var(--text-secondary)]">
            {METHODS.length} 个可迁移方法模块 · 基于陈志远教授 15 篇公开论文炼化
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {METHODS.map((method) => (
            <Link
              key={method.id}
              href={`/wiki/methods/${method.id}`}
              className={`
                group relative block p-5 rounded-xl bg-[var(--bg-surface)]
                border border-[var(--border-subtle)] border-l-2
                ${getFamilyColor(method.family)}
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
                {method.paperCount}
              </span>

              {/* Family tag */}
              <span className="inline-block text-[0.6rem] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-elevated)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] mb-3">
                {method.family}
              </span>

              <h3 className="text-base font-serif font-semibold mb-2 pr-10 group-hover:text-[var(--color-gold)] transition-colors">
                {method.name}
              </h3>

              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                {method.definition}
              </p>
            </Link>
          ))}
        </div>

        {/* Method family legend */}
        <div className="mt-12 p-5 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-subtle)]">
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-3">
            方法族
          </h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(FAMILY_COLORS).map(([family, color]) => (
              <span
                key={family}
                className={`inline-flex items-center gap-2 text-xs text-[var(--text-tertiary)] px-3 py-1.5 rounded-lg bg-[var(--bg-elevated)] border border-[var(--border-subtle)] border-l-2 ${color}`}
              >
                {family}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
