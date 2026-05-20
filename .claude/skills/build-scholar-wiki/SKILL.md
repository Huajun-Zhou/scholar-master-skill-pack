---
name: build-scholar-wiki
description: 一键总控——从论文解析到 Wiki 构建、Method Cards、Thinking Models、Skill 编译、质量报告。
---

# Build Scholar Wiki

总控 Skill，依次执行以下流程：

1. 检查项目结构和 data/raw/papers/ 下的 PDF。
2. 执行 PDF 解析（/ingest-papers）。
3. 分批生成 Paper Cards。
4. 更新 Scholar Wiki（/refine-wiki）。
5. 生成 Method Cards。
6. 提炼 Thinking Models。
7. 编译 Scholar Skill（/compile-scholar-skill）。
8. 运行质量门禁（/lint-wiki）。
9. 输出 final_report.md 到 reports/。

## 使用

```text
/build-scholar-wiki
```

## 要求

- 每步完成后生成阶段报告到 reports/phase_reports/。
- 质量门禁失败时停止，输出修复建议。
- 更新 PROJECT_STATE.md。
