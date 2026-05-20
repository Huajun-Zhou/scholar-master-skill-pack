---
name: ingest-papers
description: 解析 data/raw/papers/ 中的 PDF，生成结构化文本和 Paper Registry。
---

# Ingest Papers

解析 PDF，不做 LLM 归纳。

## 流程

1. 扫描 data/raw/papers/*.pdf。
2. 为每个文件生成稳定 source_id。
3. 提取每页文本 → data/processed/pdf_text/{source_id}.json。
4. 识别章节 → data/processed/paper_sections/{source_id}.json。
5. 生成 chunks → data/processed/chunks/{source_id}.jsonl。
6. 写入 registry → data/registry/source_registry.jsonl, paper_registry.jsonl。

## 质量门禁 QG1

- 每个 PDF 至少提取到标题候选。
- >= 70% 页面有非空文本。
- 解析差的 PDF 标记 needs_ocr_or_manual_review。

## 使用

```text
/ingest-papers
```
