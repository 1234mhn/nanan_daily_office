#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 图表生成
输出 PDF 矢量图到 figures/
"""
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

# 中文字体
for cand in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
             "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
    if os.path.exists(cand):
        font_manager.fontManager.addfont(cand)
        name = font_manager.FontProperties(fname=cand).get_name()
        plt.rcParams["font.sans-serif"] = [name]
        print(f"字体: {name} ({cand})")
        break
plt.rcParams["axes.unicode_minus"] = False

raw = pd.read_csv(os.path.join(OUT, "q1_quality_raw_compressed.csv"))
samp = pd.read_csv(os.path.join(OUT, "q1_sample_quality.csv"))
domq = pd.read_csv(os.path.join(OUT, "q1_domain_quality.csv"))
domc = pd.read_csv(os.path.join(OUT, "q1_domain_conflict.csv"))
val = pd.read_csv(os.path.join(OUT, "q1_validation.csv"))

# 图1：质量分分布（分域箱线图）
fig, ax = plt.subplots(figsize=(9, 5))
data, labels = [], []
for d, g in samp.groupby("_domain"):
    if len(g) < 50: continue
    data.append(g["Q"].values)
    labels.append(f"{d}\n(n={len(g)})")
ax.boxplot(data, tick_labels=labels, showfliers=False)
ax.set_ylabel("综合质量分 Q")
ax.set_title("各域综合质量分分布")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_quality_by_domain.pdf"))
plt.close()
print("✅ figures/q1_quality_by_domain.pdf")

# 图2：维度间相关热图（冲突来源）
cf = json.load(open(os.path.join(OUT, "q1_conflict_analysis.json"), encoding="utf-8"))
corr = pd.DataFrame(cf["dimension_corr"])
fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=45, ha="right")
ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.index)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center",
                color="white" if abs(corr.values[i, j]) > 0.5 else "black", fontsize=8)
plt.colorbar(im, label="相关系数")
ax.set_title("质量维度间相关矩阵（负值=指标冲突来源）")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_dimension_corr_heatmap.pdf"))
plt.close()
print("✅ figures/q1_dimension_corr_heatmap.pdf")

# 图3：域级质量分柱状图
fig, ax = plt.subplots(figsize=(9, 5))
d2 = domq.sort_values("Q_mean")
ax.barh(d2["_domain"], d2["Q_mean"], color="steelblue")
ax.set_xlabel("域级平均质量分 Q")
ax.set_title("各域平均质量分")
for i, (_, r) in enumerate(d2.iterrows()):
    ax.text(r["Q_mean"] + 0.002, i, f"{r['Q_mean']:.3f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_domain_quality_bar.pdf"))
plt.close()
print("✅ figures/q1_domain_quality_bar.pdf")

# 图4：域级冲突率
fig, ax = plt.subplots(figsize=(9, 5))
d3 = domc.sort_values("conflict_rate")
ax.barh(d3["_domain"], d3["conflict_rate"] * 100, color="indianred")
ax.set_xlabel("冲突率 (%)")
ax.set_title("各域质量指标冲突率（陷阱称0%，实测非零）")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_domain_conflict_bar.pdf"))
plt.close()
print("✅ figures/q1_domain_conflict_bar.pdf")

# 图5：训练拟合 + 跨尺度验证对比
fit = pd.read_csv(os.path.join(OUT, "q1_train_fit.csv"))
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].scatter(fit["actual"], fit["pred"], s=8, alpha=0.5, c="steelblue")
lo, hi = fit["actual"].min(), fit["actual"].max()
axes[0].plot([lo, hi], [lo, hi], "r--", lw=1)
axes[0].set_xlabel("实际 Loss"); axes[0].set_ylabel("预测 Loss")
axes[0].set_title("基础模型：训练集拟合")
axes[1].bar(val["scale"], val["R2"], color=["green" if x > 0 else "red" for x in val["R2"]])
axes[1].axhline(0, color="k", lw=0.8)
axes[1].set_ylabel("R²"); axes[1].set_title("跨尺度验证 R²（基础模型）")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "q1_fit_and_validation.pdf"))
plt.close()
print("✅ figures/q1_fit_and_validation.pdf")

print("\n全部图表生成完毕")
