---
page_id: concept-privacy-preserving-ml
page_type: concept
title: 隐私保护机器学习 (Privacy-Preserving ML)
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_9955C321
- PAPER_B4EA5A99
- PAPER_00BA0203
- PAPER_F530EB8C
related_pages:
- concept-trusted-communications
- ../glossary
confidence: medium
updated_at: '2026-05-19'
---

# 隐私保护机器学习 (Privacy-Preserving ML)

## 定义

在分布式多方数据上进行机器学习训练或推理时，通过密码学手段（DP/HE/SS/MPC/TEE）保护数据隐私、模型隐私或两者兼顾。核心挑战是在隐私保证、模型精度和计算/通信效率之间找到实用平衡点。

## 来源论文

- SplitAD (PAPER_BC534646): 垂直联邦异常检测，传输重构误差代替模型参数
- Key-Value LDP (PAPER_9955C321): 本地差分隐私保护键值数据收集
- Plog (PAPER_B4EA5A99): 垂直分区图数据的协作GNN训练
- PriFFT (PAPER_00BA0203): LLM联邦微调的梯度隐私保护
- Flash (PAPER_F530EB8C): 联邦图学习的安全检测

## 关键方法

1. 模型拆分+中间表示传输（Split Architecture）
2. 本地差分隐私（LDP）
3. 混合安全计算（ASS+FSS / FHE+TEE）
4. 联邦图学习

## 与其他概念的关系

- 与可信通信交叉：联邦通信需要安全信道
- 与图学习安全交叉：图数据隐私+模型安全
