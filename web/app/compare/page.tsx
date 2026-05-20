"use client";

import { useEffect, useState } from "react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";

interface ReportItem {
  run_id: string;
  workflow: string;
  created_at: string;
  agents_responded?: string[];
}

export default function ComparePage() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [leftId, setLeftId] = useState<string>("");
  const [rightId, setRightId] = useState<string>("");
  const [leftContent, setLeftContent] = useState<string>("");
  const [rightContent, setRightContent] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/reports")
      .then((r) => r.json())
      .then((data) => setReports(data.reports || []));
  }, []);

  const designReports = reports.filter((r) => r.workflow.includes("design"));

  const loadCompare = async () => {
    if (!leftId || !rightId) return;
    setLoading(true);
    const [left, right] = await Promise.all([
      fetch(`/api/reports/${leftId}`).then((r) => r.json()),
      fetch(`/api/reports/${rightId}`).then((r) => r.json()),
    ]);
    setLeftContent(left.artifacts?.["final_writer"] || "");
    setRightContent(right.artifacts?.["final_writer"] || "");
    setLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto py-8">
      <h1 className="text-2xl font-bold text-zinc-100 mb-2">方案对比</h1>
      <p className="text-zinc-400 text-sm mb-6">
        选择两个研究设计运行，并排对比差异
      </p>

      {/* 选择器 */}
      <div className="flex gap-4 mb-6 items-end">
        <div className="flex-1">
          <label className="block text-xs text-zinc-500 mb-1">左侧方案</label>
          <select
            value={leftId}
            onChange={(e) => setLeftId(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded text-sm text-zinc-200"
          >
            <option value="">选择...</option>
            {designReports.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {r.run_id} — {r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-xs text-zinc-500 mb-1">右侧方案</label>
          <select
            value={rightId}
            onChange={(e) => setRightId(e.target.value)}
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 rounded text-sm text-zinc-200"
          >
            <option value="">选择...</option>
            {designReports.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {r.run_id} — {r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={loadCompare}
          disabled={!leftId || !rightId || loading}
          className="px-4 py-2 bg-amber-500 text-black rounded text-sm font-medium
                     hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "加载中..." : "对比"}
        </button>
      </div>

      {/* 对比视图 */}
      {(leftContent || rightContent) && (
        <div className="grid grid-cols-2 gap-4 min-h-96">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 overflow-y-auto max-h-screen">
            <div className="text-xs text-amber-400 font-mono mb-3">方案 A: {leftId}</div>
            {leftContent ? (
              <div className="text-zinc-300 text-sm">
                <MarkdownRenderer content={leftContent} />
              </div>
            ) : (
              <p className="text-zinc-600 text-sm">无内容</p>
            )}
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 overflow-y-auto max-h-screen">
            <div className="text-xs text-sky-400 font-mono mb-3">方案 B: {rightId}</div>
            {rightContent ? (
              <div className="text-zinc-300 text-sm">
                <MarkdownRenderer content={rightContent} />
              </div>
            ) : (
              <p className="text-zinc-600 text-sm">无内容</p>
            )}
          </div>
        </div>
      )}

      {designReports.length === 0 && (
        <p className="text-zinc-500 text-sm py-12 text-center">
          暂无研究设计运行。前往
          <a href="/studio/design" className="text-amber-400 mx-1 hover:underline">
            研究设计
          </a>
          启动第一个工作流。
        </p>
      )}
    </div>
  );
}
