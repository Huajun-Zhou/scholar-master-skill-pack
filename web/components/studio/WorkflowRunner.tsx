"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { WorkflowType } from "@/lib/studio-store";
import { useStudioStore } from "@/lib/studio-store";
import AgentTimeline from "./AgentTimeline";
import GateStatusBadge from "./GateStatusBadge";
import WorkflowInput from "./WorkflowInput";
import AgentMessageCard from "./AgentMessageCard";

interface Props {
  workflowType: WorkflowType;
  title: string;
  description: string;
  agentLabels: Record<string, string>;
}

const ROUND_LABELS: Record<number, { icon: string; label: string; desc: string }> = {
  1: { icon: "📐", label: "Round 1", desc: "Methodologist 提出研究方案" },
  2: { icon: "⚔", label: "Round 2", desc: "Evidence Inspector + Skeptic Reviewer 并行挑战" },
  3: { icon: "🔄", label: "Round 3", desc: "Methodologist 回应批评并修订方案" },
  4: { icon: "📋", label: "Round 4", desc: "Synthesizer 整合最终报告" },
};

export default function WorkflowRunner({ workflowType, title, description }: Props) {
  const { activeRun, setActiveRun, addAgentMessage, setGateResult, setRunStatus } =
    useStudioStore();
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleSubmit = useCallback(
    async (params: {
      topic?: string;
      question?: string;
      paperPath?: string;
      targetJournal: string;
    }) => {
      setIsRunning(true);

      const body: Record<string, string> = { target_journal: params.targetJournal };
      if (params.topic) body.topic = params.topic;
      if (params.question) body.question = params.question;
      if (params.paperPath) body.paper_path = params.paperPath;

      try {
        const res = await fetch(`/api/workflow/${workflowType}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const data = await res.json();

        const run = {
          runId: data.run_id,
          workflow: workflowType,
          status: "running" as const,
          agentMessages: [],
        };
        setActiveRun(run);

        // Poll report API every 3s for live agent outputs
        pollRef.current = setInterval(async () => {
          try {
            const r = await fetch(`/api/reports/${data.run_id}`);
            if (!r.ok) return;
            const report = await r.json();
            const conversation = report.agent_conversation || [];
            conversation.forEach((entry: { agent: string; content: string }) => {
              addAgentMessage(data.run_id, {
                agent: entry.agent,
                content: entry.content,
                timestamp: new Date().toISOString(),
              });
            });
            const artifacts = report.artifacts || {};
            if (artifacts["04_final_output"] || artifacts["final_writer"]) {
              setRunStatus(data.run_id, "completed");
              setIsRunning(false);
              if (pollRef.current) clearInterval(pollRef.current);
            }
          } catch { /* not ready */ }
        }, 3000);

        // WebSocket backup
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//localhost:8000/ws/workflow/${data.run_id}`);
        wsRef.current = ws;
        ws.onmessage = (event) => {
          const msg = JSON.parse(event.data);
          if (msg.type === "done") {
            setRunStatus(data.run_id, "completed");
            setIsRunning(false);
            ws.close();
            if (pollRef.current) clearInterval(pollRef.current);
          }
        };
      } catch (err) {
        console.error("Workflow failed:", err);
        setIsRunning(false);
      }
    },
    [workflowType, setActiveRun, addAgentMessage, setRunStatus]
  );

  useEffect(() => {
    return () => {
      wsRef.current?.close();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const msgs = activeRun?.agentMessages || [];

  // Deduplicate: show each agent's latest content, but allow methodologist twice
  const seen: Record<string, number> = {};
  const displayMsgs = msgs.filter((m) => {
    seen[m.agent] = (seen[m.agent] || 0) + 1;
    if (m.agent === "methodologist") return seen[m.agent] <= 2;
    return seen[m.agent] === 1;
  });

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">{title}</h1>
          <p className="text-zinc-400 text-sm mt-1">{description}</p>
        </div>
        {activeRun && <GateStatusBadge gateResult={activeRun.gateResult} />}
      </div>

      {(activeRun?.status === "completed" || activeRun?.status === "error" || !activeRun) && (
        <WorkflowInput workflowType={workflowType} onSubmit={handleSubmit} isRunning={isRunning} />
      )}

      {activeRun && (
        <div className="flex gap-6 flex-1 min-h-0">
          <AgentTimeline messages={displayMsgs} isRunning={isRunning} />

          <div className="flex-1 min-w-0 overflow-y-auto space-y-4 pb-8">
            {/* Round progress bar */}
            {displayMsgs.length > 0 && (
              <div className="flex gap-2 mb-2">
                {[1, 2, 3, 4].map((r) => {
                  const info = ROUND_LABELS[r];
                  const done = displayMsgs.length >= r;
                  const active = displayMsgs.length === r - 1 && isRunning;
                  return (
                    <div
                      key={r}
                      className={`flex-1 rounded-lg px-3 py-2 text-center text-xs transition-all
                        ${done
                          ? "bg-zinc-800/50 border border-zinc-700/50 text-zinc-300"
                          : active
                            ? "bg-amber-500/10 border border-amber-500/30 text-amber-400"
                            : "bg-zinc-900 border border-zinc-800 text-zinc-600"
                        }`}
                    >
                      <div className="text-sm mb-0.5">{done ? "✓" : info.icon}</div>
                      <div className="font-medium">{info.label}</div>
                      <div className="text-[10px] opacity-70 hidden sm:block">{info.desc}</div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Agent cards */}
            {displayMsgs.map((msg, i) => (
              <AgentMessageCard
                key={`${msg.agent}-${i}`}
                agent={msg.agent}
                content={msg.content}
                timestamp={msg.timestamp}
                agentIndex={i + 1}
                totalAgents={4}
              />
            ))}

            {/* Loading */}
            {isRunning && (
              <div className="flex items-center gap-3 bg-zinc-900 border border-zinc-800 rounded-xl p-4">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:0ms]" />
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:150ms]" />
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:300ms]" />
                </div>
                <span className="text-zinc-500 text-sm">
                  委员会辩论中... 已完成 {displayMsgs.length}/4 轮
                </span>
              </div>
            )}

            {/* Completed */}
            {activeRun.status === "completed" && (
              <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-6 text-center">
                <span className="text-2xl">✅</span>
                <p className="text-emerald-400 text-sm font-medium mt-2">学者委员会辩论完成</p>
                <p className="text-zinc-500 text-xs mt-1">4 轮辩论已全部结束</p>
                <a
                  href={`/reports/${activeRun.runId}`}
                  className="inline-block mt-3 px-4 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-400 text-sm hover:bg-amber-500/20 transition-colors"
                >
                  查看完整报告 →
                </a>
              </div>
            )}

            {/* Error */}
            {activeRun.status === "error" && (
              <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4">
                <p className="text-red-400 text-sm">{activeRun.error || "执行失败，请重试"}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
