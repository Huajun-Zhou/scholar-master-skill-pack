---
page_id: glossary
page_type: reference
title: Glossary — 术语表
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
- research_paradigm
confidence: medium
updated_at: '2026-05-19'
---

# Glossary — 术语表

## 隐私保护技术

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| 本地差分隐私 | Local Differential Privacy (LDP) | 客户端本地扰动数据后上传，服务器即使被攻破也无法恢复原始数据 | PAPER_9955C321 |
| 同态加密 | Homomorphic Encryption (HE) | 支持在密文上直接执行计算，结果解密后等价于明文计算 | PAPER_09026E9B, PAPER_627CFA0B |
| CKKS | Cheon-Kim-Kim-Song FHE | 支持近似浮点运算的全同态加密方案 | PAPER_627CFA0B |
| 自举 | Bootstrapping | FHE中刷新密文噪声的昂贵操作，占CKKS >90%计算时间 | PAPER_627CFA0B |
| 秘密共享 | Secret Sharing | 将秘密拆分给多方分别持有，单方无法恢复 | PAPER_00BA0203, PAPER_09026E9B |
| 可信执行环境 | Trusted Execution Environment (TEE) | 硬件级安全隔离区域（如Intel SGX/TDX），保证代码和数据机密性和完整性 | PAPER_627CFA0B |
| 差分隐私 | Differential Privacy (DP) | 通过添加受控噪声使相邻数据集输出不可区分 | PAPER_BC534646, PAPER_9955C321 |

## 联邦学习与分布式系统

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| 垂直联邦学习 | Vertical Federated Learning (VFL) | 参与方共享相同样本空间但不同特征空间 | PAPER_BC534646, PAPER_B4EA5A99 |
| 水平联邦学习 | Horizontal Federated Learning (HFL) | 参与方共享相同特征空间但不同样本空间 | PAPER_F530EB8C |
| 模型拆分 | Model Splitting | 将模型分为底层（数据方本地）和顶层（聚合方）两部分 | PAPER_BC534646 |
| 诚实但好奇 | Honest-but-Curious | 参与方诚实执行协议但可能推断他人敏感信息 | PAPER_BC534646, PAPER_09026E9B |
| 非IID数据 | Non-IID Data | 分布式场景下各参与方的数据分布不一致 | PAPER_F530EB8C |

## 图神经网络与安全

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| 图神经网络 | Graph Neural Network (GNN) | 在图结构数据上学习的深度模型，通过消息传递聚合邻居信息 | PAPER_B1C0C91E, PAPER_B4EA5A99 |
| 图注意力网络 | Graph Attention Network (GAT) | 使用注意力机制加权邻居节点重要性的GNN变体 | PAPER_F530EB8C |
| 后门攻击 | Backdoor Attack | 训练阶段注入触发器使模型对特定模式产生错误输出 | PAPER_B1C0C91E |
| 自适应触发器 | Adaptive Trigger | 根据目标样本特征个性化生成的触发器（vs 固定模式） | PAPER_B1C0C91E |
| AST | Abstract Syntax Tree | 代码的抽象语法树表示 | PAPER_F530EB8C |
| JNI | Java Native Interface | Android中Java调用C/C++ Native代码的接口 | PAPER_34285F47 |

## 无人机与通信

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| RSMA | Rate-Splitting Multiple Access | 速率分割多址接入——将消息拆分为公共和私有部分传输 | PAPER_8E699870 |
| 物理层安全 | Physical Layer Security | 利用无线信道物理特性（衰落、干扰）实现信息论安全 | PAPER_8E699870 |
| MARL | Multi-Agent Reinforcement Learning | 多智能体强化学习——多个智能体在共享环境中学习协作/竞争策略 | PAPER_8E699870 |
| MIMO | Multiple-Input Multiple-Output | 多天线无线通信系统 | PAPER_513EB8C3 |
| AAV | Autonomous Aerial Vehicle | 自主空中平台 | PAPER_513EB8C3 |
| Raft | Raft Consensus | 分布式一致性协议（比PoW/PBFT更节能） | PAPER_513EB8C3 |
| ARX | AutoRegressive with eXogenous | 外源自回归模型——基于外部输入和历史输出预测当前输出 | PAPER_141EDBB3 |
| DDF | Dynamic Detection Factor | 动态检测因子——根据飞行状态动态调节模型权重 | PAPER_141EDBB3 |

## 工业物联网安全

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| 工业信息物理系统 | Industrial Cyber-Physical System (ICPS) | 深度融合计算、通信和物理过程的工业系统 | PAPER_F530EB8C |
| BIRCH | Balanced Iterative Reducing and Clustering using Hierarchies | 层次聚类算法，使用CF树进行增量聚类 | PAPER_09026E9B |
| 边缘计算 | Mobile Edge Computing (MEC) | 在网络边缘（近数据源）提供计算服务 | PAPER_513EB8C3 |
| 认证加密 | Authenticated Encryption with Associated Data (AEAD) | 同时提供机密性和完整性的加密模式 | PAPER_96645819 |

## 自编码器与异常检测

| 术语 | 英文 | 定义 | 来源 |
|------|------|------|------|
| 自编码器 | Autoencoder (AE) | 通过编码-解码学习数据紧凑表示的无监督神经网络 | PAPER_BC534646 |
| 层次化自编码器 | Hierarchical Autoencoder | 将特征分组后用多个底层AE+顶层AE实现层次化特征学习 | PAPER_BC534646 |
| 重构误差 | Reconstruction Error | 原始输入与AE重建输出之间的差异——异常检测的核心信号 | PAPER_BC534646 |
| Smashed Data | Smashed Data | VFL中底层模型输出的中间表示（重构误差/嵌入向量） | PAPER_BC534646 |
