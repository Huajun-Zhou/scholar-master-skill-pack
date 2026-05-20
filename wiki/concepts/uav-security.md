---
page_id: concept-uav-security
page_type: concept
title: 无人机安全 (UAV Security)
status: draft
evidence_level: B
source_papers:
- PAPER_141EDBB3
- PAPER_8E699870
- PAPER_E155CF85
- PAPER_0A8C55F0
related_pages:
- concept-trusted-communications
- ../glossary
confidence: medium
updated_at: '2026-05-19'
---

# 无人机安全 (UAV Security)

## 定义

覆盖无人机系统的多层次安全保障——物理层（传感器/GPS/机体攻击）、通信层（窃听/干扰/劫持）、计算层（边缘推理安全/任务调度安全）。区别于传统网络安全，UAV安全需要考虑物理运动约束、能量预算和实时性要求。

## 来源论文

- AeroGuard (PAPER_141EDBB3): 基于混合模型的实时故障检测
- RSMA UAV (PAPER_8E699870): 物理层安全通信
- Physical Attacks UAV (PAPER_E155CF85): 物理攻击系统性综述
- Joint Scheduling (PAPER_0A8C55F0): 安全感知的边缘推理调度

## 关键方法

1. 物理+DL混合故障/攻击检测
2. MARL驱动的自适应安全通信
3. RSMA速率分割实现安全速率灵活trade-off

## 与其他概念的关系

- 与可信通信交叉：UAV安全通信是可信通信的移动场景实例
- 与图学习安全交叉：UAV蜂群的图拓扑安全分析
