---
name: refine-wiki
description: 基于已有 Paper Cards 进行跨论文综合，更新 Scholar Wiki。
---

# Refine Wiki

## 职责

1. 读取 wiki/papers/*.md 和 wiki/claims/*.jsonl。
2. 更新 wiki/index.md。
3. 生成/更新 wiki/research_timeline.md。
4. 生成/更新 wiki/research_questions.md。
5. 生成/更新 wiki/glossary.md。
6. 创建/更新概念页 wiki/concepts/。
7. 创建/更新方法页草稿 wiki/methods/。
8. 创建/更新数据集页 wiki/datasets/。
9. 创建/更新实验范式页 wiki/experiments/。
10. 维护 wiki/open_questions.md。

## 规则

- 遵循 wiki-writing.md 更新协议。
- 所有更新先 staging，后合并。
- 不读取原始 PDF，优先使用 Paper Cards 和 Evidence Ledger。

## 使用

```text
/refine-wiki
```
