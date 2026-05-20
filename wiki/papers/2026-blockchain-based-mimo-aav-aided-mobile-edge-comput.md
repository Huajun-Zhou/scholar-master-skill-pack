---
page_id: paper-PAPER_513EB8C3
page_type: paper
title: 'Blockchain-Based MIMO AAV-Aided Mobile Edge Computing'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_513EB8C3
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Xiaojie Guo
venue: IEEE Transactions on Mobile Computing
---

# Paper: Blockchain-Based MIMO AAV-Aided Mobile Edge Computing

## 1. 元信息

- paper_id: PAPER_513EB8C3
- title: Blockchain-Based MIMO AAV-Aided Mobile Edge Computing
- year: 2026
- authors: Xiaojie Guo
- venue: IEEE Transactions on Mobile Computing
- DOI: 10.1109/TMC.2025.3649700

## 2. 一句话贡献

提出基于区块链的MIMO自主空中平台（AAV）辅助移动边缘计算框架，设计Energy-Based Raft（E-Raft）共识算法实现节能的AAV领导者选举，并开发在线优先级任务卸载和轨迹规划算法（OPOTS），联合优化截止期感知的任务卸载和AAV蜂群轨迹，性能提升最高达40%。（EVID-PAPER_513EB8C3-P1-C000）

## 3. 研究问题

### 3.1 原始问题
现有AAV辅助MEC方案主要考虑单天线AAV，忽略了MIMO系统的频谱效率优势。此外，区块链方案多采用能耗高的PoW共识机制，不适用于能量受限的AAV场景。需要设计能量高效的区块链共识机制和联合任务卸载-轨迹优化方案。（EVID-PAPER_513EB8C3-P1-C000）

### 3.2 学术抽象
- 问题类型：区块链+MEC+UAV联合优化
- 关键挑战：在AAV能量限制下实现可信任务卸载决策；MIMO信道下的NP-hard联合优化（卸载+轨迹）
- 形式化：给定M个移动设备和N架MIMO AAV，优化计算利润最大化问题P1=<I,F,Φ,Ω>（I:任务集，F:AAV资源，Φ:信道，Ω:能量）

### 3.3 问题重要性
将区块链可信机制引入无人机辅助MEC（移动边缘计算），同时解决AAV能耗瓶颈和MIMO通信优化，对可扩展可信边缘智能有重要意义。

## 4. 核心思想

三层协同设计：
1. **E-Raft共识**：通过一系列递减能量阈值实现动态领导者选举——高能量AAV优先成为leader执行决策，能耗尽后自动切换，避免PoW的高能耗
2. **MIMO信道建模**：利用MIMO多天线空间复用提升AAV-设备通信容量
3. **OPOTS算法**：在线优先级任务卸载和轨迹选择——基于任务截止期和计算利润的贪心优先级排序，逐轮由E-Raft选出的leader执行

（EVID-PAPER_513EB8C3-P5-C018, EVID-PAPER_513EB8C3-P8-C026, EVID-PAPER_513EB8C3-P9-C028）

## 5. 方法框架

- **输入**：移动设备任务集I（各任务含数据量、计算量、截止期）
- **输出**：任务卸载决策+AAV轨迹规划+区块链共识
- **模型**：MIMO信道模型 + MEC计算模型 + E-Raft共识模型
- **算法**：Threshold-Based Dynamic Leader Selection → Online Priority-based Offloading → Trajectory Selection (OPOTS) → Incentive Mechanism
- **数据集**：MATLAB仿真参数（见表II）
- **评价指标**：计算完成率、计算利润、移动效率、能耗

## 6. 实验设计

- **Baseline**：PoW共识方案、随机卸载方案、贪婪卸载方案
- **Ablation**：E-Raft vs PoW vs PBFT共识性能对比
- **Robustness**：不同AAV数量、任务密度下的完成率和利润

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| E-Raft共识能耗远低于PoW且保证共识安全性 | EVID-PAPER_513EB8C3-P11-C032 |
| OPOTS算法相比baseline方案实现最高40%性能提升 | EVID-PAPER_513EB8C3-P1-C000 |
| MIMO AAV相比单天线AAV在任务卸载容量上有显著优势 | EVID-PAPER_513EB8C3-P12-C034 |

## 8. 隐含假设

**论文明确假设**：AAV之间有可靠的通信链路支持共识消息传递；移动设备的任务信息真实（区块链保证）。
**系统推断**：AAV蜂群的能量消耗模型准确；E-Raft的阈值递减策略需要适当校准。

## 9. 局限性

**系统推断**：E-Raft在高AAV数量下共识延迟增加；MIMO信道状态信息（CSI）获取在高速AAV移动场景有挑战。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **能量感知共识机制**：E-Raft的"能量阈值递减领导者选举"——可迁移到其他能量受限的区块链IoT场景（如传感器网络、无人机蜂群、卫星星座）。
2. **MIMO+UAV通信增强**：MIMO空间复用提升UAV边缘计算频谱效率——可迁移到6G空天地一体化网络的边缘计算设计。
3. **区块链+边缘AI可信融合**：区块链保证卸载决策的可审计性——可迁移到联邦学习的模型聚合可信验证。

## 11. 与其他论文关系

- 前置工作：Raft共识、MIMO通信、UAV辅助MEC
- 同主题工作：与RSMA Multi-UAV Secure Communication互补（MEC计算 vs 安全通信）；与Joint Scheduling论文共享UAV边缘计算优化主题

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_513EB8C3-P1-C000 | 1 | Abstract | contribution | high |
| EVID-PAPER_513EB8C3-P1-C001 | 1 | Introduction | motivation | high |
| EVID-PAPER_513EB8C3-P3-C010 | 3 | System Model | mimo_channel | high |
| EVID-PAPER_513EB8C3-P5-C018 | 5 | Leader Selection | e_raft | high |
| EVID-PAPER_513EB8C3-P6-C020 | 6 | Consensus | consensus_detail | high |
| EVID-PAPER_513EB8C3-P8-C026 | 8 | Problem Form | optimization | high |
| EVID-PAPER_513EB8C3-P9-C028 | 9 | OPOTS | algorithm | high |
| EVID-PAPER_513EB8C3-P10-C030 | 10 | Incentive | mechanism | high |
| EVID-PAPER_513EB8C3-P11-C032 | 11 | Evaluation | result_consensus | high |
| EVID-PAPER_513EB8C3-P12-C034 | 12 | Evaluation | result_efficiency | high |
