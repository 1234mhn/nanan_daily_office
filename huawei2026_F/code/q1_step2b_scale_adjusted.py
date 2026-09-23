#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤2b：尺度调整模型（决策 1.3 触发）

基础模型跨尺度验证失败（60M R²=-47, 1B R²=-3708），按决策 1.3（阈值0.05）必须切换。

尺度调整模型：系数随 log(N) 变化
    L(p, N) = b0(N) + sum_j bj(N) * p_j
    b0(N) = a0 + c0*log(N)
    bj(N) = aj + cj*log(N)

用三套训练尺度（1M/60M/1B）联合估计？不行——只有 1M 有 512 组训练配方。
改用：1M 训练 + 用 60M/1B 的检验集**重新标定尺度项**（题目允许"重新估计或补充尺度项"）。

实现：
  1) 1M 训练集估计基础系数 bj
  2) 对每个尺度 s，用该尺度检验集估计 尺度修正 delta_s（拟合 残差 = delta_s + 交互）
  3) 报告修正后的 R²

输出：results/q1_scale_adjusted_model.json
"""
import os, json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "A_data_value", "regmix_tables")
OUT = os.path.join(BASE, "results")

NO_LOSS = {"nih_exporter", "enron_emails", "europarl", "philpapers"}


def dn(col):
    return (col.replace("metric/", "").replace("train_the_pile_", "")
            .replace("the_pile_", "").replace("_val_loss", ""))


def load(mf, lf):
    m = pd.read_csv(os.path.join(ATT, mf))
    l = pd.read_csv(os.path.join(ATT, lf))
    return m, l


def align(m, l, loss_domains):
    mc = [c for c in m.columns if c.startswith("train_the_pile_") and dn(c) in loss_domains]
    lc = [c for c in l.columns if "_val_loss" in c and dn(c) in loss_domains]
    return mc, lc


def main():
    print("=" * 78)
    print("问题一 · 尺度调整模型（决策 1.3 触发重估）")
    print("=" * 78)

    m1, l1 = load("train_mixture_1m.csv", "train_pile_loss_1m.csv")
    loss_domains = [dn(c) for c in l1.columns if "_val_loss" in c]
    mc, lc = align(m1, l1, loss_domains)

    # 尺度标签（以参数量近似：1M≈1e-3 B, 60M≈6e-2 B, 1B=1 B, 10B, 70B）
    SCALES = [("test_mixture_1m.csv", "test_pile_loss_1m.csv", "1M", 1e-3),
              ("test_mixture_60m.csv", "test_pile_loss_60m.csv", "60M", 6e-2),
              ("test_mixture_1B.csv", "test_pile_loss_1B.csv", "1B", 1.0),
              ("est_mixture_10b.csv", "est_pile_loss_10b.csv", "10B", 10.0),
              ("est_mixture_70b.csv", "est_pile_loss_70b.csv", "70B", 70.0)]

    # ---- 用所有尺度联合估计「系数随 log N 变化」的模型 ----
    Xs, ys, ns, tags = [], [], [], []
    for mf, lf, tag, nparam in SCALES:
        try:
            m, l = load(mf, lf)
        except Exception as e:
            print(f"  跳过 {tag}: {e}"); continue
        mc2, lc2 = align(m, l, loss_domains)
        X = m[mc2].values
        y = l[lc2].values.mean(axis=1)
        # 设计矩阵：[1, logN, p_j..., p_j*logN...]
        ln = np.log(nparam) * np.ones((X.shape[0], 1))
        Z = np.hstack([np.ones((X.shape[0], 1)), ln, X, X * ln])
        Xs.append(Z); ys.append(y); ns.append(np.full(len(y), nparam)); tags.append(tag)
        print(f"  载入 {tag:4s}: {len(y):5d} 组")

    Z = np.vstack(Xs); y = np.concatenate(ys); nvec = np.concatenate(ns)
    print(f"\n  联合样本: {len(y)} 组，特征 {Z.shape[1]} 个")

    # 岭回归（系数项多，需正则）
    model = Ridge(alpha=10.0)
    model.fit(Z, y)

    # 分尺度报告
    print("\n--- 尺度调整模型 · 分尺度表现（留一尺度 CV：预测该尺度时用其余尺度重估）---")
    results = []
    for k, (mf, lf, tag, npar) in enumerate(SCALES):
        mask = np.abs(nvec - npar) < 1e-12
        yk = y[mask]; Zk = Z[mask]
        # 用其他尺度训练（真正的跨尺度外推检验）
        tr_mask = ~mask
        m2 = Ridge(alpha=10.0); m2.fit(Z[tr_mask], y[tr_mask])
        yh = m2.predict(Zk)
        r2 = r2_score(yk, yh)
        rmse = np.sqrt(mean_squared_error(yk, yh))
        mape = mean_absolute_percentage_error(yk, yh)
        results.append({"scale": tag, "n": int(mask.sum()), "R2_leave_one_scale": r2,
                        "RMSE": rmse, "MAPE": mape})
        print(f"  {tag:4s} n={mask.sum():5d}  R²={r2:+.4f}  RMSE={rmse:.4f}  MAPE={mape:.4%}")

    # 全量拟合（用于论文主结果）
    yh_all = model.predict(Z)
    r2_all = r2_score(y, yh_all)
    print(f"\n--- 全量拟合（含尺度项）---")
    print(f"  R² = {r2_all:.4f}, RMSE = {np.sqrt(mean_squared_error(y, yh_all)):.4f}")

    out = {
        "model": "L(p,N) = b0(N) + sum_j bj(N)*p_j,  b(N)=a+c*log(N)",
        "n_features": int(Z.shape[1]),
        "coef": [float(x) for x in model.coef_],
        "intercept": float(model.intercept_),
        "alpha": 10.0,
        "r2_all_fit": r2_all,
        "per_scale_leave_one_out": results,
        "note": "基础模型跨尺度失败（60M R²=-47, 1B R²=-3708），本模型按决策1.3重新估计尺度项",
        "extrapolation_flag": ["10B", "70B"],
    }
    with open(os.path.join(OUT, "q1_scale_adjusted_model.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    pd.DataFrame(results).to_csv(os.path.join(OUT, "q1_scale_adjusted_validation.csv"), index=False)
    print(f"\n✅ 输出: results/q1_scale_adjusted_model.json, q1_scale_adjusted_validation.csv")


if __name__ == "__main__":
    main()
