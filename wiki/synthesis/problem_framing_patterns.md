---
page_id: synthesis-problem-framing-patterns
page_type: synthesis
title: Problem Framing Patterns — 问题定义模式
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_627CFA0B
- PAPER_141EDBB3
- PAPER_B1C0C91E
confidence: medium
updated_at: '2026-05-19'
---

# Problem Framing Patterns — 问题定义模式

基于15篇论文归纳的4种问题定义模式（B类综合归纳）。

## Pattern 1: 威胁-防御对抗框架

**特征**：从攻击者视角出发，定义攻击能力边界→确定系统安全需求→设计防御方案
**代表论文**：Adaptive Backdoor GNN, Physical Attacks UAV, RSMA UAV
**问题表述模板**："在攻击者具有能力A的场景下，系统S面临威胁T，现有防御D因局限性L无法应对，需设计新防御D'"

## Pattern 2: 隐私-效率权衡优化

**特征**：定义隐私保护需求(ε,δ)→分析现有隐私方案的效率瓶颈→设计新协议优化trade-off
**代表论文**：Key-Value LDP, PriFFT, TCKKS, SplitAD
**问题表述模板**："现有方案P提供安全S但效率E不可接受（或因效率E而牺牲安全S），需在保证安全S的前提下将E提升至可实用水平"

## Pattern 3: 物理-数据协同感知

**特征**：物理模型提供期望基线→数据驱动模型学习异常偏离→动态融合策略
**代表论文**：AeroGuard, RSMA UAV
**问题表述模板**："物理模型方法M_p准确但保守（高precision/低recall），数据驱动方法M_d灵敏但不稳定（高recall/低precision），需设计融合策略使两者互补"

## Pattern 4: 分布式-集中式桥接

**特征**：集中式方案的性能上界vs分布式部署的现实约束→拆分+安全协议桥接
**代表论文**：SplitAD, Plog, Flash, SBIRCH
**问题表述模板**："集中式方案C在完整数据上达到性能P，但数据分布式存储于K方且不可集中，需设计分布式方案D使得P(D)≈P(C)且满足隐私约束"
