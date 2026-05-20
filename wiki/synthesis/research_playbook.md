---
page_id: synthesis-research-playbook
page_type: synthesis
title: Research Playbook — 可迁移研究框架
status: draft
evidence_level: C
source_papers: []
confidence: medium
updated_at: '2026-05-19'
---

# Research Playbook — 可迁移研究框架

基于陈志远教授15篇论文的方法论提炼，为新研究者提供的可操作研究框架。**以下均为 C 类迁移推断。**

## Step 1: 威胁建模 (Threat Modeling)

1. 明确系统边界和资产（数据、模型、通信链路、物理设备）
2. 定义攻击者模型：能力（计算能力、数据访问权限、物理接近度）、目标（窃听/篡改/拒绝服务/投毒）
3. 选择安全模型：Honest-but-Curious / Malicious / Covert / Physical
4. 定义安全需求：机密性指标、完整性保证、可用性SLA

## Step 2: 密码原语选型

| 场景 | 推荐原语组合 | 理由 |
|------|-------------|------|
| 数据收集+轻量级设备 | LDP (本地差分隐私) | 无服务器信任假设，计算轻量 |
| 保护下的ML训练 | ASS(线性层)+FSS(非线性层) | 线性操作零通信，非线性操作安全外包 |
| 保护下的ML推理 | FHE+TEE混合 (TCKKS模式) | 避免自举瓶颈 |
| IIoT设备认证 | 对称密码+轻量AEAD | 避免PKI的计算开销 |
| 多方安全聚类/分析 | HE+SS混合 (SBIRCH模式) | 按运算类型分配最优安全协议 |

## Step 3: 协议设计

1. 定义协议参与方角色和交互消息格式
2. 将安全操作嵌入算法流程的最关键环节（非全链路加密）
3. 设计"正常执行+异常退出"的安全保证机制
4. 优化通信模式：减少轮次、使用单向通信（如SplitAD）

## Step 4: 安全证明

- **密码协议**：安全规约（Real-Ideal模拟、游戏序列证明）
- **ML安全**：提供隐私-精度trade-off曲线(ε-Acc)；攻击成功率+逃逸率
- **系统安全**：满足既定安全模型下所有安全需求

## Step 5: 实验设计检查清单

- [ ] 形式化安全证明完整
- [ ] ≥3种baseline方案对比
- [ ] ≥3个数据集/场景的交叉验证
- [ ] 参数敏感性分析（隐私预算/参与方数/数据规模）
- [ ] 计算/通信/存储开销的详细基准测试
- [ ] 局限性诚实讨论
- [ ] 代码开源或可重复性说明

## Step 6: 论文结构蓝图

### Introduction (4段)
P1: 应用场景和安全威胁
P2: 现有方案的局限（安全不足/效率过低）
P3: 我们的核心洞察和方法概述
P4: 贡献摘要

### Threat Model & Design Goals
- 系统+安全模型的形式化定义
- 安全需求和设计目标

### Proposed Scheme
- 密码原语背景
- 方案架构总览 → 各模块技术细节
- 安全/隐私增强机制（可选）

### Security Analysis
- 形式化安全证明（或安全论证）
- 复杂度分析

### Performance Evaluation
- 实验设置（平台/数据集/metrics/baselines）
- 主要结果+消融+鲁棒性分析

### Discussion & Conclusion
- 结果分析+major limitations+future work
