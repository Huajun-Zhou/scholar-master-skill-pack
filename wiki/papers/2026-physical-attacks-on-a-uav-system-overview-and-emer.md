---
page_id: paper-PAPER_E155CF85
page_type: paper
title: 'Physical Attacks on a UAV System: Overview and Emerging Methods'
created_at: '2026-05-19T03:02:37+00:00'
updated_at: '2026-05-19'
status: audited
evidence_level: mixed
source_papers:
- PAPER_E155CF85
related_pages: []
confidence: medium
last_lint: ''
paper_year: 2026
authors:
- Xiaomin Wei
- Xinghua Li
- Cong Sun
venue: IEEE Transactions on Intelligent Transportation Systems
---

# Paper: Physical Attacks on a UAV System: Overview and Emerging Methods

## 1. 元信息

- paper_id: PAPER_E155CF85
- title: Physical Attacks on a UAV System: Overview and Emerging Methods
- year: 2026
- authors: Xiaomin Wei, Xinghua Li, Cong Sun
- venue: IEEE Transactions on Intelligent Transportation Systems
- DOI: TBD from extraction

## 2. 一句话贡献

系统综述UAV物理层攻击（GPS欺骗、传感器干扰、通信劫持、声学/光学对抗等）的攻击向量、机理和最新进展，提出多维度的UAV物理安全威胁分类框架，并分析新兴防御方法和未来研究方向。（EVID-PAPER_E155CF85-P1-C000）

## 3. 研究问题

### 3.1 原始问题
UAV广泛应用于智能交通、物流、农业等领域，但其物理层暴露面大——GPS、通信链路、传感器均易受物理攻击（非网络攻击）。现有文献缺乏对UAV物理攻击的系统性分类和最新方法（如基于AI的对抗物理攻击）的全面综述。（EVID-PAPER_E155CF85-P1-C000）

### 3.2 学术抽象
- 问题类型：综述/调查（Survey）
- 关键贡献：构建多维度UAV物理攻击分类法；分析物理攻击与网络攻击的交叉融合趋势
- 方法论：系统文献综述 + 攻击分类框架 + 防御体系分析

### 3.3 问题重要性
UAV安全是智能交通系统(ITS)和低空经济的关键使能条件。物理攻击因其无需入侵机载网络即可实施而更具威胁性。

## 4. 核心思想

提出按攻击目标层（传感器层、通信层、导航层、控制层）和攻击物理原理（电磁、声学、光学、热学）两个维度交叉分类的框架，系统梳理每种攻击的成功条件、设备需求和应对防御，重点关注新兴AI驱动的自适应物理攻击方法。（EVID-PAPER_E155CF85-P3-C010）

## 5. 方法框架

- **输入**：公开文献数据库中的UAV物理安全论文
- **输出**：系统化分类+攻击-防御对照矩阵+未来方向
- **模型**：多维度攻击分类框架（4层×4类物理原理）
- **算法**：系统文献综述方法
- **数据集**：已发表论文、安全会议报告、CVE数据库
- **评价指标**：文献覆盖范围、分类完整性

## 6. 实验设计

- **综述方法论**：PRISMA式文献筛选流程
- **分析维度**：攻击层（Sensor/Communication/Navigation/Control）× 物理原理（EM/Acoustic/Optical/Thermal）× 防御策略
- **对比分析**：各物理攻击方法的设备成本、实施难度、成功率对比

## 7. 关键结论

| 结论 | evidence_id |
|------|-------------|
| GPS欺骗和传感器干扰是最常见且实施成本最低的UAV物理攻击 | EVID-PAPER_E155CF85-P5-C015 |
| AI驱动的自适应物理攻击正在成为新威胁（如对抗性红外补丁）| EVID-PAPER_E155CF85-P8-C025 |
| 多传感器融合+物理层异常检测是最有前途的防御方向 | EVID-PAPER_E155CF85-P12-C035 |
| 现有防御方案缺乏对复合攻击（物理+网络协同）的考虑 | EVID-PAPER_E155CF85-P15-C042 |

## 8. 隐含假设

**系统推断**：攻击者的物理接近距离和设备能力基于公开文献中的报告；防御方案评估基于论文声称的性能。

## 9. 局限性

**论文自然局限**：综述的快照性质——随新技术发展可能快速过时；部分攻击的实际效果因安全原因无法验证。
**系统推断**：可能遗漏非公开（classified）的攻击方法。

## 10. 可迁移启发

**以下为 C 类迁移推断，非原论文结论。**

1. **"物理+网络"交叉攻击意识**：UAV的物理攻击启示可迁移到其他CPS系统（自动驾驶汽车、机器人、智能电网）的安全分析——物理暴露面是不可忽视的攻击面。
2. **多维度威胁建模框架**：攻击层×物理原理的分类法可迁移到IoT设备安全分析、工业控制系统风险评估。
3. **AI对抗物理攻击**：对抗性物理补丁/干扰不仅是UAV问题——可迁移到任何依赖计算机视觉的自主系统（机器人导航、视频监控）。

## 11. 与其他论文关系

- 同主题工作：与AeroGuard互补（AeroGuard做故障检测，本论文综述攻击检测——两者构成UAV安全的两个维度）；与RSMA Multi-UAV Secure Communication互补（物理攻击 vs 通信安全）

## 12. Evidence 列表

| evidence_id | page | section | claim_type | confidence |
|---|---:|---|---|---|
| EVID-PAPER_E155CF85-P1-C000 | 1 | Introduction | motivation | high |
| EVID-PAPER_E155CF85-P3-C010 | 3 | Classification | taxonomy | high |
| EVID-PAPER_E155CF85-P5-C015 | 5 | GPS/Spoofing | attack_analysis | high |
| EVID-PAPER_E155CF85-P8-C025 | 8 | Emerging Methods | ai_attacks | high |
| EVID-PAPER_E155CF85-P12-C035 | 12 | Defense | defense_review | high |
| EVID-PAPER_E155CF85-P15-C042 | 15 | Future | future_direction | high |
