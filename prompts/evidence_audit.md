# Evidence Audit Prompt

对 Paper Card / Wiki 页面进行证据合规性核查。只审计，不改写。

## 检查清单

1. 每条非平凡结论是否附 `evidence_id`。
2. 每个 `evidence_id` 是否在原始 chunks 中可定位（`quote_or_anchor` 真实存在）。
3. 是否存在未标 C 的迁移推断。
4. B 类综合是否 ≥ 2 个 paper_id。
5. 是否出现"该学者认为……""该学者偏好……"等无来源表述。
6. `confidence` 字段是否合理（高置信度需有强 anchor）。
7. 是否有"为完整性而补"的无证据结论。

## 输出

`reports/quality_reports/audit_{run_id}.md`，结构：

```markdown
# Evidence Audit Report

## 总体
- 审计页面数:
- 总 claim 数:
- 通过 / 标记 / 拒绝:

## 标记项（needs_review）
| 页面 | claim 摘要 | 问题类型 | 修复建议 |
|---|---|---|---|

## 拒绝项（reject，未附 evidence 的强结论）
| 页面 | claim 摘要 | 拒绝理由 |
|---|---|---|

## 风险评估
- 幻觉风险:
- 过度归纳风险:
- 冒充风险:
```

## 强制规则

- 软判断不放行：缺证据就是缺证据。
- 标记的页面写入 `processing_status: needs_review`。
- 拒绝项的 claim 必须从 Paper Card 中移除或降级。
