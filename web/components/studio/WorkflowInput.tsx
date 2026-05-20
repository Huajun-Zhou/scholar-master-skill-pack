"use client";

import { useState } from "react";
import type { WorkflowType } from "@/lib/studio-store";

interface Props {
  workflowType: WorkflowType;
  onSubmit: (params: {
    topic?: string;
    question?: string;
    paperPath?: string;
    targetJournal: string;
  }) => void;
  isRunning: boolean;
}

export default function WorkflowInput({ workflowType, onSubmit, isRunning }: Props) {
  const [topic, setTopic] = useState("");
  const [question, setQuestion] = useState("");
  const [paperPath, setPaperPath] = useState("");
  const [targetJournal, setTargetJournal] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ topic, question, paperPath: paperPath || undefined, targetJournal });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-2xl">
      {(workflowType === "design" || workflowType === "committee") && (
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-1">
            研究主题
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="例如：图像去噪中的自适应阈值策略"
            className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-lg
                       text-zinc-100 placeholder:text-zinc-500
                       focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20"
            disabled={isRunning}
            required
          />
        </div>
      )}

      {workflowType === "ask" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-1">
            研究问题
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="例如：如何基于陈志远教授的方法论设计IIoT安全通信方案？"
            className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-lg
                       text-zinc-100 placeholder:text-zinc-500 min-h-24
                       focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20"
            disabled={isRunning}
            required
          />
        </div>
      )}

      {workflowType === "critique" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-1">
            论文文件路径
          </label>
          <input
            type="text"
            value={paperPath}
            onChange={(e) => setPaperPath(e.target.value)}
            placeholder="例如：drafts/my_paper.md"
            className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-lg
                       text-zinc-100 placeholder:text-zinc-500
                       focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20"
            disabled={isRunning}
            required
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-1">
          目标期刊（可选）
        </label>
        <input
          type="text"
          value={targetJournal}
          onChange={(e) => setTargetJournal(e.target.value)}
          placeholder="例如：TIP / IJCV / ICLR"
          className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 rounded-lg
                     text-zinc-100 placeholder:text-zinc-500
                     focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20"
          disabled={isRunning}
        />
      </div>

      <button
        type="submit"
        disabled={isRunning}
        className="px-6 py-3 bg-amber-500 text-black font-medium rounded-lg
                   hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors self-start"
      >
        {isRunning ? "执行中..." : "启动工作流"}
      </button>
    </form>
  );
}
