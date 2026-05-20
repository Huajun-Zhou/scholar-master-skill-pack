# Paper Card Extraction Prompt

你将读取一篇论文的结构化文本（chunks + sections）。任务不是写摘要，而是把论文炼化为 Paper Card。

## 强制规则

1. 只基于输入文本，不补充外部知识。
2. 每条核心结论必须标注 `evidence_id`，格式 `EVID-{paper_id}-P{page}-C{chunk}`。
3. 迁移启发必须标 `evidence_level: C`。
4. 隐含假设必须标 `source: inferred`。
5. 不确定就写 `unknown`，不要猜测。
6. 不要使用第一人称指代该学者（"我提出"等）。

## 10D 输出结构

按 `schemas/paper_card.schema.json` 输出 JSON，再按 §5.3 模板渲染为 Markdown：

1. 元信息（paper_id / title / year / authors / venue / doi / source_file / processing_status）
2. 一句话贡献（含 evidence_id）
3. 研究问题（原始 / 学术抽象 / 重要性）
4. 核心思想
5. 方法框架（输入 / 输出 / 模型 / 算法 / 损失 / 数据 / 指标）
6. 实验设计（baseline / ablation / robustness / case_study / human_eval）
7. 关键结论（每条带 evidence_id 与 confidence）
8. 隐含假设（区分 explicit / inferred）
9. 局限性（区分 self_stated / system_inferred）
10. 可迁移启发（标 C 类）
11. 与其他论文关系（前置 / 后续 / 同主题 / 方法继承 / 方法转向）
12. Evidence 表格（evidence_id, page, section, claim_type, confidence）

## 校验

输出后用 `python scripts/validate_json.py paper_card` 校验。校验失败回滚为 draft 并标记 `processing_status: needs_review`。
