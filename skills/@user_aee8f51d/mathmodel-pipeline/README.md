# mathmodel-pipeline — 数学建模竞赛全流程技能

> **版本** v1.1.0 ｜ **平台** ZCode / Agent Skills（`.agents/skills` 规范） ｜ **语言** 中文 ｜ **状态** 真实竞赛题目端到端验证通过

一个把"建模手 / 编程手 / 论文手"三角色协作整合为**单一技能**的数学建模竞赛全流程工作流：从赛题分析、建模、编码求解、图表，到论文撰写、编译与提交前验收，共 **九步、三道质询门禁**，内置反伪造红线、证据缺口（EVIDENCE_GAP）双向协议和验收返工规则。

## 为什么不是"三角色插件"

本技能衍生自一套 coder / modeler / writer 三个 Codex 插件（25 份提示词、约 4800 行）。审查发现其编排存在 15+ 处设计缺陷（总控模板遗漏质询门禁、EVIDENCE_GAP 协议单向、验收失败无返工路径、无人值守场景挂起、目录口径混乱、依赖清单与实际脱节、断链引用等），本技能在整合其精华（反伪造红线、问题清单门禁、内容闭环契约、批量质询协议）的同时逐一修复：

| 原版缺陷 | 本技能的修复 |
| --- | --- |
| 总控 workflow 的 plan/todo 模板遗漏质询门禁 | 门禁A（方案）/B（论证计划）/C（成稿）直接写进模板 |
| EVIDENCE_GAP 仅 writer 侧使用 | 双向协议：产生方登记 → 消费方三选一核销 |
| 验收 FAIL 后无返工路径 | 返工分类表（就地修 / 退编码 / 退建模）+ 2 轮熔断 |
| grill 门禁无人值守时无限挂起 | 降级规则：默认采用推荐答案并逐项标注，状态 READY_WITH_RISKS |
| 目录口径混乱（results/ vs code/outputs/） | `results/` 唯一结果目录，显式禁止第二口径 |
| 依赖清单与实际技能集脱节 | `scripts/preflight_check.py` 按任务 profile 判定阻塞，覆盖真实依赖 |
| 附录 FAIL/WARN 双口径等自相矛盾 | 验收清单 FAIL/WARN 唯一口径来源 |
| 三问硬编码、中英混杂、断链引用 | 动态 Q1..Qn、全中文、零断链（回归测试把关） |

## 特性

- **九步三门禁流程**：分析 → 门禁A方案质询 → 编码与图表 → 结构图（按需） → 论文内容计划 → 门禁B论证质询 → 正文与摘要 → 门禁C成稿质询 → 编译验收。
- **五条红线**：数值可溯源、EVIDENCE_GAP 双向、问题数量以题面为准、验证方法匹配模型类型、每问结论闭环。
- **无人值守模式**：限时/自动跑批时门禁不挂起——默认采用推荐答案，逐项标注"未经用户确认"，全部汇总进验收报告供事后复核。
- **判据预登记纪律**：分析窗口、判定阈值在查看数据计算之前写入建模报告，杜绝事后 p-hacking。
- **自带工程资产**：依赖预检脚本、经真实竞赛验证的 CUMCM LaTeX 模板、Windows/编译环境坑手册、拟合与数值实验防错清单。

## 安装

本技能位于用户级技能目录（全项目可用）：

```text
C:\Users\<用户名>\.agents\skills\mathmodel-pipeline\
```

安装到其他机器：把整个 `mathmodel-pipeline\` 目录复制到目标机的 `~/.agents/skills/`（用户级）或 `<项目>/.agents/skills/`（项目级）即可，无其他安装步骤。

## 使用

在 ZCode 中无需记忆命令，以下说法都会自动触发（也可用 `/mathmodel-pipeline` 显式调用）：

```text
帮我做这道数模题（附上题面 PDF 和附件数据）
用附件1和附件2建这个模型，跑出结果写篇论文
检查这篇竞赛论文能不能交
```

技能会按九步流程推进，产出：`plan.md`/`todo.md`（含门禁）、`reports/` 五类阶段报告、`code/` + `results/`（真实运行结果）、`figures/`（矢量图）、`paper/`（LaTeX/Typst/Word 论文与 PDF）。

三个门禁在有人值守时向用户提批量问题（每轮 ≤10 问、附推荐答案）；**无人值守时自动采用推荐答案继续推进**，所有默认决定在 `VERIFY_REPORT.md` 的"默认采用决策清单"中留档。

## 工作流程

```text
题面+附件 ──► ①分析建模 ──► [门禁A]方案质询 ──► ③编码求解/数据图 ──► ④结构图(按需)
                 │                                                    │
                 │            EVIDENCE_GAP 双向登记 ◄──────────────────┘
                 ▼                                                    ▼
            plan/todo(含门禁)                              RESULTS_REPORT
                                                                      │
   VERIFY_REPORT ◄─ ⑨编译+逐页验收 ◄─ [门禁C]成稿质询 ◄─ ⑦正文+摘要 ◄─┤
        │                              ▲                              ▼
        │返工分类表(≤2轮熔断)            [门禁B]论证质询 ◄─ ⑤内容计划 ──┘
        ▼
   PASS / 退回对应步骤
```

## 目录结构

```text
mathmodel-pipeline/
├── SKILL.md                          # 主提示词：流程/红线/门禁/返工（<500 行）
├── README.md                         # 本文件
├── references/                       # 按需加载的详细规范
│   ├── stage-contracts.md            #   各阶段产出契约 + 拟合防错清单
│   ├── grill-protocol.md             #   质询门禁协议 + 无人值守降级
│   ├── verification-checklist.md     #   验收 FAIL/WARN 唯一口径 + CUMCM 硬约束
│   └── windows-pitfalls.md           #   Windows/编译环境实测坑手册
├── scripts/
│   └── preflight_check.py            # 依赖预检（纯标准库，--profile/--json/--strict）
├── assets/templates/cumcm/
│   └── main.tex                      # 经真题验证的 CUMCM 风格 LaTeX 模板
└── tests/
    └── self_test.py                  # 结构回归测试（45 项断言）
```

## 依赖

- **Python ≥ 3.10**；核心包 `numpy` `pandas` `matplotlib` `openpyxl`；扩展包按需 `scipy` `statsmodels` `seaborn` `pingouin` `pint` `uncertainties`
- **论文编译**：`xelatex` 或 `typst` 至少其一；**Word 交付**：`pandoc` 或 `pypandoc`
- 可选：`drawio`（结构图导出 PDF）、`pdftoppm`/`mutool`/`magick`（PDF 视觉检查）
- 一键体检：`python scripts/preflight_check.py --profile <analysis|code|paper|word|all>`

## 测试与验证

| 层级 | 内容 | 结果 |
| --- | --- | --- |
| 结构回归 | `python tests/self_test.py`：frontmatter、引用零断链、门禁模板、协议覆盖、口径唯一、模板质量 | 45/45 通过 |
| 行为冒烟 | 子代理模拟技能触发，迷你赛题无人值守执行：门禁入模板、缺失附件不编造（EVIDENCE_GAP）、降级不挂起 | 通过 |
| 真题实测 | 2025 高教社杯全国大学生数学建模竞赛 B 题（碳化硅外延层厚度）端到端：SiC 厚度 7.76 μm（两角度偏差 0.45%）、Si 厚度 3.42 μm（四方法互验极差 1.1%）、多光束不显著（谐波 <7%）；21 页论文 xelatex 编译 0 错误/0 溢出/0 丢字 | 验收 PASS |

## 已知限制

- 使用社区通行的 CUMCM 版式（宋体/黑体/摘要框），非官方 LaTeX 模板；正式提交前建议对照当年官方论文格式规范复核。
- 未捆绑原项目的 20+ 赛事模板库与绘图脚本资产；需要时从原仓库按需取用。
- 文献检索的自动化程度取决于运行环境（OpenAlex API Key / 联网搜索工具）；无联网时退化为人工 Deep Research 流程。
- 完整端到端运行耗时与题目规模相关，真题实测约数小时（含三轮返工）。

## 版本历史

- **v1.1.0**（2026-08-29）：固化 CUMCM 2025 B 真题实测经验——判据预登记纪律、拟合与数值实验防错清单（参数简并/链式断链/粗差弃用）、`windows-pitfalls.md` 环境坑手册、CUMCM 模板资产、自带回归测试。
- **v1.0.0**（2026-08-29）：首版。整合三角色提示词精华，修复 15+ 项编排缺陷，通过结构/行为/真题三层测试。

## 致谢与许可

本技能衍生自 **MathModelAgent contributors** 的数学建模 Skills 项目（coder / modeler / writer 三插件；原仓库同时包含 Apache-2.0 与 MIT 许可文本及第三方声明）。本技能沿用原项目的许可条款；其中引用的方法学思想（TDD、系统化调试、完成前验证）来自社区广泛使用的同名 skills。使用与再分发请遵循原项目相应许可。
