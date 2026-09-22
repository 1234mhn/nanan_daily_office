# MCM/ICM 规则要点与评审标准

## 来源与时效

来源：COMAP 官方 Contest Rules, Registration and Instructions 页
https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php
本文件记录的是 **2027 年赛季**的官方条款（2026 赛季起已实施 25 页限制）。规则逐年调整，执行审查前必须按 SKILL.md 的年度校验义务拉取官网现行版本核对页数、提交方式与 AI 政策三项。若与官网冲突，以官网为准并回修本文件。

## 一、页数与内容约束

1. 论文篇幅不得超过 **25 页**，该限制适用于**整个提交**，包括 Summary Sheet、Solution、Reference List、Table of Contents、Notes、Appendices、Code 以及任何题目特定要求的内容。
2. `Report on Use of AI` 章节**没有页数限制，且不计入 25 页**。
3. 无论是否使用 AI，主解决方案报告始终限制为 25 页。
4. 鼓励使用目录，目录计入页数。
5. 参考文献列表、注释页、附录应放在解决方案正文页之后。

## 二、版式与标识

1. 必须提交为单个 Adobe PDF，英文打字，字体至少 12 号且清晰可读。
2. 每一页的页眉顶部必须包含队伍控制号与页码，格式为 `Team # 0000000, Page 6 of 25`。
3. 学生、指导教师（advisor）与学校或机构（institution）的姓名**不得出现在任何页面上**；除队伍控制号外，不得包含任何身份识别信息。
4. 不得随提交发送数据、计算机程序、软件、数据库等任何非解决方案文件。

## 三、Summary Sheet（摘要页）

1. 摘要是 MCM/ICM 论文的重要组成部分，**必须作为解决方案报告的第一页**出现；电子提交时 PDF 第 1 页即团队摘要。
2. 评委对摘要极为重视（judges place considerable weight），获奖论文常因摘要质量而区别于其他论文。
3. 应当**最后撰写摘要**，需清晰描述解决问题的方法，并突出最重要的结论，解决问题后应预留充足时间写作。
4. 写作视角：读者将依据摘要决定是否阅读正文，摘要中的简洁表述应激发读者了解细节的兴趣。
5. 薄弱摘要的判定：仅仅重述竞赛题目（mere restatements of the contest problem），或从引言中剪切粘贴样板文字（cut-and-paste boilerplate from the Introduction）。
6. COMAP 提供 Word 与 LaTeX 两种 Summary Sheet 模板，模板页作为电子提交的第一页。

## 四、AI 工具使用披露（2026 赛季起强制）

1. 团队必须公开、诚实地说明所有 AI 工具的使用情况。
2. 在 25 页解决方案正文中用**行内引用**指出 AI 工具的使用，说明使用的模型（which model）与用途（for what purpose），并在参考文献部分列出所有使用过的 AI 工具。
3. 使用 AI 时，必须在 25 页解决方案之后附加标题为 `Report on Use of AI` 的新章节，该章节无页数限制且不计入 25 页。
4. 必须验证语言模型生成内容与引用的准确性、有效性与恰当性，并纠正错误或不一致。
5. 必须检查抄袭风险：LLM 可能复制其他来源的大量文本，需回溯原始来源确认。
6. 未清晰引用和说明 AI 工具作用的段落，更可能被认定为抄袭并导致取消资格。

## 五、提交要求

1. 通过在线提交页面 https://forms.comap.org/241335097294056 提交，需提供队伍控制号、Advisor ID 号与选题。
2. PDF 附件以控制号命名，例如 `0000000.pdf`，附件必须小于 25MB。
3. 仅接受 Adobe PDF，每个提交表单限提交一份解决方案。
4. PDF 第 1 页为摘要，随后是解决方案、参考文献与附录。
5. 比赛窗口关闭后不得再做任何修改，须在截止时间前完成提交。

## 六、评委关注要素（评分导向）

评委主要关注团队的思维过程、问题分析、建模方法与数学方法。评审按完成程度分级，没有及格或截止分数，部分解决方案可接受。

官方列出的内容要素，审核时逐项对照：

| 要素 | 官方表述要点 | 审核动作 |
|------|--------------|----------|
| 总体表达 | articulate, concise, organized | 检查行文是否清晰、简洁、有条理，关键陈述是否突出主要思想与结果 |
| 目录 | Table of Contents 有助于读者预览结构 | 检查是否存在、是否与正文一致 |
| 问题澄清或重述 | clarification or restatement of the problem | 检查是否用自己的语言重述问题与任务 |
| 变量与假设 | clear exposition of all variables and hypotheses | 检查符号表是否完整、全文是否统一 |
| 假设论证 | state and justify reasonable assumptions | 检查假设是否给出理由，是否与建模相关 |
| 问题分析 | analysis of the problem, motivating or justifying the model | 检查模型选择的动机与合理性论证 |
| 推导与计算 | 正文总结，冗长部分入附录 | 检查正文是否只留关键推导，细节是否转入附录 |
| 模型设计 | design of the model, how it could be tested | 检查误差分析、灵敏度分析、稳定性分析是否齐备 |
| 优缺点 | strengths or weaknesses | 检查是否有客观自评，是否回避缺陷 |
| 结论 | conclusion and report results explicitly | 检查是否明确回答题目所问的全部问题并给出数值结果 |
| 参考文献 | document resources and references | 检查外部来源是否全部被引用，图表来源是否标注 |

补充要求：所有图像、图形、照片、表格与绘图，若取自其他来源，必须在相应位置标注来源；所有直接引文必须加引号或明确标示并给出来源。

## 七、评审等级

| 等级 | 含义 |
|------|------|
| Outstanding Winner | 最终评审中的最优者，建模、求解、分析与沟通均处最高水平 |
| Finalist | 模范报告，进入最终评审，分析完整且逻辑清晰、易读、全面 |
| Meritorious | 多方面优秀，以清晰、有支撑、组织良好的方式满足所有要求 |
| Honorable Mention | 高于平均的努力，含合理且被支撑的建模与求解过程 |
| Successful Participant | 认真努力并提交报告，但对部分要求回应不完整或存在薄弱 |
| Unsuccessful Participant | 未充分回应问题要求，或显著不完整，或访问了公开讨论赛题的网站 |
| Disqualified | 违反规则，含抄袭、未记录来源、与其他论文高度相似、赛中分享题目或解答 |
| Not Judged | 未正确提交，如文件损坏或格式错误 |

## 八、审查要点映射（供逐项打勾）

| 检查项 | 依据 | 严重程度（违规时） |
|--------|------|--------------------|
| 总页数超过 25 页 | 25 页限制条款 | 严重 |
| 缺 Summary Sheet 或不在第 1 页 | Preparing 条款 | 严重 |
| 摘要仅为题面复述或引言复制 | Summary 写作指引 | 一般 |
| 任一页缺 `Team # , Page X of 25` 页眉 | Preparing 第 3 条 | 严重 |
| 页码总数与实际不符（如 Page X of 20） | 同上 | 一般 |
| 字体小于 12 号 | Rule 10 | 一般 |
| 出现学生、指导教师或学校名称 | Rule 09 | 严重 |
| 出现致谢、签名、校徽等身份标识 | Rule 09 | 严重 |
| 使用 AI 但无行内引用或文献条目 | AI 政策 | 严重 |
| 使用 AI 但缺 `Report on Use of AI` | AI 政策 | 严重 |
| `Report on Use of AI` 被计入 25 页之内 | AI 政策 | 一般 |
| 图表未标注来源 | 提交说明 NOTE | 一般 |
| 缺目录 | 非强制，鼓励使用 | 修改建议 |
| 缺灵敏度分析或误差分析 | 评委关注要素 | 一般 |
| 缺优缺点讨论 | 评委关注要素 | 一般 |
| 结论未明确回答题目所问 | 评委关注要素 | 一般 |
| 附录、代码、参考文献顺序错误 | Preparing 第 4 条 | 一般 |
| 文件命名非控制号或超过 25MB | 提交说明 | 严重 |
| 随附数据或程序文件 | 提交说明 3E | 严重 |
