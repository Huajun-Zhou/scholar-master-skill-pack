---
page_id: limitations
page_type: hub
title: Limitations — 局限性总结
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_96645819
- PAPER_E155CF85
- PAPER_B4EA5A99
- PAPER_627CFA0B
related_pages:
- contradictions
- open_questions
confidence: medium
updated_at: '2026-05-19'
---

# Limitations — 局限性总结

跨15篇论文归纳的局限性和边界条件（B类综合归纳）。

## 1. 安全模型的局限

| 局限 | 影响 | 涉及论文 |
|------|------|---------|
| 多数论文假定Honest-but-Curious模型，不防御主动恶意攻击 | 投毒、后门等攻击可突破安全保证 | SplitAD, SBIRCH, Plog, PriFFT, TCKKS |
| 侧信道攻击不在威胁模型中 | TEE/FHE方案的理论安全与工程安全间存在缺口 | TCKKS, Lightweight Auth |
| 窃听者/攻击者能力假定为已知 | 实际攻击者能力可能超出假定 | RSMA UAV, Physical Attacks UAV |

## 2. 实验验证的局限

| 局限 | 影响 | 涉及论文 |
|------|------|---------|
| 多数方案仅仿真/公开数据集验证 | 实际部署时性能和安全可能与报告有差异 | SplitAD, RSMA UAV, Blockchain MEC, Flash |
| 参与方数量和网络规模受限 | 扩展性未在真实大规模场景验证 | Flash, Plog, PriFFT, SplitAD |
| UAV平台实验受限 | 实际飞行硬件上的验证不足 | AeroGuard, RSMA UAV, Joint Scheduling |

## 3. 技术边界的局限

| 局限 | 影响 | 涉及论文 |
|------|------|---------|
| 仅支持特定数据/模型类型 | 无法直接应用于新范式 | SplitAD(AE), TCKKS(CKKS), Plog(GNN) |
| 对特定硬件/软件的依赖 | 供应商锁定风险 | TCKKS(Intel SGX/TDX) |
| 单点/特定场景设计 | 复杂混合场景下的有效性未知 | 多数论文 |

## 4. 数据层面的局限

| 局限 | 影响 | 涉及论文 |
|------|------|---------|
| 假设数据对齐和预处理已完成 | 现实中Entity Resolution本身就是难题 | SplitAD, SBIRCH, Plog |
| Non-IID程度影响联邦学习性能 | 极端Non-IID场景精度可能显著下降 | Flash, SplitAD |
| 数据集代表性有限 | 泛化到新的领域/分布的能力未充分验证 | 多数论文 |

## 5. 综述性论文的特殊局限

- Physical Attacks UAV(PAPER_E155CF85)：综述的快照性质意味着在快速发展的攻击技术面前可能过时；因安全原因无法验证所有声称的攻击效果
