# Research Paradigm Synthesis Prompt

跨论文综合，回答"这位学者的研究范式是什么"。

## 输入

- 全量 `wiki/papers/*.md`
- `wiki/synthesis/research_lines.md`、`method_evolution.md`、`problem_framing_patterns.md`、`evidence_standards.md`
- `method_cards/cards/*.md`、`thinking_models/models/*.md`

## 输出

`wiki/research_paradigm.md`，包含：

1. **稳定问题意识**：偏好哪类问题？怎么定义"好问题"？（基于多篇论文模式）
2. **抽象套路**：如何把现实问题转为可研究问题？
3. **方法选择倾向**：在多种可行方法中通常选哪类？为什么？
4. **证据标准**：什么样的实验 / case study / ablation 才被该学者视为"够"？
5. **贡献叙事**：通常如何陈述创新点（机制级 / 应用级 / 性能级）？
6. **范式演化**：早期 vs 近期的转向。
7. **边界**：哪些问题不属于该学者范式覆盖范围。

## 强制规则

- 每条结论 ≥ 2 篇论文支持，否则降级 candidate。
- 单篇论文的特殊做法不入范式。
- 标记 B 类。
- 写明"哪一年开始稳定出现该模式"（research_timeline 锚点）。
