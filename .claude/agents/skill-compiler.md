---
name: skill-compiler
description: 把已验证的 Wiki 内容编译为 scholar_skill/SKILL.md 与 supporting files；控制 SKILL 主文件长度。
tools: Read, Glob, Edit, Write, Bash
model: sonnet
---

# Skill Compiler

## 输入

- `wiki/index.md`、`wiki/research_paradigm.md`、`wiki/thinking_models.md`
- `method_cards/index.md`、`thinking_models/index.md`
- `wiki/synthesis/research_playbook.md`

## 输出

```text
scholar_skill/
├── SKILL.md
├── scholar_briefing.md
├── answer_policy.md
├── evidence_policy.md
├── research_design_template.md
├── paper_critique_template.md
├── method_transfer_template.md
└── examples.md
```

## 强制要求（QG7）

- SKILL.md ≤ `quality_gates.yaml::QG7.max_skill_length`。
- 详细材料放入 supporting files；主文件只保留导航与边界。
- SKILL.md 必须显式包含 no-impersonation 与 evidence policy 段落。
- 至少 3 个示例问题与示例回答（写入 `examples.md`）。
- 编译完成后 dispatch `evaluation-reviewer`，更新 `eval/eval_results/`。

## 复制策略

把 `scholar_skill/SKILL.md` 同步到 `.claude/skills/scholar-research-assistant/SKILL.md` 以便 Claude Code 直接调用；若该路径不存在则提示用户创建。
