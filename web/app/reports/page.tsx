"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface ReportItem {
  run_id: string;
  workflow: string;
  created_at: string;
  n_messages: number;
  agents_responded: string[];
  gate_passed?: boolean;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    fetch("/api/reports")
      .then((r) => r.json())
      .then((data) => {
        setReports(data.reports || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = filter === "all"
    ? reports
    : reports.filter((r) => r.workflow.includes(filter));

  const workflowLabel = (w: string) => {
    if (w.includes("design")) return "研究设计";
    if (w.includes("ask")) return "学者问答";
    if (w.includes("critique")) return "论文审查";
    return w;
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-2xl font-bold text-zinc-100 mb-2">运行报告</h1>
      <p className="text-zinc-400 text-sm mb-6">AutoGen 工作流历史记录</p>

      {/* 筛选 */}
      <div className="flex gap-2 mb-6">
        {["all", "design", "ask", "critique"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded text-xs transition-colors
              ${filter === f
                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-700"
              }`}
          >
            {f === "all" ? "全部" : workflowLabel(f)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-zinc-500 text-sm">加载中...</div>
      ) : filtered.length === 0 ? (
        <div className="text-zinc-500 text-sm py-12 text-center">
          暂无运行报告。前往
          <Link href="/studio" className="text-amber-400 mx-1 hover:underline">
            研究工作室
          </Link>
          启动第一个工作流。
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((report) => (
            <Link
              key={report.run_id}
              href={`/reports/${report.run_id}`}
              className="block bg-zinc-900 border border-zinc-800 rounded-lg p-4
                         hover:border-amber-500/20 hover:bg-zinc-800/50 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-zinc-100 font-medium">
                  {workflowLabel(report.workflow)}
                </span>
                <span className="text-xs text-zinc-500">
                  {report.created_at ? new Date(report.created_at).toLocaleString() : ""}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-zinc-500">
                <span>{report.n_messages} 条消息</span>
                <span>{report.agents_responded?.length || 0} agents 响应</span>
                {report.gate_passed !== undefined && (
                  <span className={report.gate_passed ? "text-emerald-400" : "text-red-400"}>
                    Gate: {report.gate_passed ? "通过" : "未通过"}
                  </span>
                )}
                <span className="text-zinc-600 font-mono">{report.run_id}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
