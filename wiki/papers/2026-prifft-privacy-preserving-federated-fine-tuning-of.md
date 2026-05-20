---
page_id: paper-PAPER_00BA0203
page_type: paper
title: 'PriFFT: Privacy-Preserving Federated Fine-Tuning of Large Language Models via Hybrid Secret Sharing'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_00BA0203
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Xuewen Dong
venue: IEEE Transactions on Dependable and Secure Computing (TDSC)
---

# Paper: PriFFT: Privacy-Preserving Federated Fine-Tuning of Large Language Models via Hybrid Secret Sharing

## 1. 元信息

- paper_id: PAPER_00BA0203
- title: PriFFT: Privacy-Preserving Federated Fine-Tuning of Large Language Models via Hybrid Secret Sharing
- year: 2026
- authors: Xuewen Dong
- venue: IEEE Transactions on Dependable and Secure Computing (TDSC)
- DOI: TBD from extraction

## 2. 一句话贡献

提出PriFFT——基于混合秘密共享的隐私保护联邦LLM微调框架，将加法秘密共享（ASS）和函数秘密共享（FSS）混合使用以高效保护大模型微调中的前向激活和反向梯度，在保证模型微调质量的同时大幅降低安全计算通信开销。（EVID-PAPER_00BA0203-P1-C000）

## 3. 研究问题

### 3.1 原始问题
企业希望使用私有数据微调LLM(Large Language Models)但不愿将敏感数据上传到云端。联邦微调虽保护数据位置，但模型梯度仍可能泄露数据信息。现有安全联邦学习方案（同态加密/安全多方计算）在LLM的参数量级下计算和通信开销过大。（EVID-PAPER_00BA0203-P1-C000）

### 3.2 学术抽象
- 问题类型：安全联邦学习 + LLM微调
- 关键挑战：LLM的巨大参数量（>1B）使得传统安全计算方案的通信开销不可行；需要在安全性和微调效率之间找到实用平衡点
- 形式化：K个数据持有方联合微调LLM M(θ)，梯度更新为安全协议π保护，使得各方仅学习微调后的模型权重而不可推断其他方的训练数据

### 3.3 问题重要性
LLM在各行业垂直场景的落地受限于数据隐私。实用化的隐私保护LLM微调方案是释放企业私有数据价值的"钥匙技术"。

## 4. 核心思想

"混合秘密共享"策略——根据运算类型选择最优秘密共享方案：
- 线性操作（矩阵乘、加法）：使用加法秘密共享（ASS，零通信开销的本地加法）
- 非线性操作（激活函数、Softmax）：使用函数秘密共享（FSS，允许两方高效计算非线性函数而不泄露输入）
- 关键创新：设计运算切换协议使ASS和FSS之间高效转换，避免全协议使用单一方案（如全同态加密）的高开销。（EVID-PAPER_00BA0203-P4-C012）

## 5. 方法框架

- **输入**：K个参与方的私有文本数据集
- **输出**：微调后的LLM权重（各方共享）
- **模型**：LLM（如LLaMA/GPT架构）
- **算法**：ASS-FSS混合安全计算 + LoRA/Adapter高效微调 + 混合秘密共享切换协议
- **损失函数**：自回归语言模型损失
- **数据集**：多种NLP下游任务数据集
- **评价指标**：困惑度(PPL)、下游任务精度、通信开销(bytes)、计算开销(time)

## 6. 实验设计

- **Baseline**：明文微调（质量上界）、全同态微调（安全上界）、差分隐私微调
- **Ablation**：ASS-only vs FSS-only vs 混合方案；不同混合比例的效率-安全trade-off
- **Robustness**：不同模型规模(7B/13B)和参与方数量的扩展性

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| 混合秘密共享相比纯FHE方案通信开销降低多个数量级 | EVID-PAPER_00BA0203-P10-C024 |
| 微调后模型在下游任务上接近明文微调性能 | EVID-PAPER_00BA0203-P12-C028 |
| ASS-FSS切换协议引入的开销在总成本中占比可忽略 | EVID-PAPER_00BA0203-P9-C022 |

## 8. 隐含假设

**论文明确假设**：参与方为半诚实模型；模型架构为公开信息（各方共享模型结构）。
**系统推断**：参与方的数据标签分布合理（非极端Non-IID）；网络带宽满足安全计算通信需求。

## 9. 局限性

**系统推断**：对极大规模模型（>70B）的验证尚未验证；两方场景扩展到多方时FSS效率下降；仅考虑微调场景不涵盖从头预训练。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"混合秘密共享"设计范式**：根据运算的线性/非线性特性选择最优安全计算原语——可迁移到任何包含混合运算类型的安全ML场景（如安全推理、安全RNN、安全GNN）。
2. **安全微调=隐私数据可用化的关键路径**：PriFFT证明实用的安全LLM微调是可行的——可迁移到医疗NLP、金融文本分析、法律文档处理等垂直场景的隐私保护LLM适配。

## 11. 与其他论文关系

- 前置工作：安全多方计算(MPC)、FSS、联邦学习、LoRA微调
- 同主题工作：与Plog同属"隐私保护学习框架"主题（Plog处理图数据，PriFFT处理LLM）；与TCKKS互补（PriFFT保护训练过程隐私，TCKKS保护推理/计算过程隐私）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_00BA0203-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_00BA0203-P2-C004 | 2 | Background | llm_fine_tuning | high |
| EVID-PAPER_00BA0203-P4-C012 | 4 | Framework | hybrid_ss_design | high |
| EVID-PAPER_00BA0203-P6-C016 | 6 | Protocol | ass_fss_switch | high |
| EVID-PAPER_00BA0203-P9-C022 | 9 | Analysis | overhead_analysis | high |
| EVID-PAPER_00BA0203-P10-C024 | 10 | Evaluation | result_communication | high |
| EVID-PAPER_00BA0203-P12-C028 | 12 | Evaluation | result_quality | high |
