---
page_id: paper-PAPER_96645819
page_type: paper
title: 'Lightweight and Trustworthy Authentication and Data Transmission Schemes in the Industrial IoT'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_96645819
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Yebo Gu
- Xiang Dai
- Tao Shen
venue: IEEE Internet of Things Journal
---

# Paper: Lightweight and Trustworthy Authentication and Data Transmission Schemes in the Industrial IoT

## 1. 元信息

- paper_id: PAPER_96645819
- title: Lightweight and Trustworthy Authentication and Data Transmission Schemes in the Industrial IoT
- year: 2026
- authors: Yebo Gu, Xiang Dai, Tao Shen
- venue: IEEE Internet of Things Journal, Vol. 13, No. 4
- DOI: 10.1109/JIOT...

## 2. 一句话贡献

提出IIoT中轻量级可信认证与数据传输方案，设计资源高效的设备身份认证协议和安全数据传输机制，在保证通信安全（机密性、完整性、不可否认性）的同时满足IIoT设备的严格计算和能量约束。（EVID-PAPER_96645819-P1-C000）

## 3. 研究问题

### 3.1 原始问题
IIoT设备通常资源受限（低功耗MCU、有限存储、电池供电），传统公钥基础设施(PKI)和TLS协议的计算开销在这些设备上不可接受。需要轻量级但可达"可信"（Trustworthy）级别的认证和数据保护方案。（EVID-PAPER_96645819-P1-C000）

### 3.2 学术抽象
- 问题类型：轻量级密码协议设计（Lightweight Cryptography）
- 关键挑战：在计算/能量/存储极度受限下实现经得起形式化验证的安全认证和数据传输
- 形式化：设计认证协议π使得资源开销O(π)<<O(TLS)同时满足IND-CCA/SUF-CMA等安全定义

### 3.3 问题重要性
IIoT环境中设备数量庞大且物理安全难以保证，轻量级认证是保障工业系统端到端安全的第一道防线，直接关系到生产安全。

## 4. 核心思想

采用"对称密码原语+轻量级数字签名"的混合设计：认证阶段使用基于HMAC的挑战-响应协议降低计算开销（避免非对称运算），数据传输阶段使用轻量级AEAD（认证加密）方案保证机密性和完整性。方案经过形式化安全证明（随机预言机模型或标准模型下的规约安全）。（EVID-PAPER_96645819-P3-C008）

## 5. 方法框架

- **输入**：IIoT设备身份凭证
- **输出**：安全的会话密钥+认证通道
- **模型**：对称密码+轻量级签名混合协议
- **算法**：轻量级挑战-响应认证 → 会话密钥协商 → AEAD加密数据传输
- **数据集**：N/A（密码协议论文，安全性通过形式化证明验证）
- **评价指标**：计算开销（CPU cycles）、通信开销（bytes）、存储开销（bytes）、安全强度（bit-security）

## 6. 实验设计

- **Baseline**：TLS-PSK、DTLS、现有轻量级认证方案
- **Ablation**：不同密码原语组合的性能对比
- **其他**：形式化安全证明（Protocol Verification）；资源受限平台（ARM Cortex-M级别）的实现基准测试

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| 方案在IIoT典型MCU平台上实现<10ms认证延迟 | EVID-PAPER_96645819-P9-C020 |
| 相比TLS/DTLS，计算开销和通信开销降低数倍 | EVID-PAPER_96645819-P9-C021 |
| 形式化证明满足双向认证和会话密钥安全 | EVID-PAPER_96645819-P7-C016 |

## 8. 隐含假设

**论文明确假设**：设备在生产阶段安全注入初始密钥材料；时钟同步在可接受误差范围内（防重放攻击）。
**系统推断**：侧信道攻击不在威胁模型考虑范围。

## 9. 局限性

**系统推断**：对称密码方案需要密钥管理基础设施支持；前向安全性可能弱于非对称方案。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"轻量级可信"设计原则**：通过"对称运算为主+非对称运算最小化"实现资源效率和安全性的平衡——可迁移到车联网(V2X)通信、智能家居设备配对、医疗植入设备安全通信。
2. **形式化验证驱动的协议设计**：从安全定义出发设计的轻量级协议比"朴素设计+后期修补"方式更可靠——可推广为IoT安全协议的通用设计方法论。

## 11. 与其他论文关系

- 前置工作：TLS/DTLS轻量级变体、SPAKE2、OPAQUE
- 同主题工作：与TCKKS论文互补（本方案在设备和边缘层认证，TCKKS在云端提供同态加密支持）；与Plog/PriFFT同属"可信+安全"主题

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_96645819-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_96645819-P2-C004 | 2 | Models/Design | system_model | high |
| EVID-PAPER_96645819-P3-C008 | 3 | Proposed Scheme | lightweight_design | high |
| EVID-PAPER_96645819-P7-C016 | 7 | Security Analysis | formal_proof | high |
| EVID-PAPER_96645819-P9-C020 | 9 | Performance | result_efficiency | high |
| EVID-PAPER_96645819-P9-C021 | 9 | Performance | result_comparison | high |
