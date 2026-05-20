---
page_id: paper-PAPER_09026E9B
page_type: paper
title: 'Achieving Secure and Efficient Clustering for Multiple Source Time Series Data in Industrial Internet of Things'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_09026E9B
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Songnian Zhang
- Hui Zhu
- Yandong Zheng
- Fengwei Wang
venue: IEEE Transactions on Industrial Informatics
---

# Paper: Achieving Secure and Efficient Clustering for Multiple Source Time Series Data in Industrial Internet of Things

## 1. 元信息

- paper_id: PAPER_09026E9B
- title: Achieving Secure and Efficient Clustering for Multiple Source Time Series Data in Industrial IIoT
- year: 2026
- authors: Songnian Zhang, Hui Zhu, Yandong Zheng, Fengwei Wang (Xidian Univ.)
- venue: IEEE Transactions on Industrial Informatics
- DOI: 10.1109/TII.2026.3662497

## 2. 一句话贡献

提出SBIRCH-I和SBIRCH-II两种安全高效的工业物联网多源时序数据聚类方案，基于同态加密和秘密共享实现BIRCH聚类算法的隐私保护版本，在保护数据隐私的同时保持聚类精度。（EVID-PAPER_09026E9B-P1-C001）

## 3. 研究问题

### 3.1 原始问题
IIoT中多源时间序列数据分布在多个数据持有方，出于隐私和法规考虑各方不愿直接共享原始数据，但需要联合聚类分析以支持故障分类、设备管理等决策。现有隐私保护聚类方案通常牺牲效率或准确性。（EVID-PAPER_09026E9B-P1-C001）

### 3.2 学术抽象
- 问题类型：隐私保护分布式聚类（Privacy-Preserving Clustering）
- 关键挑战：在加密数据上高效执行BIRCH的CF树插入和节点分裂操作；平衡安全性（密码学强度）和效率
- 形式化：给定N个参与方的时序数据集，在不泄露原始数据的前提下，联合构建BIRCH CF树并输出聚类结果

### 3.3 问题重要性
IIoT中的时序数据聚类是故障检测、预测性维护、异常发现的基础操作。解决隐私保护下的多源数据聚类对工业4.0数据安全共享至关重要。

## 4. 核心思想

将BIRCH聚类算法的核心操作（CF树更新插入、节点分裂）改造为安全计算协议——SBIRCH-I使用加法同态加密实现基础隐私保护，SBIRCH-II使用算术+布尔秘密共享实现更强安全性。关键创新在于将CF距离比较（欧氏距离D2）转化为安全多方计算协议（SMIC协议），以及安全节点分裂（SHUI协议）的高效实现。（EVID-PAPER_09026E9B-P4-C030）

## 5. 方法框架

- **输入**：N个参与方的时序数据（垂直分割，不同参与方持有不同特征）
- **输出**：BIRCH CF树聚类结果
- **模型**：BIRCH（Balanced Iterative Reducing and Clustering using Hierarchies）算法
- **算法**：
  - SMIC协议：安全最小距离比较（基于同态加密）
  - SHUI协议：安全层次更新插入
  - SNS协议：安全节点分裂（含SOF混淆操作）
  - OSID协议：混淆安全ID关联
- **数据集**：IIoT基准时序数据集
- **评价指标**：聚类精度（与明文BIRCH对比）、计算/通信效率

## 6. 实验设计

- **Baseline**：明文BIRCH（聚类上界）、基础安全BIRCH方案
- **Ablation**：SBIRCH-I vs SBIRCH-II不同安全级别效率对比
- **Robustness**：不同数据规模下的性能稳定性

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| SBIRCH方案在保护数据隐私的同时达到与明文BIRCH接近的聚类精度 | EVID-PAPER_09026E9B-P8-C033 |
| SBIRCH-II提供比SBIRCH-I更强的安全保证（抵御共谋攻击）| EVID-PAPER_09026E9B-P7-C028 |
| SMIC协议高效实现加密数据的聚类距离比较 | EVID-PAPER_09026E9B-P4-C030 |

## 8. 隐含假设

**论文明确假设**：半诚实安全模型（honest-but-curious）；参与方数据已对齐。
**系统推断**：时序数据在聚类前已完成标准化预处理。

## 9. 局限性

**系统推断**：同态加密操作增加计算开销；仅支持BIRCH聚类算法（不适用于其他聚类范式如DBSCAN）。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **安全聚类算子抽象**：将聚类核心操作（距离比较、节点分裂）抽象为安全计算协议——可迁移到K-Means、层次聚类等其他聚类算法的隐私保护改造。
2. **阶梯式安全方案设计**：从同态加密基础版到秘密共享增强版的渐进式安全升级思路——可迁移到其他数据分析原语的安全改造（如安全回归、安全PCA）。

## 11. 与其他论文关系

- 前置工作：BIRCH聚类算法、同态加密、算术/布尔秘密共享
- 同主题工作：待后续跨论文综合（与Flash的图联邦学习、Plog的垂直分区图数据存在隐私计算技术关联）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_09026E9B-P1-C001 | 1 | Introduction | motivation | high |
| EVID-PAPER_09026E9B-P3-C010 | 3 | Models/Design | system_model | high |
| EVID-PAPER_09026E9B-P4-C030 | 4 | SMIC Protocol | secure_comparison | high |
| EVID-PAPER_09026E9B-P5-C031 | 5 | SHUI Protocol | secure_insertion | high |
| EVID-PAPER_09026E9B-P6-C032 | 6 | SNS Protocol | secure_split | high |
| EVID-PAPER_09026E9B-P7-C028 | 7 | Security Analysis | sbirch_ii_security | high |
| EVID-PAPER_09026E9B-P8-C033 | 8 | Performance | result_accuracy | high |
| EVID-PAPER_09026E9B-P8-C033 | 8 | Performance | result_efficiency | high |
| EVID-PAPER_09026E9B-P12-C040 | 12 | Conclusion | conclusion | high |
