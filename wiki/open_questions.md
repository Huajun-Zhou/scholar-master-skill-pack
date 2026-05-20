---
page_id: open-questions
page_type: hub
title: Open Questions — 开放问题
status: draft
evidence_level: C
source_papers: []
related_pages:
- research_questions
- contradictions
- limitations
confidence: low
updated_at: '2026-05-19'
---

# Open Questions — 开放问题

基于15篇论文中识别的新兴研究方向、论文未覆盖领域和未来工作建议（C类迁移推断和综合归纳）。

## 1. 隐私计算实用化

- **FHE+TEE混合计算的实际部署标准**：TCKKS提出FHE+TEE混合架构，但TEE侧信道防御、enclave内存限制、跨厂商兼容性等问题尚未解决——何时能形成工业标准？
- **联邦LLM微调的生产级方案**：PriFFT展示了安全LLM微调的可行性，但扩展到>70B模型和100+参与方时的效率如何？安全微调与提示工程/RLHF的结合方案？

## 2. UAV可信自主系统

- **统一攻防框架**：当前故障检测（AeroGuard）、物理攻击感知（Physical Attacks UAV）和安全通信（RSMA）是分离的——能否构建UAV可信自主系统的统一安全框架？
- **AI对抗UAV安全的边界**：AI驱动的自适应物理攻击正在出现——防御侧能否利用同样的AI能力进行"自适应防御"？

## 3. 图神经网络安全的成熟度

- **GNN后门防御的标准基准**：Adaptive Backdoor GNN揭示了GNN后门的隐蔽性——防御界需要什么水平的后门检测标准？
- **图学习+安全的交叉验证**：Flash和GNNDroid用GNN做检测，而Adaptive Backdoor用GNN做攻击——两者在更真实场景下的对抗结果？

## 4. 跨域整合

- **工业元宇宙的安全基础设施**：Blockchain MIMO MEC的区块链+边缘计算+UAV组合是否能支撑工业元宇宙的可信计算底座？
- **6G空天地一体化安全**：RSMA+MIMO+多UAV的技术路线能否从5G-Advanced演进到6G的安全通信架构？
- **Trusted-Secure-Robust三位一体**：目前TEE可信、密码学安全、MARL鲁棒是分离的——如何设计统一的Trusted-Secure-Robust系统架构？

## 5. 数据层面

- **垂直与水平混合分区**：当前隐私方案假定明确的垂直或水平分区——现实中常出现混合分区（部分样本共享、部分特征共享）——如何处理？
- **时序图数据的隐私保护**：Flash处理静态Bash代码图，Plog处理静态关系图——时序演化的动态图如何做隐私保护GNN？
