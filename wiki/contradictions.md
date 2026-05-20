---
page_id: contradictions
page_type: hub
title: Contradictions — 矛盾候选
status: draft
evidence_level: C
source_papers:
- PAPER_BC534646
- PAPER_B1C0C91E
- PAPER_627CFA0B
related_pages:
- limitations
- open_questions
confidence: low
updated_at: '2026-05-19'
---

# Contradictions — 矛盾候选

跨论文综合中发现的潜在矛盾、方法论张力或值得深入探讨的设计权衡（C类迁移推断）。

## 1. 隐私保护的"充分性"标准

**张力**：SplitAD(PAPER_BC534646) 声称传输重构误差而非模型参数"足以"保护隐私，但随后又设计了DP增强机制——暗示基础方案可能不足以抵御某些推断攻击。Key-Value LDP(PAPER_9955C321) 和 Plog(PAPER_B4EA5A99) 均在基础方案之外提供了额外的安全保证。

**矛盾候选**：不同论文对"什么是充分隐私保护"有不同的隐性标准——系统设计者和攻击者之间的知识不对称是否在方法论层面得到了充分认识？

## 2. TEE信任根 vs 数学安全

**张力**：TCKKS(PAPER_627CFA0B) 将CKKS的数学安全（信息论级）与TEE的硬件信任根（需信任Intel）混合——这在密码学纯粹主义者看来是"安全降级"，在系统工程师看来是"实用折衷"。

**矛盾候选**：是否存在将硬件信任根视为"安全债务"的方法论倾向？与Lightweight Auth(PAPER_96645819) 纯密码学方案形成了微妙对比。

## 3. 攻击研究的方法论价值

**张力**：Adaptive Backdoor GNN(PAPER_B1C0C91E) 是一篇攻击论文——提出了更危险的后门攻击方法。这在安全研究界是常规操作（"以攻促防"），但论文本身的方法论贡献是否能直接用于防御设计？

**矛盾候选**：攻击论文的"方法论可迁移性"与防御论文不同——攻击方法不能直接"迁移"为防御，读者需要额外的逆向思维步骤。

## 4. 集中式 vs 联邦式的精度权衡

**张力**：SplitAD(PAPER_BC534646) 声称联邦训练达到"接近集中式训练"的精度（t-test p>0.1），但Privacy-Preserving Key-Value Collection(PAPER_9955C321) 和 Plog(PAPER_B4EA5A99) 均承认隐私约束下存在固有精度损失。

**矛盾候选**：不同任务类型下的"精度损失可接受阈值"缺乏统一标准——什么程度的精度损失能换取多少隐私保护？缺少方法论级指导。
