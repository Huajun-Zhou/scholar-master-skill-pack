---
page_id: paper-PAPER_B1C0C91E
page_type: paper
title: 'Adaptive Backdoor Attacks With Reasonable Constraints on Graph Neural Networks'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_B1C0C91E
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2025
authors:
- Jiachen Li
- Shujun Li
venue: IEEE Transactions on Dependable and Secure Computing (TDSC)
---

# Paper: Adaptive Backdoor Attacks With Reasonable Constraints on Graph Neural Networks

## 1. 元信息

- paper_id: PAPER_B1C0C91E
- title: Adaptive Backdoor Attacks With Reasonable Constraints on Graph Neural Networks
- year: 2025
- authors: Jiachen Li, Shujun Li
- venue: IEEE Transactions on Dependable and Secure Computing (TDSC), Vol. 22, No. 4
- DOI: 10.1109/TDSC.2025.3543020

## 2. 一句话贡献

提出针对GNN的自适应后门攻击框架，在图级（graph-level）和节点级（node-level）任务上分别设计具备"合理约束"的自适应触发器生成策略，克服了现有攻击使用固定模式触发器易被检测的缺陷，在保持攻击成功率（ASR）的同时大幅提升隐蔽性。（EVID-PAPER_B1C0C91E-P1-C000）

## 3. 研究问题

### 3.1 原始问题
GNN在安全敏感场景（恶意软件检测、医疗诊断）广泛应用，其后门攻击威胁日益严重。但现有攻击使用固定模式触发器且缺乏合理约束，导致攻击隐蔽性不足—固定触发器在拓扑结构和节点特征上产生异常模式，容易被防御机制检测。（EVID-PAPER_B1C0C91E-P1-C001）

### 3.2 学术抽象
- 问题类型：图神经网络对抗攻击安全性（Adversarial Attack on GNNs）
- 关键挑战：设计自适应触发器使之适应各图样本的独特特征（拓扑、边关系、节点属性），同时施加合理约束使其不偏离正常数据分布
- 形式化：对于图级任务，给定目标图G_i和标签y_t，生成自适应触发器T_i使f(G_i+T_i)=y_t且T_i在分布上接近合法子图

### 3.3 问题重要性
GNN后门攻击研究是"以攻促防"的典型——理解攻击者如何设计隐蔽后门有助于开发更鲁棒的检测和防御机制。

## 4. 核心思想

- **图级攻击**：Proportional Random Node Selection——基于节点度和中心性等图属性自适应选择触发节点，而非对所有目标图使用相同的触发子图拓扑
- **节点级攻击**：Feature Selection——基于节点特征的敏感度分析自适应选择哪些特征维度注入触发器，施加Lp范数约束使之不可区分于正常特征扰动
- 核心洞察：触发器需要"看起来像正常数据"才能逃避检测，这需要针对每个样本做自适应调整而非使用固定模式（EVID-PAPER_B1C0C91E-P4-C020）

## 5. 方法框架

- **输入**：目标图/目标节点 + 目标标签
- **输出**：含后门触发器的投毒样本
- **模型**：图级攻击-比例随机节点选择；节点级攻击-特征敏感度选择
- **算法**：Adaptive Graph-Level Backdoor Attack（图级）；Adaptive Node-Level Backdoor Attack（节点级）
- **损失函数**：攻击成功率(ASR) + 触发器隐蔽性约束（图级：子图同构性约束；节点级：特征扰动范数约束）
- **数据集**：图分类数据集 + 节点分类数据集（详见论文Table II/III）
- **评价指标**：ASR（攻击成功率）、ACC（主任务精度下降）、Evasion Rate（对防御的逃逸率）

## 6. 实验设计

- **Baseline**：固定模式GNN后门攻击方案（节点级和图层级各baseline）
- **Ablation**：自适应触发器 vs 固定模式触发器；有约束 vs 无约束触发器
- **Robustness**：针对现有后门防御机制的逃逸实验
- **Case Study**：恶意软件检测和医疗诊断场景

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| 自适应触发器在ASR相近的情况下隐蔽性显著优于固定模式 | EVID-PAPER_B1C0C91E-P10-C030 |
| 合理约束（比例选择+特征扰动范数）有效降低触发器可检测性 | EVID-PAPER_B1C0C91E-P10-C031 |
| 攻击对GNN后门防御机制具有高逃逸率 | EVID-PAPER_B1C0C91E-P14-C033 |
| 图级和节点级的自适应策略均有效 | EVID-PAPER_B1C0C91E-P14-C034 |

## 8. 隐含假设

**论文明确假设**：攻击者可在训练阶段注入投毒样本但无法控制推理阶段的输入（标准后门威胁模型）；攻击者已知目标模型架构但不控制训练过程。
**系统推断**：对手能获取足够的合法样本用于学习数据分布以约束触发器生成。

## 9. 局限性

**论文明确局限**：仅针对GNN的特定架构评估；未考虑自适应防御（如动态触发器检测）。
**系统推断**：当防御者同样使用自适应策略时逃逸率可能下降；仅研究监督学习场景。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"自适应攻击"设计原则**：攻击应根据目标样本的个体特征（而非全局固定模式）生成——此原则可迁移到其他ML后门攻击场景（如NLP后门、联邦学习后门）。
2. **合理约束作为隐蔽性工具**：将攻击隐蔽性形式化为对触发器分布的统计约束——可迁移到隐私攻击（成员推理、属性推理）中的隐蔽性设计。
3. **"以攻促防"价值**：该攻击揭示GNN防御的薄弱点——防御方应重点检测偏离样本自身分布的异常子结构而非全局异常模式。

## 11. 与其他论文关系

- 前置工作：BadNets (图像后门)、GTA/UDA (GNN后门)
- 同主题工作：待后续跨论文综合（与GNNDroid的Android恶意软件检测防御存在攻防关联）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_B1C0C91E-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_B1C0C91E-P1-C001 | 1 | Introduction | problem_gap | high |
| EVID-PAPER_B1C0C91E-P2-C005 | 2 | Related Work | literature | high |
| EVID-PAPER_B1C0C91E-P3-C009 | 3 | Preliminary | gnn_background | high |
| EVID-PAPER_B1C0C91E-P4-C020 | 4 | Graph-Level Attack | adaptive_trigger | high |
| EVID-PAPER_B1C0C91E-P5-C021 | 5 | Node Selection | proportional_random | high |
| EVID-PAPER_B1C0C91E-P7-C024 | 7 | Node-Level Attack | feature_selection | high |
| EVID-PAPER_B1C0C91E-P10-C030 | 10 | Evaluation | result_evasion | high |
| EVID-PAPER_B1C0C91E-P10-C031 | 10 | Evaluation | result_constraint | high |
| EVID-PAPER_B1C0C91E-P14-C033 | 14 | Node Class | result_node | high |
| EVID-PAPER_B1C0C91E-P14-C034 | 14 | Node Class | result_graph | high |
