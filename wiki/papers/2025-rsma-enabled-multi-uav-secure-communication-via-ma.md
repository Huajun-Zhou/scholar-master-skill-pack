---
page_id: paper-PAPER_8E699870
page_type: paper
title: 'RSMA-Enabled Multi-UAV Secure Communication via MARL With Multi-Task Attention DRNN'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_8E699870
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2025
authors:
- Lijie Zheng
- Ji He
venue: IEEE journal
---

# Paper: RSMA-Enabled Multi-UAV Secure Communication via MARL With Multi-Task Attention DRNN

## 1. 元信息

- paper_id: PAPER_8E699870
- title: RSMA-Enabled Multi-UAV Secure Communication via MARL With Multi-Task Attention DRNN
- year: 2025
- authors: Lijie Zheng, Ji He
- venue: IEEE journal (TBD)

## 2. 一句话贡献

提出基于速率分割多址接入(RSMA)的多UAV安全通信方案，利用多智能体强化学习(MARL)结合多任务注意力DRNN，在存在窃听者(Eve)的物理层安全场景下联合优化UAV轨迹、功率分配和RSMA预编码，最大化安全通信速率。（EVID-PAPER_8E699870-P1-C000）

## 3. 研究问题

### 3.1 原始问题
多UAV安全通信面临频谱稀缺、干扰管理和抗窃听三大挑战。传统正交多址接入(OMA)频谱效率低，而现有NOMA方案在多UAV场景下SIC复杂度高。RSMA作为通用多址框架在理论上更优，但其在多UAV安全通信中的资源分配是一个高维非凸优化问题。（EVID-PAPER_8E699870-P1-C000）

### 3.2 学术抽象
- 问题类型：物理层安全 + 多智能体强化学习优化
- 关键挑战：在高维连续动作空间（UAV轨迹+功率+RSMA预编码器）中联合优化；对抗性环境（窃听者信道不确定性）
- 形式化：max_{P, W, Q} R_sec = Σ_k [R_k - R_eve_k]^+，s.t. UAV机动约束、功率预算、RSMA码本大小

### 3.3 问题重要性
UAV在军事、应急、智慧城市中的安全通信是核心需求。RSMA作为6G候选多址技术，其与UAV物理层安全的结合代表了前沿方向。

## 4. 核心思想

两层创新：
1. **通信层**：采用RSMA将每UAV的消息拆分为公共部分（所有接收者可解码）和私有部分（仅目标接收者可解码），通过调节拆分比例在安全速率和服务质量之间灵活trade-off
2. **决策层**：MARL框架中每UAV作为独立智能体，使用多任务注意力DRNN共享部分观测（协作）同时保持个体策略（竞争），注意力机制使UAV自适应关注关键窃听威胁方向
（EVID-PAPER_8E699870-P3-C010, EVID-PAPER_8E699870-P5-C016）

## 5. 方法框架

- **输入**：UAV位置、信道状态信息(CSI)、窃听者信道估计
- **输出**：UAV轨迹调整、发射功率、RSMA预编码矩阵
- **模型**：RSMA通信模型 + Multi-Task Attention DRNN（多智能体深度循环神经网络）
- **算法**：MARL训练→分布式策略执行（每UAV基于本地观测决策）
- **损失函数**：负安全通信速率（最大化安全速率 = 最小化负安全速率）
- **数据集**：仿真的多UAV通信场景
- **评价指标**：安全通信速率、保密中断概率、频谱效率

## 6. 实验设计

- **Baseline**：OMA（TDMA/FDMA）、NOMA、无注意力DRNN MARL、随机策略
- **Ablation**：有/无RSMA vs 有/无注意力机制 vs 有/无多任务学习
- **Robustness**：窃听者CSI不确定性；不同UAV数量的扩展性

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| RSMA+MARL方案在安全速率上显著优于OMA和NOMA基线 | EVID-PAPER_8E699870-P12-C032 |
| 多任务注意力机制提升了对抗窃听的方向性防御能力 | EVID-PAPER_8E699870-P13-C034 |
| 方案在窃听者CSI不完美时仍保持鲁棒安全性能 | EVID-PAPER_8E699870-P13-C035 |

## 8. 隐含假设

**论文明确假设**：合法接收者和窃听者的CSI可获取（或统计已知）；UAV间协作通信链路可靠。
**系统推断**：MARL策略的泛化性受限于训练环境多样性；RSMA的码本设计假设了特定的SIC能力。

## 9. 局限性

**系统推断**：MARL训练时间可能较长（离线训练+在线推理假设）；RSMA的SIC在实际硬件上的实现复杂度较高；仅考虑单窃听者场景。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"RSMA+MARL"安全通信范式**：RSMA提供灵活的速率安全trade-off维度，MARL提供分布式自适应决策——可迁移到车联网安全V2X通信、卫星星座安全通信、水下传感网络安全传输。
2. **多任务注意力在安全中的应用**：注意力机制用于重点关注安全威胁方向——可迁移到其他对抗性场景（如对抗ML中的注意力防御、频谱对抗中的注意力抗干扰）。
3. **物理层安全+AI决策融合**：物理层安全的数学基础和强化学习的自适应能力互补——可迁移到智能反射面(IRS)辅助安全通信、太赫兹安全通信等6G场景。

## 11. 与其他论文关系

- 前置工作：RSMA理论、MIMO物理层安全、MARL资源分配
- 同主题工作：与Blockchain MIMO MEC互补（MIMO用于计算增强 vs MIMO+RSMA用于安全通信）；与Joint Scheduling论文互补（边缘计算调度 vs 安全通信调度）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_8E699870-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_8E699870-P2-C005 | 2 | System Model | rsma_system | high |
| EVID-PAPER_8E699870-P3-C010 | 3 | MARL Framework | marl_setup | high |
| EVID-PAPER_8E699870-P5-C016 | 5 | Attention DRNN | attention_mechanism | high |
| EVID-PAPER_8E699870-P8-C022 | 8 | Training | marl_training | high |
| EVID-PAPER_8E699870-P12-C032 | 12 | Evaluation | result_secrecy | high |
| EVID-PAPER_8E699870-P13-C034 | 13 | Evaluation | result_attention | high |
| EVID-PAPER_8E699870-P13-C035 | 13 | Evaluation | result_robustness | high |
