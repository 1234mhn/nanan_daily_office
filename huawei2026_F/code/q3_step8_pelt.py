#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 补齐3：PELT 变点检测识别结构性转移

规范要求：在预算上取 60–100 个点重复求解，得到份额向量与标度指数，
         用 PELT 或 Bai-Perron 变点检测找 C*。

本步：
  1. 加密预算扫描到 81 个点（10^17.5 – 10^25.5）
  2. 对每条序列（份额 / 标度指数 / logN / logD / log r）做 PELT 变点检测
  3. 交叉验证变点位置，确认结构性转移 C*

输出：results/q3_pelt_changepoint.json
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import ruptures as rpt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

g2 = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
p = g2["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ, DELTA = (p["E"], p["A"], p["alpha"], p["B"],
                                     p["beta"], p["C"], p["delta"])
ETA = 2e-4
g_pow = lambda Q: 5e9 * Q**4
Q0 = 0.5
L = 8192


def solve(C_budget, n_starts=80, seed=20260923, use_grid_init=False):
    rng = np.random.default_rng(seed)
    best = None
    bounds = [(1e4, 1e15), (1e5, 1e17), (Q0+1e-6, 1.0)]

    def cost(x):
        N, D, Q = x
        return 6*N*D + D*max(g_pow(Q)-g_pow(Q0), 0) + ETA*N*D*L

    def loss(x):
        N, D, Q = x
        return E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA

    starts = []
    if use_grid_init:
        # 用解析估计的起点：D/N ≈ 6.5
        for lgN in np.linspace(5, 13, 9):
            N0 = 10**lgN
            # 反推可行 D
            D0 = min(N0*6.5, (C_budget)/( (6+ETA*L)*N0 + max(g_pow(1.0)-g_pow(Q0),0)*0 ) )
            starts.append([N0, D0, 1.0])
    for _ in range(n_starts):
        N0 = 10**rng.uniform(4.5, 13.5)
        starts.append([N0, 6.5*N0, rng.uniform(Q0, 1.0)])

    for s0 in starts:
        x0 = np.array(s0, dtype=float)
        for _t in range(100):
            if cost(x0) <= C_budget: break
            x0[:2] *= 0.92
        try:
            r = minimize(loss, x0, method="SLSQP", bounds=bounds,
                         constraints=[{"type": "ineq",
                                       "fun": lambda x: C_budget - cost(x)}],
                         options={"maxiter": 1000, "ftol": 1e-14})
            if r.success and (best is None or r.fun < best.fun):
                best = r
        except Exception:
            pass
    return best


def main():
    print("=" * 78)
    print("问题三 · 补齐3：PELT 变点检测识别结构性转移")
    print("=" * 78)

    budgets = np.logspace(17.5, 25.5, 81)
    print(f"\n预算扫描: 10^{np.log10(budgets[0]):.1f} – 10^{np.log10(budgets[-1]):.1f}"
          f"，共 {len(budgets)} 点")

    rows = []
    for Cb in budgets:
        r = solve(Cb)
        if r is None:
            print("  求解失败 at", Cb); continue
        N, D, Q = r.x
        ct = 6*N*D; cq = D*max(g_pow(Q)-g_pow(Q0), 0); ca = ETA*N*D*L
        tot = ct+cq+ca
        rows.append({"logC": np.log10(Cb), "N": N, "D": D, "Q": Q,
                     "loss": E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA,
                     "s_train": ct/tot, "s_Q": cq/tot, "s_attn": ca/tot,
                     "util": tot/Cb, "r_DN": D/N,
                     "kN": np.nan, "kD": np.nan})
    df = pd.DataFrame(rows).sort_values("logC").reset_index(drop=True)
    df["lnN"] = np.log(df.N); df["lnD"] = np.log(df.D); df["lnC"] = np.log(10**df.logC)
    df["kN"] = df.lnN.diff()/df.lnC.diff()
    df["kD"] = df.lnD.diff()/df.lnC.diff()
    print(f"成功求解 {len(df)} 点")

    print("\n--- 处理后的关键统计 ---")
    print(f"  D/N 范围: [{df.r_DN.min():.3f}, {df.r_DN.max():.3f}]  均值 {df.r_DN.mean():.3f}")
    print(f"  利用率范围: [{df.util.min():.4f}, {df.util.max():.4f}]  均值 {df.util.mean():.4f}")
    print(f"  κ_N 均值 {df.kN.mean():.4f}  κ_D 均值 {df.kD.mean():.4f}")

    # ---- PELT 变点检测 ----
    print("\n" + "=" * 78)
    print("PELT 变点检测（ruptures，rbf 核 + L2 代价模型交叉验证）")
    print("=" * 78)
    signals = {
        "份额向量 s(C)": df[["s_train", "s_Q", "s_attn"]].values,
        "标度指数 κ_N": df[["kN"]].dropna().values,
        "log N*": df[["lnN"]].values,
        "log D*": df[["lnD"]].values,
        "log(D/N)": np.log(df[["r_DN"]].values),
    }
    cp_res = {}
    for name, sig in signals.items():
        for model_name, mdl in [("l2", rpt.Pelt(model="l2")),
                                ("rbf", rpt.Pelt(model="rbf"))]:
            try:
                if model_name == "rbf":
                    mdl = rpt.Pelt(model="rbf").fit(sig)
                    cps = mdl.predict(pen=3.0)
                else:
                    mdl = rpt.Pelt(model="l2").fit(sig)
                    cps = mdl.predict(pen=0.5)
                cps = [c for c in cps if c < len(df)]
                lgs = [round(float(df.logC.iloc[c]), 2) for c in cps]
                cp_res[f"{name}|{model_name}"] = lgs
                print(f"  {name:20s} [{model_name:3s}]: 变点 logC = {lgs}")
            except Exception as ex:
                print(f"  {name:20s} [{model_name:3s}]: 失败 {ex}")

    # ---- 汇总：变点位置的众数 ----
    print("\n" + "-" * 78)
    all_cps = []
    for k, v in cp_res.items():
        all_cps.extend(v)
    if all_cps:
        from collections import Counter
        cnt = Counter([round(c, 0) for c in all_cps])
        print("\n变点位置汇总（按出现频次）:")
        for lg, n in cnt.most_common():
            print(f"  logC ≈ {lg:.0f}  (出现 {n} 次, 对应 C ≈ {10**lg:.2e} FLOPs)")
        main_cp = cnt.most_common(1)[0][0]
        print(f"\n  ⟹ 主要结构性转移点 C* ≈ 10^{main_cp:.0f} = {10**main_cp:.2e} FLOPs")
    else:
        main_cp = None
        print("  未检出变点")

    # 与 M1/M4 对照
    ss = json.load(open(os.path.join(OUT, "q3_structural_shift.json"), encoding="utf-8"))
    print(f"\n  与 M1 主导成分切换点对照: logC = "
          f"{[round(c['logC'],2) for c in ss['M1_dominant_changes']]}")

    out = {
        "scan": {"n": len(df), "logC_range": [float(df.logC.min()), float(df.logC.max())],
                 "L": L},
        "pelt_changepoints": cp_res,
        "main_changepoint_logC": float(main_cp) if main_cp else None,
        "main_changepoint_C": float(10**main_cp) if main_cp else None,
        "cross_check_M1_logC": [round(c["logC"], 2) for c in ss["M1_dominant_changes"]],
        "table": df[["logC", "N", "D", "Q", "loss", "s_train", "s_Q", "s_attn",
                     "util", "r_DN", "kN", "kD"]].to_dict(orient="records"),
    }
    with open(os.path.join(OUT, "q3_pelt_changepoint.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_pelt_changepoint.json")


if __name__ == "__main__":
    main()
