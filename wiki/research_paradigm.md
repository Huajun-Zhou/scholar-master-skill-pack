---
page_id: research-paradigm
page_type: synthesis
title: Research Paradigm — 研究范式
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_0A8C55F0
- PAPER_9955C321
- PAPER_09026E9B
- PAPER_B1C0C91E
- PAPER_141EDBB3
- PAPER_513EB8C3
- PAPER_F530EB8C
- PAPER_34285F47
- PAPER_96645819
- PAPER_E155CF85
- PAPER_B4EA5A99
- PAPER_00BA0203
- PAPER_8E699870
- PAPER_627CFA0B
related_pages:
- research_questions
- synthesis/research_lines
- synthesis/method_evolution
- synthesis/problem_framing_patterns
- synthesis/evidence_standards
- synthesis/research_playbook
confidence: medium
updated_at: '2026-05-19'
---

# Research Paradigm — 研究范式

基于15篇公开论文提炼的陈志远教授研究范式。**以下均为 B 类综合归纳。**

## 1. 范式总览

陈志远教授的研究范式可概括为：**"威胁模型驱动的安全系统设计"范式**——从特定场景（IIoT/UAV/分布式学习）的安全威胁出发，建立形式化威胁模型和安全需求定义，然后设计满足安全性证明的密码学/系统方案，最后通过理论分析+实验验证证明方案的有效性。

范式沿三条轴线展开：
- **威胁建模轴线**：威胁模型定义（Honest-but-Curious/Malicious/Physical）→安全需求形式化→攻击面识别
- **方案设计轴线**：密码原语选择→协议设计→安全规约证明→效率优化
- **验证评估轴线**：形式化安全证明→合成/基准实验→真实数据验证→性能基准测试

## 2. 研究范式特征

| 维度 | 范式特征 | 代表论文 |
|------|---------|---------|
| 问题来源 | 系统安全威胁与隐私法规驱动的实用问题 | SplitAD, Lightweight Auth, Physical Attacks |
| 方法论 | 威胁建模→密码学设计→安全证明→实验验证 | 几乎所有论文 |
| 创新模式 | 在密码原语/协议层面创新，混合多种安全技术 | TCKKS(FHE+TEE), PriFFT(ASS+FSS) |
| 证据标准 | 形式化安全证明+性能基准+（部分）真实数据验证 | SplitAD, Key-Value LDP, SBIRCH |
| 系统导向 | 不仅关注算法创新，更关注端到端系统可行性和效率 | Blockchain MEC, AeroGuard |

## 3. 问题选择范式

### 3.1 偏好问题特征

1. **有明确威胁模型的安全问题**：可定义攻击者能力边界（计算能力、物理接近度、数据访问权限）以及安全目标（机密性/完整性/可用性/不可否认性）
2. **存在可优化的效率瓶颈**：现有方案虽有安全保证但计算/通信开销不可接受
3. **跨域交叉问题**：隐私+安全、FHE+TEE、联邦+安全、图学习+攻击——交叉处往往有未解决的系统性问题

### 3.2 回避问题特征

- 纯理论密码学无系统实现的问题
- 无明确威胁模型的开放式问题
- 攻击仅做描述性分析而无防御方案的问题（Adaptive Backdoor为少数例外，以攻促防）

## 4. 方法设计范式

### 4.1 方法层级

1. **威胁建模层**：确定安全模型（半诚实/恶意/物理攻击）和安全需求
2. **密码原语层**：选择基础密码学工具（HE/SS/DP/TEE）并组合
3. **协议设计层**：设计满足安全需求的交互协议
4. **系统优化层**：在保证安全性的前提下最小化计算/通信/存储开销
5. **验证层**：形式化证明+实验验证

### 4.2 方法创新模式

- **混合增强型**（TCKKS, PriFFT）：组合不同的安全技术取各自优势弥补各自弱点
- **模型拆分型**（SplitAD, Plog）：将集中式方案改造为分布式安全版本
- **轻量化型**（Lightweight Auth, E-Raft）：针对资源受限场景的协议精简
- **攻击研究型**（Adaptive Backdoor, Physical Attacks）：系统性理解攻击以指导防御

## 5. 证据标准

### 5.1 典型验证链

密码协议论文：形式化安全定义→安全规约证明→性能基准(cpu cycles/bytes/latency) vs 基线方案
ML安全论文：威胁模型定义→攻击成功率(ASR)/检测精度(F1)→逃逸率/误报率→多种数据集交叉验证
系统论文：系统架构→仿真验证→（部分）真实硬件平台基准测试

### 5.2 证据来源偏好

- 形式化安全证明（密码学论文的核心）
- 公开基准数据集（ML安全/检测任务）
- 与≥3种基线方案的系统对比
- 不同参数设置下的性能稳定性（隐私预算ε、参与方数量、数据规模）

## 6. 叙事风格

典型的论文叙事结构：
1. 场景驱动的安全威胁/隐私需求陈述
2. 现有方案的局限性（安全不足或效率过低）
3. 威胁模型和设计目标的精确定义
4. 方案设计的逐层展开（密码原语→协议→系统）
5. 安全分析（形式化证明/安全性论证）
6. 实验评估（安全指标+性能指标）
7. 局限性诚实讨论+未来工作
