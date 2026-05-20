---
page_id: paper-PAPER_627CFA0B
page_type: paper
title: 'TCKKS: An Efficient TEE-Assistance CKKS Scheme Without Bootstrapping'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_627CFA0B
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Hui Zhu
venue: IEEE Transactions on Dependable and Secure Computing (TDSC)
---

# Paper: TCKKS: An Efficient TEE-Assistance CKKS Scheme Without Bootstrapping

## 1. 元信息

- paper_id: PAPER_627CFA0B
- title: TCKKS: An Efficient TEE-Assistance CKKS Scheme Without Bootstrapping
- year: 2026
- authors: Hui Zhu (Xidian Univ.)
- venue: IEEE Transactions on Dependable and Secure Computing (TDSC)
- DOI: TBD from extraction

## 2. 一句话贡献

提出TCKKS——结合可信执行环境(TEE)和CKKS全同态加密的高效方案，通过将CKKS中最耗时的自举(bootstrapping)操作委托给TEE安全执行，消除CKKS方案的同态自举瓶颈，在保持语义安全的同时大幅提升同态计算效率。（EVID-PAPER_627CFA0B-P1-C000）

## 3. 研究问题

### 3.1 原始问题
CKKS是支持近似浮点运算的主流全同态加密(FHE)方案，但其核心瓶颈——自举(bootstrapping)——消耗了绝大部分计算时间（约占90%以上）。虽然自举对深层次同态计算是必要的，但在许多实际场景中计算深度有限，此时自举成为不必要的性能开销。（EVID-PAPER_627CFA0B-P1-C000）

### 3.2 学术抽象
- 问题类型：密码工程优化（Cryptographic Engineering）
- 关键挑战：如何在不牺牲CKKS安全性的前提下消除/规避自举瓶颈；TEE和FHE的安全模型差异如何协调
- 形式化：设计TCKKS = CKKS - Bootstrapping + TEE-Assisted Noise Management，使得深层次同态计算可通过TEE安全执行噪声刷新(noise refresh)代替自举

### 3.3 问题重要性
CKKS是隐私保护机器学习中最有前途的同态加密方案之一。消除自举瓶颈可使其在推理即服务(MLaaS)、安全数据分析等场景中更加实用。

## 4. 核心思想

核心洞察：CKKS的自举本质上是"同态解密+重加密"以刷新密文噪声——这一操作可在TEE（如Intel SGX/TDX）中更高效地执行。TCKKS利用TEE的安全隔离能力：当CKKS密文噪声达到阈值时，将密文安全传入TEE、在TEE内部解密并重新加密（明文级噪声刷新），然后输出低噪声新密文。这避免了昂贵的同态自举电路评估，同时TEE的硬件级隔离保证了中间明文的安全。（EVID-PAPER_627CFA0B-P4-C012）

## 5. 方法框架

- **输入**：CKKS密文数据
- **输出**：同态计算结果（或刷新噪声后的新密文）
- **模型**：CKKS FHE + TEE (Intel SGX/TDX) 混合架构
- **算法**：
  - 普通同态运算（加/乘）→标准CKKS执行
  - 噪声刷新 → 密文传入TEE → TEE内部解密 → TEE内部重加密 → 低噪声密文输出
- **损失函数**：N/A（密码方案）
- **数据集**：N/A（通过密码学安全性证明和性能基准评估）
- **评价指标**：计算延迟、吞吐量、通信开销（TEE-CPU数据传输）、安全级别

## 6. 实验设计

- **Baseline**：标准CKKS with Bootstrapping；SEAL/PALISADE等FHE库中的CKKS实现
- **Ablation**：不同计算深度下的TEE-CKKS vs Native CKKS性能对比
- **其他**：TEE内存限制对批处理大小的影响；SGX/TDX enclave的启动和远程认证开销

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| TCKKS在中等计算深度(≤10层乘法)下相比CKKS+自举方案加速一个数量级以上 | EVID-PAPER_627CFA0B-P10-C024 |
| TEE辅助噪声刷新引入的额外通信开销可接受 | EVID-PAPER_627CFA0B-P11-C028 |
| 方案的混合安全模型（FHE+TEE）满足实际安全需求 | EVID-PAPER_627CFA0B-P8-C020 |

## 8. 隐含假设

**论文明确假设**：TEE的侧信道防御有效（SGX/TDX的硬件安全保证）；同态计算中的数据流可预测（用于调度TEE刷新时机）。
**系统推断**：TEE enclave的内存限制（通常128-512MB EPC）可能限制batch size。

## 9. 局限性

**论文提及局限**：依赖Intel SGX/TDX硬件（供应商锁定）；TEE侧信道攻击（如Spectre/Meltdown变种）可能在理论威胁模型中。
**系统推断**：TEE-CPU的I/O带宽可能成为吞吐量瓶颈。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"FHE+TEE"混合计算范式**：将FHE的计算瓶颈操作委托给TEE——可迁移到其他FHE方案的类似瓶颈（如BGV/BFV的自举）、安全多方计算的预处理阶段。
2. **噪声管理外包**：任何基于噪声的密码系统（LWE/NTRU等格密码）都可考虑TEE辅助的噪声刷新——可迁移到后量子密码的性能优化。
3. **混合信任模型设计**：FHE（数学安全，无硬件信任根）+TEE（硬件安全，性能高）的组合代表了实用的密码工程哲学——不过度依赖任何单一安全假设。

## 11. 与其他论文关系

- 前置工作：CKKS (Cheon et al., ASIACRYPT 2017)、Intel SGX/TDX、FHE自举优化
- 同主题工作：与PriFFT互补（PriFFT用MPC保护联邦训练，TCKKS用FHE+TEE保护推理计算——两篇同属隐私计算基础设施）；与Lightweight Auth互补（设备认证 vs 云端同态计算安全）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_627CFA0B-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_627CFA0B-P2-C005 | 2 | Background | ckks_bootstrapping | high |
| EVID-PAPER_627CFA0B-P3-C008 | 3 | TEE Model | tee_capabilities | high |
| EVID-PAPER_627CFA0B-P4-C012 | 4 | TCKKS Design | hybird_design | high |
| EVID-PAPER_627CFA0B-P6-C016 | 6 | Protocol | noise_refresh | high |
| EVID-PAPER_627CFA0B-P8-C020 | 8 | Security | security_analysis | high |
| EVID-PAPER_627CFA0B-P10-C024 | 10 | Evaluation | result_latency | high |
| EVID-PAPER_627CFA0B-P11-C028 | 11 | Evaluation | result_comm | high |
