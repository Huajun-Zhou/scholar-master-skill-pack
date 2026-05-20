"use client";

interface Props {
  gateResult?: { passed: boolean; summary: string };
}

export default function GateStatusBadge({ gateResult }: Props) {
  if (!gateResult) {
    return (
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-800 text-zinc-500 text-xs">
        <span className="w-2 h-2 rounded-full bg-zinc-600" />
        等待审计
      </div>
    );
  }

  const isPassed = gateResult.passed;

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs
        ${isPassed
          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
          : "bg-red-500/10 text-red-400 border border-red-500/20"
        }`}
      title={gateResult.summary}
    >
      <span
        className={`w-2 h-2 rounded-full ${isPassed ? "bg-emerald-400" : "bg-red-400"}`}
      />
      {isPassed ? "证据通过" : "证据未通过"}
      <span className="text-zinc-500 ml-1">{gateResult.summary}</span>
    </div>
  );
}
