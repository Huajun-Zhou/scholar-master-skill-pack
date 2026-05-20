"""共享数据类型定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvidenceItem:
    """单条证据。"""
    claim: str
    evidence_level: str          # A / B / C / Insufficient
    source_id: str               # paper_id 或 wiki page_id
    confidence: float = 1.0
    limitation: str = ""


@dataclass
class WikiChunk:
    """从 Wiki 检索出的页面片段。"""
    page_id: str
    title: str
    content: str                 # 页面全文
    evidence_level: str = "B"
    source_papers: list[str] = field(default_factory=list)
    path: str = ""


@dataclass
class MethodCard:
    """方法卡片。"""
    name: str
    definition: str
    source_papers: list[str] = field(default_factory=list)
    applicable_problems: list[str] = field(default_factory=list)
    core_mechanism: str = ""
    typical_flow: list[str] = field(default_factory=list)
    input_conditions: list[str] = field(default_factory=list)
    output_results: list[str] = field(default_factory=list)
    advantages: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    transfer_conditions: str = ""
    unsuitable_scenarios: list[str] = field(default_factory=list)
    path: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"## Method Card: {self.name}",
            "",
            f"**定义**: {self.definition}",
            "",
            "### 来源论文",
        ]
        for pid in self.source_papers:
            lines.append(f"- `{pid}`")
        lines.extend([
            "",
            "### 适用问题类型",
        ])
        for p in self.applicable_problems:
            lines.append(f"- {p}")
        lines.extend([
            "",
            "### 核心机制",
            "",
            self.core_mechanism,
            "",
            "### 局限",
        ])
        for lim in self.limitations:
            lines.append(f"- {lim}")
        lines.extend([
            "",
            "### 不适用场景",
        ])
        for s in self.unsuitable_scenarios:
            lines.append(f"- {s}")
        lines.extend([
            "",
            f"### 迁移条件",
            "",
            self.transfer_conditions,
        ])
        return "\n".join(lines)


@dataclass
class ThinkingModel:
    """思维模型。"""
    name: str
    description: str
    reasoning_chain: str
    applicable_scenarios: list[str] = field(default_factory=list)
    unsuitable_scenarios: list[str] = field(default_factory=list)
    source_papers: list[str] = field(default_factory=list)
    path: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"## Thinking Model: {self.name}",
            "",
            f"**描述**: {self.description}",
            "",
            "### 推理链",
            "",
            self.reasoning_chain,
            "",
            "### 适用场景",
        ]
        for s in self.applicable_scenarios:
            lines.append(f"- {s}")
        lines.extend([
            "",
            "### 不适用场景",
        ])
        for s in self.unsuitable_scenarios:
            lines.append(f"- {s}")
        lines.extend([
            "",
            "### 来源论文",
        ])
        for pid in self.source_papers:
            lines.append(f"- `{pid}`")
        return "\n".join(lines)


@dataclass
class MethodMapping:
    """方法迁移映射。"""
    scholar_method: str
    original_context: str
    transfer_logic: str
    evidence_level: str = "C"
    risk: str = ""


@dataclass
class ScholarAnswer:
    """学者问答结果。"""
    question: str
    direct_answer: str
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    methodological_insight: str = ""
    transferable_suggestions: str = ""
    limitations: list[str] = field(default_factory=list)
    sources_used: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        evidence_rows = []
        for item in self.evidence_items:
            evidence_rows.append(
                f"| {item.claim[:80]} | {item.evidence_level} | "
                f"{item.source_id} | {item.confidence:.2f} | {item.limitation[:60]} |"
            )

        evidence_table = "\n".join(evidence_rows) if evidence_rows else "（无直接证据项）"

        sources = "\n".join(f"- {s}" for s in self.sources_used) if self.sources_used else "（无）"

        return f"""# 基于 Scholar Skill 的科研回答

## 问题

{self.question}

## 回答

{self.direct_answer}

## 证据

| Claim | Level | Source | Confidence | Limitation |
|---|---|---|---|---|
{evidence_table}

## 方法论洞察

{self.methodological_insight}

## 可迁移建议

{self.transferable_suggestions}

## 局限

{chr(10).join(f'- {x}' for x in self.limitations) if self.limitations else '（无）'}

## 使用的知识来源

{sources}
"""


@dataclass
class ResearchDesign:
    """研究设计方案。"""
    topic: str
    target_journal: str = ""
    problem_framing: str = ""
    theoretical_gap: str = ""
    research_questions: list[str] = field(default_factory=list)
    method_mappings: list[MethodMapping] = field(default_factory=list)
    data_requirements: list[str] = field(default_factory=list)
    method_pipeline: list[str] = field(default_factory=list)
    evaluation_strategy: list[str] = field(default_factory=list)
    expected_contributions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    evidence_limits: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        mapping_rows = []
        for m in self.method_mappings:
            mapping_rows.append(
                f"| {m.scholar_method} | {m.original_context} | "
                f"{m.transfer_logic} | {m.evidence_level} | {m.risk} |"
            )

        return f"""# Research Design Report

## 题目

{self.topic}

## 目标期刊

{self.target_journal or '待定'}

## 问题框架

{self.problem_framing}

## 理论 Gap

{self.theoretical_gap}

## 研究问题

{chr(10).join(f'- {x}' for x in self.research_questions) if self.research_questions else '（待定义）'}

## 方法迁移映射

| Scholar Method | Original Context | Transfer Logic | Evidence Level | Risk |
|---|---|---|---|---|
{mapping_rows if mapping_rows else '（待定义）'}

## 数据需求

{chr(10).join(f'- {x}' for x in self.data_requirements) if self.data_requirements else '（待定义）'}

## 方法管线

{chr(10).join(f'- {x}' for x in self.method_pipeline) if self.method_pipeline else '（待定义）'}

## 评估策略

{chr(10).join(f'- {x}' for x in self.evaluation_strategy) if self.evaluation_strategy else '（待定义）'}

## 预期贡献

{chr(10).join(f'- {x}' for x in self.expected_contributions) if self.expected_contributions else '（待定义）'}

## 风险

{chr(10).join(f'- {x}' for x in self.risks) if self.risks else '（待定义）'}

## 证据局限

{chr(10).join(f'- {x}' for x in self.evidence_limits) if self.evidence_limits else '（无）'}

## 下一步

{chr(10).join(f'{i}. {x}' for i, x in enumerate(self.next_steps, 1)) if self.next_steps else '（待定义）'}
"""


@dataclass
class AuditedClaim:
    """被审计的单条 claim。"""
    claim: str
    evidence_level: str = "Insufficient"   # A / B / C / Insufficient
    support: str = ""                       # 支撑证据描述
    risk: str = ""                          # 风险
    action: str = "keep"                    # keep / downgrade / remove
    is_major: bool = False                  # 是否为核心主张
    is_method: bool = False                 # 是否为方法论主张
    is_core: bool = False                   # 是否为不可移除的核心主张


@dataclass
class EvidenceAudit:
    """证据审计结果。"""
    claims: list[AuditedClaim] = field(default_factory=list)
    pass_gate: bool = True
    unsupported_major_claims: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: str = ""

    def to_markdown(self) -> str:
        rows = []
        for c in self.claims:
            rows.append(
                f"| {c.claim[:60]} | {c.evidence_level} | {c.support[:50]} | "
                f"{c.risk[:40]} | {c.action} |"
            )

        table = "\n".join(rows) if rows else "（无 claims）"

        return f"""# Evidence Audit

## 总结

{self.summary}

## Gate 结果: {'通过' if self.pass_gate else '**未通过**'}

## 无证据核心主张

{chr(10).join(f'- {x}' for x in self.unsupported_major_claims) if self.unsupported_major_claims else '（无）'}

## 警告

{chr(10).join(f'- {x}' for x in self.warnings) if self.warnings else '（无）'}

## Claims

| Claim | Evidence Level | Support | Risk | Action |
|---|---|---|---|---|
{table}
"""


@dataclass
class PaperReview:
    """论文审查结果。"""
    paper_title: str = ""
    overall_verdict: str = ""
    paradigm_alignment: str = ""
    problem_quality: str = ""
    method_validity: str = ""
    evidence_chain: str = ""
    contribution_clarity: str = ""
    major_risks: list[str] = field(default_factory=list)
    must_fix: list[str] = field(default_factory=list)
    should_fix: list[str] = field(default_factory=list)
    optional: list[str] = field(default_factory=list)
    recommendation: str = ""
    sources_used: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        return f"""# Paper Critique Report

## 总体判断

{self.overall_verdict}

## 与研究范式的一致性

{self.paradigm_alignment}

## 问题定义质量

{self.problem_quality}

## 方法有效性

{self.method_validity}

## 证据链

{self.evidence_chain}

## 贡献清晰度

{self.contribution_clarity}

## 主要风险

{chr(10).join(f'- {x}' for x in self.major_risks) if self.major_risks else '（无）'}

## 必须修改

{chr(10).join(f'{i}. {x}' for i, x in enumerate(self.must_fix, 1)) if self.must_fix else '（无）'}

## 建议修改

{chr(10).join(f'{i}. {x}' for i, x in enumerate(self.should_fix, 1)) if self.should_fix else '（无）'}

## 可选改进

{chr(10).join(f'{i}. {x}' for i, x in enumerate(self.optional, 1)) if self.optional else '（无）'}

## 投稿建议

{self.recommendation}

## 使用的标准来源

{chr(10).join(f'- {s}' for s in self.sources_used) if self.sources_used else '（无）'}
"""
