#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建《问题三 模型建立与求解》Word 文档（含四项补齐）"""
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
op = L("q3_optimization.json"); ss = L("q3_structural_shift.json")
lx = L("q3_Lctx_sensitivity.json"); kk = L("q3_kkt_analysis.json")
ac = L("q3_active_constraint.json"); gv = L("q3_grid_verification.json")
fl = L("q3_flatness.json"); pe = L("q3_pelt_changepoint.json")
ps = L("q3_param_sensitivity.json"); kf = L("q3_kkt_full.json")

doc = Document()
st = doc.styles["Normal"]; st.font.name = "宋体"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
for i in range(1, 4):
    h = doc.styles[f"Heading {i}"]
    h.font.name = "黑体"; h.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    h.font.color.rgb = RGBColor(0, 0, 0)


def P(t, bold=False, size=10.5, align=None, indent=True):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = bold; r.font.size = Pt(size)
    r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if align: p.alignment = align
    if indent: p.paragraph_format.first_line_indent = Pt(21)
    p.paragraph_format.space_after = Pt(6)


def T(cap, headers, rows):
    P(cap, bold=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
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
            q = doc.add_paragraph(); r = q.add_run(cap); r.font.size = Pt(9); r.italic = True
            r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            q.alignment = WD_ALIGN_PARAGRAPH.CENTER


# ===== 标题 =====
t = doc.add_heading("问题三 模型建立与求解", 0); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
s = doc.add_paragraph(); r = s.add_run("—— 算力约束下的多维资源联合优化与结构性转移")
r.font.size = Pt(12); r.italic = True
r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
s.alignment = WD_ALIGN_PARAGRAPH.CENTER

P("本问在总算力预算约束下，联合优化参数量 N、数据量 D 与数据质量 Q，"
  "并考察预算跨量级时最优策略是否发生结构性转移。目标函数直接采用问题二建立的"
  "广义标度律（加性模型），成本函数严格依据题面与附录 B。"
  "上下文长度 L_ctx 依题面要求作为外生变量，其可行取值取自附件 C7，"
  "并解析求出注意力与训练开销相等的临界值。")

# ===== 1 优化模型 =====
doc.add_heading("1 优化模型的建立", 1)
doc.add_heading("1.1 目标函数", 2)
P("目标函数采用问题二 AIC 选优的广义标度律（加性形式，R² = 0.9727）：")
P("    min  L(N,D,Q) = E + A/N^α + B/D^β + C·(1−Q)^δ",
  align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
lp = op["model"]["loss_params"]
P(f"其中参数为问题二的拟合结果：E = {lp['E']:.5f}，A = {lp['A']:.4f}，α = {lp['alpha']:.5f}，"
  f"B = {lp['B']:.4f}，β = {lp['beta']:.5f}，C = {lp['C']:.5f}，δ = {lp['delta']:.5f}。")
lp2 = fl["final_recommended"]

doc.add_heading("1.2 约束条件", 2)
T("表 1 算力开销的三个组成部分",
  ["开销项", "公式", "说明"],
  [["基础训练", "C_train = 6ND", "Chinchilla 近似"],
   ["质量提升", "C_Q = D·[g(Q) − g(Q₀)]⁺", "增量成本形式"],
   ["长文本注意力", "C_attn = η·N·D·L_ctx", "η = 2×10⁻⁴"]])
P("总约束为 C_train + C_Q + C_attn ≤ C，且 N,D > 0，Q ∈ (Q₀, 1]。"
  "基线质量取 Q₀ = 0.5。")

doc.add_heading("1.3 质量成本函数（附录 B）", 2)
T("表 2 三类质量成本函数及其参数",
  ["类型", "形式", "γ", "λ"],
  [["指数型", "g(Q) = γ·e^(λQ)", "1×10⁷", "6.0"],
   ["幂函数型", "g(Q) = γ·Q^λ", "5×10⁹", "4.0"],
   ["对数渐进型", "g(Q) = γ·ln(1+λQ)", "2×10⁹", "10.0"]])
P("本问以幂函数型为主成本函数，并在第 6 节对三种函数做完整对比。")

# ===== 2 求解 =====
doc.add_heading("2 最优资源配置求解", 1)
doc.add_heading("2.1 求解方法", 2)
P("采用两种互相独立的方法求解并交叉验证：(1) SLSQP 序列二次规划，"
  "在对数尺度上以多起点随机初始化（每档预算 100 个起点）；"
  "(2) 对数网格穷举，在 (log N, log D, Q) 三维上做 260×260×60 的网格搜索。")

doc.add_heading("2.2 求解结果与平坦性发现", 2)
P("交叉验证发现一个重要现象：两种方法给出的 Loss 仅相差 0.002%–0.05%，"
  "但对应的 N、D 数值相差数倍。经诊断，原因是")
P("Loss 曲面在最优解附近【极度平坦】，存在多重近最优解。", bold=True)
cr = fl["final_recommended"]["中(1e22)"]["flatness"]
P(f"以中预算为例，在最优解处做局部扰动：N 变化 ±5% 时 Loss 变化仅 "
  f"{abs(cr['perturb'][-1]['delta_loss']):.2e} 量级；"
  f"对数尺度曲率 ∂²L/∂(lnN)² = {cr['curv_lnN']:.3e}，∂²L/∂(lnD)² = {cr['curv_lnD']:.3e}，"
  f"均接近零。这说明 Loss 对 N、D 的局部配置不敏感。")

T("表 3 三种求解方法的结果对比（L_ctx = 8192）",
  ["预算", "方法", "N* (B)", "D* (B)", "Loss*", "预算利用率"],
  [[k, "SLSQP", f"{gv['results'][k]['slsqp']['N']/1e9:.4f}",
    f"{gv['results'][k]['slsqp']['D']/1e9:.3f}",
    f"{gv['results'][k]['slsqp']['loss']:.6f}", "—"] for k in ["低(1e19)", "中(1e22)", "高(1e24)"]] +
  [[k, "网格穷举", f"{gv['results'][k]['grid_refined']['N']/1e9:.4f}",
    f"{gv['results'][k]['grid_refined']['D']/1e9:.3f}",
    f"{gv['results'][k]['grid_refined']['loss']:.6f}", "—"] for k in ["低(1e19)", "中(1e22)", "高(1e24)"]] +
  [[k, "精修(推荐)", f"{fl['final_recommended'][k]['refined']['N']/1e9:.4f}",
    f"{fl['final_recommended'][k]['refined']['D']/1e9:.3f}",
    f"{fl['final_recommended'][k]['refined']['loss']:.6f}",
    f"{fl['final_recommended'][k]['refined']['utilization']:.4f}"]
   for k in ["低(1e19)", "中(1e22)", "高(1e24)"]])

P("据此确立选取准则：由于 Loss 在平坦区内差异可忽略，"
  "应以【吃满预算预算利用率最高】为最终配置准则。推荐解如下：", bold=True)
T("表 4 最终推荐配置（网格初值 + SLSQP 精修）",
  ["预算", "N* (B)", "D* (B)", "Q*", "Loss*", "预算利用率", "D*/N*"],
  [[k.replace("(", "\n("), f"{fl['final_recommended'][k]['refined']['N']/1e9:.4f}",
    f"{fl['final_recommended'][k]['refined']['D']/1e9:.3f}",
    f"{fl['final_recommended'][k]['refined']['Q']:.4f}",
    f"{fl['final_recommended'][k]['refined']['loss']:.6f}",
    f"{fl['final_recommended'][k]['refined']['utilization']:.6f}",
    f"{fl['final_recommended'][k]['refined']['r_DN']:.3f}"]
   for k in ["低(1e19)", "中(1e22)", "高(1e24)"]])

P("特别需要指出：修正后的最优 D*/N* 约为 6.5，而非经典 Chinchilla 的 20。"
  "其根本原因是本问采用的广义标度律中 α = 0.283 与 β = 0.300 几乎相等，"
  "当 α ≈ β 时，使 A/N^α + B/D^β 最小的 N 与 D 应处于相近量级，"
  "而非 20:1。SLSQP 单跑时因平坦性收敛到「守 20:1 但浪费约 3% 预算」的局部解，"
  "经网格穷举与 KKT 解析共同修正后确认 D*/N* ≈ 6.5。")
IMG("q3_solver_verification.png", 16, "图 1 三种求解方法对比与 D*/N* 的修正")

# ===== 3 KKT =====
doc.add_heading("3 KKT 解析条件", 1)
doc.add_heading("3.1 三方向一阶条件", 2)
P("构造拉格朗日函数 Λ = L(N,D,Q) + λ[C_tot(N,D,Q) − C]，三方向一阶必要条件为：")
T("表 5 三方向 KKT 条件",
  ["方向", "条件", "物理含义"],
  [["N", "A·α·N^(−α−1) = λ·D·(6 + ηL)", "参数的边际收益 = λ × 参数的边际成本"],
   ["D", "B·β·D^(−β−1) = λ·[6N + (g(Q)−g(Q₀)) + ηNL]", "数据的边际收益 = λ × 数据的边际成本"],
   ["Q", "C·δ·(1−Q)^(δ−1) = λ·D·g'(Q)", "质量的边际收益 = λ × 质量的边际成本"]])
P("三式的经济学含义是：在最优解处，N、D、Q 三个方向【每单位算力投入所换取的"
  "Loss 下降量（即影子价格的倒数）必须完全相等】，否则总可通过调整配置进一步降低 Loss。")

doc.add_heading("3.2 Q 方向：Q*→1 的解析证明", 2)
P(f"在条件 K3 中，左边 C·δ·(1−Q)^(δ−1) 的指数 δ−1 = {kk['kkt_conclusion']['delta']-1:.5f} < 0，"
  f"故当 Q→1 时 (1−Q)^(δ−1) → +∞，左边发散；"
  f"而右边 λ·D·g'(Q) 对三类成本函数均取有限值。"
  f"要使等式成立必须 λ → 0，即预算约束在质量维度上的影子价格趋于零。"
  f"⟹ Q* 必然取上界（Q_max = 1）。")
P("这说明 Q*→1 是真实的数学最优，而非求解器陷入边界。"
  "但该结论源于 δ<1 使边际收益发散，现实中数据质量无法达到理论完美，"
  "故引入质量上界 Q_max < 1 做敏感性分析：")
qm = kk["qmax_sensitivity"]
T("表 6 质量上界 Q_max 对最优 Loss 的影响",
  ["Q_max", "低预算 Loss", "中预算 Loss", "高预算 Loss"],
  [[q, f"{qm[q]['低']['loss']:.4f}", f"{qm[q]['中']['loss']:.4f}",
    f"{qm[q]['高']['loss']:.4f}"]
   for q in sorted(qm, key=lambda x: -float(x.split("=")[1]))])
P("质量上界从 1.0 降到 0.7，最优 Loss 上升约 0.11（约 7%），"
  "说明高质量数据对最终性能具有决定性影响。")

doc.add_heading("3.3 数值验证", 2)
P("在最终推荐解处事实验证：N、D 两个方向的单位算力边际收益高度一致：")
nv = kf["numerical_verification"]
T("表 7 最优解处各方向的单位算力边际收益（应相等）",
  ["预算", "λ_eff(N)", "λ_eff(D)", "相对差"],
  [[k.replace("(1e", " (10^").replace(")", ")"),
    f"{nv[k]['lambda_N_eff']:.4e}", f"{nv[k]['lambda_D_eff']:.4e}",
    f"{abs(nv[k]['lambda_N_eff']-nv[k]['lambda_D_eff'])/max(nv[k]['lambda_N_eff'],nv[k]['lambda_D_eff'])*100:.3f}%"]
   for k in nv])
P("三档预算下两方向的相对差均低于 2.2%，KKT 条件得到数值验证。")

# ===== 4 结构性转移 =====
doc.add_heading("4 结构性转移的数学定义与识别", 1)
doc.add_heading("4.1 数学定义", 2)
P("设最优解映射为 x*(C) = (N*(C), D*(C), Q*(C))。定义三个结构指标：")
P("(i) 结构指标向量 θ(C) = (ln N*(C), ln D*(C), Q*(C))；", indent=False)
P("(ii) 成本占比向量 s(C) = (s_train, s_Q, s_attn)，各分量和为 1；", indent=False)
P("(iii) 活跃约束集 A(C) = (预算约束是否紧, 主导成本成分, 占比>50%的成分集合)。", indent=False)
P("若存在预算 C* 使得 θ(C) 的一阶导数在 C* 处不连续，"
  "或者主导成分 argmax s(C) 发生切换，或者活跃集 A(C) 发生跃迁，"
  "则称在 C* 处发生结构性转移。")

doc.add_heading("4.2 五种识别方法", 2)
P("M1 主导成分切换法：监测 argmax(s_train, s_Q, s_attn) 的变化点；")
P("M2 弹性突变法：计算规模弹性 κ_N = d ln N*/d ln C 与 κ_D = d ln D*/d ln C 的突变；")
P("M3 配比不变式检验：考察 D*/N* 是否发生定性变化；")
P("M4 活跃约束集合跃迁法：监测 A(C) = (是否紧, 主导成分, >50%成分集) 的跃迁；")
P("M5 PELT 变点检测法：对份额向量、标度指数等时间序列做 PELT 统计变点检测"
  "（使用 ruptures 库，l2 与 rbf 代价模型交叉验证）。")

doc.add_heading("4.3 识别结果", 2)
P("对预算 10^17.5–10^25.5 共 81 个点做扫描（L_ctx = 8192），各方法结果如下：")
T("表 8 主导成本成分的切换点（M1）",
  ["预算 log10C", "预算 C", "主导成分", "训练%", "质量%", "注意力%"],
  [[f"{c['logC']:.1f}", f"{c['C']:.2e}", c['dominant'].replace("share_", ""),
    f"{c['shares']['train']*100:.1f}", f"{c['shares']['Q']*100:.1f}",
    f"{c['shares']['attn']*100:.1f}"] for c in ss["M1_dominant_changes"]])

T("表 9 PELT 变点检测结果（M5）",
  ["信号", "l2 代价模型变点", "rbf 代价模型变点"],
  [[k.split("|")[0], str(pe["pelt_changepoints"].get(k + "|l2", "—")),
    str(pe["pelt_changepoints"].get(k + "|rbf", "—"))]
   for k in ["份额向量 s(C)", "标度指数 κ_N", "log N*", "log D*", "log(D/N)"]])

P(f"结论：PELT 变点检测（M5）检出的最强变点位于 log10C = "
  f"{pe['main_changepoint_logC']:.1f}（出现频次最高），对应 C* ≈ "
  f"{pe['main_changepoint_C']:.2e} FLOPs；M1 与 M4 独立识别出同一位置的跃迁（log10C ≈ 20.33）；"
  f"三种方法互相印证。")
P(f"进一步的定量边界：质量占比跌破 50% 于 log10C = "
  f"{ac['threshold_crossings']['quality_over_50_at_logC']:.3f}，"
  f"训练占比升破 50% 于 log10C = {ac['threshold_crossings']['train_over_50_at_logC']:.3f}，"
  f"即转移在预算 1.2×10²⁰ 至 2.9×10²⁰ FLOPs 的窄区间内完成。")
P("转移的本质是成本结构主导权的更替：低预算区资金几乎全部用于提升数据质量"
  "（10¹⁸ 处质量开销占 98.3%），高预算区资金转向模型与数据规模扩张"
  "（10²⁴ 处训练开销占 77.9%）。值得注意的是，修正后的 D*/N* 在转移点前后"
  "均为缓慢变化而非突变，说明【转移体现在钱的花法而非规模比例】。")
IMG("q3_cost_structure.png", 16, "图 2 成本结构演进与结构性转移")
IMG("q3_pelt_changepoint.png", 15, "图 3 PELT 变点检测与 D*/N* 演化")

# ===== 5 L_ctx =====
doc.add_heading("5 上下文长度的敏感性分析", 1)
P("令注意力开销与训练开销相当：")
P("    6ND = η·N·D·L_ctx   ⟹   L_ctx^crit = 6/η = 6/(2×10⁻⁴) = 30000",
  align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
P(f"附件 C7 中 max_position_embeddings 的取值集合为 {lx['C7_feasible_values']}，"
  f"恰好覆盖临界值 30000 的两侧。")
T("表 10 注意力与训练开销之比随上下文长度的变化",
  ["L_ctx", "C_attn/C_train = L/30000", "判定"],
  [[r["L"], f"{r['ratio_attn_train']:.4f}",
    "注意力 > 训练" if r["ratio_attn_train"] > 1 else "训练 > 注意力"]
   for r in lx["attention_over_train_ratio"]])
rows = []
for bn in ["低(1e19)", "中(1e22)", "高(1e24)"]:
    for Lv in lx["C7_feasible_values"]:
        v = lx["opt_by_budget_and_L"][bn].get(str(Lv))
        if v:
            rows.append([bn, Lv, f"{v['N']/1e9:.4f}", f"{v['D']/1e9:.2f}",
                         f"{v['Q']:.4f}", f"{v['loss']:.4f}",
                         f"{v['share_attn']*100:.2f}"])
T("表 11 不同上下文长度下的最优配置",
  ["预算", "L_ctx", "N* (B)", "D* (B)", "Q*", "Loss*", "注意力占比%"], rows)
P("在 10²² 预算档，L_ctx 从 2048 增至 131072 时，注意力占比从 5.9% 飙升到 78.4%，"
  "最优参数量被压缩。由于 L_ctx 由架构外生给定，实际决策含义是："
  "【当训练目标需要长上下文时，应预期可用训练算力被大幅挤占，需相应下调模型规模】。")
IMG("q3_Lctx_sensitivity.png", 16, "图 4 上下文长度对成本结构与最优配置的影响")

# ===== 6 成本函数 =====
doc.add_heading("6 成本函数与参数敏感性分析", 1)
doc.add_heading("6.1 三类质量成本函数对比", 2)
cc = op["cost_function_comparison"]
rows = []
for k in sorted(cc):
    v = cc[k]
    rows.append([k] + [f"N={v[b]['N']/1e9:.3f}B, D={v[b]['D']/1e9:.1f}B"
                       if v.get(b) else "—" for b in ["低", "中", "高"]])
T("表 12 不同质量成本函数下的最优配置（L_ctx = 8192）",
  ["成本函数 / Q₀", "低预算", "中预算", "高预算"], rows)
P("中、高预算档三种成本函数给出几乎相同的最优配置，说明预算充裕时结论稳健；"
  "低预算档出现可见差异，说明预算越紧张，质量成本函数的选择越关键——"
  "这与结构性转移的结论一致（低预算区正是质量开销主导的区间）。")

doc.add_heading("6.2 标度律参数扰动敏感性", 2)
P("对问题二广义标度律的 7 个参数分别做 ±20% 的单因素扰动，并做 200 次"
  "蒙特卡洛联合扰动（各参数独立均匀 ±20%）：")
sf = ps["single_factor_pm20pct"]
T("表 13 单因素参数扰动 ±20% 对最优解的影响",
  ["参数", "扰动", "N* (B)", "D* (B)", "ΔLoss%", "D*/N*"],
  [[k.replace("-20%", "-20%").replace("+20%", "+20%"), "",
    f"{v['N']/1e9:.4f}", f"{v['D']/1e9:.3f}", f"{v['delta_loss_pct']:+.4f}",
    f"{v['r_DN']:.3f}"]
   for k, v in sorted(sf.items(), key=lambda x: (x[0][:-4], x[0][-4:]))]
  if False else
  [[k[:-4], k[-4:], f"{v['N']/1e9:.4f}", f"{v['D']/1e9:.3f}",
    f"{v['delta_loss_pct']:+.4f}", f"{v['r_DN']:.3f}"]
   for k, v in sorted(sf.items(), key=lambda x: (x[0][:-4], x[0][-4:]))])
mc = ps["monte_carlo"]
T("表 14 蒙特卡洛联合扰动下的稳定性（200 次）",
  ["量", "均值", "标准差", "变异系数 CV"],
  [["N", f"{mc['stats']['N']['mean']/1e9:.4f}B", f"{mc['stats']['N']['std']/1e9:.4f}B",
    f"{mc['stats']['N']['cv_pct']:.4f}%"],
   ["D", f"{mc['stats']['D']['mean']/1e9:.3f}B", f"{mc['stats']['D']['std']/1e9:.3f}B",
    f"{mc['stats']['D']['cv_pct']:.4f}%"],
   ["D*/N*", f"{mc['stats']['r_DN']['mean']:.4f}", f"{mc['stats']['r_DN']['std']:.4f}",
    f"{mc['stats']['r_DN']['cv_pct']:.4f}%"],
   ["Q*", f"{mc['stats']['Q']['mean']:.4f}", f"{mc['stats']['Q']['std']:.4f}",
    f"{mc['stats']['Q']['cv_pct']:.4f}%"],
   ["Loss*", f"{mc['stats']['loss']['mean']:.4f}", f"{mc['stats']['loss']['std']:.4f}",
    f"{mc['stats']['loss']['cv_pct']:.4f}%"]])
P(f"敏感性分析的两点关键结论：(1) E（不可约损失）是唯一主导参数，"
  f"其 ±20% 扰动使最优 Loss 同幅变化 ±20%，而 A、B、α、β 的扰动影响均在 0.2% 以内，"
  f"C 与 δ 的扰动几乎无影响（因 Q 已饱和于上界，质量项被旁路）；"
  f"(2) 在 200 次联合扰动下，Q* 取上界的比例高达 "
  f"{mc['q_at_upper_pct']:.1f}%，D*/N* 的变异系数仅 {mc['stats']['r_DN']['cv_pct']:.2f}%，"
  f"说明核心结论对参数不确定性高度稳健。")
P(f"结构性转移点的稳健性：在 30 次参数扰动试验中，转移点 log10C 的均值为 "
  f"{ps['changepoint_robustness']['logC_mean']:.3f}，标准差 "
  f"{ps['changepoint_robustness']['logC_std']:.3f}，即 C* ≈ "
  f"{10**ps['changepoint_robustness']['logC_mean']:.2e} FLOPs，与基准结论一致。")
IMG("q3_param_sensitivity.png", 16, "图 5 参数敏感性分析与蒙特卡洛稳健性")

# ===== 7 结论 =====
doc.add_heading("7 本问结论", 1)
P("(1) 建立了以问题二广义标度律为目标、以三部分算力开销为约束的联合优化模型，"
  "并用 SLSQP 与对数网格穷举两种独立方法交叉验证求解；")
P("(2) 发现 Loss 曲面在最优解附近极度平坦，据此确立「吃满预算」的配置准则，"
  "并修正了最优 D*/N*（由 Chinchilla 的 20 修正为约 6.5，原因是 α ≈ β）；")
P("(3) 给出三方向完整 KKT 解析条件并数值验证（两方向边际收益相对差 < 2.2%）；"
  "解析证明 Q*→1 是 δ<1 导致边际收益发散的真实最优；")
P(f"(4) 解析求出临界上下文长度 L_ctx^crit = 6/η = 30000，并在 C7 全部可行取值上"
  f"完成敏感性分析；")
P(f"(5) 用 PELT 变点检测、主导成分切换、活跃约束集跃迁三种独立方法共同确认"
  f"结构性转移点 C* ≈ 10²⁰ FLOPs；")
P("(6) 参数扰动敏感性表明 E 为主导参数，而核心结论（Q*→1、D*/N*≈6.5、"
  "转移点 C*）对 ±20% 参数扰动高度稳健。")

doc.add_heading("附录 程序与结果文件", 1)
for line in ["code/q3_step1_optimize.py — 联合优化主求解与成本函数对比",
             "code/q3_step2_kkt.py — Q 方向 KKT 与质量上界敏感性",
             "code/q3_step3_structural.py — 结构性转移定义与 M1/M2/M3",
             "code/q3_step3b_active.py — M4 活跃约束集合跃迁",
             "code/q3_step4_Lctx.py — 上下文长度临界值与敏感性",
             "code/q3_step6_gridverify.py — 对数网格穷举交叉验证",
             "code/q3_step6b_flatness.py — Loss 曲面平坦性诊断与真全局最优",
             "code/q3_step7_kkt_full.py — 三方向完整 KKT 解析",
             "code/q3_step8_pelt.py — PELT 变点检测（81 点扫描）",
             "code/q3_step9_param_sens.py — 标度律参数扰动敏感性",
             "code/q3_step10_figures2.py — 补充图表"]:
    p = doc.add_paragraph(line, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(9.5); r.font.name = "宋体"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

out = os.path.join(DOCD, "问题三_模型建立与求解.docx")
doc.save(out)
print(f"✅ {out}  ({os.path.getsize(out)/1024:.1f} KB)")
print(f"   段落 {len(doc.paragraphs)}, 表格 {len(doc.tables)}, 图片 {len(doc.inline_shapes)}")
