"use client";

import WorkflowRunner from "@/components/studio/WorkflowRunner";

export default function CritiquePage() {
  return (
    <WorkflowRunner
      workflowType="critique"
      title="论文审查"
      description="6-agent 管线：task_decomposer → scholar_mentor → risk_reviewer → evidence_auditor → revision_planner → final_writer"
      agentLabels={{}}
    />
  );
}
