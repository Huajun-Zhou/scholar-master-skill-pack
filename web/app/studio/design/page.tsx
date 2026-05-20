"use client";

import WorkflowRunner from "@/components/studio/WorkflowRunner";

export default function DesignPage() {
  return (
    <WorkflowRunner
      workflowType="committee"
      title="学者委员会 — 研究方案辩论"
      description="Round 1: Methodologist 提案 → Round 2: Evidence Inspector ∥ Skeptic Reviewer 并行挑战 → Round 3: Methodologist 回应修订 → Round 4: Synthesizer 整合报告"
      agentLabels={{}}
    />
  );
}
