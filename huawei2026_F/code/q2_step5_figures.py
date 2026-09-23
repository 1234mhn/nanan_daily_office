#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F题 问题二 · 图表"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.optimize import least_squares

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "B_scaling_laws")
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

gl = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
el = json.load(open(os.path.join(OUT, "q2_elasticity.json"), encoding="utf-8"))

pb = gl["model_B_additive"]["params"]
pB = [pb["E"], pb["A"], pb["alpha"], pb["B"], pb["beta"], pb["C"], pb["delta"]]
pa = gl["model_A_multiplicative"]["params"]
pA = [pa["E"], pa["A"], pa["alpha"], pa["B"], pa["beta"], pa["gamma"]]
pc = gl["classical_baseline"]["params"]
pC = [pc["E"], pc["A"], pc["alpha"], pc["B"], pc["beta"]]


def mB(p, N, D, Q): return p[0] + p[1]/N**p[2] + p[3]/D**p[4] + p[5]*(1-Q)**p[6]
def mA(p, N, D, Q): return p[0] + p[1]/N**p[2] + p[3]/(D**p[4]*Q**p[5])
def mC(p, N, D): return p[0] + p[1]/N**p[2] + p[3]/D**p[4]


# 图1：Loss vs Q（固定 N,D）
fig, ax = plt.subplots(figsize=(9, 5.5))
b6 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment.csv"))
b8 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment_large.csv"))
for (n, d), sub in b6.groupby(["N_params_B", "D_tokens_B"]):
    s = sub.sort_values("Q_score")
    ax.plot(s.Q_score, s.val_loss, "o-", ms=3, alpha=0.5, lw=1)
qs = np.linspace(0.05, 1, 100)
for n, d in [(1.0, 50), (1.0, 150)]:
    ax.plot(qs, mB(pB, np.full_like(qs, n), np.full_like(qs, d), qs), "k--", lw=2,
            label=f"加性模型 N={n}B,D={d}B")
ax.set_xlabel("质量分 Q"); ax.set_ylabel("验证 Loss")
ax.set_title("质量 Q 与 Loss 的关系（B6/B7，实测）")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_loss_vs_quality.pdf"))
plt.close()
print("✅ q2_loss_vs_quality.pdf")

# 图2：Q 反向编码诊断
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
s6 = b6[(b6.N_params_B == 0.7) & (b6.D_tokens_B == 10)].sort_values("Q_score")
s8 = b8[(b8.N_params_B == 0.7) & (b8.D_tokens_B == 10)].sort_values("Q_score")
axes[0].plot(s6.Q_score, s6.val_loss, "o-", color="steelblue")
axes[0].set_xlabel("Q_score"); axes[0].set_ylabel("Loss")
axes[0].set_title(f"B6/B7 (主拟合)\ncorr(Q,Loss)={-0.925:.3f}")
axes[1].plot(s8.Q_score, s8.val_loss, "s-", color="indianred")
axes[1].set_xlabel("Q_score"); axes[1].set_ylabel("Loss")
axes[1].set_title(f"B8 (外部验证)\ncorr(Q,Loss)={+0.984:.3f} ← 反向编码!")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_Q_direction_diagnosis.pdf"))
plt.close()
print("✅ q2_Q_direction_diagnosis.pdf")

# 图3：AIC 模型比较
fig, ax = plt.subplots(figsize=(8, 5))
names = ["经典\n(无Q)", "A 乘性", "B 加性"]
aics = [gl["classical_baseline"]["AIC"], gl["model_A_multiplicative"]["AIC"],
        gl["model_B_additive"]["AIC"]]
r2s = [gl["classical_baseline"]["R2"], gl["model_A_multiplicative"]["R2"],
       gl["model_B_additive"]["R2"]]
x = np.arange(3); w = 0.38
ax2 = ax.twinx()
ax.bar(x - w/2, [-a for a in aics], w, label="-AIC (越大越好)", color="steelblue")
ax2.bar(x + w/2, r2s, w, label="R²", color="lightcoral")
ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_ylabel("-AIC"); ax2.set_ylabel("R²")
ax.set_title("广义标度律模型比较（AIC 选优 → 加性方案）")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_model_comparison.pdf"))
plt.close()
print("✅ q2_model_comparison.pdf")

# 图4：参数 vs 质量 的替代关系（等 Loss 曲线）
fig, ax = plt.subplots(figsize=(9, 5.5))
D0 = 100.0
for Lv in [2.0, 2.2, 2.4, 2.6]:
    Ns, Qs = [], []
    for q in np.linspace(0.1, 1.0, 80):
        # 解 N 使 mB(N,D0,q)=Lv
        try:
            f = lambda n: mB(pB, n, np.array([D0]), np.array([q]))[0] - Lv
            from scipy.optimize import brentq
            n = brentq(f, 1e-3, 1e4)
            Ns.append(n); Qs.append(q)
        except Exception:
            pass
    if Ns:
        ax.plot(Qs, Ns, "-", lw=2, label=f"Loss={Lv}")
ax.set_yscale("log")
ax.set_xlabel("质量分 Q"); ax.set_ylabel("所需参数量 N (B, log)")
ax.set_title("参数规模与数据质量的替代关系（等 Loss 曲线, D=100B）")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_substitution_curve.pdf"))
plt.close()
print("✅ q2_substitution_curve.pdf")

# 图5：弹性柱状图
fig, ax = plt.subplots(figsize=(9, 5))
mp = pd.DataFrame(el["elasticity"]["multi_point"])
x = np.arange(len(mp)); w = 0.26
ax.bar(x - w, mp["eps_N"], w, label="ε_N", color="steelblue")
ax.bar(x, mp["eps_D"], w, label="ε_D", color="darkorange")
ax.bar(x + w, mp["eps_Q"], w, label="ε_Q", color="seagreen")
ax.axhline(0, color="k", lw=1)
ax.set_xticks(x)
ax.set_xticklabels([f"N={r.N}B\nD={r.D}B Q={r.Q}" for _, r in mp.iterrows()], fontsize=8)
ax.set_ylabel("弹性系数")
ax.set_title("各因素的 Loss 弹性（均为负 → 规模/质量提升均降低 Loss）")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_elasticity_bars.pdf"))
plt.close()
print("✅ q2_elasticity_bars.pdf")

# 图6：B8 校准前后
fig, ax = plt.subplots(figsize=(9, 5.5))
N, D, Q, L = b8.N_params_B.values, b8.D_tokens_B.values, b8.Q_score.values, b8.val_loss.values
pr = mB(pB, N, D, Q)
ax.scatter(L, pr, s=5, alpha=0.3, c="indianred", label=f"原始 Q (r={np.corrcoef(pr,L)[0,1]:.2f})")
pr2 = mB(pB, N, D, 1 - Q)
ax.scatter(L, pr2, s=5, alpha=0.3, c="seagreen", label=f"修正 Q'=1-Q (r={np.corrcoef(pr2,L)[0,1]:.2f})")
lo, hi = L.min(), L.max()
ax.plot([lo, hi], [lo, hi], "k--", lw=1)
ax.set_xlabel("实际 Loss (B8)"); ax.set_ylabel("预测 Loss")
ax.set_title("B8 外部验证：Q 反向编码修正前后")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q2_B8_calibration.pdf"))
plt.close()
print("✅ q2_B8_calibration.pdf")

print("\n问题二图表全部生成")
