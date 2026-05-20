"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import Link from "next/link";

interface ReportDetail {
  run_id: string;
  metadata?: Record<string, unknown>;
  artifacts: Record<string, string>;
  agent_conversation: { agent: string; content: string }[];
  gate_history?: { attempt: number; passed: boolean }[];
}

const AGENT_ORDER = [
  "task_decomposer", "scholar_mentor", "method_mapper",
  "thinking_model_agent", "research_designer", "evidence_auditor",
  "risk_reviewer", "revision_planner", "final_writer",
];

export default function ReportDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("conversation");

  useEffect(() => {
    fetch(`/api/reports/${runId}`)
      .then((r) => r.json())
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [runId]);

  if (loading) {
    return <div className="p-8 text-zinc-500">加载中...</div>;
  }

  if (!report) {
    return <div className="p-8 text-zinc-500">报告未找到: {runId}</div>;
  }

  const conversation = (report.agent_conversation || []).sort(
    (a, b) => AGENT_ORDER.indexOf(a.agent) - AGENT_ORDER.indexOf(b.agent)
  );

  const artifactKeys = Object.keys(report.artifacts || {}).filter(
    (k) => !["metadata", "gate_history"].includes(k)
  );

  return (
    <div className="max-w-5xl mx-auto py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link href="/reports" className="text-zinc-500 text-sm hover:text-zinc-300">
            ← 返回报告列表
          </Link>
          <h1 className="text-2xl font-bold text-zinc-100 mt-1">
            {String(report.metadata?.workflow || "运行报告")}
          </h1>
          <p className="text-zinc-500 text-xs font-mono mt-1">{runId}</p>
        </div>

        {/* Gate status */}
        {report.gate_history && report.gate_history.length > 0 && (
          <div className={`px-3 py-1 rounded text-xs ${
            report.gate_history[report.gate_history.length - 1].passed
              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
              : "bg-red-500/10 text-red-400 border border-red-500/20"
          }`}>
            Gate: {report.gate_history[report.gate_history.length - 1].passed ? "通过" : "未通过"}
            {report.gate_history.length > 1 && ` (${report.gate_history.length} 次尝试)`}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-zinc-800 pb-2">
        {[
          { key: "conversation", label: "Agent 对话" },
          { key: "final", label: "最终报告" },
          { key: "artifacts", label: `产物 (${artifactKeys.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-3 py-1.5 rounded text-sm transition-colors
              ${activeTab === tab.key
                ? "bg-zinc-800 text-zinc-100"
                : "text-zinc-500 hover:text-zinc-300"
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === "conversation" && (
        <div className="space-y-4">
          {conversation.map((entry, i) => (
            <div
              key={i}
              className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden"
            >
              <div className="flex items-center justify-between px-4 py-2 bg-zinc-800/50 border-b border-zinc-800">
                <span className="text-amber-400 text-xs font-mono">{entry.agent}</span>
                <span className="text-zinc-600 text-xs">
                  {AGENT_ORDER.indexOf(entry.agent) + 1}/{AGENT_ORDER.length}
                </span>
              </div>
              <div className="p-4 text-zinc-300 text-sm max-h-96 overflow-y-auto">
                <MarkdownRenderer content={entry.content} />
              </div>
            </div>
          ))}

          {conversation.length === 0 && (
            <p className="text-zinc-500 text-sm py-12 text-center">
              暂无 agent 对话记录。工作流可能尚未完成或产物在 artifacts 中。
            </p>
          )}
        </div>
      )}

      {activeTab === "final" && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
          {report.artifacts["final_writer"] ? (
            <div className="prose prose-invert max-w-none">
              <MarkdownRenderer content={report.artifacts["final_writer"]} />
            </div>
          ) : (
            <p className="text-zinc-500 text-sm py-12 text-center">
              未找到 final_writer 输出。查看 Agent 对话了解各阶段产出。
            </p>
          )}
        </div>
      )}

      {activeTab === "artifacts" && (
        <div className="space-y-4">
          {artifactKeys.length === 0 ? (
            <p className="text-zinc-500 text-sm py-12 text-center">无产物文件</p>
          ) : (
            artifactKeys.map((key) => {
              const content = report.artifacts[key];
              const isJSON = key.endsWith(".json") || typeof content === "object";
              return (
                <div
                  key={key}
                  className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden"
                >
                  <div className="px-4 py-2 bg-zinc-800/50 border-b border-zinc-800 text-xs text-zinc-400 font-mono">
                    {key}
                  </div>
                  <div className="p-4 text-zinc-300 text-sm max-h-96 overflow-y-auto">
                    {isJSON ? (
                      <pre className="text-xs font-mono whitespace-pre-wrap">
                        {typeof content === "string" ? content : JSON.stringify(content, null, 2)}
                      </pre>
                    ) : (
                      <MarkdownRenderer content={String(content)} />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
