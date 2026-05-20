---
page_id: paper-PAPER_0A8C55F0
page_type: paper
title: 'Joint Scheduling of Sensing Data Offloading and Edge Inference for Multi-UAV Networks'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_0A8C55F0
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2025
authors:
- Yanan Du
- Sai Xu
- Yinbo Yu
venue: IEEE Transactions on Mobile Computing
---

# Paper: Joint Scheduling of Sensing Data Offloading and Edge Inference for Multi-UAV Networks

## 1. 元信息

- paper_id: PAPER_0A8C55F0
- title: Joint Scheduling of Sensing Data Offloading and Edge Inference for Multi-UAV Networks
- year: 2025
- authors: Yanan Du (Univ. of Sheffield), Sai Xu (UCL), Yinbo Yu (NUAA)
- venue: IEEE Transactions on Mobile Computing
- DOI: 10.1109/TMC.2025.3649700

## 2. 一句话贡献

提出多无人机网络中感知数据卸载与边缘推理的联合调度框架，利用跨阶段通信-计算并行性，通过遗传算法（GA-Joint/GA-DAG）优化数据卸载策略和DNN推理调度，最小化端到端感知延迟。（EVID-PAPER_0A8C55F0-P1-C000）

## 3. 研究问题

### 3.1 原始问题
多UAV协同感知需要将异构感知流（RGB/深度/LiDAR）经无线上行卸载到边缘服务器进行多分支DNN推理，但现有方案忽略卸载与推理间的跨阶段交互——异步分支执行可在通信-计算间实现流水线并行优化。（EVID-PAPER_0A8C55F0-P1-C000）

### 3.2 学术抽象
- 问题类型：多UAV边缘推理的计算-通信联合调度优化
- 关键挑战：同步感知融合约束下的异步调度；策略空间的紧凑表征
- 形式化：N个UAV、M分支DNN，联合优化数据卸载顺序和DNN分支执行时间表以最小化端到端延迟

### 3.3 问题重要性
多UAV网络是巡检、监视、搜救等实时应用的使能技术，端到端延迟直接影响决策质量。跨阶段并行优化是提升系统效率的关键。

## 4. 核心思想

利用异步分支执行的灵活性：早到达的感知流允许其对应的DNN分支提前开始推理，无需等待所有流完成传输。将问题建模为联合调度优化问题，用GA搜索最优策略——GA-Joint（20维全联合调度）和GA-DAG（12维轻量DAG调度），后者在接近GA-Joint性能的同时大幅降低搜索复杂度。（EVID-PAPER_0A8C55F0-P5-C021, EVID-PAPER_0A8C55F0-P7-C028）

## 5. 方法框架

- **输入**：多UAV异构感知流（RGB图像、深度图、LiDAR点云）
- **输出**：最小化端到端延迟的调度方案（数据卸载顺序+推理时间表）
- **模型**：多分支DNN（各分支处理对应模态，边缘服务器端特征级/决策级融合）
- **算法**：
  - GA-Joint: Synchronization-Aware Fusion Model + Release-Time Propagation + DAG Scheduling + Communication-Stage Decoding
  - GA-DAG: 轻量级12维策略向量的GA调度
- **损失函数**：端到端延迟（最小化目标）
- **数据集**：仿真生成的多UAV感知场景
- **评价指标**：端到端延迟（不同通信负载C=2/4/6）

## 6. 实验设计

- **Baseline**：严格同步调度策略（所有流传输完成后才启动推理）
- **Ablation**：GA-Joint vs GA-DAG性能对比
- **Robustness**：不同通信负载(C=2/4/6)下的延迟表现
- **其他**：遗传算法收敛性分析

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| 异步分支调度相比同步策略显著降低端到端延迟 | EVID-PAPER_0A8C55F0-P10-C030 |
| GA-DAG轻量方案在接近GA-Joint性能的同时大幅降低搜索空间 | EVID-PAPER_0A8C55F0-P10-C031 |
| 通信负载增加时联合调度优势更显著 | EVID-PAPER_0A8C55F0-P11-C032 |
| Release-time propagation有效实现跨阶段流水线并行 | EVID-PAPER_0A8C55F0-P5-C021 |

## 8. 隐含假设

**系统推断**：边缘服务器算力充足且DNN推理时间可预测；UAV间通信信道稳定；感知模态间无强依赖可独立处理。

## 9. 局限性

**系统推断**：仅仿真验证未实际部署；GA调度为离线优化未考虑动态拓扑；未建模无线信道竞争和干扰。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **跨阶段并行调度范式**：将通信和计算"异步化"，允许部分结果先行处理——可迁移到车联网协同感知、卫星边缘推理等分布式感知场景。
2. **策略空间降维方法**：从20维到12维的策略降维思路——在复杂调度中设计"轻量代理策略"大幅降低搜索复杂度。

## 11. 与其他论文关系

- 前置工作：多UAV协同感知、DNN模型分割推理、移动边缘计算
- 同主题工作：待跨论文综合（与RSMA Multi-UAV Secure Communication存在UAV通信优化关联）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_0A8C55F0-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_0A8C55F0-P2-C004 | 2 | System Model | architecture | high |
| EVID-PAPER_0A8C55F0-P4-C014 | 4 | Sync-Aware Fusion | fusion_model | high |
| EVID-PAPER_0A8C55F0-P5-C021 | 5 | GA-Joint | algorithm | high |
| EVID-PAPER_0A8C55F0-P7-C028 | 7 | GA-DAG | lightweight_alg | high |
| EVID-PAPER_0A8C55F0-P10-C030 | 10 | Simulation | result_latency | high |
| EVID-PAPER_0A8C55F0-P10-C031 | 10 | Simulation | result_comparison | high |
| EVID-PAPER_0A8C55F0-P11-C032 | 11 | Impact of Comm | robustness | high |
| EVID-PAPER_0A8C55F0-P12-C034 | 12 | Conclusions | conclusion | high |
