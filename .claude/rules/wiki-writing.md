# Wiki Writing Rule

## Wiki 页面要求

每个 Wiki 页面必须包含：

1. YAML frontmatter（page_id, page_type, title, status, evidence_level, source_papers, related_pages, confidence, updated_at）
2. 可追溯的 evidence_id
3. 反向链接到来源论文
4. 与其他页面的交叉引用
5. 证据等级标注
6. 不确定性标记

## Wiki 更新协议

1. 先 staging，后合并。所有自动生成的更新先写入 wiki/logs/staging/{run_id}/
2. 新内容优先追加到相应小节，而非覆盖。
3. 新旧结论冲突时，不覆盖旧结论，写入 wiki/contradictions.md。
4. 更新页面时必须更新 updated_at 和 related_pages。
5. 同一概念不重复建页。
6. 每次更新有 change log。

## 禁止

- 不允许直接删除旧信息（除非是明显的解析错误）。
- 不允许在无记录的情况下覆盖旧结论。
- 不允许跳过 staging 直接修改核心 Wiki 页面。
