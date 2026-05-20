# Academic Master Skill Pack

基于目标学者公开论文集合，构建 LLM Wiki + Scholar Skill Pack，把研究成果、方法体系、问题意识、研究范式和可迁移思维模型炼化为 AI 科研助手可调用的能力模块。

## 快速开始

```bash
cd academic-master-skill-pack
mkdir -p data/raw/papers
# 把目标学者的所有论文 PDF 放入 data/raw/papers/
```

然后在 Claude Code 中：

```text
/build-scholar-wiki
```

构建完成后：

```text
/ask-scholar "请基于这位学者的方法论，帮我设计研究框架。"
/design-research "我想研究……"
/critique-paper "请审查 drafts/my_paper.md"
```

## 项目结构

```
academic-master-skill-pack/
├── CLAUDE.md                  # 项目级指令
├── PROJECT_STATE.md           # 当前进度
├── config/                    # 配置文件
├── data/                      # 数据层（raw / processed / registry）
├── schemas/                   # JSON Schema
├── wiki/                      # Scholar Wiki
├── method_cards/              # 方法卡片
├── thinking_models/           # 思维模型
├── scholar_skill/             # 编译后的 Skill
├── .claude/                   # Claude Code 原生配置
├── src/                       # Python 包
├── scripts/                   # 运维脚本
├── prompts/                   # LLM Prompt 模板
├── eval/                      # 评估体系
└── reports/                   # 阶段报告
```

## 核心理念

- **不做人格复刻**，做公开成果炼化
- **LLM Wiki 优先**，非临时 RAG
- **三级证据**：A 直接证据 / B 综合归纳 / C 迁移推断
- **质量高于速度**，宁可标记"证据不足"也不编造
