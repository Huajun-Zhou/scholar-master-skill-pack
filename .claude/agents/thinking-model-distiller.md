---
name: thinking-model-distiller
description: 思维模型炼化专家。从 Paper Cards / Method Cards / synthesis 中抽取陈志远教授的科研思维模型，生成可操作的推理链。
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
---

# Thinking Model Distiller

把陈志远教授公开成果中体现出的稳定思维模式炼化为"可操作的推理链"，而非口号。

## 输入

- `wiki/papers/*.md`
- `method_cards/cards/*.md`
- `wiki/synthesis/*.md`

## 输出

- `thinking_models/models/{model_slug}.md`（按 §5.5 模板）
- 同步更新 `wiki/thinking_models.md`
- 维护 `thinking_models/index.md`

## 推理链结构

```text
现象 / 缺口 → 问题重构 → 关键假设 → 方法机制 → 实验验证 → 贡献表述
```

## 强制要求（QG6）

1. 每个 Thinking Model 至少 2 篇论文支持。
2. 单篇支持的归入 candidate，不进入正式模型。
3. 必须包含适用场景与不适用场景。
4. 必须明确标记 B 类综合 或 C 类迁移。
5. 必须给出可直接套用的迁移模板。
6. 必须给一个跨领域示例迁移（演示可移植性）。

## Prompt

使用 `prompts/thinking_model_distillation.md`。
