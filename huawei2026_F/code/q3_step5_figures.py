#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F题 问题三 · 图表生成"""
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

ss = json.load(open(os.path.join(OUT, "q3_structural_shift.json"), encoding="utf-8"))
lx = json.load(open(os.path.join(OUT, "q3_Lctx_sensitivity.json"), encoding="utf-8"))
kk = json.load(open(os.path.join(OUT, "q3_kkt_analysis.json"), encoding="utf-8"))
op = json.load(open(os.path.join(OUT, "q3_optimization.json"), encoding="utf-8"))

df = pd.DataFrame(ss["table"])
if "C" not in df.columns:
    df["C"] = 10 ** df["logC"]
# 修正下标字符，避免字体缺字
import re as _re

# ---- 图1：成本占比堆叠图（结构性转移核心图）----
fig, ax = plt.subplots(figsize=(11, 6))
ax.stackplot(df.logC, df.share_train*100, df.share_Q*100, df.share_attn*100,
             labels=["基础训练 6ND", "质量提升 D[g(Q)-g(Q0)]", "长文本注意力 ηNDL"],
             colors=["#4C72B0", "#DD8452", "#55A868"], alpha=0.85)
ax.axvline(20.33, color="red", ls="--", lw=2)
ax.text(20.4, 55, f"结构转移点\nC*≈{10**20.33:.1e}", color="red", fontsize=10, fontweight="bold")
ax.set_xlabel("算力预算 log10(C)  [FLOPs]", fontsize=11)
ax.set_ylabel("成本占比 (%)", fontsize=11)
ax.set_title("算力预算提升时的成本结构演进与结构性转移（L_ctx=8192）", fontsize=12)
ax.legend(loc="center left", fontsize=9); ax.set_xlim(df.logC.min(), df.logC.max())
ax.set_ylim(0, 100); ax.grid(alpha=0.25)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_cost_structure.pdf")); plt.close()
print("✅ q3_cost_structure.pdf")

# ---- 图2：N*、D* 随预算的演化 ----
fig, ax = plt.subplots(figsize=(10, 6))
ax.loglog(df.C, df.N, "o-", ms=4, label="N* (参数量)", color="#4C72B0")
ax.loglog(df.C, df.D, "s-", ms=4, label="D* (Token数)", color="#DD8452")
# 参考斜率线
C0 = df.C.iloc[0]
ax.loglog(df.C, df.N.iloc[0]*(df.C/C0)**0.5, "k:", lw=1.5, label="斜率 1/2 参考线")
ax.set_xlabel("算力预算 C (FLOPs)"); ax.set_ylabel("规模")
ax.set_title("最优规模随算力预算的演进（双对数）")
ax.legend(fontsize=9); ax.grid(alpha=0.3, which="both")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_scale_evolution.pdf")); plt.close()
print("✅ q3_scale_evolution.pdf")

# ---- 图3：Chinchilla 比 r=D/N ----
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(df.logC, df.r_DN, "o-", ms=4, color="#55A868")
ax.axhline(20, color="red", ls="--", lw=1.5, label="Chinchilla 最优比 = 20")
ax.set_xlabel("算力预算 log10(C)"); ax.set_ylabel("D*/N*")
ax.set_ylim(0, 25)
ax.set_title("最优 Chinchilla 比 D*/N* 随预算的变化（恒定 ≈20）")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_chinchilla_ratio.pdf")); plt.close()
print("✅ q3_chinchilla_ratio.pdf")

# ---- 图4：L_ctx 敏感性 ----
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5))
Ls = lx["C7_feasible_values"]
for bn, color, mk in [("低(1e19)", "#4C72B0", "o"), ("中(1e22)", "#DD8452", "s"),
                      ("高(1e24)", "#55A868", "^")]:
    row = lx["opt_by_budget_and_L"][bn]
    xs, ys = [], []
    for L in Ls:
        if str(L) in row:
            xs.append(L); ys.append(row[str(L)]["share_attn"]*100)
    axes[0].plot(xs, ys, mk + "-", color=color, label=bn, ms=6)
axes[0].axvline(lx["L_crit_analytic"]["value"], color="red", ls="--", lw=2,
                label=f"L_crit={lx['L_crit_analytic']['value']:.0f}")
axes[0].set_xscale("log", base=2)
axes[0].set_xlabel("上下文长度 L_ctx"); axes[0].set_ylabel("注意力开销占比 (%)")
axes[0].set_title("注意力开销占比 vs 上下文长度")
axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3, which="both")

for bn, color, mk in [("低(1e19)", "#4C72B0", "o"), ("中(1e22)", "#DD8452", "s"),
                      ("高(1e24)", "#55A868", "^")]:
    row = lx["opt_by_budget_and_L"][bn]
    xs, ys = [], []
    for L in Ls:
        if str(L) in row:
            xs.append(L); ys.append(row[str(L)]["N"]/1e9)
    axes[1].plot(xs, ys, mk + "-", color=color, label=bn, ms=6)
axes[1].axvline(lx["L_crit_analytic"]["value"], color="red", ls="--", lw=2)
axes[1].set_xscale("log", base=2); axes[1].set_yscale("log")
axes[1].set_xlabel("上下文长度 L_ctx"); axes[1].set_ylabel("最优参数量 N* (B)")
axes[1].set_title("最优参数规模 vs 上下文长度")
axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3, which="both")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_Lctx_sensitivity.pdf")); plt.close()
print("✅ q3_Lctx_sensitivity.pdf")

# ---- 图5：Q_max 敏感性 ----
fig, ax = plt.subplots(figsize=(10, 5.5))
qmax = kk["qmax_sensitivity"]
qm = [1.0, 0.95, 0.90, 0.80, 0.70]
for bn, color, mk in [("低", "#4C72B0", "o"), ("中", "#DD8452", "s"), ("高", "#55A868", "^")]:
    ys = [qmax[f"Qmax={q}"][bn]["loss"] if bn in qmax[f"Qmax={q}"] else np.nan for q in qm]
    ax.plot(qm, ys, mk + "-", color=color, label=f"{bn}预算", ms=6)
ax.set_xlabel("质量上界 Q_max"); ax.set_ylabel("最优 Loss")
ax.set_title("质量可达上界对最优 Loss 的影响（敏感性分析）")
ax.invert_xaxis(); ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_qmax_sensitivity.pdf")); plt.close()
print("✅ q3_qmax_sensitivity.pdf")

# ---- 图6：三档预算最优配置对比 ----
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
names = ["低\n10^19", "中\n10^22", "高\n10^24"]
Ns = [op["main_power_law"]["低"]["8192"]["N"], op["main_power_law"]["中"]["8192"]["N"],
      op["main_power_law"]["高"]["8192"]["N"]]
Ds = [op["main_power_law"]["低"]["8192"]["D"], op["main_power_law"]["中"]["8192"]["D"],
      op["main_power_law"]["高"]["8192"]["D"]]
Ls_ = [op["main_power_law"]["低"]["8192"]["loss"], op["main_power_law"]["中"]["8192"]["loss"],
       op["main_power_law"]["高"]["8192"]["loss"]]
axes[0].bar(names, [n/1e9 for n in Ns], color="#4C72B0"); axes[0].set_yscale("log")
axes[0].set_ylabel("N* (B)"); axes[0].set_title("最优参数量")
axes[1].bar(names, [d/1e9 for d in Ds], color="#DD8452"); axes[1].set_yscale("log")
axes[1].set_ylabel("D* (B)"); axes[1].set_title("最优数据量")
axes[2].bar(names, Ls_, color="#55A868"); axes[2].set_ylabel("Loss")
axes[2].set_title("最优 Loss")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_optimal_config.pdf")); plt.close()
print("✅ q3_optimal_config.pdf")

print("\n问题三图表全部生成")
