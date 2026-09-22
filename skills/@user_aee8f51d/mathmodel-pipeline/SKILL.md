---
name: mathmodel-pipeline
description: 数学建模竞赛全流程技能：赛题分析、建模、编码求解、数据图表、结构图、论文撰写与提交前验收的完整流水线，内置方案质询门禁、证据缺口（EVIDENCE_GAP）双向协议和验收返工规则。当用户提到数学建模、建模竞赛、国赛/CUMCM、华为杯、华中杯、MCM/ICM、APMCM、赛题、附件数据、建模求解、灵敏度分析、竞赛论文、摘要、论文验收时使用——即使用户只说"帮我做这道数模题""跑一下这个模型写篇论文""检查论文能不能交"也应触发。
---

# 数学建模全流程（mathmodel-pipeline）

把"建模手 / 编程手 / 论文手"三个角色的职责整合为单一技能的九步流水线。每一步有明确的输入、产物和验收口径；三个质询门禁内建在流程里；验收失败有明确的返工路径。

## 不可违背的红线

1. **数值必须可溯源。** 论文和报告中的每一个数值都必须能追溯到 `results/` 下的真实产物或 `reports/RESULTS_REPORT.md`。禁止凭模型记忆编造数值、文献、数据字段。
2. **EVIDENCE_GAP 双向协议。** 证据的**产生方**（分析、编码阶段）发现缺口时，必须在对应报告中写一行 `EVIDENCE_GAP: <缺什么> <影响哪一问> <补齐方式>`；证据的**消费方**（写作、验收阶段）必须逐项核销每个 EVIDENCE_GAP：补齐证据、删除论点、或降低结论强度并写入局限，三选一，不得用"结果表明"之类的空话掩盖。
3. **问题数量以题面为准。** 先从题面提取实际问题清单（如 Q1..Qn），所有章节、代码文件、结果文件、图表按 N 动态组织。禁止默认三问，也禁止从模板文件数量推断问题数量。
4. **验证方法匹配模型类型。** 回归报交叉验证/残差，分类报混淆矩阵与不平衡指标，优化报可行性与扰动稳定性，评价报指标方向与权重来源。没有对应验证证据时降低结论强度。
5. **结论闭环。** 每一问都要走完：题目要求 → 模型/算法 → 真实结果 → 结果解释 → 验证 → 适用边界 → 对题目要求的明确回答。

## 总流程：九步三门禁

| 步骤 | 阶段 | 主要产物 | 门禁 |
| --- | --- | --- | --- |
| 1 | 赛题分析与建模设计 | `reports/ANALYSIS_MODELING_REPORT.md` | — |
| 2 | 方案质询 | `reports/MODEL_GRILL_REPORT.md` | **门禁 A** |
| 3 | 编程实现与数据图表 | `code/`、`results/`、`reports/RESULTS_REPORT.md`、`figures/*.pdf` | — |
| 4 | 结构图绘制（确有需要时） | `figures/*.drawio`、`reports/DRAWIO_REPORT.md` | — |
| 5 | 论文内容计划 | `reports/PAPER_CONTENT_PLAN.md` | — |
| 6 | 论证计划质询 | 更新 `PAPER_GRILL_REPORT.md` | **门禁 B** |
| 7 | 正文撰写与摘要 | `paper/`、参考文献文件 | — |
| 8 | 成稿质询 | 更新 `PAPER_GRILL_REPORT.md` | **门禁 C** |
| 9 | 编译与验收 | 最终 PDF/DOCX、`reports/VERIFY_REPORT.md` | — |

开始任务前先做依赖预检（见"依赖预检"一节），再生成 `plan.md` 与 `todo.md`，模板如下。模板中的门禁行是流程的一部分，跳过门禁直接进入下一阶段视为流程违规。

```markdown
# 方案

用户偏好（未指定的项在门禁 A 一并确认，不要单独追问）：
- 排版引擎：<LaTeX（默认）/ Typst / Word>
- 竞赛类型：<国赛 / 华为杯 / MCM / ...>
- 论文语言：<中文 / 英文，MCM/ICM 强制英文>
- 实际问题清单：<Q1..Qn 及一句话要求，未知则写"待分析阶段确定">

workflow:
1. 赛题分析与建模设计          → ANALYSIS_MODELING_REPORT.md
2. [门禁A] 方案质询            → MODEL_GRILL_REPORT.md
3. 编程实现与数据图表          → RESULTS_REPORT.md、results/、figures/
4. 结构图绘制（按需）          → DRAWIO_REPORT.md
5. 论文内容计划                → PAPER_CONTENT_PLAN.md
6. [门禁B] 论证计划质询        → PAPER_GRILL_REPORT.md
7. 正文撰写与摘要              → paper/
8. [门禁C] 成稿质询            → 更新 PAPER_GRILL_REPORT.md
9. 编译与验收                  → VERIFY_REPORT.md
```

```markdown
# 待办事项
- [ ] 1. 赛题分析与建模设计
- [ ] 2. [门禁A] 方案质询
- [ ] 3. 编程实现与数据图表
- [ ] 4. 结构图绘制（按需）
- [ ] 5. 论文内容计划
- [ ] 6. [门禁B] 论证计划质询
- [ ] 7. 正文撰写与摘要
- [ ] 8. [门禁C] 成稿质询
- [ ] 9. 编译与验收
```

## 目录与命名约定（全文唯一口径）

```text
<WORK_ROOT>/
├── plan.md  todo.md
├── reports/        # 各阶段报告（文件名固定，见总流程表）
├── code/           # 按问题组织：q1_model.py、q2_solve.py、...、utils.py
├── results/        # 唯一的真实运行产物目录（表格、JSON、日志、图表源数据）
├── figures/        # 全部图表（数据图 + 结构图 PDF/drawio）
└── paper/          # 论文源文件与参考文献
```

中间数据一律进 `results/`，不要另造 `code/outputs/` 之类的第二结果目录。每个 `results/` 文件都必须在 `RESULTS_REPORT.md` 中有一行用途说明。

## 阶段要点

各阶段的完整产出模板和细则在 `references/stage-contracts.md`，写作前按需读取。要点：

1. **分析**：拆解题面顶层问题清单；对影响结果的歧义给出至少两种解释并验算选型；**判据、阈值与分析窗口必须在查看数据计算之前写入建模报告，之后不得更改口径**（确需收缩窗口时按预声明规则执行并在结果报告中记录）；每问写清输入/变量/目标函数/约束/算法与停止条件/验证指标；末尾附"代码实现任务清单"表。
2. **编码**：按问题逐个实现，先可行解再优化；每个问题跑出真实结果后立即写入 RESULTS_REPORT；保存随机种子、参数、迭代历史、约束残差；数据图出 PDF 矢量图，图内不写大标题。
3. **写作**：先建 PAPER_CONTENT_PLAN（论点—证据—章节矩阵，每格绑定 `results/` 实文件），再逐问成文；摘要最后写，必须覆盖每问方法与精确数值；正文用连贯学术段落，不堆列表。
4. **验收**：跑统一检查清单（`references/verification-checklist.md`），编译，PDF 逐页视觉检查（无视觉能力时如实记录并完成程序化检查）。

## 门禁与无人值守规则

三个门禁共用一套批量质询协议，完整协议在 `references/grill-protocol.md`：

- 提问前先自行核对题面、数据和报告，能自答的不问用户；每轮最多 10 个编号问题，每问附影响说明和推荐答案；最多 3 轮。
- **无人值守降级（限时/全自动场景）**：用户明确离席，或一个门禁批次发出后未获回复时，**全部采用推荐答案继续推进**，在质询报告中对每项标注 `默认采用（未经用户确认）`，门禁状态记为 `READY_WITH_RISKS`。禁止因等不到回复而挂起流程；高风险默认选择必须同时写入 VERIFY_REPORT 的"仍需处理的问题"。
- 门禁结论只有三种：`READY`、`READY_WITH_RISKS`、`BLOCKED`。`BLOCKED` 仅当证据缺口属于"补不齐且无法降级"时使用，且必须写明缺口和补救路径，交由用户决策。

## 验收与返工

验收 FAIL 时按类别返工，不要原地反复重试：

| FAIL 类别 | 处理 |
| --- | --- |
| 占位符、笔误、图片路径错、编译语法错 | 就地小修后重跑验收 |
| 数值与 results/ 冲突 | 以 results/ 为准修正论文；若 results/ 本身有错，退回步骤 3 只重跑受影响问题 |
| 某问缺验证证据或 EVIDENCE_GAP 未核销 | 退回步骤 3 补证据，或删论点/降结论（回写 PAPER_CONTENT_PLAN） |
| 模型本身不可行或结果不可信 | 退回步骤 1 修订建模，更新 ANALYSIS_MODELING_REPORT 后按序重跑 |

每次返工更新 `todo.md` 状态，并在 VERIFY_REPORT 记录返工轮次。同一问题返工超过 2 轮仍 FAIL，停下来向用户说明根因，不要继续猜测。

## 依赖预检

任务开始前运行一次（Python 标准库实现，无第三方依赖）：

```text
python "<SKILL_DIR>/scripts/preflight_check.py" --profile <analysis|code|paper|word|all> --json
```

按任务类型判断阻塞：只做分析只需 Python；编码需 numpy/pandas/matplotlib；论文编译需 typst 或 xelatex 二选一；Word 交付需 pandoc 或 pypandoc。缺失的可选依赖不阻塞流程，如实记录即可。`--strict` 让阻塞项缺失时以非零码退出。

## 参考文件

- `references/stage-contracts.md` — 各阶段报告模板、论文章节结构、摘要契约、按模型类型的验证证据表、拟合与数值实验防错清单。**在对应阶段开始前读取。**
- `references/grill-protocol.md` — 质询门禁完整协议、问题维度、无人值守降级细则。**在步骤 2/6/8 前读取。**
- `references/verification-checklist.md` — 验收统一检查清单（FAIL/WARN 唯一口径）、CUMCM 提交硬约束。**在步骤 9 前读取。**
- `references/windows-pitfalls.md` — Windows/编译环境实测坑：PDF 文本层乱码的读图替代、MiKTeX 因 PATH 坏条目崩溃的绕行、fancyvrb 与 CJK 等排版陷阱。**遇到 pdftotext 乱码、xelatex "cannot retrieve attributes"、附录丢字时读取。**
- `assets/templates/cumcm/main.tex` — 经真实竞赛论文验证的 CUMCM 风格 LaTeX 模板（宋体正文/黑体标题/摘要框/希腊字母映射）。**LaTeX 引擎 + CUMCM 类赛事时以此为起点。**
