---
page_id: research-design-template
page_type: template
evidence_level: C
---

# Research Design Template — 研究设计模板

基于陈志远教授研究范式的可操作模板。**以下均为 C 类迁移推断。**

## Step 1: 问题定义

```markdown
### 现实现象
[描述你观察到的现象或工程需求]

### 学术抽象
将该现象抽象为：
- 问题类型: [逆问题 / 检测 / 估计 / 生成 / 其他]
- 前向过程: [如果存在物理模型，描述前向过程]
- 关键挑战: [1-3个]

### 可建模问题
数学形式化为：
- 输入 X: [数据类型、维度、特性]
- 输出 Y: [目标类型、维度、特性]
- 目标函数: [min/max] [目标]

### 可验证假设
H1: [具体、可证伪的假设]
H2: [如适用]
```

## Step 2: 方法设计（遵循5层方法论）

```markdown
### Layer 1: 物理建模
- 前向模型: [如有]
- 关键参数: [低维控制参数]

### Layer 2: 数学优化
- 优化框架: [ADMM / EM / 梯度下降 / 流形优化]
- 损失函数: [考虑鲁棒性—是否需要自适应阈值？]
- 约束条件: [列出并考虑如何转化为无约束]

### Layer 3: 网络设计
- 骨干网络: [选择]
- 创新模块: [在哪个环节创新？问题抽象层/求解机制层/架构层]
- 是否嵌入物理先验: [是/否，如何嵌入]

### Layer 4: 训练策略
- 优化器:
- 学习率策略:
- 是否需要预训练模型:
- 是否需要自适应调制:

### Layer 5: 实验验证
见实验设计检查清单
```

## Step 3: 实验设计检查清单

```markdown
### 理论验证
- [ ] 推导关键定理/引理
- [ ] 证明方法收敛性/最优性（如适用）

### 合成实验
- [ ] 设计可控合成数据集
- [ ] 模拟多种退化/噪声水平
- [ ] 验证方法在理想条件下的性能上限

### 真实数据验证
- [ ] 选择 ≥ 2 个公开基准数据集
- [ ] 覆盖不同场景/条件
- [ ] 与 ≥ 5 个 baseline 比较（经典+最新）

### 消融研究（4层）
- [ ] Layer 1: 必要性消融（去掉核心模块）
- [ ] Layer 2: 设计选择消融（替换为替代方案）
- [ ] Layer 3: 参数敏感性（关键参数扫描）
- [ ] Layer 4: 极端测试（噪声/退化推到极限）

### 补充分析
- [ ] 计算复杂度分析
- [ ] 可视化/定性分析
- [ ] 失败案例分析
```

## Step 4: 论文结构蓝图

```markdown
### Introduction (4段)
P1: 问题背景 + 为什么重要
P2: 现有方法 + 它们的隐含假设（要挑战的）
P3: 我们的 insight + 为什么现有假设不成立
P4: 我们的方法概述 + 贡献列表

### Related Work (3段)
1. [任务领域]的现有方法 — 按方法论分组
2. [关键技术]的发展 — 说明与我们的根本区别
3. [相关理论]的进展 — 我们的理论定位

### Method
1. Problem Formulation — 问题建模与符号定义
2. Core Mechanism — 核心机制（为什么有效）
3. Architecture/Algorithm — 具体实现
4. Optimization — 训练/求解策略

### Experiments
1. Experimental Setup (datasets, metrics, baselines)
2. Comparison with State-of-the-Art
3. Ablation Studies (4 layers)
4. Robustness Analysis
5. Qualitative Results / Case Studies

### Conclusion
- 总结贡献
- 诚实列出局限性
- 未来工作
```
