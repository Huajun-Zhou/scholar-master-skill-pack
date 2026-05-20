"""研究设计生成 — 基于检索 + 模板填充，生成发表级研究方案。

纯检索 + 模板填充，不依赖 AutoGen。model_client 用于 LLM 辅助组合（Phase 2）。
"""

from __future__ import annotations

from typing import Any

from .retrieval import retrieve_method_cards, retrieve_thinking_models, search_scholar_wiki
from .types import MethodMapping, ResearchDesign


def design_research(topic: str, target_journal: str = "",
                    *, model_client: Any = None) -> ResearchDesign:
    """基于 Scholar Wiki 的知识资产生成研究设计方案。

    参数:
        topic: 研究主题
        target_journal: 目标投稿期刊（可选）
        model_client: 可选的 LLM client（Phase 2 集成）

    返回:
        ResearchDesign: 结构化研究方案
    """
    # 1. 检索相关知识
    wiki_pages = search_scholar_wiki(topic, top_k=8)
    method_cards = retrieve_method_cards(topic, top_k=5)
    thinking_models = retrieve_thinking_models(topic, top_k=3)

    # 2. 生成方法映射
    mappings: list[MethodMapping] = []
    for card in method_cards[:4]:
        mappings.append(MethodMapping(
            scholar_method=card.name,
            original_context=card.definition[:120] if card.definition else "见方法卡片",
            transfer_logic=_derive_transfer_logic(card, topic),
            evidence_level="B" if len(card.source_papers) >= 2 else "C",
            risk=_assess_risk(card, topic),
        ))

    # 3. 从 Wiki 知识中提取问题框架
    paradigm_context = ""
    for page in wiki_pages:
        if "research_paradigm" in page.path or "problem_framing" in page.path:
            paradigm_context += page.content + "\n\n"
    problem_framing = _compose_problem_framing(topic, paradigm_context, wiki_pages)

    # 4. 构建研究问题
    research_questions = _generate_research_questions(topic, method_cards, thinking_models)

    # 5. 方法管线
    pipeline = _compose_pipeline(method_cards, thinking_models)

    # 6. 数据需求
    data_reqs = _derive_data_requirements(topic, method_cards)

    # 7. 评估策略
    evaluation = _compose_evaluation(method_cards, thinking_models)

    # 8. 预期贡献
    contributions = _compose_contributions(topic, method_cards, thinking_models)

    return ResearchDesign(
        topic=topic,
        target_journal=target_journal,
        problem_framing=problem_framing,
        theoretical_gap=_compose_theoretical_gap(topic, wiki_pages),
        research_questions=research_questions,
        method_mappings=mappings,
        data_requirements=data_reqs,
        method_pipeline=pipeline,
        evaluation_strategy=evaluation,
        expected_contributions=contributions,
        risks=_compose_risks(method_cards, topic),
        evidence_limits=["研究设计中的方法迁移映射均为 C 类迁移推断",
                        "具体性能指标需在实现后通过实验验证"],
        next_steps=[
            "1. 完成理论推导和问题形式化定义",
            "2. 实现核心方法模块",
            "3. 构建合成+真实数据集",
            "4. 执行4层消融实验（必要性 → 替代方案 → 参数敏感性 → 极限测试）",
            "5. 撰写论文草稿",
        ],
    )


def _derive_transfer_logic(card: Any, topic: str) -> str:
    """推导方法迁移逻辑。"""
    mechanism = card.core_mechanism[:150] if card.core_mechanism else "核心机制见方法卡片"
    problems = ", ".join(card.applicable_problems[:2]) if card.applicable_problems else "通用"
    return f"将 {card.name} 从「{problems}」迁移到「{topic}」——{mechanism}"


def _assess_risk(card: Any, topic: str) -> str:
    """评估迁移风险。"""
    if card.unsuitable_scenarios:
        return f"不适用条件: {card.unsuitable_scenarios[0][:80]}"
    return "需验证迁移假设"


def _compose_problem_framing(topic: str, paradigm: str,
                             wiki_pages: list[Any]) -> str:
    """组合问题框架。"""
    lines = [
        f"研究主题「{topic}」可以从陈志远教授研究范式中的「物理/几何先验驱动的逆问题求解」视角来框架化。",
        "",
        "**问题抽象路径**（基于 B 类综合归纳的四种问题定义模式）：",
    ]

    # 尝试匹配模式
    if any(kw in topic.lower() for kw in ("去噪", "恢复", "复原", "增强", "denois", "restor")):
        lines.append("- **模式 A (物理先验驱动)**: 识别噪声/退化的物理生成过程 → 建立前向模型 → 从统计原理推导求解策略")
    if any(kw in topic.lower() for kw in ("自适应", "调制", "阈值", "adaptiv")):
        lines.append("- **模式 C (稳健性优先)**: 假设模型/数据存在偏差 → 设计鲁棒自适应机制 → 理论证明最优性")
    if any(kw in topic.lower() for kw in ("协同", "融合", "多模态", "multi")):
        lines.append("- **模式 D (几何先验桥梁)**: 识别深层几何结构 → 将几何量作为信息桥梁 → 多任务/多模态协同")

    if len(lines) <= 2:
        lines.append("- **模式 B (连续空间插值)**: 识别参数空间的连续结构 → 有限基础状态 → 插值/调制适配新条件")

    lines.extend([
        "",
        "**关键隐含假设 gap**（C 类迁移推断，需在实际研究中验证）：",
        f"- 主流方法在「{topic}」领域的最强隐含假设是什么？",
        "- 现实条件中哪些因素违背了这些假设？",
        "- 是否能用一个 ≤1行的公式描述这一 gap？",
    ])

    return "\n".join(lines)


def _compose_theoretical_gap(topic: str, wiki_pages: list[Any]) -> str:
    """识别理论 gap。"""
    related_methods = []
    for page in wiki_pages:
        if "method" in page.path.lower() and page.source_papers:
            related_methods.append(page.title)

    if related_methods:
        related_str = "、".join(related_methods[:5])
        return (f"现有工作在「{topic}」方面：\n"
                f"1. 可借鉴陈志远教授的 {related_str} 等方法论\n"
                f"2. 但将这些方法直接应用到「{topic}」时存在条件不匹配的问题\n"
                f"3. 理论上需要：推导新条件下的最优参数、证明收敛性/最优性、设计对应的实验验证框架")
    return f"「{topic}」的理论 gap 需要在文献调研后进一步明确。"


def _generate_research_questions(topic: str, cards: list[Any],
                                 models: list[Any]) -> list[str]:
    """生成研究问题。"""
    questions = [
        f"RQ1 (理论): 在「{topic}」的特定条件下，核心方法的最优参数/阈值的理论值是多少？",
        f"RQ2 (机制): 该方法的什么设计导致了其有效性？能否从第一原理（信息论/统计/几何）推导？",
        f"RQ3 (泛化): 该方法在不同噪声类型/数据分布/应用场景下的性能边界在哪里？",
        f"RQ4 (对比): 该方法相比领域 SOTA 在理论保证和实际性能两个维度上的优势是什么？",
    ]
    return questions


def _compose_pipeline(cards: list[Any], models: list[Any]) -> list[str]:
    """组合方法管线。"""
    pipeline = [
        "第 1 步: 问题形式化 — 建立前向模型，明确输入/输出/目标函数",
        "第 2 步: 数据表征 — 确定数据格式、标注策略、预处理管线",
    ]

    for i, card in enumerate(cards[:4], 3):
        pipeline.append(f"第 {i} 步: {card.name} — {card.definition[:80] if card.definition else '见方法卡片'}")

    pipeline.extend([
        "第 N-1 步: 实验验证 — 4层消融（必要性→替代方案→参数敏感性→极限测试）",
        "第 N 步: 结果分析与局限性讨论",
    ])
    return pipeline


def _derive_data_requirements(topic: str, cards: list[Any]) -> list[str]:
    """推导数据需求。"""
    return [
        "合成数据集: 在受控条件下验证方法核心假设",
        "公开基准数据集: ≥2个与领域相关的标准测试集",
        "真实世界数据 (如适用): 验证方法在非理想条件下的表现",
        "Ground truth: 全参考指标 (PSNR/SSIM) 或无参考指标 (BRISQUE/NIQE)",
        "噪声/退化模拟: 多种类型×多种水平",
    ]


def _compose_evaluation(cards: list[Any], models: list[Any]) -> list[str]:
    """组合评估策略。"""
    return [
        "理论验证: 推导关键定理/引理，证明方法收敛性/最优性",
        "合成实验: 多种噪声类型 × 多种水平 × 多种内容类型的定量对比",
        "真实数据: ≥2个真实基准数据集验证",
        "消融实验 Layer 1: 必要性消融（去掉核心模块）",
        "消融实验 Layer 2: 设计选择消融（替换为 ≥2 种替代方案）",
        "消融实验 Layer 3: 参数敏感性分析",
        "消融实验 Layer 4: 极限条件测试（超出训练范围的噪声水平）",
        "效率分析: 参数量、FLOPs、推理时间",
        "定性分析: 可视化结果 + 失败案例分析",
    ]


def _compose_contributions(topic: str, cards: list[Any],
                           models: list[Any]) -> list[str]:
    """组合预期贡献。"""
    contributions = [
        f"首次从X角度系统研究「{topic}」中的Y问题（理论贡献）",
        f"提出Z方法/框架，解决现有方法的隐含假设 gap（方法贡献）",
        "通过4层消融实验系统验证方法的有效性（实验贡献）",
    ]
    return contributions


def _compose_risks(cards: list[Any], topic: str) -> list[str]:
    """识别风险。"""
    risks = [
        "理论风险: 核心推导可能需要较强的假设条件，假设不成立时方法退化",
        "实验风险: 真实数据可能无法覆盖所有退化类型",
        "发表风险: 如果理论贡献不够充分，审稿人可能认为只是渐进性改进",
        "C 类迁移风险: 方法迁移假设需要在目标领域逐一验证，并非原方法作者的观点",
    ]
    for card in cards[:2]:
        if card.unsuitable_scenarios:
            risks.append(f"方法边界: {card.name} 在以下场景不适用 — {card.unsuitable_scenarios[0][:80]}")
    return risks
