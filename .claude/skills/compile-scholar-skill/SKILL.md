---
name: compile-scholar-skill
description: 把已验证的 Scholar Wiki 编译为 scholar_skill/SKILL.md 与 supporting files。
---

# Compile Scholar Skill

## 输入

- `wiki/index.md`
- `wiki/research_paradigm.md`
- `wiki/thinking_models.md`
- `method_cards/index.md`
- `thinking_models/index.md`
- `wiki/synthesis/research_playbook.md`

## 输出

- `scholar_skill/SKILL.md`（主文件，控制长度）
- `scholar_skill/scholar_briefing.md`
- `scholar_skill/answer_policy.md`
- `scholar_skill/evidence_policy.md`
- `scholar_skill/research_design_template.md`
- `scholar_skill/paper_critique_template.md`
- `scholar_skill/method_transfer_template.md`
- `scholar_skill/examples.md`

## 强制要求（QG7）

- SKILL.md 主文件不超过 `config/quality_gates.yaml::QG7.max_skill_length`。
- 必须包含 no-impersonation 与 evidence policy。
- 必须包含至少 3 个示例问题与示例回答。
- 详细材料放入 supporting files，不塞进主文件。
- 编译完成后自动 dispatch 到 `eval` 流程。

## 使用

```text
/compile-scholar-skill
```
