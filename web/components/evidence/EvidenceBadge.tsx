"use client";

import { useState } from "react";
import * as Tooltip from "@radix-ui/react-tooltip";

type EvidenceLevel = "A" | "B" | "C";

interface EvidenceBadgeProps {
  level: EvidenceLevel;
  evidenceId?: string;
  paperId?: string;
  paperTitle?: string;
  claim?: string;
  className?: string;
}

const LEVEL_CONFIG: Record<
  EvidenceLevel,
  { label: string; tooltip: string }
> = {
  A: {
    label: "A",
    tooltip: "直接证据 — 可在此学者论文中找到直接支持",
  },
  B: {
    label: "B",
    tooltip: "综合归纳 — 多篇论文共同体现的稳定模式 (≥2 篇)",
  },
  C: {
    label: "C",
    tooltip: "迁移推断 — 方法论迁移到新问题，非原论文结论",
  },
};

export function EvidenceBadge({
  level,
  evidenceId,
  paperTitle,
  className,
}: EvidenceBadgeProps) {
  const [open, setOpen] = useState(false);
  const config = LEVEL_CONFIG[level];

  return (
    <Tooltip.Provider delayDuration={300}>
      <Tooltip.Root open={open} onOpenChange={setOpen}>
        <Tooltip.Trigger asChild>
          <span
            className={`evidence-badge evidence-badge--${level.toLowerCase()} ${
              className ?? ""
            }`}
            onClick={() => setOpen(!open)}
          >
            [{config.label}]
            {evidenceId && (
              <span className="opacity-60 ml-0.5 text-[0.65rem]">
                {evidenceId.slice(-8)}
              </span>
            )}
          </span>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            side="top"
            align="start"
            sideOffset={6}
            className="max-w-sm z-50"
            data-radix-tooltip-content
          >
            <div className="space-y-1 min-w-[240px]">
              <div className="flex items-center gap-2">
                <span className={`evidence-badge evidence-badge--${level.toLowerCase()}`}>
                  [{config.label}]  {config.tooltip.slice(0, 10)}...
                </span>
              </div>
              {evidenceId && (
                <div className="text-xs font-mono opacity-70">{evidenceId}</div>
              )}
              {paperTitle && (
                <div className="text-xs opacity-80 leading-relaxed">
                  {paperTitle}
                </div>
              )}
              <div className="text-xs opacity-50">{config.tooltip}</div>
            </div>
            <Tooltip.Arrow className="fill-[var(--bg-elevated)]" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}

export function EvidenceLevelPill({
  level,
  count,
}: {
  level: EvidenceLevel;
  count?: number;
}) {
  const colors = {
    A: "border-[var(--color-evidence-a)] text-[var(--color-evidence-a)]",
    B: "border-[var(--color-evidence-b)] text-[var(--color-evidence-b)]",
    C: "border-[var(--color-evidence-c)] text-[var(--color-evidence-c)]",
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-semibold tracking-wide ${colors[level]}`}
    >
      {level}
      {count !== undefined && (
        <span className="opacity-60 ml-0.5">{count}</span>
      )}
    </span>
  );
}
