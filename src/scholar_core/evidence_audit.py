"""证据审计 — 对文本中的 claims 进行 A/B/C/Insufficient 分类。

纯检索 + 规则引擎，不依赖 AutoGen。可以接受 model_client 做 LLM 辅助判断。
"""

from __future__ import annotations

import re
from typing import Any

from .config import get_evidence_config
from .retrieval import retrieve_evidence
from .types import AuditedClaim, EvidenceAudit


def audit_evidence(text: str, *, strict: bool = True,
                   model_client: Any = None) -> EvidenceAudit:
    """对文本中的每个 claim 执行证据等级审计。

    参数:
        text: 待审计的文本（通常是 agent 输出或论文草稿）
        strict: True = 严格模式，无证据的 major claim 会 fail gate
        model_client: 可选的 LLM client（暂未使用，Phase 2 集成）

    返回:
        EvidenceAudit: 包含所有 claims 的审计结果
    """
    # 1. 提取 claims
    raw_claims = _extract_claims(text)

    # 2. 检索可用的 evidence
    all_evidence = retrieve_evidence()  # 获取全部 evidence 做对照

    # 3. 对每个 claim 判断证据等级
    audited: list[AuditedClaim] = []
    for rc in raw_claims:
        ac = _classify_claim(rc, all_evidence, strict)
        audited.append(ac)

    # 4. Gate 检查
    unsupported_major = [c.claim for c in audited if c.is_major and c.evidence_level == "Insufficient"]
    c_core_claims = [c for c in audited if c.evidence_level == "C" and c.is_core]
    method_c = [c for c in audited if c.is_method and c.evidence_level == "C"]

    warnings: list[str] = []
    if c_core_claims:
        warnings.append(f"{len(c_core_claims)} 个核心主张为 C 级迁移推断（上限 2 个）")
    if method_c:
        warnings.append(f"{len(method_c)} 个方法论主张为 C 级，建议降级标记")

    pass_gate = len(unsupported_major) == 0
    if strict and c_core_claims and len(c_core_claims) > 2:
        pass_gate = False

    summary = "通过" if pass_gate else "未通过"
    if unsupported_major:
        summary += f" — {len(unsupported_major)} 个无证据核心主张"
    if warnings:
        summary += f" — {len(warnings)} 个警告"

    return EvidenceAudit(
        claims=audited,
        pass_gate=pass_gate,
        unsupported_major_claims=unsupported_major,
        warnings=warnings,
        summary=summary,
    )


def _extract_claims(text: str) -> list[dict[str, Any]]:
    """从文本中提取 claims。使用启发式方法。"""
    claims: list[dict[str, Any]] = []

    # 按段落分割
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for i, para in enumerate(paragraphs):
        # 跳过纯标题行
        if para.startswith("#") or len(para) < 20:
            continue

        # 检测是否是主张性语句
        is_claim = _is_claim_sentence(para)
        is_major = i < len(paragraphs) * 0.3  # 前 30% 的段落视为 major
        is_method = bool(re.search(
            r"(方法|模型|算法|框架|机制|策略|架构|损失|优化)",
            para,
        ))
        is_core = is_major and len(para) > 60

        claims.append({
            "text": para[:300],
            "is_claim": is_claim,
            "is_major": is_major,
            "is_method": is_method,
            "is_core": is_core,
        })

    return claims


def _is_claim_sentence(text: str) -> bool:
    """判断文本是否包含主张性语句。"""
    claim_patterns = [
        r"(提出|发现|证明|验证|实验.*表明|结果.*表明|我们.*(方法|框架|模型))",
        r"(优于|超越|达到.*SOTA|state-of-the-art)",
        r"(贡献|创新|首次|novel|contribution)",
        r"(可以|能够|有效|显著|明显).*(解决|改进|提升|增强)",
    ]
    for pat in claim_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _classify_claim(claim: dict[str, Any],
                    evidence_pool: list[Any],
                    strict: bool) -> AuditedClaim:
    """判断单个 claim 的证据等级。"""
    text = claim["text"]
    text_lower = text.lower()

    # 检测是否已自带证据标记
    has_a_mark = bool(re.search(r"[\[（(]\s*A\s*[\]）)]|evidence.*A|A.*直接证据", text))
    has_b_mark = bool(re.search(r"[\[（(]\s*B\s*[\]）)]|B.*综合归纳|综合.*B", text))
    has_c_mark = bool(re.search(r"[\[（(]\s*C\s*[\]）)]|C.*迁移|迁移.*推断|C.*inference", text))
    has_insufficient = bool(re.search(r"证据不足|insufficient|不确定|无法确定", text, re.IGNORECASE))
    has_citation = bool(re.search(r"PAPER_[A-F0-9]{8}|EVID-|\[\d+\]", text))

    # 在 evidence pool 中做简单匹配
    matched = _match_against_evidence(text_lower, evidence_pool)

    if has_a_mark or (has_citation and matched >= 2):
        level = "A"
        support = "文本自带 A 类标记或匹配到 ≥2 条 evidence"
        risk = "低"
        action = "keep"
    elif has_b_mark or (has_citation and matched >= 1):
        level = "B"
        support = "文本自带 B 类标记或匹配到 ≥1 条 evidence"
        risk = "低-中"
        action = "keep"
    elif has_c_mark:
        level = "C"
        support = "文本自带 C 类标记 — 需验证迁移条件"
        risk = "中"
        action = "downgrade" if claim["is_core"] else "keep"
    elif has_insufficient:
        level = "Insufficient"
        support = "文本已标注证据不足"
        risk = "高" if claim["is_major"] else "中"
        action = "remove" if claim["is_major"] else "downgrade"
    elif has_citation:
        level = "B"
        support = f"至少 {matched} 条 evidence 匹配"
        risk = "低-中"
        action = "keep"
    elif claim["is_core"] and strict:
        level = "Insufficient"
        support = "核心主张无 evidence 支持"
        risk = "高"
        action = "remove"
    else:
        level = "C"
        support = "非核心主张，标记为推断"
        risk = "中"
        action = "downgrade"

    return AuditedClaim(
        claim=text[:200],
        evidence_level=level,
        support=support,
        risk=risk,
        action=action,
        is_major=claim["is_major"],
        is_method=claim["is_method"],
        is_core=claim["is_core"],
    )


def _match_against_evidence(text_lower: str, evidence_pool: list[Any]) -> int:
    """统计有多少条 evidence 与文本匹配。"""
    count = 0
    for ev in evidence_pool:
        try:
            claim_text = (ev.claim or "").lower()
            source_id = (ev.source_id or "").lower()
            if any(term in text_lower for term in claim_text.split()[:6] if len(term) >= 4):
                count += 1
            elif source_id and source_id in text_lower:
                count += 1
        except Exception:
            pass
        if count >= 5:
            break
    return count
