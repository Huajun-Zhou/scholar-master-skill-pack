---
page_id: synthesis-method-evolution
page_type: synthesis
title: Method Evolution — 方法族演化
status: draft
evidence_level: B
source_papers:
- PAPER_BC534646
- PAPER_627CFA0B
- PAPER_00BA0203
confidence: medium
updated_at: '2026-05-19'
---

# Method Evolution — 方法族演化

基于15篇论文识别的7个方法族及其演化路径（B类综合归纳）。

## 方法族1: 联邦模型拆分 (Federated Model Splitting)

**来源**：SplitAD | **核心机制**：底层模型分配给数据方本地训练，顶层模型在聚合方训练，中间仅传输低维中间表示

**演化路径**：KitNet(集中式层次AE)→SplitAD(联邦式层次AE)→可向联邦图学习拆分(Plog的潜在扩展)

## 方法族2: 本地差分隐私扰动 (Local DP Perturbation)

**来源**：Key-Value LDP | **核心机制**：分段随机响应(Segmented RR)将复合数据拆分后差异化扰动

**演化路径**：GRR/RAPPOR(简单类型)→Segmented RR(键值复合类型)→可向多维时序LDP扩展

## 方法族3: 混合安全计算架构 (Hybrid Secure Computation)

**来源**：TCKKS, PriFFT | **核心机制**：根据运算特性(线性/非线性)选择最优安全原语(FHE/TEE/ASS/FSS)并混合使用

**演化路径**：单一FHE(CKKS)→FHE+TEE(TCKKS)/ASS+FSS(PriFFT)→可向多方混合安全计算统一框架发展

## 方法族4: 图学习安全分析 (Graph-Learning Security)

**来源**：Flash, GNNDroid, Adaptive Backdoor GNN | **核心机制**：将代码/应用转化为图结构(AST/调用图/特征图)，用GNN学习区分性模式

**演化路径**：静态图分类(GNNDroid)→联邦图学习(Flash)→自适应图攻击(Adaptive Backdoor)→可向动态图安全演变

## 方法族5: 轻量级认证协议 (Lightweight Authentication)

**来源**：Lightweight Auth | **核心机制**：对称密码原语+轻量级签名混合设计，避免昂贵的非对称运算

**演化路径**：TLS-PSK/DTLS→轻量级HMAC挑战-响应+AEAD→可向量子安全轻量级协议发展

## 方法族6: UAV混合故障检测 (Hybrid UAV Fault Detection)

**来源**：AeroGuard | **核心机制**：物理模型(ARX)提供期望基线+数据驱动模型(LSTM)学习异常偏离+动态检测因子(DDF)自适应融合

**演化路径**：单一模型方法→ARX+LSTM混合→DDF动态融合→可向多UAV协同故障检测扩展

## 方法族7: 多智能体安全通信 (MARL Secure Communication)

**来源**：RSMA UAV | **核心机制**：RSMA提供安全速率灵活trade-off维度，MARL提供分布式自适应决策，注意力机制聚焦安全威胁方向

**演化路径**：OMA→NOMA→RSMA+单智能体→RSMA+MARL+注意力→可向6G RIS辅助的安全通信扩展
