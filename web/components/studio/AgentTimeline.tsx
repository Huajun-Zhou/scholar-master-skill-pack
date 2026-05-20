"use client";

import type { AgentMessage } from "@/lib/studio-store";

const AGENT_ORDER: Record<string, number> = {
  // Committee agents
  methodologist: 1,
  evidence_inspector: 2,
  skeptic_reviewer: 3,
  synthesizer: 4,
  // Legacy 9-agent pipeline
  task_decomposer: 0,
  scholar_mentor: 5,
  method_mapper: 6,
  thinking_model_agent: 7,
  research_designer: 8,
  evidence_auditor: 9,
  risk_reviewer: 10,
  revision_planner: 11,
  final_writer: 12,
};

const AGENT_LABELS: Record<string, string> = {
  // Committee agents
  methodologist: "Methodologist 提案",
  evidence_inspector: "证据检察官",
  skeptic_reviewer: "怀疑论审稿",
  synthesizer: "最终报告",
  // Legacy agents
  task_decomposer: "任务拆解",
  scholar_mentor: "博导方法论",
  method_mapper: "方法映射",
  thinking_model_agent: "思维模型",
  research_designer: "研究设计",
  evidence_auditor: "证据审计",
  risk_reviewer: "审稿风险",
  revision_planner: "修改规划",
  final_writer: "最终报告",
};

interface Props {
  messages: AgentMessage[];
  isRunning: boolean;
}

export default function AgentTimeline({ messages, isRunning }: Props) {
  const completedAgents = new Set(messages.map((m) => m.agent));

  return (
    <div className="flex flex-col gap-1 w-64 shrink-0">
      {Object.entries(AGENT_LABELS)
        .sort(([, a], [, b]) => (AGENT_ORDER[a] ?? 99) - (AGENT_ORDER[b] ?? 99))
        .map(([agent, label]) => {
          const isCompleted = completedAgents.has(agent);
          const isActive = isRunning && !isCompleted && completedAgents.size > 0;
          const isLastCompleted =
            messages.length > 0 && messages[messages.length - 1]?.agent === agent;

          return (
            <div
              key={agent}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-all
                ${isLastCompleted
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  : isCompleted
                    ? "text-zinc-400"
                    : isActive
                      ? "text-zinc-200 animate-pulse"
                      : "text-zinc-600"
                }`}
            >
              <span className="text-xs w-5 shrink-0">
                {isLastCompleted ? "●" : isCompleted ? "✓" : isActive ? "○" : "·"}
              </span>
              <span className="truncate">{label}</span>
            </div>
          );
        })}
    </div>
  );
}
