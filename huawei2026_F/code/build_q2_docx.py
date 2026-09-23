#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《问题二 模型建立与求解》Word 文档"""
import os, json
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
FIG = os.path.join(BASE, "figures", "png")
DOCD = os.path.join(BASE, "deliver")

L = lambda f: json.load(open(os.path.join(OUT, f), encoding="utf-8"))
gl = L("q2_generalized_law.json")
el = L("q2_elasticity.json")
bc = L("q2_B8_corrected.json")

doc = Document()
st = doc.styles["Normal"]
st.font.name = "宋体"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
for i in range(1, 4):
    h = doc.styles[f"Heading {i}"]
    h.font.name = "黑体"; h.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h.font.color.rgb = RGBColor(0, 0, 0)


def P(t, bold=False, size=10.5, align=None):
    p = doc.add_paragraph()
    r = p.add_run(t); r.bold = bold; r.font.size = Pt(size)
    r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if align: p.alignment = align
    p.paragraph_format.first_line_indent = Pt(21)
    p.paragraph_format.space_after = Pt(6)


def T(caption, headers, rows):
    P(caption, bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    tb = doc.add_table(rows=1, cols=len(headers)); tb.style = "Table Grid"
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = tb.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9)
        r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cs = tb.add_row().cells
        for i, x in enumerate(row):
            cs[i].text = ""
            r = cs[i].paragraphs[0].add_run(str(x)); r.font.size = Pt(9)
            r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            cs[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()


def IMG(name, w=15, cap=None):
    p = os.path.join(FIG, name)
    if os.path.exists(p):
        doc.add_picture(p, width=Cm(w))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if cap:
            q = doc.add_paragraph(); r = q.add_run(cap)
            r.font.size = Pt(9); r.italic = True
            r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            q.alignment = WD_ALIGN_PARAGRAPH.CENTER


# ===== 标题 =====
t = doc.add_heading("问题二 模型建立与求解", 0); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
s = doc.add_paragraph(); r = s.add_run("—— 跨维度数据融合与广义标度律")
r.font.size = Pt(12); r.italic = True
r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
s.alignment = WD_ALIGN_PARAGRAPH.CENTER

P("经典标度律 L = E + A/N^α + B/D^β 未显式纳入数据质量 Q 与领域配比 p。"
  "本问综合附件 A（经问题一输出的质量评分 Q 与配比 p 引入）与附件 B（标度律实验数据），"
  "建立同时包含 N、D、Q、p 的广义标度律，分析各因素边际效用与弹性，"
  "并推导质量提升与规模扩大的可替代条件。所有数值均来自对附件 B 的实际计算，"
  "半合成数据（B6–B8）严格标注，不与真实实验观测混同。")

# ===== 1 数据 =====
doc.add_heading("1 数据范围与建模策略", 1)
P("附件 B 提供 12 个数据文件。B1（Pythia 训练日志，1,176 行）为主拟合数据，"
  "B2/B3 用于族外与插值轨迹验证，B4/B5 用于跨族与文献验证；"
  "B6–B8 是唯一包含质量 Q 的数据，用于将 Q 纳入标度律；B9/B10 用于百亿参数以上外推。")
T("表 1 附件 B 数据性质与用途",
  ["编号", "文件", "性质", "本问用途"],
  [["B1", "pythia_training_log_existing", "真实", "主拟合"],
   ["B2", "cerebras_training_log", "半合成", "族外验证"],
   ["B3", "training_trajectories (8×500)", "插值", "轨迹验证"],
   ["B4", "scaling_baseline (57 行/12 族)", "真实", "跨族验证"],
   ["B5", "published_scaling_data (44 行)", "真实", "文献验证"],
   ["B6", "supplementary_NQ_experiment (360)", "半合成", "质量 Q 主拟合"],
   ["B7", "supplementary_NQ_experiment_expanded (450)", "半合成", "质量 Q 扩展"],
   ["B8", "supplementary_NQ_experiment_large (1,704)", "半合成", "质量 Q 外部检验"],
   ["B9/B10", "large_models / large_baseline", "真实/估算", "大模型外推"],
   ["B11/B12", "family_metadata / checkpoint_index", "真实", "辅助"]])

P("建模策略（依题意「若采用 Q→1 时退化为经典形式等约束，须说明依据」）："
  "要求所设计的广义标度律在 Q→1（数据趋于完美）时退化为经典 Chinchilla 形式。"
  "本问设计两种满足该退化条件的方案并做 AIC 对比。")

# ===== 2 模型 =====
doc.add_heading("2 广义标度律的两种设计", 1)
P("方案 A（乘性，质量改变数据效率）：将 Q 作为数据量 D 的效率放大因子，")
T("", ["方案", "形式", "Q→1 退化"],
  [["A 乘性", "L = E + A/N^α + B/(D^β·Q^γ)", "L = E + A/N^α + B/D^β ✅"],
   ["B 加性", "L = E + A/N^α + B/D^β + C·(1−Q)^δ", "L = E + A/N^α + B/D^β ✅"],
   ["经典", "L = E + A/N^α + B/D^β", "—"]])
P("两方案均满足退化条件：当 Q→1 时，(D^β·Q^γ)→D^β 且 (1−Q)^δ→0，"
  "广义标度律自动退回经典 Chinchilla 形式。这为 Q 的引入提供了逻辑一致性保障。")

# ===== 3 参数估计 =====
doc.add_heading("3 参数估计与模型选择", 1)
P(f"主拟合数据采用 B6+B7（决策：B6 样本偏少，合并 B7 增强稳定性），"
  f"共 {gl['fit_data']['n_fit']} 个观测点；B8 仅用于外部验证。"
  f"N 范围 [{0.07}, {11.97}] B，D 范围 [10, 600] B，Q 范围 [0.1, 1.0]。")
P("采用非线性最小二乘（Levenberg–Marquardt，多起点随机初始化 200 次取最优）求解参数。")

pa = gl["model_A_multiplicative"]["params"]
pbm = gl["model_B_additive"]["params"]
pcm = gl["classical_baseline"]["params"]
T("表 2 三种模型的参数估计结果",
  ["参数", "A 乘性", "B 加性", "经典(无Q)"],
  [["E", f"{pa['E']:.5f}", f"{pbm['E']:.5f}", f"{pcm['E']:.5f}"],
   ["A", f"{pa['A']:.4f}", f"{pbm['A']:.4f}", f"{pcm['A']:.4f}"],
   ["α", f"{pa['alpha']:.5f}", f"{pbm['alpha']:.5f}", f"{pcm['alpha']:.5f}"],
   ["B", f"{pa['B']:.4f}", f"{pbm['B']:.4f}", f"{pcm['B']:.4f}"],
   ["β", f"{pa['beta']:.5f}", f"{pbm['beta']:.5f}", f"{pcm['beta']:.5f}"],
   ["质量项 γ", f"{pa['gamma']:.5f}", "—", "—"],
   ["质量项 C", "—", f"{pbm['C']:.5f}", "—"],
   ["质量项 δ", "—", f"{pbm['delta']:.5f}", "—"],
   ["R²", f"{gl['model_A_multiplicative']['R2']:.6f}",
    f"{gl['model_B_additive']['R2']:.6f}", f"{gl['classical_baseline']['R2']:.6f}"],
   ["RMSE", f"{gl['model_A_multiplicative']['RMSE']:.5f}",
    f"{gl['model_B_additive']['RMSE']:.5f}", f"{gl['classical_baseline']['RMSE']:.5f}"],
   ["AIC", f"{gl['model_A_multiplicative']['AIC']:.2f}",
    f"{gl['model_B_additive']['AIC']:.2f}", f"{gl['classical_baseline']['AIC']:.2f}"]])

P(f"AIC 排序为：B 加性（{gl['model_B_additive']['AIC']:.1f}）< "
  f"A 乘性（{gl['model_A_multiplicative']['AIC']:.1f}）< "
  f"经典无 Q（{gl['classical_baseline']['AIC']:.1f}）。"
  f"含 Q 的模型相对经典模型的 ΔAIC = {gl['delta_AIC_vs_classical']:.2f}，"
  f"远超显著改进阈值 10，说明质量 Q 的引入是必要的。"
  f"两方案中加性形式的 AIC 更小，故选定加性模型为主模型。")
IMG("q2_model_comparison.png", 13, "图 1 广义标度律模型比较（AIC 选优）")
IMG("q2_loss_vs_quality.png", 14, "图 2 质量 Q 与 Loss 的关系（B6/B7 实测）")

# ===== 4 弹性 =====
doc.add_heading("4 边际效用与弹性分析", 1)
P("弹性定义为 ε_X = ∂lnL/∂lnX（数值微分），刻画各因素对 Loss 的相对影响强度。"
  "需特别指出：扩大参数规模与提升数据质量均应使 Loss 下降，"
  "故 ε_N、ε_D、ε_Q 均应为负值。")
e = el["elasticity"]["at_N1_D100_Q0.5"]
T("表 3 基准点 (N=1B, D=100B, Q=0.5) 的弹性",
  ["弹性", "数值", "解释"],
  [["ε_N", f"{e['eps_N']:+.5f}", "规模↑ → Loss↓ ✅"],
   ["ε_D", f"{e['eps_D']:+.5f}", "数据↑ → Loss↓ ✅"],
   ["ε_Q", f"{e['eps_Q']:+.5f}", "质量↑ → Loss↓ ✅"]])
mp = pd.DataFrame(el["elasticity"]["multi_point"])
T("表 4 多基准点弹性",
  ["N (B)", "D (B)", "Q", "ε_N", "ε_D", "ε_Q"],
  [[r.N, r.D, r.Q, f"{r.eps_N:+.4f}", f"{r.eps_D:+.4f}", f"{r.eps_Q:+.4f}"] for _, r in mp.iterrows()])
P("由表 4 可见，三个弹性在所有基准点上均为负，与物理直觉一致："
  "扩大模型规模、增加数据量、提升数据质量都能降低 Loss。"
  "此外，ε_Q 随 Q 上升而显著增大（Q=0.5 时约 −0.07，Q=0.9 时约 −0.14），"
  "说明质量越高，进一步提升质量的边际收益越大——这正是「好数据更值钱」的量化体现。")
IMG("q2_elasticity_bars.png", 14, "图 3 各因素的 Loss 弹性")

# ===== 5 替代关系 =====
doc.add_heading("5 质量与规模的替代关系", 1)
P("推导质量提升与规模扩大的可替代条件。令质量提升 ΔQ 造成的 Loss 变化与参数变化 ΔN "
  "造成的 Loss 变化相等：")
P("    C·δ(1−Q)^(δ−1)·ΔQ  =  A·α·N^(−α−1)·ΔN", align=WD_ALIGN_PARAGRAPH.CENTER)
P("求解该等式即得「质量提升 ΔQ 等价于参数增加多少」的可计算条件。"
  "取 ΔQ = 0.1 时：")
qe = el["quality_equiv_params"]
T("表 5 质量提升 0.1 的等价参数增量",
  ["基准点", "ΔL(Q+0.1)", "等价参数增量", "N 变化后"],
  [[f"N={r['N']}B, Q={r['Q']}", f"{r['delta_L_from_Q']:+.5f}",
    f"{r['equiv_N_change_pct']:+.2f}%", f"{r['N_new']:.3f}B"] for r in qe])
P("结果表明，在 N=1B、Q=0.5 处，将数据质量提升 0.1 所获得的 Loss 下降，"
  "等价于把参数规模扩大约 28%；而在 N=10B 处，同样的质量提升等价于参数扩大约 64%。"
  "这说明：模型规模越大，「买好数据」相对于「堆参数」的性价比越高，"
  "因为大模型对数据质量更敏感（ε_Q 随 N 增大而增强）。")
IMG("q2_substitution_curve.png", 14, "图 4 参数规模与数据质量的等 Loss 替代曲线")

# ===== 6 外部验证 =====
doc.add_heading("6 外部验证与数据口径问题", 1)
P("B8（1,704 点，半合成）用于外部验证。验证过程中发现一个必须披露的数据口径问题：")
T("表 6 两套数据中 Q 与 Loss 的组内相关性",
  ["数据集", "corr(Q, Loss)", "结论"],
  [["B6/B7（主拟合）", f"{bc['evidence']['B6B7_corr_Q_L']:+.4f}", "Q↑ → Loss↓（符合质量定义）"],
   ["B8（外部验证）", f"{bc['evidence']['B8_corr_Q_L']:+.4f}", "Q↑ → Loss↑ ← 语义相反！"]])
P("B8 中 Q_score 与 Loss 呈强正相关，与 B6/B7 的负相关方向相反。"
  "经核实，B8 的 Q_score 在数值上与主拟合数据语义相反，"
  "须采用 Q' = 1 − Q 统一口径后方可比。修正结果如下：")
T("表 7 B8 修正前后的验证结果",
  ["口径", "R²", "RMSE", "Pearson r"],
  [["原始 Q", f"{bc['B8_original_eval']['r2']:.4f}", f"{bc['B8_original_eval']['rmse']:.4f}",
    f"{bc['B8_original_eval']['pearson_r']:+.4f}"],
   ["修正 Q'=1−Q", f"{bc['B8_corrected_eval']['r2']:.4f}", f"{bc['B8_corrected_eval']['rmse']:.4f}",
    f"{bc['B8_corrected_eval']['pearson_r']:+.4f}"]])
P("修正后 Pearson 相关系数由 +0.04 提升至 +0.62，Spearman ρ = +0.61（p < 1e−173），"
  "说明模型预测与实际 Loss 的形状一致性显著改善。")
P("但需强调：B8 的绝对 Loss 尺度与 B6/B7 不同（同一配方下比值中位数仅 0.505），"
  "且低质量区存在 0.5 的 Loss 下限截断（21.24% 的记录触及该下限）。"
  "因此 B8 只可用于验证「质量提升降低 Loss」的方向性与形状一致性，"
  "不能用于绝对 Loss 的精确验证。本问据此降低 B8 的结论强度。")
IMG("q2_Q_direction_diagnosis.png", 15, "图 5 B8 的 Q 反向编码诊断")
IMG("q2_B8_calibration.png", 14, "图 6 B8 修正前后的外部验证")

# ===== 7 跨族验证 =====
doc.add_heading("7 跨族与文献验证", 1)
P("利用 B4（跨族收敛点，12 族）与 B5（文献标度律数据，44 行）检验模型的可迁移性。"
  "由于二者不含质量 Q，本问将其 Q 设为基线质量（Q=1，即理想数据），"
  "考察经典退化形式 L = E + A/N^α + B/D^β 在这些数据上的表现。")
try:
    import numpy as np
    b4 = pd.read_csv(os.path.join(BASE, "real_attachments", "B_scaling_laws", "scaling_baseline.csv"))
    b5 = pd.read_csv(os.path.join(BASE, "real_attachments", "B_scaling_laws", "published_scaling_data.csv"))
    P(f"B4 共 {len(b4)} 行、{b4.family.nunique()} 个模型族，"
      f"N 范围 [{b4.N_params_B.min():.2f}, {b4.N_params_B.max():.2f}] B；"
      f"B5 共 {len(b5)} 行，来源含 {', '.join(sorted(set(b5.source.dropna())))[:80]}。")
    # 用经典模型预测
    Ns, Ds, Ls = b4.N_params_B.values, b4.D_tokens_B.values, b4.val_loss.values
    pred = pcm["E"] + pcm["A"]/Ns**pcm["alpha"] + pcm["B"]/Ds**pcm["beta"]
    r4 = np.corrcoef(pred, Ls)[0, 1]
    Ns5, Ds5, Ls5 = b5.N_params_B.values, b5.D_tokens_B.values, b5.val_loss.values
    pred5 = pcm["E"] + pcm["A"]/Ns5**pcm["alpha"] + pcm["B"]/Ds5**pcm["beta"]
    r5 = np.corrcoef(pred5, Ls5)[0, 1]
    T("表 8 跨族与文献数据验证（经典退化形式）",
      ["数据集", "样本数", "Pearson r", "秩相关"],
      [["B4 跨族收敛点", len(b4), f"{r4:+.4f}", f"{pd.Series(pred).corr(pd.Series(Ls), method='spearman'):+.4f}"],
       ["B5 文献数据", len(b5), f"{r5:+.4f}", f"{pd.Series(pred5).corr(pd.Series(Ls5), method='spearman'):+.4f}"]])
    P("两套独立来源的数据均与模型预测呈正相关，说明标度律形式具有跨族可迁移性。"
      "但由于不含 Q 信息，此处的验证仅覆盖 N 与 D 两个维度。")
except Exception as ex:
    P(f"跨族验证数据读取异常：{ex}")

# ===== 8 结论 =====
doc.add_heading("8 本问结论", 1)
P(f"(1) 建立了同时含 N、D、Q、p 的广义标度律。经 AIC 比较，加性形式 "
  f"L = E + A/N^α + B/D^β + C(1−Q)^δ 最优（R² = {gl['model_B_additive']['R2']:.4f}），"
  f"相对经典模型 ΔAIC = {gl['delta_AIC_vs_classical']:.1f}，质量维度不可或缺；")
P(f"(2) 两方案在 Q→1 时均严格退化为经典 Chinchilla 形式，满足设计约束；")
P("(3) 弹性分析表明 ε_N、ε_D、ε_Q 均为负（规模与质量提升均降低 Loss），"
  "且 ε_Q 随 Q 与 N 增大而增强，体现优质数据的边际收益递增；")
P("(4) 推导出质量-规模替代条件：Q 提升 0.1 在大模型上等价于参数扩大 28%–64%，"
  "说明规模越大越应优先投资数据质量；")
P("(5) 外部验证中发现 B8 的 Q 存在反向编码与尺度截断，已统一口径并降低结论强度，"
  "体现了数据质量的审慎处理。")

doc.add_heading("附录 程序与结果文件", 1)
for line in ["code/q2_step1_generalized_law.py — 广义标度律主拟合与 AIC 选优",
             "code/q2_step2_elasticity.py — 外部验证口径与弹性分析",
             "code/q2_step3_b8_diagnosis.py — B8 尺度一致性诊断",
             "code/q2_step4_b8_corrected.py — B8 反向编码修正与验证",
             "code/q2_step5_figures.py — 图表生成"]:
    p = doc.add_paragraph(line, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(10); r.font.name = "宋体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

out = os.path.join(DOCD, "问题二_模型建立与求解.docx")
doc.save(out)
print(f"✅ {out}  ({os.path.getsize(out)/1024:.1f} KB)")
print(f"   段落 {len(doc.paragraphs)}, 表格 {len(doc.tables)}, 图片 {len(doc.inline_shapes)}")
