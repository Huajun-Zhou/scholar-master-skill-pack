---
name: critique-paper
description: 按陈志远教授公开成果中体现出的证据标准与研究范式审查用户论文。
---

# Critique Paper

基于陈志远教授 多篇公开论文中体现的证据标准和研究范式，对用户论文进行系统审查。

## 调用

```text
/critique-paper "请审查 drafts/my_paper.md"
```

## 执行流程

### Step 1: 读取目标论文
读取用户指定的论文文件（Markdown / PDF 文本）。

### Step 2: 加载审查框架
读取：
- `scholar_skill/paper_critique_template.md` — 8 维度审查框架
- `wiki/synthesis/evidence_standards.md` — 该学者的证据标准
- `wiki/research_paradigm.md` — Section 5 论文叙事范式

### Step 3: 逐维度审查
按 8 维度逐一评审：
1. **问题是否重要** — 参考该学者的问题偏好
2. **抽象是否清晰** — 问题是否可形式化建模
3. **方法是否必要** — 是否在问题抽象层创新
4. **证据是否充分** — 是否满足 4 层消融标准
5. **实验是否支持核心 claim** — 实验设计是否真正测试了核心贡献
6. **贡献是否真实** — 是否被过度声明
7. **局限是否诚实** — 是否区分了自述局限和可观察局限
8. **叙事是否符合范式** — 4 段式 Introduction, 3 段式 Related Work

### Step 4: 输出审查报告
按 `scholar_skill/paper_critique_template.md` 的报告模板输出，包含：
- 总体评分 (1-10)
- 逐项评分 + 具体建议
- 关键问题排序
- 可执行的改进建议（引用该学者方法论作为参考）
- 修改优先级排序

## 强制要求

- 每条意见给出 evidence 锚点（来自目标论文 + Wiki）。
- 区分"该学者范式中可见的标准 vs 通用学术标准"。
- 不做空泛建议，必须可执行。
- 不冒充该学者本人。
- 不替该学者发表"主观偏好"型评价。
