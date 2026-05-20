# Method Card Distillation Prompt

读取多篇 Paper Cards，识别稳定出现的方法模块，按 §5.4 模板生成 Method Card。

## 不能做的事

1. 不要按论文逐篇摘要。
2. 不要只复述模型结构——必须解释"解决什么问题"。
3. 不要把单篇论文的特殊实现升格为通用方法。

## 必须做的事

1. 把方法抽象为：**问题类型 → 核心机制 → 输入条件 → 输出结果 → 验证方式**。
2. 每个 Method Card 至少 2 个 paper_id 来源；核心方法至少 3 个。
3. 写"适用问题类型"与"不适用场景"（QG5 硬性）。
4. 写"迁移条件"。
5. 迁移建议必须标 C 类。
6. 不足 2 篇支持 → 归入 `candidate_methods/`，不进入正式卡片。
7. 列出"与其他方法的组合"（如何与本项目其他 Method Card 串联）。

## 校验

`python scripts/validate_json.py method_card`。
