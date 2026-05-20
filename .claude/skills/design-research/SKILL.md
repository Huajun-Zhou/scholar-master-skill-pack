---
name: design-research
description: 按陈志远教授公开成果中体现的方法论，为用户生成研究设计草案。
---

# Design Research

基于陈志远教授的研究范式，将用户的研究想法转化为可执行的研究方案。

## 调用

```text
/design-research "我想研究……"
```

## 执行流程

### Step 1: 加载模板
读取 `scholar_skill/research_design_template.md` 获取 4 步填空框架。

### Step 2: 匹配方法论
根据用户问题，检索最相关的：
- **方法卡片**: `method_cards/cards/` — 7 张方法卡片，看 Section 3 (适用问题类型) 和 Section 4 (核心机制)
- **思维模型**: `thinking_models/models/` — 6 个思维模型，选择 1-2 个最匹配的
- **研究范式**: `wiki/research_paradigm.md` — Section 9 可迁移研究框架

### Step 3: 生成研究方案
按 6 步生成：
1. **现象/缺口**: 将现实问题重构为学术问题
2. **问题重构**: 使用 `wiki/synthesis/problem_framing_patterns.md` 中的 4 种模式
3. **关键假设**: 明确列出并标注哪些是推断
4. **方法机制**: 从 Method Cards 中匹配，说明为什么选择这个方法
5. **实验验证**: 按 `wiki/synthesis/evidence_standards.md` 的 4 层消融设计
6. **创新点与风险**: 区分 B 类综合和 C 类迁移

### Step 4: 检查清单
用 `scholar_skill/research_design_template.md` 的 Step 3 检查清单逐项验证。

## 输出要求

- 每个方法选择必须给 evidence 来源（paper_id）。
- 创新点必须区分 B/C 类。
- 写明迁移条件与不适用边界。
- 末尾给出"下一步行动"清单。

## 强制要求

- 不冒充该学者本人。
- 不允许仅凭单篇论文的特殊做法当作稳定范式。
