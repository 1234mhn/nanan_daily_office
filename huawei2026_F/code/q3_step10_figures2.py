#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补充生成问题三的两张新图（网格验证 + PELT变点 + 参数敏感性）"""
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
for cand in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]:
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=cand).get_name()]
plt.rcParams["axes.unicode_minus"] = False

gv = json.load(open(os.path.join(OUT, "q3_grid_verification.json"), encoding="utf-8"))
fl = json.load(open(os.path.join(OUT, "q3_flatness.json"), encoding="utf-8"))
pe = json.load(open(os.path.join(OUT, "q3_pelt_changepoint.json"), encoding="utf-8"))
ps = json.load(open(os.path.join(OUT, "q3_param_sensitivity.json"), encoding="utf-8"))

# ---- 图7：求解方法交叉验证 + D/N 修正 ----
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5))
ks = ["低(1e19)", "中(1e22)", "高(1e24)"]
x = np.arange(3); w = 0.27
sl = [gv["results"][k]["slsqp"]["loss"] for k in ks]
gr = [gv["results"][k]["grid_refined"]["loss"] for k in ks]
rf = [fl["final_recommended"][k]["refined"]["loss"] for k in ks]
axes[0].bar(x-w, sl, w, label="SLSQP(原)", color="#4C72B0")
axes[0].bar(x, gr, w, label="网格穷举", color="#DD8452")
axes[0].bar(x+w, rf, w, label="精修(推荐)", color="#55A868")
axes[0].set_xticks(x); axes[0].set_xticklabels(["10^19", "10^22", "10^24"])
axes[0].set_ylabel("最优 Loss"); axes[0].set_ylim(1.521, 1.5265)
axes[0].set_title("三种求解方法的最优 Loss 对比")
axes[0].legend(fontsize=8)

dn_sl = [gv["results"][k]["slsqp"]["D"]/gv["results"][k]["slsqp"]["N"] for k in ks]
dn_rf = [fl["final_recommended"][k]["refined"]["r_DN"] for k in ks]
axes[1].bar(x-w/2, dn_sl, w, label="SLSQP(局部解)", color="#C44E52")
axes[1].bar(x+w/2, dn_rf, w, label="精修(全局解)", color="#55A868")
axes[1].axhline(20, color="red", ls="--", lw=1.5, label="Chinchilla 比 20（不适用）")
axes[1].set_xticks(x); axes[1].set_xticklabels(["10^19", "10^22", "10^24"])
axes[1].set_ylabel("D*/N*"); axes[1].set_title("最优 D*/N* 的修正（20 → 约6.5）")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_solver_verification.pdf")); plt.close()
print("✅ q3_solver_verification.pdf")

# ---- 图8：PELT 变点检测 ----
tbl = pd.DataFrame(pe["table"])
fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
axes[0].plot(tbl.logC, tbl.s_train, "-", lw=2, label="训练份额")
axes[0].plot(tbl.logC, tbl.s_Q, "-", lw=2, label="质量份额")
axes[0].plot(tbl.logC, tbl.s_attn, "-", lw=2, label="注意力份额")
cp = pe["main_changepoint_logC"]
axes[0].axvline(cp, color="red", ls="--", lw=2, label=f"PELT 变点 logC={cp:.1f}")
axes[0].axvline(20.33, color="purple", ls=":", lw=2, label="M1/M4 跃迁 logC=20.33")
axes[0].set_ylabel("成本份额"); axes[0].set_title("成本结构 + PELT 变点检测（81 点扫描）")
axes[0].legend(fontsize=8); axes[0].grid(alpha=0.25)

axes[1].plot(tbl.logC, tbl.r_DN, "o-", ms=3, color="#55A868")
axes[1].axvline(cp, color="red", ls="--", lw=2)
axes[1].axvline(20.33, color="purple", ls=":", lw=2)
axes[1].axhline(20, color="gray", ls="--", lw=1, alpha=0.6)
axes[1].set_xlabel("log10(C)  算力预算"); axes[1].set_ylabel("D*/N*")
axes[1].set_title("最优 D*/N* 随预算的演化（灰线为 Chinchilla 比 20，不再适用）")
axes[1].grid(alpha=0.25)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_pelt_changepoint.pdf")); plt.close()
print("✅ q3_pelt_changepoint.pdf")

# ---- 图9：参数敏感性 ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
sf = ps["single_factor_pm20pct"]
params = ["E", "A", "alpha", "B", "beta", "C", "delta"]
dl = [abs(sf[f"{k}-20%"]["delta_loss_pct"]) if f"{k}-20%" in sf else 0 for k in params]
colors = ["#C44E52" if d > 1 else "#4C72B0" for d in dl]
axes[0].barh(params, dl, color=colors)
axes[0].set_xlabel("|ΔLoss| (%)  （参数 ±20% 时）")
axes[0].set_title("单因素参数敏感性（E 为主导参数）")
axes[0].grid(alpha=0.25, axis="x")

mc = ps["monte_carlo"]
labs = ["N*", "D*", "r_DN", "Q*", "Loss*"]
cvs = [mc["stats"]["N"]["cv_pct"], mc["stats"]["D"]["cv_pct"],
       mc["stats"]["r_DN"]["cv_pct"], mc["stats"]["Q"]["cv_pct"],
       mc["stats"]["loss"]["cv_pct"]]
axes[1].bar(labs, cvs, color=["#4C72B0", "#DD8452", "#55A868", "#8172B3", "#C44E52"])
axes[1].set_ylabel("变异系数 CV (%)")
axes[1].set_title("蒙特卡洛联合扰动下各量的稳定性（200 次）")
axes[1].grid(alpha=0.25, axis="y")
for i, v in enumerate(cvs):
    axes[1].text(i, v, f"{v:.2f}%", ha="center", va="bottom", fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "q3_param_sensitivity.pdf")); plt.close()
print("✅ q3_param_sensitivity.pdf")

print("\n新增 3 张图")
