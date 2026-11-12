---
name: "thinking-models-toolkit"
description: "28 个结构化思维框架（芒格/第一性原理/能力圈等），用于决策、诊断、风险、战略与创新分析。"
---

# 思维模型工具箱（thinking-models-toolkit）

来源：`tjboudreaux/cc-thinking-skills`（MIT，1635★）。28 个 eval-informed Agent Skills，每个是一个**可执行的分析程序**（不是知识点清单）。

## 核心用法（必须遵守）

1. **不确定用哪个框架 → 先用路由器** `thinking-model-router`
   - 输入问题 → 输出 `NONE`（不需要框架）/ 1 个框架 / 最多 3 个互补框架
   - **禁止**"手里有锤子看什么都像钉子"——先路由再选

2. **一个框架有盲区 → 用** `thinking-model-combination` 组合多个框架**按顺序**跑

3. **调用方式**：读取对应 `SKILL.md`，按其 `Procedure` 步骤执行，按 `Output` 格式输出

## 框架清单（按用途分组）

### 路由与组合
- `thinking-model-router` — 选框架（返回 NONE / 1 个 / ≤3 个互补）
- `thinking-model-combination` — 多框架按序组合，补盲区

### 诊断与理解
- `thinking-scientific-method` — 排序原因，测最便宜的判别实验
- `thinking-five-whys-plus` — 找系统性根因
- `thinking-kepner-tregoe` — IS / IS-NOT 对比，must/want 选项
- `thinking-systems` — 映射流动、反馈、延迟、高杠杆点
- `thinking-map-territory` — 化解"文档 vs 实际行为"冲突
- `thinking-cynefin` — 判定因果域（简单/复杂/混沌/混乱）
- `thinking-socratic` — 用直问暴露隐藏需求

### 决策与评估
- `thinking-reversibility` — 区分"易撤销"与"昂贵承诺"
- `thinking-opportunity-cost` — 对比被放弃的最优选项
- `thinking-probabilistic` — 基准率、区间、信念更新
- `thinking-second-order` — 追踪延迟效应、激励、反馈
- `thinking-steel-manning` — 先建最强反方论证
- `thinking-bounded-rationality` — 设"够好"阈值，停止搜索
- `thinking-circle-of-competence` — 检查证据边界（防自信编造）
- `thinking-lindy-effect` — 权衡耐久性，警惕领域突变

### 创造与改进
- `thinking-first-principles` — 分离"物理约束"与"惯例"，从基础重建
- `thinking-triz` — 化解看似不可兼容的设计要求
- `thinking-via-negativa` — 先移除有害/非必要元素
- `thinking-thought-experiment` — 真实测试太贵时的受控 what-if
- `thinking-jobs-to-be-done` — 用户"雇用"产品要完成的进步
- `thinking-effectuation` — 不确定下从现有手段出发行动

### 风险与执行
- `thinking-pre-mortem` — 把失败路径转成修复与停止检查
- `thinking-red-team` — 受控攻击路径复核，可复现发现
- `thinking-margin-of-safety` — 按错误与突破成本定缓冲
- `thinking-theory-of-constraints` — 找并管理吞吐瓶颈
- `thinking-ooda` — 时间压力下边观察边行动

## 每个框架的固定结构

每个 `SKILL.md` 含：
- `When to Use` / `When NOT to Use` — 适用边界（**必须遵守**，防止过度套用）
- `Procedure` — 编号步骤
- `Output` — 结构化输出模板
- `Verification` — 自检 + 过度套用防护

## 🔴 使用铁律

1. **先路由再选**：不确定就用 router，别硬套
2. **尊重 When NOT**：每个框架都写了不适用场景，禁止无脑套用
3. **按 Output 模板输出**：框架的价值在"结构"，不要写成散文
4. **诚实性**：`circle-of-competence` 要求未证实的断言必须标 uncertainty 或 abstain，禁止 fluent fabrication
5. **用于用户真实信息分析时**：先让用户明确分析目标（赚钱方向 / 职业路径 / 试工具），不同目标选不同框架组

## 证据说明（README 原文，保持诚实）

仓库自审报告：唯一有实验证据的是 `scientific-method` +4.0 个百分点，**低于 +5 的效用门槛**，只能当方向性证据，不能当精度声明。→ 本工具箱是**结构化思考的辅助**，不是"自动出正确答案"的机器。
