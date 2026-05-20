"use client";

import WorkflowRunner from "@/components/studio/WorkflowRunner";

export default function AskPage() {
  return (
    <WorkflowRunner
      workflowType="ask"
      title="学者问答"
      description="4-agent 管线：task_decomposer → scholar_mentor → evidence_auditor → final_writer"
      agentLabels={{}}
    />
  );
}
