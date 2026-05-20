---
page_id: paper-PAPER_9955C321
page_type: paper
title: 'Achieving Privacy-Preserving and High-Accuracy Collection of Key-Value Data With Local Differential Privacy'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_9955C321
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Junpeng Zhang
- Hui Zhu
- Jiaqi Zhao
- Mengqian Li
venue: IEEE Transactions on Information Forensics and Security (TIFS)
---

# Paper: Achieving Privacy-Preserving and High-Accuracy Collection of Key-Value Data With Local Differential Privacy

## 1. 元信息

- paper_id: PAPER_9955C321
- title: Achieving Privacy-Preserving and High-Accuracy Collection of Key-Value Data With Local Differential Privacy
- year: 2026
- authors: Junpeng Zhang, Hui Zhu, Jiaqi Zhao, Mengqian Li (Xidian Univ. & Hebei Normal Univ.)
- venue: IEEE Transactions on Information Forensics and Security (TIFS), Vol. 21
- DOI: 10.1109/TIFS.2026.3671048

## 2. 一句话贡献

提出基于分段随机响应（Segmented Randomized Response）的本地差分隐私键值数据收集方案，在单轮通信内同时实现高精度键频率估计和值均值估计，解决了现有LDP方案在复合数据类型上精度-隐私-通信三重权衡的难题。（EVID-PAPER_9955C321-P1-C000）

## 3. 研究问题

### 3.1 原始问题
IoT服务商依赖用户键值数据（如app使用频率、健康指标）进行分析决策，但直接传输敏感数据存在严重隐私风险。现有LDP方案主要面向简单数据类型，对键值等复合数据的支持不足，且多轮迭代方案通信开销大。（EVID-PAPER_9955C321-P1-C001）

### 3.2 学术抽象
- 问题类型：隐私保护数据收集（LDP-based Private Data Collection）
- 关键挑战：在(ε,δ)-LDP约束下，同时保证键频率和值均值估计的高精度，并最小化通信轮次
- 形式化：N个用户各持有键值对集合{(k_i,v_i)}，设计本地扰动机制M使服务器可从扰动数据中无偏估计各键频率f̂_k和均值μ̂_k

### 3.3 问题重要性
键值数据是IoT中最普遍的复合数据类型之一。隐私保护的键值收集对智能家居、健康监测、城市感知等有直接应用价值。

## 4. 核心思想

将键值数据拆分为键和值两部分——键部分使用优化后的分段随机响应（Segmented Randomized Response, 基于GRR改进），值部分根据键的存在与否做有条件扰动。通过一次通信即可完成数据收集，避免多轮迭代，理论上证明方案满足(ε,δ)-LDP。（EVID-PAPER_9955C321-P3-C004, EVID-PAPER_9955C321-P4-C008）

## 5. 方法框架

- **输入**：N个用户持有的键值对集合
- **输出**：服务端键频率估计{f̂_k}和均值估计{μ̂_k}
- **模型**：客户端-服务器架构，本地扰动+服务端统计估计
- **算法**：
  - Phase I: 客户端执行Segmented Randomized Response扰动
  - Phase II: 服务器收集扰动数据
  - Phase III: 服务器统计估计（频率+均值联合估计）
- **损失函数**：MSE（均方误差）
- **数据集**：合成数据集 + 真实世界数据集
- **评价指标**：MSE（键频率/均值估计误差）、NCR（归一化累积排名）

## 6. 实验设计

- **Baseline**：MLPKV等现有LDP键值收集方案
- **Ablation**：不同隐私预算ε对估计精度的影响
- **Robustness**：不同数据规模和数据分布下的性能稳定性
- **Case Study**：真实世界数据集上的键值频率/均值估计

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| 分段随机响应机制在相同隐私预算下实现优于baseline的频率和均值估计精度 | EVID-PAPER_9955C321-P9-C017 |
| 单轮通信方案避免了现有多轮迭代的高通信开销 | EVID-PAPER_9955C321-P5-C010 |
| 理论证明方案满足(ε,δ)-LDP | EVID-PAPER_9955C321-P6-C012 |
| 真实数据集上MSE显著优于baseline | EVID-PAPER_9955C321-P10-C018 |
| NCR验证了方案在键频率排序上的保序性 | EVID-PAPER_9955C321-P9-C016 |

## 8. 隐含假设

**论文明确假设**：服务器是honest-but-curious的半可信方（LDP标准假设）；用户本地数据真实完整。
**系统推断**：键空间大小在可枚举范围内；value为连续数值类型。

## 9. 局限性

**系统推断**：键候选集过大会影响GRR效率；仅支持数值型value；单轮方案在高维键空间下估计效率可能下降。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"分段扰动"隐私范式**：将复合数据拆分为结构和数值两部分，针对不同语义使用差异化扰动策略——可迁移到图数据的拓扑+特征隐私保护、时间序列的趋势+残差隐私保护。
2. **单轮通信设计原则**：通过精心设计本地扰动编码在LDP中实现通信-精度trade-off——可迁移到联邦学习中梯度更新的隐私保护。
3. **统计后处理技术**：服务端校准方法实现扰动后无偏估计——通用可迁移的隐私数据统计分析技术。

## 11. 与其他论文关系

- 前置工作：RAPPOR (Google), Apple LDP, MLPKV
- 同主题工作：待跨论文综合（与Plog图数据隐私、PriFFT联邦学习隐私存在技术关联）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_9955C321-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_9955C321-P1-C001 | 1 | Introduction | problem_gap | high |
| EVID-PAPER_9955C321-P2-C003 | 2 | Models/Design | system_model | high |
| EVID-PAPER_9955C321-P3-C004 | 3 | Preliminaries | ldp_background | high |
| EVID-PAPER_9955C321-P4-C008 | 4 | Building Blocks | segmented_rr | high |
| EVID-PAPER_9955C321-P5-C010 | 5 | Proposed Scheme | algorithm | high |
| EVID-PAPER_9955C321-P6-C012 | 6 | Privacy Analysis | proof | high |
| EVID-PAPER_9955C321-P8-C015 | 8 | Performance | analysis | high |
| EVID-PAPER_9955C321-P9-C016 | 9 | Evaluation | ncr_result | high |
| EVID-PAPER_9955C321-P9-C017 | 9 | Evaluation | mse_result | high |
| EVID-PAPER_9955C321-P10-C018 | 10 | Real Datasets | real_result | high |
