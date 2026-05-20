"use client";

import { useState } from "react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";

interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: string;
}

interface Props {
  agent: string;
  content: string;
  timestamp: string;
  agentIndex: number;
  totalAgents: number;
}

const AGENT_INFO: Record<string, { label: string; icon: string; color: string; role: string }> = {
  methodologist: {
    label: "Methodologist",
    icon: "📐",
    color: "amber",
    role: "方法论专家 — 基于 Scholar Wiki 提出研究方案",
  },
  evidence_inspector: {
    label: "Evidence Inspector",
    icon: "🔍",
    color: "emerald",
    role: "证据检察官 — 独立审计每个 claim 的证据等级",
  },
  skeptic_reviewer: {
    label: "Skeptic Reviewer",
    icon: "⚔",
    color: "rose",
    role: "怀疑论审稿人 — 从多维度攻击方案弱点",
  },
  synthesizer: {
    label: "Synthesizer",
    icon: "📋",
    color: "sky",
    role: "综合报告员 — 整合辩论记录为最终报告",
  },
};

function parseAgentOutput(content: string): {
  toolCalls: ToolCall[];
  cleanText: string;
} {
  const toolCalls: ToolCall[] = [];
  let cleanText = content;

  // Remove FunctionCall blocks: [FunctionCall(id=..., arguments='...', name='...')]
  const fcRegex = /\[FunctionCall\([^\]]*?name='([^']+)'[^\]]*?arguments='(\{[^}]*\})'[^\]]*\)\]/g;
  let match;
  while ((match = fcRegex.exec(content)) !== null) {
    try {
      toolCalls.push({
        name: match[1],
        args: JSON.parse(match[2].replace(/\\"/g, '"')),
      });
    } catch {
      toolCalls.push({ name: match[1], args: {} });
    }
  }
  cleanText = cleanText.replace(/\[FunctionCall\([^\]]*\)\]/g, "");

  // Remove FunctionExecutionResult blocks
  const ferRegex = /\[FunctionExecutionResult\([^\]]*?content='([^']*?)'[^\]]*\)\]/g;
  let ferMatch;
  let resultIdx = 0;
  while ((ferMatch = ferRegex.exec(content)) !== null) {
    const resultText = ferMatch[1].replace(/\\n/g, "\n");
    if (toolCalls[resultIdx]) {
      toolCalls[resultIdx].result = resultText.slice(0, 500);
    }
    resultIdx++;
  }
  cleanText = cleanText.replace(/\[FunctionExecutionResult\([^\]]*\)\]/g, "");

  // Remove raw wiki search results (between "## Scholar Wiki 检索" and next section)
  cleanText = cleanText.replace(/## Scholar Wiki [\w\W]*?(?=## |\n\n#|PROPOSAL_COMPLETE|AUDIT_COMPLETE|ATTACK_COMPLETE|REVISION_COMPLETE|FINAL_REPORT)/g, "");

  // Collapse multiple blank lines
  cleanText = cleanText.replace(/\n{4,}/g, "\n\n\n");

  // Trim
  cleanText = cleanText.trim();

  return { toolCalls, cleanText };
}

export default function AgentMessageCard({
  agent,
  content,
  timestamp,
  agentIndex,
  totalAgents,
}: Props) {
  const [showTools, setShowTools] = useState(false);
  const info = AGENT_INFO[agent] || {
    label: agent,
    icon: "🤖",
    color: "zinc",
    role: "",
  };

  const { toolCalls, cleanText } = parseAgentOutput(content);

  const colorMap: Record<string, string> = {
    amber: "border-amber-500/30 bg-amber-500/5",
    emerald: "border-emerald-500/30 bg-emerald-500/5",
    rose: "border-rose-500/30 bg-rose-500/5",
    sky: "border-sky-500/30 bg-sky-500/5",
    zinc: "border-zinc-700 bg-zinc-900",
  };

  const badgeColorMap: Record<string, string> = {
    amber: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    emerald: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    rose: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    sky: "bg-sky-500/20 text-sky-400 border-sky-500/30",
    zinc: "bg-zinc-700 text-zinc-400 border-zinc-600",
  };

  return (
    <div
      className={`border rounded-xl overflow-hidden transition-all ${colorMap[info.color]}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/50">
        <div className="flex items-center gap-3">
          <span className="text-lg">{info.icon}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-zinc-100">
                {info.label}
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full border ${badgeColorMap[info.color]}`}
              >
                Round {agentIndex}/{totalAgents}
              </span>
            </div>
            <span className="text-xs text-zinc-500">{info.role}</span>
          </div>
        </div>
        <span className="text-xs text-zinc-600">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>

      {/* Tool Calls (collapsible) */}
      {toolCalls.length > 0 && (
        <div className="border-b border-zinc-800/50">
          <button
            onClick={() => setShowTools(!showTools)}
            className="w-full flex items-center gap-2 px-4 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/30 transition-colors"
          >
            <span className={`transform transition-transform ${showTools ? "rotate-90" : ""}`}>
              ▸
            </span>
            <span>🔧 调用了 {toolCalls.length} 个工具</span>
            <span className="text-zinc-600">
              ({toolCalls.map((t) => t.name).join(", ")})
            </span>
          </button>
          {showTools && (
            <div className="px-4 pb-3 space-y-2">
              {toolCalls.map((tc, i) => (
                <div
                  key={i}
                  className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-3 text-xs"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-amber-400 font-mono">{tc.name}</span>
                  </div>
                  <div className="text-zinc-500 font-mono mb-1">
                    {JSON.stringify(tc.args, null, 2).slice(0, 200)}
                  </div>
                  {tc.result && (
                    <div className="text-zinc-400 mt-1 pt-1 border-t border-zinc-800 line-clamp-3">
                      {tc.result}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Content */}
      <div className="px-4 py-4 text-sm text-zinc-300 max-h-[500px] overflow-y-auto">
        {cleanText ? (
          <MarkdownRenderer content={cleanText} />
        ) : (
          <div className="text-zinc-600 italic">执行中...</div>
        )}
      </div>
    </div>
  );
}
