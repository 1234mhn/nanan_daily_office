# 任务：F 题论文收尾（Claude Code 执行）

## 项目位置
`/root/.openclaw/workspace/huawei2026_F/paper/`

## 主生成器
`code/gen_front_correct.py` —— 这是**唯一入口**，运行 `python3 code/gen_front_correct.py` 生成 `docx/F题_论文.docx`。

## 章节模块（不要改结构，只增内容）
- `code/gen_51.py` → `build_51(doc, L)` 问题一
- `code/gen_52.py` → `build_52(doc, L)` 问题二
- `code/gen_53.py` → `build_53(doc, L)` 问题三
- `code/gen_54.py` → `build_54(doc, L)` 问题四

所有模块签名：`build_XX(doc, L)`，其中 `L` 是工具函数字典，含键：
`H1 H2 H3 BODY CAP TABLE P PAGEBREAK FIGURE FIG_DIR`

## 可用工具函数（签名，务必按此调用）
```python
H1(doc, text)              # 一级标题 16pt 黑体居中
H2(doc, text)              # 二级标题 14pt 黑体左对齐
H3(doc, text)              # 三级标题 11pt 黑体
BODY(doc, text)            # 正文 12pt 宋体 1.5倍行距 首行缩进24pt（自动处理 10^N 上标）
CAP(doc, text)             # 图表标题 10.5pt 居中
TABLE(doc, headers, rows)  # 表格（详见函数定义）
P(doc, text, size=...)     # 通用段落（自动处理上标）
FIGURE(doc, path)          # 插图（path 用 FIG_DIR + "/xxx.png"）
PAGEBREAK(doc)             # 分页
```

## 图片目录
`figures/`，命名规范：`q1_fig1.png` ~ `q1_fig6.png`、`q2_fig1.png`~`q2_fig6.png`、`q3_fig1.png`~`q3_fig5.png`、`q4_fig1.png`~`q4_fig6.png`

## 格式红线（官方模板，绝不可违反）
- 页面 A4，上下边距 2.54cm，左右 3.1772cm
- 一级标题：三号（16pt）黑体加粗居中
- 其他标题/正文：小四（12pt）宋体
- 行距 1.5 倍
- 无页眉；页码从摘要页起页脚居中，从 1 连续编号
- 身份保密（不出现学校、姓名、队号真实信息）
- 图号 `图5.N`、表号 `表N`，必须连续无跳号
- 数学公式里的 `10^N` 必须显示为上标（生成器已自动处理，写法用 `10^19`）

---

# 要做两件事

## 任务一：修摘要「针对问题三」段（与正文不一致）

**现状问题**：`code/gen_front_correct.py` 第 353 行摘要写的是：
> "通过**梯度投影法**求解非线性规划问题…在 **10^21、10^22、10^23 FLOPs** 三个预算水平下…"

**但 5.3 正文实际用的是**（见 `code/gen_53.py`）：
- 方法：**KKT 条件 + SLSQP 多初值 + 独立网格验证 + PELT 变点检测**
- 预算档位：**10^19、10^22、10^24 FLOPs**（三个数量级），另用 61 个对数等距预算点扫描
- 关键结果：L_ctx_crit=30000；Q_0=0.605095；首个结构变点 1.334×10^19 FLOPs；
  指数型成本在 10^19 时 Q=0.948353 内部解，10^22/10^24 时三类成本函数均 Q=1；
  成本份额 0.3369/0.2952/0.3680（10^19）→ 0.4606/0.0363/0.5031（10^22）→ 质量份额 0.0049（10^24）

**要做的**：把摘要该段改为与 5.3 正文一致，**只改这一段文字**，其他段落一字不动。
建议改写（可微调措辞但数值必须一致、口径必须一致）：
> "针对问题三，本文以问题二的乘性质量缩放律为目标函数，将基础训练、质量提升与长上下文注意力三类开销统一折算为 FLOPs，在预算约束下联合优化参数规模、数据规模与数据质量。模型由 KKT 条件刻画边际资源配置关系，用 SLSQP 多初值求解并以确定性网格独立验证，通过 PELT 与活跃集变化共同识别结构转变。结果表明：当上下文长度超过临界值 30000 时注意力开销单独超过基础训练开销；在低预算阶段优先提升数据质量，预算跨越约 1.334×10^19 FLOPs 后质量触及上界、新增预算主要分配给参数与数据规模。"

## 任务二：补写四个章节（目录里现标"待补"）

在 5.4 之后，按顺序补：
1. **六、模型分析检验**
2. **七、模型评价与推广**
3. **参考文献**（≥10 篇，真实可查的经典文献：Kaplan 2020 Scaling Laws、Hoffmann 2022 Chinchilla、Clark 2022、Rae 2021 Gopher、Muennighoff 2023、Srivastava 2022、Touvron 2023 LLaMA、Brown 2020 GPT-3、Bahri 2024、Sorscher 2022、Gadre 2024 datacomp、Penedo 2023 RefinedWeb、Longpre 2023、Lee 2023 dedup 等，按 GB/T 7714 格式）
4. **附录**（附：关键代码清单/参数文件说明/数据来源说明）

补充要求：
- 每个新章节都要用 `H1`/`H2` 或 `BODY` 生成，保持全文格式一致
- **不要编造数据**：所有数值必须来自已写好的 5.1~5.4 正文，或来自源文档（`/tmp/fq1/q1.txt`、`/tmp/fq2b/q2.txt`、
  `/tmp/fq3/q3.docx`、`/tmp/fq4/q4.docx`）。写不了实数的地方用定性表述。

## 更新目录
`code/gen_front_correct.py` 里有个 `toc_entries` 结构（形如 `(标题, is_h1, [(子标题,页码)], own_page)`），
新增章节后要把「六、模型分析检验」等条目的「待补」替换为**真实页码**（生成 PDF 后用 `pdftotext`/`pdfinfo` 查）。

## 完成后必须自检（必做）
1. 运行 `python3 code/gen_front_correct.py` 成功
2. `soffice --headless --convert-to pdf --outdir /tmp/cc_check docx/F题_论文.docx` 转换成功
3. 用 `pdfinfo /tmp/cc_check/F题_论文.pdf | grep Pages` 看总页数
4. 用 `pdftotext -f N -l N` 逐页确认**没有空白页**
5. 确认图号 5.1~5.23 连续、表号 1~7 连续（新章节若加表则接续表8...）
6. 确认上标正常（docx 里 `r.font.superscript` 为 True）
7. 把自检结果贴出来

## 禁止事项
- ❌ 不要改动 5.1~5.4 已有正文的数值或结构
- ❌ 不要改 `gen_51.py`~`gen_54.py` 的建模内容（除任务一那一段摘要在 `gen_front_correct.py`）
- ❌ 不要编造任何数据
- ❌ 不要重写整个 `gen_front_correct.py`，只做**目标区块的精准修改**
- ❌ 改前先备份：`cp code/gen_front_correct.py code/gen_front_correct_backup_$(date +%Y%m%d_%H%M).py`
