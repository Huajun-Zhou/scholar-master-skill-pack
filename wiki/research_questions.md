---
page_id: research-questions
page_type: synthesis
title: Research Questions — 研究问题体系
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_0A8C55F0
- PAPER_9955C321
- PAPER_09026E9B
- PAPER_B1C0C91E
- PAPER_141EDBB3
- PAPER_513EB8C3
- PAPER_F530EB8C
- PAPER_34285F47
- PAPER_96645819
- PAPER_E155CF85
- PAPER_B4EA5A99
- PAPER_00BA0203
- PAPER_8E699870
- PAPER_627CFA0B
related_pages:
- research_paradigm
- synthesis/research_lines
confidence: medium
updated_at: '2026-05-19'
---

# Research Questions — 研究问题体系

基于15篇论文归纳的四类核心研究问题（B类综合归纳）。

## Q1: 如何在数据不可见前提下实现协作学习？

**核心挑战**：多方持有互补数据，隐私和法规要求不共享原始数据，但联合建模收益巨大。

| 子问题 | 代表论文 |
|--------|---------|
| 垂直分区数据的联邦异常检测 | SplitAD (PAPER_BC534646) |
| 隐私保护键值数据收集 | Key-Value LDP (PAPER_9955C321) |
| 垂直分区图数据的协作GNN训练 | Plog (PAPER_B4EA5A99) |
| 联邦图学习的恶意脚本检测 | Flash (PAPER_F530EB8C) |
| 联邦LLM微调的梯度隐私 | PriFFT (PAPER_00BA0203) |

## Q2: 如何在资源受限条件下实现可信通信？

**核心挑战**：IIoT/UAV设备计算和能量受限，传统密码协议开销过大，但安全需求不降低。

| 子问题 | 代表论文 |
|--------|---------|
| IIoT轻量级可信认证与数据传输 | Lightweight Auth (PAPER_96645819) |
| 边缘计算中节能区块链共识 | Blockchain MIMO MEC (PAPER_513EB8C3) |
| CKKS同态加密的自举瓶颈消除 | TCKKS (PAPER_627CFA0B) |
| 安全高效的IIoT时序数据聚类 | SBIRCH (PAPER_09026E9B) |

## Q3: 如何保障UAV系统的物理层和通信安全？

**核心挑战**：UAV物理暴露面大，通信链路易受窃听/干扰，但飞行安全要求实时性。

| 子问题 | 代表论文 |
|--------|---------|
| RSMA多址接入的抗窃听安全通信 | RSMA Multi-UAV (PAPER_8E699870) |
| UAV物理攻击的系统性防御 | Physical Attacks UAV (PAPER_E155CF85) |
| 实时多类型UAV故障检测 | AeroGuard (PAPER_141EDBB3) |
| 多UAV感知数据卸载与边缘推理调度 | Joint Scheduling (PAPER_0A8C55F0) |

## Q4: 如何检测和防御图数据的对抗攻击？

**核心挑战**：GNN在图结构数据上的安全脆弱性（后门攻击、恶意软件），需要有效的检测和攻击理解。

| 子问题 | 代表论文 |
|--------|---------|
| GNN的自适应隐蔽后门攻击 | Adaptive Backdoor GNN (PAPER_B1C0C91E) |
| Android恶意软件的图学习检测 | GNNDroid (PAPER_34285F47) |

## 交叉研究主题

**隐私 × 安全**：PriFFT、Plog、SplitAD、Key-Value LDP均在安全模型下保护隐私
**UAV × 可信**：RSMA UAV、AeroGuard、Physical Attacks UAV构成UAV可信自主系统
**图学习 × 安全**：Adaptive Backdoor GNN和GNNDroid分别从攻和防两个角度研究GNN安全
**联邦学习 × 效率**：Flash、SplitAD、PriFFT均关注联邦范式下的通信/计算效率优化
