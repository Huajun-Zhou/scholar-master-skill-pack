---
page_id: method-cards-index
page_type: hub
title: Method Cards Index
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_9955C321
- PAPER_627CFA0B
- PAPER_00BA0203
- PAPER_141EDBB3
- PAPER_8E699870
- PAPER_34285F47
related_pages:
- ../wiki/synthesis/method_evolution.md
- ../wiki/synthesis/research_lines.md
confidence: medium
updated_at: '2026-05-19'
---

# Method Cards — 方法卡片

基于陈志远教授15篇论文炼化的7个可迁移方法模块。

## 方法卡片清单

| # | 方法 | 论文数 | 方法族 | 核心问题 |
|---:|---|:---:|---|---|
| 1 | 联邦模型拆分与中间表示传输 | 1 | 联邦模型拆分 | 如何在垂直分区数据上实现隐私保护协作学习 |
| 2 | 分段随机响应LDP扰动 | 1 | 本地差分隐私 | 如何在复合键值数据上平衡LDP隐私和统计精度 |
| 3 | FHE+TEE混合安全计算 | 1 | 混合安全计算 | 如何消除同态加密的自举瓶颈 |
| 4 | 混合秘密共享联邦学习 | 1 | 混合安全计算 | 如何在LLM联邦微调中保护梯度隐私 |
| 5 | 图学习安全检测 | 3 | 图学习安全 | 如何用GNN检测恶意代码和图攻击 |
| 6 | 物理+DL混合UAV故障检测 | 1 | UAV安全 | 如何在UAV实时约束下检测多类型故障 |
| 7 | MARL驱动的安全通信优化 | 1 | UAV安全 | 如何在有窃听者的场景下优化多UAV安全通信 |

## 方法族总览

### 族1: 隐私保护协作学习 (2 cards)
- 联邦模型拆分 (SplitAD)
- 分段随机响应LDP (Key-Value LDP)

### 族2: 混合安全计算架构 (2 cards)
- FHE+TEE混合计算 (TCKKS)
- 混合秘密共享FL (PriFFT)

### 族3: 图学习安全分析 (1 card)
- 图学习安全检测 (Flash, GNNDroid, Adaptive Backdoor GNN)

### 族4: UAV可信自主系统 (2 cards)
- 物理+DL混合故障检测 (AeroGuard)
- MARL安全通信优化 (RSMA UAV)

## 方法成熟度

| 成熟度 | 方法 |
|---:|------|
| **核心** (≥3 papers) | 图学习安全检测 |
| **发展中** (1-2 papers) | 联邦模型拆分、LDP扰动、混合安全计算、UAV故障检测、MARL安全通信 |
