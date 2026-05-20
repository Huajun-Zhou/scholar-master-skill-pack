# Evidence Extraction Prompt

把论文中的关键陈述抽取为 Evidence Ledger 条目。

## 输入

- `data/processed/chunks/{source_id}.jsonl`
- 已识别的 sections

## 输出

每条 evidence 按 `schemas/evidence.schema.json`：

```json
{
  "evidence_id": "EVID-PAPER_003-P12-C04",
  "paper_id": "PAPER_003",
  "source_file": "...",
  "page": 12,
  "section": "Method",
  "chunk_id": "...-C04",
  "claim": "...",
  "support_type": "direct|paraphrase|inferred|negative|uncertain",
  "evidence_level": "A|B|C",
  "confidence": "low|medium|high",
  "quote_or_anchor": "原文片段或位置锚点",
  "notes": ""
}
```

## 强制规则

1. `quote_or_anchor` 必须存在；可以是引用片段或 page+section 锚点。
2. `support_type=direct` 必须有原文片段。
3. `support_type=inferred` 必须在 `notes` 中说明推断依据。
4. 不为论文不支持的 claim 生成 evidence。
5. 单个 chunk 可生成多条 evidence；evidence_id 需唯一。
