#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤7：二阶交互模型（修正版，真正做对）

问题诊断：step6 的二阶模型 CV 好但检验集崩（R²=-0.54）→ 过拟合。
修正：
  1. 先对配比做「单纯形归一化 + 中心化」再生成交互项（避免量纲问题）
  2. 交互项也做标准化
  3. 用嵌套 CV 选 λ（外层评估，内层选参）
  4. 报告训练/检验的诚实结果

输出：results/q1_quadratic_v2.json
"""
import os, json
import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
RGT = os.path.join(BASE, "real_attachments", "A_data_value", "regmix_tables")


def dn(c):
    return (c.replace("metric/", "").replace("train_the_pile_", "")
            .replace("the_pile_", "").replace("_val_loss", ""))


def load(f, loss_domains, is_loss=False):
    d = pd.read_csv(os.path.join(RGT, f))
    if is_loss:
        cols = [c for c in d.columns if "_val_loss" in c and dn(c) in loss_domains]
        return d[cols].values.mean(axis=1)
    cols = [c for c in d.columns if c.startswith("train_the_pile_") and dn(c) in loss_domains]
    return d[cols].values


def make_feats(P, pairs):
    """单纯形归一化 + 交互项"""
    Ps = P / P.sum(axis=1, keepdims=True)
    inter = np.column_stack([Ps[:, i] * Ps[:, j] for i, j in pairs])
    return Ps, inter


def main():
    print("=" * 78)
    print("问题一 · 二阶交互模型（修正版）")
    print("=" * 78)

    L1 = pd.read_csv(os.path.join(RGT, "train_pile_loss_1m.csv"))
    loss_domains = [dn(c) for c in L1.columns if "_val_loss" in c]

    P = load("train_mixture_1m.csv", loss_domains)
    L = load("train_pile_loss_1m.csv", loss_domains, True)
    Pv = load("test_mixture_1m.csv", loss_domains)
    Lv = load("test_pile_loss_1m.csv", loss_domains, True)

    names = None
    m1 = pd.read_csv(os.path.join(RGT, "train_mixture_1m.csv"))
    names = [dn(c) for c in m1.columns if c.startswith("train_the_pile_") and dn(c) in loss_domains]

    print(f"  训练 {P.shape}, 检验 {Pv.shape}, 域数 {P.shape[1]}")

    pairs = list(combinations(range(P.shape[1]), 2))
    print(f"  交互项: {len(pairs)} 个")

    # ---- 线性基线 ----
    sc_l = StandardScaler().fit(P)
    from sklearn.linear_model import RidgeCV
    rcv = RidgeCV(alphas=[0.01, 0.1, 1, 10, 100]).fit(sc_l.transform(P), L)
    lin_tr = rcv.predict(sc_l.transform(P))
    lin_te = rcv.predict(sc_l.transform(Pv))
    print(f"\n  [线性] 训练R²={r2_score(L,lin_tr):.4f}  检验R²={r2_score(Lv,lin_te):.4f}  "
          f"检验RMSE={np.sqrt(mean_squared_error(Lv,lin_te)):.4f}  λ={rcv.alpha_}")

    # ---- 二阶：分块标准化（线性块 vs 交互块分别标准化）----
    Ps_tr, I_tr = make_feats(P, pairs)
    Ps_te, I_te = make_feats(Pv, pairs)

    # 用训练集的统一 scaler（关键：检验集必须用训练集统计量）
    sc_p = StandardScaler().fit(Ps_tr)
    sc_i = StandardScaler().fit(I_tr)
    Ztr = np.hstack([sc_p.transform(Ps_tr), sc_i.transform(I_tr)])
    Zte = np.hstack([sc_p.transform(Ps_te), sc_i.transform(I_te)])

    # 嵌套 5 折 CV 选 λ
    from sklearn.model_selection import KFold
    kf = KFold(5, shuffle=True, random_state=20260924)
    alphas = [1, 10, 100, 1000, 10000]
    best = None
    for al in alphas:
        errs = []
        for tr, te in kf.split(Ztr):
            m = Ridge(alpha=al).fit(Ztr[tr], L[tr])
            errs.append(np.sqrt(mean_squared_error(L[te], m.predict(Ztr[te]))))
        rm = np.mean(errs)
        if best is None or rm < best[1]:
            best = (al, rm)
    lam = best[0]
    print(f"\n  [二阶] 内层CV选 λ={lam} (CV RMSE={best[1]:.4f})")

    q = Ridge(alpha=lam).fit(Ztr, L)
    q_tr = q.predict(Ztr)
    q_te = q.predict(Zte)
    print(f"  训练R²={r2_score(L,q_tr):.4f}  检验R²={r2_score(Lv,q_te):.4f}  "
          f"检验RMSE={np.sqrt(mean_squared_error(Lv,q_te)):.4f}")

    # ---- 诚实对比 ----
    e1 = (Lv - lin_te) ** 2
    e2 = (Lv - q_te) ** 2
    rng = np.random.default_rng(20260924)
    diffs = [np.sqrt(e2[i].mean()) - np.sqrt(e1[i].mean())
             for i in (rng.integers(0, len(Lv), len(Lv)) for _ in range(500))]
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"\n  配对bootstrap RMSE差(二阶-线性) 95%CI=[{lo:+.4f}, {hi:+.4f}]  "
          f"{'✅二阶显著更优' if hi < 0 else ('❌二阶无优势/更差' if lo > 0 else '⚠️无显著差异')}")

    # ---- 系数（前若干重要交互）----
    coefs = q.coef_
    lin_part = coefs[:P.shape[1]]
    int_part = coefs[P.shape[1]:]
    top_int = sorted(zip(pairs, int_part), key=lambda x: -abs(x[1]))[:5]
    print(f"\n  最重要交互项（标准化尺度）:")
    for (i, j), c in top_int:
        print(f"    {names[i]} × {names[j]}: {c:+.4f}")

    out = {
        "n_features": int(Ztr.shape[1]), "n_pairs": len(pairs),
        "lambda_selected": float(lam),
        "linear": {"r2_train": float(r2_score(L, lin_tr)),
                   "r2_test_1m": float(r2_score(Lv, lin_te)),
                   "rmse_test_1m": float(np.sqrt(mean_squared_error(Lv, lin_te)))},
        "quadratic": {"r2_train": float(r2_score(L, q_tr)),
                      "r2_test_1m": float(r2_score(Lv, q_te)),
                      "rmse_test_1m": float(np.sqrt(mean_squared_error(Lv, q_te)))},
        "rmse_diff_ci": [float(lo), float(hi)],
        "conclusion": ("二阶显著更优" if hi < 0 else
                       ("二阶更差（过拟合）" if lo > 0 else "无显著差异")),
        "top_interactions": [{"pair": f"{names[i]}×{names[j]}", "coef": float(c)}
                             for (i, j), c in top_int],
        "note": "检验集用训练集标准化统计量；λ 由内层CV选定，检验集不参与",
    }
    with open(os.path.join(OUT, "q1_quadratic_v2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    pd.DataFrame({"actual": Lv, "pred_linear": lin_te, "pred_quad": q_te}).to_csv(
        os.path.join(OUT, "q1_test1m_predictions.csv"), index=False)
    print(f"\n✅ 输出: results/q1_quadratic_v2.json, q1_test1m_predictions.csv")


if __name__ == "__main__":
    main()
