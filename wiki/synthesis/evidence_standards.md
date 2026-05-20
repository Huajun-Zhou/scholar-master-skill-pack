---
page_id: synthesis-evidence-standards
page_type: synthesis
title: Evidence Standards — 实验验证范式
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_96645819
- PAPER_627CFA0B
- PAPER_8E699870
- PAPER_141EDBB3
confidence: medium
updated_at: '2026-05-19'
---

# Evidence Standards — 实验验证范式

基于15篇论文归纳的4类实验验证范式（B类综合归纳）。

## Type 1: 密码协议验证 (Cryptographic Protocol)

**适用论文**：TCKKS, Lightweight Auth, SBIRCH

- 形式化安全证明（安全规约、游戏序列证明）
- 性能基准测试：计算延迟/吞吐量/通信量 vs 标准方案
- 平台基准：ARM Cortex-M / Intel SGX / CPU
- 代码开源或可用性声明

## Type 2: 机器学习安全验证 (ML Security)

**适用论文**：Adaptive Backdoor GNN, Flash, GNNDroid, SplitAD

- 多数据集交叉验证（3+数据集）
- 与≥3种baseline方案对比
- 消融研究：模块必要性→设计选择→参数敏感性→极端测试
- 隐私-精度trade-off曲线（ε-F1曲线）
- 统计显著性检验（t-test, p-value）

## Type 3: 通信系统仿真验证 (Communication Simulation)

**适用论文**：RSMA UAV, Blockchain MIMO MEC, Joint Scheduling

- MATLAB/Python仿真环境
- 多个baseline（OMA/NOMA/随机策略/贪婪策略）
- 不同参数配置下的性能对比（通信负载、参与方数量、信噪比）
- 收敛性和运行时间分析

## Type 4: 系统/综述验证 (System/Survey)

**适用论文**：AeroGuard, Physical Attacks UAV

- 多平台验证（多种真实UAV）
- 故障注入实验（硬件/软件故障）
- 资源利用率分析（CPU/内存/推理延迟）
- 系统性文献综述（PRISMA方法）
