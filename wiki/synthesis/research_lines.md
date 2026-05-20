---
page_id: synthesis-research-lines
page_type: synthesis
title: Research Lines — 研究主线
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_B4EA5A99
- PAPER_00BA0203
- PAPER_627CFA0B
- PAPER_8E699870
related_pages:
- ../research_paradigm
- method_evolution
confidence: medium
updated_at: '2026-05-19'
---

# Research Lines — 研究主线

基于15篇论文归纳的5条研究主线（B类综合归纳）。

## Line 1: 隐私保护协作学习 (Privacy-Preserving Collaborative Learning)

**论文数**：5 | **代表论文**：SplitAD, Key-Value LDP, Plog, PriFFT, Flash

从垂直联邦异常检测(SplitAD)到隐私数据收集(Key-Value LDP)，到图数据隐私保护(Plog)，到LLM安全微调(PriFFT)，再到联邦图学习安全检测(Flash)——该主线演化路径为：**单一任务→复合数据→大模型→安全应用**。

**核心方法论**：密码学隐私保护（DP/HE/SS/MPC）与分布式机器学习的交叉，根据不同数据和任务特性选择最优安全计算原语组合。

## Line 2: 工业物联网可信安全 (IIoT Trusted Security)

**论文数**：3 | **代表论文**：SBIRCH, Lightweight Auth, Flash

从IIoT时序数据的安全聚类(SBIRCH)到资源受限设备的轻量级认证(Lightweight Auth)，再到工业CPS的恶意脚本检测(Flash)——关注工业环境中"安全可用性"的工程约束。

**核心方法论**：在强安全保证和严格资源约束之间寻找实用平衡点。

## Line 3: 无人机安全与可信自主 (UAV Security & Trusted Autonomy)

**论文数**：4 | **代表论文**：RSMA UAV, AeroGuard, Physical Attacks UAV, Joint Scheduling

从物理层安全通信(RSMA)到实时故障检测(AeroGuard)到物理攻击系统性分析(Physical Attacks)，再到边缘推理调度(Joint Scheduling)——构成"感知→通信→计算→安全"的UAV可信自主技术栈。

**核心方法论**：物理建模+AI驱动+安全约束的交叉融合。

## Line 4: 图神经网络攻防 (GNN Attack & Defense)

**论文数**：3 | **代表论文**：Adaptive Backdoor GNN, GNNDroid, Flash

从GNN后门攻击(Adaptive Backdoor)到Android恶意软件检测(GNNDroid)到联邦图学习安全检测(Flash)——攻防互补，构成图学习安全的完整视角。

**核心方法论**：图结构分析+对抗学习+安全检测——以图为中心的安全分析范式。

## Line 5: 密码学工程优化 (Cryptographic Engineering)

**论文数**：4 | **代表论文**：TCKKS, PriFFT, SBIRCH, Key-Value LDP

从CKKS自举瓶颈消除(TCKKS)到混合秘密共享(PriFFT)到安全聚类(SBIRCH)到LDP数据收集(Key-Value LDP)——关注密码学方案从"理论可行"到"工程实用"的优化。

**核心方法论**：密码原语的性能剖析+混合架构设计+系统级优化。
