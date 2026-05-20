# Wiki Update Protocol Prompt

每次自动更新 Wiki 必须遵守此协议。

## 1. 先 staging，后合并

所有自动生成的更新先写入：

```text
wiki/logs/staging/{run_id}/
├── proposed_new_pages/
├── proposed_edits/
├── merge_plan.md
├── evidence_diff.md
├── quality_warnings.md
└── review_summary.md
```

`review_summary.md` 必须列出每条修改的：受影响页面、变更类型、证据来源、置信度、是否新增冲突。

## 2. 合并规则

1. 同一概念不重复建页（先查 alias 表）。
2. 新内容追加到对应小节，而非整页覆盖。
3. 新旧结论冲突 → 不覆盖；写入 `wiki/contradictions.md`。
4. 更新 `updated_at`、`related_pages`、backlinks。
5. 合并完成写入 `wiki/logs/{date}-{run_id}.md`。

## 3. 矛盾页模板

```markdown
# Contradiction Candidate

## 冲突主题
## 旧结论（含 evidence_id）
## 新结论（含 evidence_id）
## 可能解释（时间演化 / 数据集差异 / 问题设定差异 / 真实矛盾）
## 处理建议
```

## 4. 禁止

- 跳过 staging 直接编辑核心 Wiki。
- 无 change log 的覆盖。
- 删除旧信息（除非是明显解析错误，且需在 review_summary 中说明）。
