---
page_id: paper-PAPER_B4EA5A99
page_type: paper
title: 'Plog: An Efficient and Privacy-Preserving Collaborative Learning Framework on Vertically Partitioned Graph Data'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_B4EA5A99
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Hui Zhu
venue: IEEE Transactions on Knowledge and Data Engineering (TKDE)
---

# Paper: Plog: An Efficient and Privacy-Preserving Collaborative Learning Framework on Vertically Partitioned Graph Data

## 1. 元信息

- paper_id: PAPER_B4EA5A99
- title: Plog: An Efficient and Privacy-Preserving Collaborative Learning Framework on Vertically Partitioned Graph Data
- year: 2026
- authors: Hui Zhu (Xidian Univ.)
- venue: IEEE Transactions on Knowledge and Data Engineering (TKDE)
- DOI: TBD from extraction

## 2. 一句话贡献

提出Plog——面向垂直分区图数据的高效隐私保护协作学习框架，解决图数据按特征或子图垂直分割存储在多个参与方时，如何在不泄露图结构隐私的前提下联合训练GNN模型的难题。（EVID-PAPER_B4EA5A99-P1-C000）

## 3. 研究问题

### 3.1 原始问题
图数据（如社交网络、分子结构、金融交易图）常以垂直方式分布在不同组织间（银行持有用户特征+电商持有交易关系）。各参与方的图数据互补但都包含敏感信息（用户隐私、商业秘密）。现有VFL方案主要面向表格数据，未能处理图数据的拓扑结构和节点间依赖。（EVID-PAPER_B4EA5A99-P1-C000）

### 3.2 学术抽象
- 问题类型：隐私保护图学习（Privacy-Preserving Graph Learning）
- 关键挑战：GNN的消息传递机制天然需要跨参与方的邻接信息传递；如何在不泄露各参与方的图局部结构的前提下完成消息传递
- 形式化：给定K个参与方，分别持有图G的不同子图G_k=(V, E_k, X_k)，联合训练GNN f_θ使得θ对所有参与方可用，且不泄露任意G_k的私有部分

### 3.3 问题重要性
图数据垂直分区在金融（银行-电商数据）、医疗（医院-保险公司数据）、安全（威胁情报共享）中普遍存在，实现隐私保护下图协作学习是实现"数据可用不可见"图智能的关键。

## 4. 核心思想

基于"图拆分+安全聚合"的隐私保护策略：将GNN的消息传递过程分解为安全的节点嵌入计算和跨参与方安全聚合两步。各参与方在本地计算节点嵌入（基于自身持有的图结构），然后通过安全多方计算协议（如加法秘密共享）聚合邻接信息，避免直接暴露图拓扑。（EVID-PAPER_B4EA5A99-P4-C012）

## 5. 方法框架

- **输入**：K个参与方各自的子图G_k = (V, E_k, X_k)，节点集V共享但边E_k和特征X_k各自持有
- **输出**：联合训练的GNN模型参数θ
- **模型**：隐私保护GNN（消息传递+安全聚合的交替执行）
- **算法**：本地图嵌入计算→安全跨参与方消息传递→全局聚合→模型更新
- **损失函数**：图分类/节点分类损失
- **数据集**：真实图数据集
- **评价指标**：模型精度（vs集中式训练）、隐私保护强度、通信和计算开销

## 6. 实验设计

- **Baseline**：集中式GNN训练、本地训练（无协作）、基础安全GNN方案
- **Ablation**：不同图分割方式的性能影响（按特征分割 vs 按边分割）
- **Robustness**：不同参与方数量和数据规模下的扩展性

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| Plog在垂直分区图上达到接近集中式训练的模型精度 | EVID-PAPER_B4EA5A99-P8-C020 |
| 安全聚合通信开销与参与方数量呈线性关系 | EVID-PAPER_B4EA5A99-P9-C022 |
| 按特征分割的垂直分区对GNN性能影响小于按边分割 | EVID-PAPER_B4EA5A99-P8-C021 |

## 8. 隐含假设

**论文明确假设**：参与方共享相同的节点集V（实体对齐已完成）；半诚实安全模型。
**系统推断**：图结构的稀疏性有助于降低安全聚合开销。

## 9. 局限性

**系统推断**：消息传递的轮数增加会导致安全计算开销累积；实体对齐(V)在实际中可能不完整（需结合Entity Resolution技术）。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"图拆分+安全传递"范式**：将GNN消息传递分解为本地嵌入+安全聚合两步——可迁移到联邦图学习、跨机构知识图谱融合、隐私保护推荐系统。
2. **垂直分区图的安全处理**：相较于"水平分区"（各参与方有不同的节点集），垂直分区的难度更大（节点共享但结构互补）——Plog的框架可适配于联邦知识图谱补全、医疗多模态图融合。

## 11. 与其他论文关系

- 前置工作：垂直联邦学习(VFL)、GNN、安全多方计算图算法
- 同主题工作：与SBIRCH-II互补（表格数据的聚类安全 vs 图数据的GNN安全）；与Flash互补（联邦图学习在安全检测[Flash] vs 隐私保护框架[Plog]）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_B4EA5A99-P1-C000 | 1 | Introduction | motivation_problem | high |
| EVID-PAPER_B4EA5A99-P2-C004 | 2 | Models/Design | system_model | high |
| EVID-PAPER_B4EA5A99-P4-C012 | 4 | Framework | secure_gcn_design | high |
| EVID-PAPER_B4EA5A99-P6-C016 | 6 | Security Analysis | privacy_guarantee | high |
| EVID-PAPER_B4EA5A99-P8-C020 | 8 | Evaluation | result_accuracy | high |
| EVID-PAPER_B4EA5A99-P8-C021 | 8 | Evaluation | result_partition | high |
| EVID-PAPER_B4EA5A99-P9-C022 | 9 | Evaluation | result_overhead | high |
