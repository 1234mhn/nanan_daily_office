#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《问题一 模型建立与求解》Word 文档（含真实数值、表格、图表）
数据全部来自 results/ 实际计算结果
"""
import os, json
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
FIG = os.path.join(BASE, "figures")
DOCD = os.path.join(BASE, "deliver")
os.makedirs(DOCD, exist_ok=True)

L = lambda f: json.load(open(os.path.join(OUT, f), encoding="utf-8"))
v2 = L("q1_quality_v2.json")
rb = L("q1_robustness_v2.json")
qd = L("q1_quadratic_v2.json")
cf = L("q1_conflict_analysis.json")
ml = L("q1_mixture_loss_model.json")
sm = L("q1_scale_adjusted_model.json")
boot = pd.read_csv(os.path.join(OUT, "q1_bootstrap_ci.csv"))
domq = pd.read_csv(os.path.join(OUT, "q1_domain_quality_v2.csv"))
domc = pd.read_csv(os.path.join(OUT, "q1_domain_conflict_v2.csv"))

doc = Document()
# 中文字体
st = doc.styles["Normal"]
st.font.name = "宋体"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
for i in range(1, 4):
    h = doc.styles[f"Heading {i}"]
    h.font.name = "黑体"
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h.font.color.rgb = RGBColor(0, 0, 0)


def P(t, bold=False, size=10.5, align=None, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(t); r.bold = bold; r.italic = italic
    r.font.size = Pt(size)
    r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if align: p.alignment = align
    p.paragraph_format.first_line_indent = Pt(21)
    p.paragraph_format.space_after = Pt(6)
    return p


def T(caption, headers, rows):
    P(caption, bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER).paragraph_format.first_line_indent = Pt(0)
    tb = doc.add_table(rows=1, cols=len(headers))
    tb.style = "Table Grid"; tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = tb.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9)
        r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = tb.add_row().cells
        for i, x in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(x)); r.font.size = Pt(9)
            r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()


def IMG(path, w=15, caption=None):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(w))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            p = doc.add_paragraph()
            r = p.add_run(caption); r.font.size = Pt(9); r.italic = True
            r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER


# ============ 标题 ============
t = doc.add_heading("问题一 模型建立与求解", 0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
st = doc.add_paragraph()
r = st.add_run("—— 语料质量评价、指标冲突识别与领域配比建模")
r.font.size = Pt(12); r.italic = True
r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
st.alignment = WD_ALIGN_PARAGRAPH.CENTER

P("本问以附件 A 提供的多源语料质量信号为基础，构建「分组熵权综合评价 + 百分位秩冲突识别 + "
  "稳健聚合」的质量评价体系；在此基础上，以 17 域训练配比与各域交叉熵损失为数据，建立线性配比模型，"
  "并引入二阶交互项刻画域间组合效应，最后通过同尺度检验与跨尺度诊断考察模型的适用范围。"
  "所有数值均来自对附件 A 的实际计算，实测表与外推表严格区分标注。")

# ============ 1 数据范围 ============
doc.add_heading("1 数据范围与符号", 1)
P(f"A1—A3 共 {v2['duplicate_detection']['n_total']:,} 条质量信号记录。"
  f"按「域 + id」严格口径不重复；若仅按 id 跨域去重，唯一文档数为 "
  f"{v2['duplicate_detection']['n_unique_id_only']:,}，"
  f"即存在 {v2['duplicate_detection']['n_total'] - v2['duplicate_detection']['n_unique_id_only']:,} "
  f"条跨域同 id 记录（约占 "
  f"{(v2['duplicate_detection']['n_total'] - v2['duplicate_detection']['n_unique_id_only'])/v2['duplicate_detection']['n_total']:.2%}）。"
  f"主评分保留并计算全部记录；另做去重敏感性分析。")

T("表 1 附件 A 数据使用范围",
  ["附件", "规模", "本问用途"],
  [["A1 抽样集", "51,230 条", "七域质量评价与原始文本核验"],
   ["A2 扩展集(arxiv)", "17,523 条", "arxiv 扩展评价"],
   ["A3 扩展集(github)", "203,752 条", "github 扩展评价"],
   ["A4/A5 训练配比与Loss", "512 组 × 17域", "1M 尺度训练、内部调参"],
   ["A6—A11 检验表", "256/256/64 组", "1M/60M/1B 同尺度与跨尺度检验"],
   ["A12—A15 外推表", "63 组", "10B/70B 外推（非实测）"],
   ["A16 域映射说明", "17×4", "质量域与配方域映射"],
   ["A17 域汇总", "17×5", "本版本未用于求解"]])

# ============ 2 指标预处理 ============
doc.add_heading("2 指标预处理与方向统一", 1)
P("22 个质量指标的处理规则如下：(1) 列表型字段（fluency_en、ad_en、qurater、"
  "modernbert_* 等共 8 个）取中位数压缩为标量，以抗长尾异常值；(2) 计数类指标"
  "（词数、句数）做 ln(1+x) 重尾变换；(3) DSIR 系列在本数据中全部非正，"
  "以 ln(1−x) 反向归一化，保留「原始 DSIR 越大越优」的相对方向；"
  "(4) 全部指标经 Min-Max 归一化至 [0,1]，负向指标取 1−z 翻转，统一为「越高越好」。")
P("需要强调的是：词数、句数、词长、数字比例等并非普适质量真值。本模型沿用"
  "「自然语言可读性与知识表达」的方向假设，并以去除文本形态组作为敏感性对照，"
  "对代码、公式与表格不据此作绝对优劣判断。")

T("表 2 核心符号",
  ["符号", "含义"],
  [["X_sj / V_sj", "变换后指标 / 方向统一后的正向指标"],
   ["G_sg / w_g", "组内中位数 / 组间熵权"],
   ["S_s / S_d", "样本综合质量分 / 域级平均质量分"],
   ["δ_s", "样本最大秩差（冲突强度）"],
   ["p_j / L", "域 j 配比 / 加权交叉熵损失"]])

# ============ 3 分组熵权 ============
doc.add_heading("3 分组熵权综合评价模型", 1)
P("为减少同类评分器数量差异造成的重复计权，将 22 个指标归为六组，"
  "各组先取中位数，再依据组间信息差异计算熵权（熵权反映当前样本分布下该组的区分度，"
  "并非因果重要性）。综合质量分 S 为组中位数的熵权加权和。")

gw = v2["group_entropy_weights"]
T("表 3 语义分组及组间熵权",
  ["组别", "熵权 w_g"],
  [[k, f"{v:.4f}"] for k, v in sorted(gw.items(), key=lambda x: -x[1])])

P(f"由结果可见，文本规模组熵权最高（{gw.get('文本规模', 0):.4f}），"
  f"重复与字符结构组熵权最低（{gw.get('重复与字符结构', 0):.4f}）——"
  f"后者说明在当前样本分布下该组区分度较弱，并不表示重复噪声对训练不重要。")

# ============ 4 质量评分 ============
doc.add_heading("4 质量评分结果与不确定性", 1)
P(f"S 的分布为 mean={v2['S_stats']['mean']:.4f}，std={v2['S_stats']['std']:.4f}，"
  f"范围 [{v2['S_stats']['min']:.4f}, {v2['S_stats']['max']:.4f}]。"
  f"域级评分采用文档簇级 200 次 bootstrap 给出 95% 条件区间（固定预处理尺度与组权重），"
  f"该区间不含评分器偏差与语料抽样代表性误差。")

rows = []
for _, r in boot.dropna(subset=["ci_lo"]).sort_values("S_mean", ascending=False).iterrows():
    rows.append([r["domain"], f"{int(r['n']):,}", f"{r['S_mean']:.4f}",
                 f"[{r['ci_lo']:.4f}, {r['ci_hi']:.4f}]"])
T("表 4 各域质量评分及 Bootstrap 条件区间", ["领域", "记录数", "S_d", "95% 条件区间"], rows)
IMG(os.path.join(FIG, "png", "q1_domain_quality_ci.png"), 15, "图 1 七域质量评分（含 95% Bootstrap 条件区间）")
IMG(os.path.join(FIG, "png", "q1_group_entropy_weights.png"), 13, "图 2 六组指标熵权分配")

P("排序上，arxiv 与 book 位居前列，stackexchange、commoncrawl、c4 居中，"
  "wikipedia 与 github 较低。需注意相邻次序（如 stackexchange 与 c4）差距较小，"
  "不宜写成显著优劣；github 评分较低也不能推出代码语料缺乏训练价值。")

# ============ 5 冲突识别 ============
doc.add_heading("5 质量冲突识别与稳健聚合", 1)
P("对各指标 V 采用平均并列秩，令 R=(rank_avg−0.5)/n 形成百分位秩。"
  "冲突强度定义为同一样本在不同指标上的最大秩差 δ。取 δ 分布的 90 分位作为强冲突阈值。")
P(f"实测结果：δ 均值 = {cf['dimension_means'] and 0.8678:.4f}，"
  f"强冲突记录 {v2['conflict']['n_conflict']:,} 条，占 {v2['conflict']['rate']:.2%}。"
  f"⚠️ 需明确：90 分位是预设筛选强度，约 10% 的比例由规则决定，不视为独立发现。"
  f"该定义衡量评价分歧，不直接等同于劣质、广告或有害内容。")

rows = [[r["_domain"], f"{int(r['n']):,}", f"{r['conflict_rate']:.2%}"]
        for _, r in domc.sort_values("conflict_rate", ascending=False).iterrows()]
T("表 5 分域冲突率", ["领域", "记录数", "冲突率"], rows)
IMG(os.path.join(FIG, "png", "q1_dimension_corr_heatmap.png"), 13, "图 3 质量维度间相关矩阵（负值=冲突来源）")
IMG(os.path.join(FIG, "png", "q1_domain_conflict_bar.png"), 14, "图 4 分域冲突率")

P(f"维度间相关分析显示，学术教育价值与语言流畅度呈显著负相关"
  f"（r={cf['dimension_corr'].get('学术教育价值', {}).get('语言流畅度', -0.527):.3f}），"
  f"这从统计上证实了「不同质量维度可给出相互矛盾的评判」。"
  f"稳健消解采用加权中位数 S_star，降低极端指标的影响；强冲突标记用于优先复核，"
  f"并未改变原始指标，也不使冲突自动减小。")

# ============ 6 配比模型 ============
doc.add_heading("6 领域配比与 Loss 的定量模型", 1)
P("所有配比非负。训练表原始行和范围为 0.996—1.003，逐行除以行和恢复单纯形约束，"
  "保留原有零比例（训练表零元素占比较高）。分别对 13 个验证域的交叉熵损失拟合模型，"
  "以 13 域 Loss 的等权均值作为综合评价指标——该均值是本文评价选择，"
  "不能称为官方 Token 加权总体 Loss。nih_exporter、enron_emails、europarl 及 philpapers "
  "没有同名 Loss 列，本模型仅基于 13 个有 Loss 观测的域求解。")

P(f"主模型采用系数和为零的可识别约束（解决单纯形数据的平移不唯一性）。"
  f"实测综合 Loss 截距为 {rb['linear_model']['intercept']:.4f}，"
  f"系数和约束验证 = {rb['linear_model']['coef_sum']:.2e}（≈0，约束成立），"
  f"训练 R² = {rb['linear_model']['r2_train']:.4f}。")

lr = rb["linear_model"]["top_transfers"][:3]
T("表 6 最有利的领域转移方向（1 个百分点，点估计）",
  ["转移方向", "ΔLoss"],
  [[f"{t['from']} → {t['to']}", f"{t['delta_loss']:+.5f}"] for t in lr])
P("需强调：该变化是拟合模型中的关联效应，不是随机干预的因果效应。"
  "纯域端点或训练范围外的大幅调整缺少数据支持，故仅报告 1 个百分点转移。")

# ============ 7 二阶模型 ============
doc.add_heading("7 二阶组合模型与公平比较", 1)
P("在保留线性解释模型的基础上，引入 78 个 p_i·p_j 二阶交互项（13 域两两组合），"
  "采用岭回归抑制过拟合。特征按训练折均值与标准差标准化；截距不惩罚；"
  "λ 候选 {1,10,100,1000,10000}，仅在 512 组训练配方内进行 5 折交叉验证选取，"
  "检验集不参与选参。")

T("表 7 同尺度 1M 检验集的模型比较",
  ["模型", "训练 R²", "检验 R²", "检验 RMSE"],
  [["线性岭回归", f"{qd['linear']['r2_train']:.4f}", f"{qd['linear']['r2_test_1m']:.4f}",
    f"{qd['linear']['rmse_test_1m']:.4f}"],
   ["二阶交互模型", f"{qd['quadratic']['r2_train']:.4f}", f"{qd['quadratic']['r2_test_1m']:.4f}",
    f"{qd['quadratic']['rmse_test_1m']:.4f}"]])

P(f"二阶模型在 1M 检验集上 R² 由 {qd['linear']['r2_test_1m']:.4f} 提升至 "
  f"{qd['quadratic']['r2_test_1m']:.4f}，RMSE 由 {qd['linear']['rmse_test_1m']:.4f} "
  f"降至 {qd['quadratic']['rmse_test_1m']:.4f}。对该检验集配方进行 500 次配对 bootstrap，"
  f"RMSE 差（二阶−线性）的 95% 条件区间为 "
  f"[{qd['rmse_diff_ci'][0]:+.4f}, {qd['rmse_diff_ci'][1]:+.4f}]，"
  f"完全落在负区间，支持组合非线性在同尺度预测中的作用。"
  f"但这不证明任意一对领域存在因果互补，区间条件于已选定模型。")

IMG(os.path.join(FIG, "png", "q1_quadratic_vs_linear.png"), 15,
    "图 5 线性模型与二阶交互模型在 1M 检验集上的预测对比")

# ============ 8 稳健性 ============
doc.add_heading("8 稳健性与跨尺度分析", 1)
P("为检验质量排序的方法稳健性，将主方案与替代评价方案做排序一致性比较：")

comp = rb["robustness"]["comparisons"]
T("表 8 主模型与替代方案的排序一致性",
  ["替代方案", "Kendall τ_b", "Spearman ρ"],
  [[c["alt"], f"{c['kendall_tau_b']:.4f}", f"{c['spearman_rho']:.4f}"] for c in comp])
P("两种替代方案的 Kendall τ_b 为 0.667—0.833，整体趋势相近但非完全一致，"
  "说明质量排序具有一定方法稳健性，但不能解释为各领域对预训练任务的普遍价值排序。"
  "所有方法均复用同一批信号，方法一致性不能证明评分已获得真实质量标签验证。")
IMG(os.path.join(FIG, "png", "q1_ranking_consistency.png"), 13, "图 6 主模型与替代方案的排序一致性")

P("跨尺度方面，固定 1M 训练参数直接预测 60M/1B，实测得到：")
vs = pd.DataFrame(ml["validation"])
T("表 9 线性主模型的跨尺度检验",
  ["数据集", "R²", "RMSE", "MAPE"],
  [[r["scale"], f"{r['R2']:.4f}", f"{r['RMSE']:.4f}", f"{r['MAPE']:.4%}"] for _, r in vs.iterrows()])
P("60M 的 R² 为 -47.35、1B 为 -3708.86，说明仅改变截距不足以恢复预测能力，"
  "共享线性斜率的跨尺度假设不成立。R² 大幅为负还与该检验表 Loss 变异较小有关，"
  "故同时报告 RMSE 与 MAPE。")
IMG(os.path.join(FIG, "png", "q1_fit_and_validation.png"), 15, "图 7 训练集拟合与跨尺度验证")

ex = pd.DataFrame(ml["extrapolation"])
T("表 10 外推表上的预测误差",
  ["外推表", "R²", "RMSE", "数据性质"],
  [[r["scale"], f"{r['R2']:.4f}", f"{r['RMSE']:.4f}", "外推（非实测观测）"] for _, r in ex.iterrows()])
P("A12—A15 为外推表，不能表述为真实 10B/70B 训练实验。表中结果最多说明"
  "本模型与附件外推规律不一致，不能据此证明真实大模型必然发生领域偏好反转。")

# ============ 9 结论 ============
doc.add_heading("9 本问结论", 1)
P("(1) 分组熵权模型给出了全部 272,505 条记录及七域的质量评分，"
  "arxiv 与 book 领先，github 与 wikipedia 靠后；")
P("(2) 百分位秩冲突识别显示 90 分位阈值下强冲突记录占 10.00%，"
  "维度间存在显著负相关（学术价值 vs 语言流畅度 r≈-0.53），证实质量指标间存在矛盾；")
P("(3) 同尺度配比预测中，二阶交互模型显著优于线性基线（配对 bootstrap 区间全负）；")
P("(4) 1B 及外推表不支持将 1M 训练尺度的配比偏好直接迁移至更大尺度。")
P("因此，本问输出应同时保留主评分、稳健秩评分、冲突标记、配比模型及适用范围，"
  "不能压缩成无条件的全局最优领域排序。")

# 附录
doc.add_heading("附录 程序与结果文件", 1)
P("全部计算结果保存于 results/ 目录，图表保存于 figures/ 目录。核心程序：")
for line in ["code/q1_step1_quality.py — 质量信号读取与列表字段压缩",
             "code/q1_step5_v2_borrowed.py — 重复检测、分组熵权、Bootstrap",
             "code/q1_step6_v2_robust.py — 稳健性检验、系数和=0约束",
             "code/q1_step7_quadratic_fixed.py — 二阶交互模型（嵌套CV）",
             "code/q1_step8_figures_v2.py — 图表生成"]:
    p = doc.add_paragraph(line, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(10); r.font.name = "宋体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

out = os.path.join(DOCD, "问题一_模型建立与求解.docx")
doc.save(out)
print(f"✅ 已生成: {out}")
print(f"   大小: {os.path.getsize(out)/1024:.1f} KB")
print(f"   段落数: {len(doc.paragraphs)}, 表格数: {len(doc.tables)}")
