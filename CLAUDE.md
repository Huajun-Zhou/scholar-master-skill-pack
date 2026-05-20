# Academic Master Skill Pack Instructions

本项目目标是把目标学者的公开论文集合炼化为 Scholar Wiki 和 Scholar Skill。

## 永久规则

1. 禁止冒充目标学者本人。
2. 所有非平凡学术判断必须附 evidence_id。
3. 必须区分 A 直接证据、B 综合归纳、C 迁移推断。
4. 不允许为了让答案完整而补充无证据结论。
5. Wiki 更新必须保留旧信息，并记录 change log。
6. 每次批量处理后必须运行质量门禁。
7. Paper Card 是基础层，Method Card 和 Thinking Model 不得绕过 Paper Card 直接生成。
8. 所有页面使用统一 frontmatter。
9. 所有脚本必须支持可重复运行。
10. 用户只负责把 PDF 放入 data/raw/papers/，其他步骤尽可能自动化。

## 安装

项目使用 src 布局，首次使用前需要：

```bash
pip install -e .
```

未安装时也可临时用 `PYTHONPATH=src python -m scholar_skill_pack.cli ...` 运行。

## 目标学者

陈志远教授 (Zhiyuan Chen)，北京邮电大学网络空间安全学院。
16 篇公开论文，覆盖通信安全、工业物联网安全、无人机安全通信、可信计算、鲁棒组网、隐私保护。

## CLI 命令

| 命令 | Phase | 功能 |
|---|---|---|
| `init` | 0 | 初始化/自检项目结构 |
| `parse` | 1 | 解析 data/raw/papers/*.pdf |
| `extract-paper-cards` | 2 | 生成 Paper Card 提取提示与模板 |
| `audit-evidence` | 2 | 审计 Paper Card 证据覆盖 |
| `build-wiki` | 3-4 | 构建 Wiki + 跨论文综合 |
| `lint` | — | 运行 Wiki lint 与质量门禁 |
| `compile-skill` | 7 | 编译 Scholar Skill |
| `ask "问题"` | 8 | 无 UI 询问 Scholar Skill |
| `update` | 10 | 增量更新（新论文） |
| `snapshot` | — | 导出当前版本快照 |

交互命令: `PYTHONPATH=src python -m scholar_skill_pack.cli <command>`

## Scholar Skills

- `/ask-scholar "问题"` — 基于 Scholar Wiki 回答科研问题 (A/B/C 证据)
- `/design-research "想法"` — 按学者方法论生成研究方案
- `/critique-paper "论文路径"` — 8 维度论文审查

## 增量更新流程（新论文到达时）

```bash
# 1. 放入新 PDF
cp new_paper.pdf data/raw/papers/

# 2. 自动检测并增量更新
PYTHONPATH=src python -m scholar_skill_pack.cli update

# 3. 为新论文生成 Paper Card (使用 Claude Code)
/ingest-papers

# 4. 更新受影响的 Wiki 页面
# 5. 重新编译 Skill
PYTHONPATH=src python -m scholar_skill_pack.cli compile-skill

# 6. 质量检查
PYTHONPATH=src python -m scholar_skill_pack.cli lint
```

## 关键文件

- 项目规划: `../Academic_Master_Skill_Pack_项目规划书.md`
- 最终报告: `reports/final_report.md`
- 项目状态: `PROJECT_STATE.md`
- Scholar Skill: `scholar_skill/SKILL.md`
