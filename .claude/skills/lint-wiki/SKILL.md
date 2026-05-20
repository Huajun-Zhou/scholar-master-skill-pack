---
name: lint-wiki
description: 检查 Scholar Wiki 质量——孤立页、断链、缺证据、重复概念、矛盾候选、过期页、缺 frontmatter。
---

# Lint Wiki

## 检查项

1. **orphan pages**：未被任何页面链接的页面。
2. **broken links**：Markdown 链接指向不存在的文件或锚点。
3. **missing evidence**：A 类结论缺 evidence_id；B 类综合不足 2 个 paper_id。
4. **duplicated concepts**：同一概念存在多个 slug。
5. **contradiction candidates**：跨页结论冲突。
6. **weak synthesis claims**：综合归纳证据不足。
7. **stale pages**：updated_at 过老但 source_papers 已变化。
8. **missing frontmatter**：未按 wiki_page.schema.json 提供完整 YAML 头。

## 实现

调用 `python scripts/check_wiki_links.py` 与 `python scripts/check_evidence_coverage.py`，并由 `src/scholar_skill_pack/lint.py` 汇总报告到 `reports/quality_reports/`。

## 失败处理

- 标记失败原因；
- 不自动修复关键结构问题；
- 输出到 `reports/quality_reports/lint_{date}.md`。

## 使用

```text
/lint-wiki
```
