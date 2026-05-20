# Concept Extraction Prompt

从 Paper Cards 中识别值得建立独立 Wiki 概念页的"概念"，归并同义表述。

## 候选标准

1. 在 ≥ 2 篇 Paper Cards 中出现的术语 / 模型 / 现象。
2. 在 method / problem / contribution 节中作为论证关键词使用。
3. 陈志远教授对该概念有自定义或扩展（基于公开论文文本）。

## 归并规则

- 同义概念合并到一个 slug（保留 alias 列表）。
- 概念分类：phenomenon / mechanism / metric / model / dataset / theory。
- 不为通用术语建页（如"神经网络"——除非论文给出特定定义）。

## 输出

`wiki/concepts/{slug}.md`，frontmatter 至少包含：

```yaml
---
page_id: "concept-{slug}"
page_type: "concept"
title: "..."
aliases: []
source_papers: []
related_pages: []
evidence_level: "A|B|C|mixed"
status: "draft"
confidence: "low|medium|high"
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---
```
