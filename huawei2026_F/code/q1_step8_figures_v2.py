#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F题 问题一 · 图表（v2 借鉴版）"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
FIG = os.path.join(BASE, "figures")
os.makedirs(FIG, exist_ok=True)

for cand in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=cand).get_name()]
        break
plt.rcParams["axes.unicode_minus"] = False

v2 = json.load(open(os.path.join(OUT, "q1_quality_v2.json"), encoding="utf-8"))
rb = json.load(open(os.path.join(OUT, "q1_robustness_v2.json"), encoding="utf-8"))
qd = json.load(open(os.path.join(OUT, "q1_quadratic_v2.json"), encoding="utf-8"))
boot = pd.read_csv(os.path.join(OUT, "q1_bootstrap_ci.csv"))

# 图1：域级质量分 + bootstrap CI（借鉴：带误差棒）
fig, ax = plt.subplots(figsize=(10, 5))
b = boot.dropna(subset=["ci_lo"]).sort_values("S_mean")
y = np.arange(len(b))
ax.barh(y, b["S_mean"], xerr=[b["S_mean"] - b["ci_lo"], b["ci_hi"] - b["S_mean"]],
        color="steelblue", capsize=3, error_kw={"lw": 1, "ecolor": "black"})
ax.set_yticks(y); ax.set_yticklabels(b["domain"])
ax.set_xlabel("域级质量分 S（含 95% Bootstrap 条件区间）")
ax.set_title("七域质量评分（分组熵权 + Bootstrap CI）")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_domain_quality_ci.pdf"))
plt.close()
print("✅ q1_domain_quality_ci.pdf")

# 图2：组间熵权
gw = v2["group_entropy_weights"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ks = sorted(gw, key=lambda k: -gw[k])
ax.bar(ks, [gw[k] for k in ks], color="darkorange")
ax.set_ylabel("熵权 w_g")
ax.set_title("六组指标的熵权分配（区分度决定权重）")
plt.xticks(rotation=20, ha="right")
for i, k in enumerate(ks):
    ax.text(i, gw[k] + 0.005, f"{gw[k]:.4f}", ha="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_group_entropy_weights.pdf"))
plt.close()
print("✅ q1_group_entropy_weights.pdf")

# 图3：二阶 vs 线性（检验集散点）
pred = pd.read_csv(os.path.join(OUT, "q1_test1m_predictions.csv"))
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
lo, hi = pred["actual"].min(), pred["actual"].max()
for ax, col, ttl in [(axes[0], "pred_linear", f"线性模型 (R²={qd['linear']['r2_test_1m']:.4f})"),
                     (axes[1], "pred_quad", f"二阶交互模型 (R²={qd['quadratic']['r2_test_1m']:.4f})")]:
    ax.scatter(pred["actual"], pred[col], s=10, alpha=0.5, c="steelblue")
    ax.plot([lo, hi], [lo, hi], "r--", lw=1)
    ax.set_xlabel("实际 Loss"); ax.set_ylabel("预测 Loss"); ax.set_title(ttl)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_quadratic_vs_linear.pdf"))
plt.close()
print("✅ q1_quadratic_vs_linear.pdf")

# 图4：稳健性对比（排序一致性）
comp = pd.DataFrame(rb["robustness"]["comparisons"])
fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(len(comp)); wd = 0.35
ax.bar(x - wd/2, comp["kendall_tau_b"], wd, label="Kendall τ_b", color="steelblue")
ax.bar(x + wd/2, comp["spearman_rho"], wd, label="Spearman ρ", color="lightcoral")
ax.set_xticks(x); ax.set_xticklabels(comp["alt"])
ax.set_ylim(0, 1.05); ax.set_ylabel("排序相关系数")
ax.set_title("主模型与替代评价方案的排序一致性")
ax.legend(); ax.axhline(1.0, color="gray", ls=":", lw=0.8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_ranking_consistency.pdf"))
plt.close()
print("✅ q1_ranking_consistency.pdf")

print("\n图表全部生成")
