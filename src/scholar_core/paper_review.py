"""论文审查 — 按陈志远教授研究范式审查论文草稿。

纯检索 + 模板填充，可接受 model_client 做 LLM 辅助审查。
"""

from __future__ import annotations

from typing import Any

from .retrieval import retrieve_method_cards, search_scholar_wiki
from .types import PaperReview


def critique_paper(paper_path: str, target_journal: str = "",
                   *, model_client: Any = None) -> PaperReview:
    """按陈志远教授公开成果中的证据标准与研究范式审查论文。

    参数:
        paper_path: 论文草稿路径
        target_journal: 目标投稿期刊（可选）
        model_client: 可选的 LLM client（Phase 2 集成）

    返回:
        PaperReview: 结构化审查报告
    """
    from pathlib import Path

    # 1. 加载论文内容
    path = Path(paper_path)
    if not path.is_file():
        return PaperReview(
            paper_title=path.name,
            overall_verdict=f"文件不存在: {paper_path}",
            recommendation="无法审查",
        )

    paper_text = path.read_text(encoding="utf-8")
    title = _extract_title(paper_text) or path.stem

    # 2. 检索相关审查标准
    paradigm_pages = search_scholar_wiki("研究范式 方法设计 实验验证 证据标准", top_k=5)
    evidence_standards = search_scholar_wiki("evidence standards 验证链 消融", top_k=3)
    method_cards = retrieve_method_cards("", top_k=3)  # 获取通用方法标准

    # 3. 执行审查
    paradigm_alignment = _check_paradigm_alignment(paper_text, paradigm_pages)
    problem_quality = _check_problem_quality(paper_text)
    method_validity = _check_method_validity(paper_text, method_cards)
    evidence_chain = _check_evidence_chain(paper_text, evidence_standards)
    contribution_clarity = _check_contribution(paper_text)
    major_risks = _identify_major_risks(paper_text)
    must_fix, should_fix, optional = _classify_fixes(paper_text, major_risks)

    # 4. 生成投稿建议
    if len(must_fix) >= 4:
        recommendation = '当前版本不建议投稿。完成所有[必须修改]项后重新评估。'
        verdict = "Major Revision (大修) — 在问题定义、理论深度、证据完整性三个维度上存在显著不足"
    elif len(must_fix) >= 2:
        recommendation = f"建议完成必须修改项后投稿 {target_journal or '领域主流期刊'}。"
        verdict = "Moderate Revision (中修) — 核心 idea 有一定价值但论证不完整"
    else:
        recommendation = f"可考虑投稿 {target_journal or '领域主流期刊'}。"
        verdict = "Minor Revision (小修) — 论文框架合理，细节需要打磨"

    return PaperReview(
        paper_title=title,
        overall_verdict=verdict,
        paradigm_alignment=paradigm_alignment,
        problem_quality=problem_quality,
        method_validity=method_validity,
        evidence_chain=evidence_chain,
        contribution_clarity=contribution_clarity,
        major_risks=major_risks,
        must_fix=must_fix,
        should_fix=should_fix,
        optional=optional,
        recommendation=recommendation,
        sources_used=[p.path for p in paradigm_pages[:3]] + [p.path for p in evidence_standards[:2]],
    )


def _extract_title(text: str) -> str:
    """从论文文本中提取标题。"""
    for line in text.split("\n")[:10]:
        line = line.strip()
        if line.startswith("# ") and len(line) > 5:
            return line[2:].strip()
    return ""


def _check_paradigm_alignment(text: str, paradigm_pages: list[Any]) -> str:
    """检查与研究范式的一致性。"""
    issues: list[str] = []
    text_lower = text.lower()

    # 检查是否有"问题抽象"环节
    if not any(kw in text_lower for kw in ("问题", "problem", "formulation", "建模", "model")):
        issues.append("缺少明确的问题抽象/建模环节（陈志远教授范式第1层）")

    # 检查是否有理论分析
    if not any(kw in text_lower for kw in ("定理", "theorem", "证明", "proof", "推导", "derive", "收敛", "optimal")):
        issues.append("缺少理论分析或数学推导（陈志远教授范式第2层）")

    # 检查是否有"隐含假设"的讨论
    if not any(kw in text_lower for kw in ("假设", "assumption", "隐含", "implicit")):
        issues.append("未讨论现有方法的隐含假设 gap（陈志远教授范式核心选题策略）")

    if not issues:
        return "论文框架与陈志远教授的四层方法论（物理建模→数学推导→网络设计→实验验证）基本一致。"
    return "与该学者研究范式的差距：\n" + "\n".join(f"- {i}" for i in issues)


def _check_problem_quality(text: str) -> str:
    """检查问题定义质量。"""
    issues: list[str] = []
    text_lower = text.lower()

    if not any(kw in text_lower for kw in ("gap", "差距", "不足", "limitation", "挑战", "challenge")):
        issues.append("未明确识别研究 gap 或现有方法的不足")

    if not any(kw in text_lower for kw in ("贡献", "contribution", "创新", "novel")):
        issues.append("贡献陈述不清晰")

    if len(text) < 3000:
        issues.append("论文内容过短，可能缺少完整的论证链")

    if not issues:
        return "问题定义清晰，有明确的研究 gap 识别和贡献陈述。"
    return "问题定义存在以下不足：\n" + "\n".join(f"- {i}" for i in issues)


def _check_method_validity(text: str, method_cards: list[Any]) -> str:
    """检查方法有效性。"""
    issues: list[str] = []
    text_lower = text.lower()

    if not any(kw in text_lower for kw in ("损失", "loss", "优化", "optim", "目标函数", "objective")):
        issues.append("缺少明确的损失函数/目标函数定义")

    if not any(kw in text_lower for kw in ("自适应", "adaptive", "鲁棒", "robust")):
        issues.append("未讨论方法的鲁棒性或自适应性（陈志远教授方法论DNA之一）")

    if not issues:
        return "方法设计合理，有清晰的目标函数和求解框架。"
    return "方法设计存在以下不足：\n" + "\n".join(f"- {i}" for i in issues)


def _check_evidence_chain(text: str, evidence_pages: list[Any]) -> str:
    """检查证据链完整性。"""
    issues: list[str] = []
    text_lower = text.lower()

    if not any(kw in text_lower for kw in ("消融", "ablation")):
        issues.append("缺少消融实验（陈志远教授范式的必要实验环节）")

    if not any(kw in text_lower for kw in ("鲁棒", "robustness", "噪声", "noise level")):
        issues.append("缺少鲁棒性/极限条件测试")

    if not any(kw in text_lower for kw in ("可视化", "visual", "定性", "qualitative", "案例", "case")):
        issues.append("缺少定性分析或案例研究")

    if "real" not in text_lower and "真实" not in text_lower:
        issues.append("未验证方法在真实数据（非合成）上的效果")

    if not issues:
        return "证据链完整，包含合成实验、消融分析、鲁棒性测试。"
    return "证据链存在以下不完整项：\n" + "\n".join(f"- {i}" for i in issues)


def _check_contribution(text: str) -> str:
    """检查贡献清晰度。"""
    issues: list[str] = []
    text_lower = text.lower()

    if not any(kw in text_lower for kw in ("首次", "first", "novel", "创新")):
        issues.append("贡献表述不够有力——建议使用'首次'定位（陈志远教授范式贡献 framing 模式）")

    if any(kw in text_lower for kw in ("比 sota", "优于", "outperform", "better than")):
        issues.append("贡献 framing 偏向'比SOTA好X%'——陈志远教授范式通常避免以性能提升为主要贡献")

    if not issues:
        return "贡献陈述清晰有力，有明确的'首次'定位和完整的问题-理论-方法-实验闭环。"
    return "贡献表述存在以下问题：\n" + "\n".join(f"- {i}" for i in issues)


def _identify_major_risks(text: str) -> list[str]:
    """识别主要风险。"""
    risks: list[str] = []
    text_lower = text.lower()

    if not any(kw in text_lower for kw in ("局限", "limitation", "限制", "不足")):
        risks.append("论文未诚实讨论局限性——这是审稿人的首要攻击目标")

    if not any(kw in text_lower for kw in ("理论", "theorem", "证明", "proof", "推导", "收敛")):
        risks.append("缺少理论贡献——在当前CV/ML领域，纯架构改进在顶刊的接受率急剧下降")

    if not any(kw in text_lower for kw in ("真实", "real", "实际场景")):
        risks.append("缺少真实世界验证——审稿人会质疑方法的实用性")

    if "计算" not in text_lower and "效率" not in text_lower and "complexity" not in text_lower:
        risks.append("未讨论计算复杂度——影响方法实用性的评估")

    return risks if risks else ["论文整体框架较好，未发现明显的高风险问题"]


def _classify_fixes(text: str, risks: list[str]) -> tuple[list[str], list[str], list[str]]:
    """将修改建议分为必须/建议/可选三类。"""
    must: list[str] = []
    should: list[str] = []
    optional: list[str] = []

    text_lower = text.lower()

    # 必须修改
    if not any(kw in text_lower for kw in ("理论", "theorem", "证明", "proof", "推导")):
        must.append("[必须] 添加理论分析或数学推导，强化理论贡献")
    if not any(kw in text_lower for kw in ("消融", "ablation")):
        must.append("[必须] 补充消融实验（至少 Layer 1 必要性 + Layer 2 设计选择）")
    if not any(kw in text_lower for kw in ("局限", "limitation")):
        must.append("[必须] 添加诚实、具体的局限性讨论")

    # 建议修改
    if not any(kw in text_lower for kw in ("真实", "real")):
        should.append("[建议] 添加真实世界数据验证")
    if not any(kw in text_lower for kw in ("假设", "assumption", "隐含")):
        should.append("[建议] 明确讨论现有方法的隐含假设 gap")

    # 可选
    optional.append("[可选] 添加计算效率分析（参数量/FLOPs/推理时间）")
    optional.append("[可选] 添加失败案例分析")

    return must, should, optional
