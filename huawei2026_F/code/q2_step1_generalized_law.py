#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题二 · 步骤1：广义标度律 —— 质量 Q 的引入（主拟合）

题面要求：L(N,D,Q,p)，Q→1 时退化为经典 Chinchilla 形式。

设计（乘性 vs 加性，决策 2.1 = A+B 对比，AIC 选优）：

  方案 A（乘性，质量改变数据效率）：
      L = E + A/N^α + B/(D^β · Q^γ)
      Q→1 时退化为 L = E + A/N^α + B/D^β ✅

  方案 B（加性，独立项）：
      L = E + A/N^α + B/D^β + C·(1-Q)^δ
      Q→1 时退化为经典形式 ✅

  拟合数据（决策 2.2 = C）：B6(360) + B7(450) = 810 点
  验证：B8(1704) 仅作外部验证（决策 2.2）

输出：results/q2_generalized_law.json
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "B_scaling_laws")
OUT = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)


def load_nq(fname):
    d = pd.read_csv(os.path.join(ATT, fname))
    return d[["N_params_B", "D_tokens_B", "Q_score", "val_loss"]].dropna()


# ---------------- 方案 A：乘性 ----------------
def modelA(params, N, D, Q):
    E, A, alpha, B, beta, gamma = params
    return E + A / N**alpha + B / (D**beta * Q**gamma)


def residA(params, N, D, Q, L):
    return modelA(params, N, D, Q) - L


# ---------------- 方案 B：加性 ----------------
def modelB(params, N, D, Q):
    E, A, alpha, B, beta, C, delta = params
    return E + A / N**alpha + B / D**beta + C * (1 - Q) ** delta


def residB(params, N, D, Q, L):
    return modelB(params, N, D, Q) - L


# ---------------- 经典 Chinchilla（无 Q，基线）----------------
def modelC(params, N, D):
    E, A, alpha, B, beta = params
    return E + A / N**alpha + B / D**beta


def aic_bic(resid, k):
    n = len(resid)
    rss = np.sum(resid**2)
    ll = -n / 2 * (np.log(2 * np.pi * rss / n) + 1)
    return 2 * k - 2 * ll, k * np.log(n) - 2 * ll


def main():
    print("=" * 78)
    print("问题二 · 广义标度律（质量 Q 的引入）")
    print("=" * 78)

    # ---- 载入（决策 2.2：B6+B7 主拟合）----
    b6 = load_nq("supplementary_NQ_experiment.csv")
    b7 = load_nq("supplementary_NQ_experiment_expanded.csv")
    b8 = load_nq("supplementary_NQ_experiment_large.csv")
    fit = pd.concat([b6, b7], ignore_index=True).drop_duplicates()
    print(f"  主拟合 B6+B7: {len(fit)} 点 (B6={len(b6)}, B7={len(b7)}, 去重后={len(fit)})")
    print(f"  外部验证 B8: {len(b8)} 点")

    N = fit["N_params_B"].values
    D = fit["D_tokens_B"].values
    Q = fit["Q_score"].values
    L = fit["val_loss"].values

    print(f"\n  N 范围: [{N.min()}, {N.max()}] B")
    print(f"  D 范围: [{D.min()}, {D.max()}] B")
    print(f"  Q 范围: [{Q.min()}, {Q.max()}]")

    # ---- 方案 A：乘性 ----
    print("\n--- 方案 A：乘性  L = E + A/N^α + B/(D^β·Q^γ) ---")
    best_a, best_rss = None, np.inf
    rng = np.random.default_rng(20260923)
    for _ in range(200):
        p0 = [rng.uniform(1, 3), rng.uniform(10, 500), rng.uniform(0.05, 0.5),
              rng.uniform(10, 500), rng.uniform(0.1, 0.5), rng.uniform(0.1, 2)]
        try:
            r = least_squares(residA, p0, args=(N, D, Q, L),
                              bounds=([0, 0, 0.01, 0, 0.01, 0.01],
                                      [10, 1e5, 2, 1e5, 2, 5]), max_nfev=5000)
            if r.cost < best_rss:
                best_rss, best_a = r.cost, r.x
        except Exception:
            pass
    rA = residA(best_a, N, D, Q, L)
    r2A = 1 - np.sum(rA**2) / np.sum((L - L.mean())**2)
    aicA, bicA = aic_bic(rA, 6)
    print(f"  E={best_a[0]:.5f}, A={best_a[1]:.4f}, α={best_a[2]:.5f}, "
          f"B={best_a[3]:.4f}, β={best_a[4]:.5f}, γ={best_a[5]:.5f}")
    print(f"  R²={r2A:.6f}  RMSE={np.sqrt(np.mean(rA**2)):.5f}  AIC={aicA:.2f}  BIC={bicA:.2f}")

    # ---- 方案 B：加性 ----
    print("\n--- 方案 B：加性  L = E + A/N^α + B/D^β + C·(1-Q)^δ ---")
    best_b, best_rss_b = None, np.inf
    for _ in range(200):
        p0 = [rng.uniform(1, 3), rng.uniform(10, 500), rng.uniform(0.05, 0.5),
              rng.uniform(10, 500), rng.uniform(0.1, 0.5),
              rng.uniform(0.1, 5), rng.uniform(0.1, 3)]
        try:
            r = least_squares(residB, p0, args=(N, D, Q, L),
                              bounds=([0, 0, 0.01, 0, 0.01, 0, 0.01],
                                      [10, 1e5, 2, 1e5, 2, 1e3, 5]), max_nfev=5000)
            if r.cost < best_rss_b:
                best_rss_b, best_b = r.cost, r.x
        except Exception:
            pass
    rB = residB(best_b, N, D, Q, L)
    r2B = 1 - np.sum(rB**2) / np.sum((L - L.mean())**2)
    aicB, bicB = aic_bic(rB, 7)
    print(f"  E={best_b[0]:.5f}, A={best_b[1]:.4f}, α={best_b[2]:.5f}, "
          f"B={best_b[3]:.4f}, β={best_b[4]:.5f}, C={best_b[5]:.5f}, δ={best_b[6]:.5f}")
    print(f"  R²={r2B:.6f}  RMSE={np.sqrt(np.mean(rB**2)):.5f}  AIC={aicB:.2f}  BIC={bicB:.2f}")

    # ---- 经典基线（无 Q）----
    print("\n--- 经典 Chinchilla 基线（无 Q，对照）---")
    def residC(p, N, D, L):
        return modelC(p, N, D) - L
    best_c, best_rss_c = None, np.inf
    for _ in range(100):
        p0 = [rng.uniform(1, 3), rng.uniform(10, 500), rng.uniform(0.05, 0.5),
              rng.uniform(10, 500), rng.uniform(0.1, 0.5)]
        r = least_squares(residC, p0, args=(N, D, L),
                          bounds=([0, 0, 0.01, 0, 0.01], [10, 1e5, 2, 1e5, 2]))
        if r.cost < best_rss_c:
            best_rss_c, best_c = r.cost, r.x
    rC = residC(best_c, N, D, L)
    r2C = 1 - np.sum(rC**2) / np.sum((L - L.mean())**2)
    aicC, bicC = aic_bic(rC, 5)
    print(f"  R²={r2C:.6f}  RMSE={np.sqrt(np.mean(rC**2)):.5f}  AIC={aicC:.2f}  BIC={bicC:.2f}")

    # ---- 决策 2.1：AIC 选优 ----
    print("\n--- 决策 2.1：AIC 选优 ---")
    cands = {"A 乘性": (aicA, "A"), "B 加性": (aicB, "B"), "经典(无Q)": (aicC, "C")}
    winner = min(cands.items(), key=lambda x: x[1][0])
    print(f"  AIC 排序: " + " < ".join(f"{k}({v[0]:.1f})" for k, v in sorted(cands.items(), key=lambda x: x[1][0])))
    print(f"  ⭐ 选优: {winner[0]}")
    delta_aic = aicC - min(aicA, aicB)
    print(f"  含 Q 模型相对经典模型的 ΔAIC = {delta_aic:.2f} "
          f"({'✅显著改进' if delta_aic > 10 else '改进有限'})")

    # ---- 外部验证（B8，标注为半合成）----
    print("\n--- 外部验证（B8，半合成，仅验证不拟合）---")
    Nb, Db, Qb, Lb = (b8["N_params_B"].values, b8["D_tokens_B"].values,
                      b8["Q_score"].values, b8["val_loss"].values)
    oos = {}
    for name, pred in [("A 乘性", modelA(best_a, Nb, Db, Qb)),
                       ("B 加性", modelB(best_b, Nb, Db, Qb)),
                       ("经典", modelC(best_c, Nb, Db))]:
        rm = np.sqrt(np.mean((pred - Lb) ** 2))
        rr = 1 - np.sum((pred - Lb) ** 2) / np.sum((Lb - Lb.mean()) ** 2)
        oos[name] = {"rmse": float(rm), "r2": float(rr)}
        print(f"  {name:8s} R²={rr:.5f}  RMSE={rm:.5f}")

    out = {
        "fit_data": {"B6": len(b6), "B7": len(b7), "n_fit": len(fit),
                     "note": "决策2.2：B6+B7 主拟合；B8 仅外部验证（半合成）"},
        "model_A_multiplicative": {
            "form": "L = E + A/N^α + B/(D^β·Q^γ)",
            "params": {"E": float(best_a[0]), "A": float(best_a[1]), "alpha": float(best_a[2]),
                       "B": float(best_a[3]), "beta": float(best_a[4]), "gamma": float(best_a[5])},
            "R2": float(r2A), "RMSE": float(np.sqrt(np.mean(rA**2))),
            "AIC": float(aicA), "BIC": float(bicA)},
        "model_B_additive": {
            "form": "L = E + A/N^α + B/D^β + C·(1-Q)^δ",
            "params": {"E": float(best_b[0]), "A": float(best_b[1]), "alpha": float(best_b[2]),
                       "B": float(best_b[3]), "beta": float(best_b[4]),
                       "C": float(best_b[5]), "delta": float(best_b[6])},
            "R2": float(r2B), "RMSE": float(np.sqrt(np.mean(rB**2))),
            "AIC": float(aicB), "BIC": float(bicB)},
        "classical_baseline": {"form": "L = E + A/N^α + B/D^β",
                               "params": {"E": float(best_c[0]), "A": float(best_c[1]),
                                          "alpha": float(best_c[2]), "B": float(best_c[3]),
                                          "beta": float(best_c[4])},
                               "R2": float(r2C), "RMSE": float(np.sqrt(np.mean(rC**2))),
                               "AIC": float(aicC), "BIC": float(bicC)},
        "decision_2_1_winner": winner[0],
        "delta_AIC_vs_classical": float(delta_aic),
        "out_of_sample_B8": oos,
        "degeneracy_check": "当 Q→1：方案A→ E+A/N^α+B/D^β；方案B→ E+A/N^α+B/D^β。两者均退化为经典形式 ✅",
    }
    with open(os.path.join(OUT, "q2_generalized_law.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q2_generalized_law.json")


if __name__ == "__main__":
    main()
