---
page_id: concept-trusted-communications
page_type: concept
title: 可信通信 (Trusted Communications)
status: draft
evidence_level: B
source_papers:
- PAPER_96645819
- PAPER_8E699870
- PAPER_513EB8C3
related_pages:
- concept-privacy-preserving-ml
- ../glossary
confidence: medium
updated_at: '2026-05-19'
---

# 可信通信 (Trusted Communications)

## 定义

在IIoT和UAV场景中，通信不仅需要满足传统安全属性（机密性、完整性、可用性），还需要在资源受限条件下提供可验证的信任锚——包括设备身份的真实性、消息来源的不可否认性、以及通信行为的可审计性。

## 来源论文

- Lightweight Auth (PAPER_96645819): IIoT设备的轻量级双向认证
- RSMA UAV (PAPER_8E699870): 物理层安全的抗窃听通信
- Blockchain MIMO MEC (PAPER_513EB8C3): 区块链共识保证卸载决策的可审计性

## 关键方法

1. 轻量级挑战-响应认证协议
2. 物理层安全（利用信道特性实现信息论安全）
3. 区块链辅助的通信行为不可篡改记录

## 与其他概念的关系

- 与隐私保护ML交叉：联邦学习中的安全梯度传输
- 与UAV安全交叉：无人机通信链路的物理层保护
