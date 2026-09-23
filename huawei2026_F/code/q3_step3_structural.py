#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 步骤3：结构性转移的数学定义与识别

题面要求：
  "当预算 C 跨越不同量级时，资源分配是否出现结构性转移（最优策略发生质的变化），
   并给出明确的数学定义与识别方法。"

本步任务：
  1. 给出结构性转移的【数学定义】
  2. 设计可执行的【识别方法】
  3. 用实际计算结果检验是否发生转移

数学定义（本问采用）：
  设最优解映射 x*(C) = (N*(C), D*(C), Q*(C))，定义【结构指标】：
    θ(C) = (log N*(C), log D*(C), Q*(C))        归一化后
    s(C) = 各成本分项的占比向量 (share_train, share_Q, share_attn)

  定义【结构性转移点】C*：
    存在 C* 使得 θ(C) 的一阶导数在 C* 处出现不连续（跳跃），
    或主导成分（argmax share）发生切换。

识别方法（三种，交叉验证）：
  M1 成本占比切换法：主导项 argmax(share) 变化
  M2 弹性突变法：局部幂指数 κ = dlnN*/dlnC 的突变
  M3 配比不变式检验：Chinchilla 比 r = D/N 的定性变化

输出：results/q3_structural_shift.json
"""
import os, json
import numpy as np
from scipy.optimize import minimize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

g2 = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
_p = g2["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ, DELTA = (_p["E"], _p["A"], _p["alpha"], _p["B"],
                                     _p["beta"], _p["C"], _p["delta"])
ETA = 2e-4
g_pow = lambda Q: 5e9 * Q**4


def solve(C_budget, L, Q0=0.5, Qmax=1.0, n_starts=150, seed=20260923):
    rng = np.random.default_rng(seed)
    best = None
    bounds = [(1e4, 1e15), (1e5, 1e17), (Q0 + 1e-6, Qmax)]

    def cost(x):
        N, D, Q = x
        return 6*N*D + D*max(g_pow(Q)-g_pow(Q0), 0) + ETA*N*D*L

    def loss(x):
        N, D, Q = x
        return E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA

    for _ in range(n_starts):
        N0 = 10**rng.uniform(5, 12)
        x0 = np.array([N0, 20*N0, rng.uniform(Q0, Qmax)])
        for _t in range(80):
            if cost(x0) <= C_budget: break
            x0[:2] *= 0.5
        try:
            r = minimize(loss, x0, method="SLSQP", bounds=bounds,
                         constraints=[{"type": "ineq",
                                       "fun": lambda x: C_budget - cost(x)}],
                         options={"maxiter": 600, "ftol": 1e-13})
            if r.success and (best is None or r.fun < best.fun):
                best = r
        except Exception:
            pass
    return best


def main():
    print("=" * 78)
    print("问题三 · 结构性转移的数学定义与识别")
    print("=" * 78)

    L = 8192
    # 跨 6 个量级的预算扫描
    budgets = np.logspace(18, 25, 43)   # 10^18 ... 10^25
    print(f"\n预算扫描: 10^{np.log10(budgets[0]):.0f} ... 10^{np.log10(budgets[-1]):.0f} "
          f"共 {len(budgets)} 个点, L={L}")

    rows = []
    for Cb in budgets:
        r = solve(Cb, L)
        if r is None:
            continue
        N, D, Q = r.x
        ct = 6*N*D; cq = D*max(g_pow(Q)-g_pow(0.5), 0); ca = ETA*N*D*L
        tot = ct+cq+ca
        rows.append({"C": float(Cb), "logC": float(np.log10(Cb)),
                     "N": float(N), "D": float(D), "Q": float(Q),
                     "loss": float(E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA),
                     "share_train": float(ct/tot), "share_Q": float(cq/tot),
                     "share_attn": float(ca/tot), "r_DN": float(D/N)})

    import pandas as pd
    df = pd.DataFrame(rows)
    print(f"成功求解 {len(df)} 个预算点")

    print("\n--- 预算扫描结果（每 6 个点打印一次）---")
    print(f"{'logC':>6} {'N(B)':>10} {'D(B)':>12} {'Q':>7} {'Loss':>8} "
          f"{'训练%':>7} {'质量%':>7} {'注意力%':>8} {'D/N':>8}")
    for i in range(0, len(df), 6):
        r = df.iloc[i]
        print(f"{r.logC:>6.1f} {r.N/1e9:>10.4f} {r.D/1e9:>12.3f} {r.Q:>7.4f} "
              f"{r.loss:>8.4f} {r.share_train*100:>7.2f} {r.share_Q*100:>7.2f} "
              f"{r.share_attn*100:>8.2f} {r.r_DN:>8.2f}")
    r = df.iloc[-1]
    print(f"{r.logC:>6.1f} {r.N/1e9:>10.4f} {r.D/1e9:>12.3f} {r.Q:>7.4f} "
          f"{r.loss:>8.4f} {r.share_train*100:>7.2f} {r.share_Q*100:>7.2f} "
          f"{r.share_attn*100:>8.2f} {r.r_DN:>8.2f}")

    # ---- M1 主导成分切换 ----
    print("\n" + "=" * 78)
    print("识别方法 M1：主导成本成分切换法")
    print("=" * 78)
    df["dominant"] = df[["share_train", "share_Q", "share_attn"]].idxmax(axis=1)
    chg = df[df.dominant != df.dominant.shift()]
    print("\n  主导成分变化点:")
    for _, r in chg.iterrows():
        print(f"    logC={r.logC:5.1f} (C={r.C:.2e}) → 主导 = {r.dominant} "
              f"(训练{r.share_train:.1%} 质量{r.share_Q:.1%} 注意力{r.share_attn:.1%})")

    # ---- M2 弹性突变 ----
    print("\n" + "=" * 78)
    print("识别方法 M2：规模弹性 κ = dlnN*/dlnC 及 κ_D = dlnD*/dlnC")
    print("=" * 78)
    df["lnN"] = np.log(df.N); df["lnD"] = np.log(df.D)
    df["lnC"] = np.log(df.C)
    df["kN"] = df.lnN.diff() / df.lnC.diff()
    df["kD"] = df.lnD.diff() / df.lnC.diff()
    print(f"\n  {'logC':>6} {'κ_N':>8} {'κ_D':>8}")
    for i in range(1, len(df), 5):
        r = df.iloc[i]
        if pd.notna(r.kN):
            print(f"  {r.logC:>6.1f} {r.kN:>8.4f} {r.kD:>8.4f}")
    print(f"\n  κ_N 均值 = {df.kN.mean():.4f}  (std={df.kN.std():.4f})")
    print(f"  κ_D 均值 = {df.kD.mean():.4f}  (std={df.kD.std():.4f})")
    print("  → 若 κ_N ≈ κ_D ≈ 常数，说明是【平滑演进】而非结构突变")

    # ---- M3 Chinchilla 比 ----
    print("\n" + "=" * 78)
    print("识别方法 M3：Chinchilla 比 r = D/N 的定性变化")
    print("=" * 78)
    print(f"\n  r = D/N 范围: [{df.r_DN.min():.2f}, {df.r_DN.max():.2f}]")
    print(f"  r 均值 = {df.r_DN.mean():.2f} (Chinchilla 参考值 ≈ 20)")
    for i in range(0, len(df), 8):
        r = df.iloc[i]
        print(f"    logC={r.logC:5.1f}: r={r.r_DN:7.2f}  N={r.N/1e9:8.4f}B D={r.D/1e9:10.3f}B")

    # ---- 汇总判定 ----
    print("\n" + "=" * 78)
    print("结构性转移判定")
    print("=" * 78)
    n_dom_changes = len(chg) - 1
    print(f"  M1 主导成分切换次数: {n_dom_changes}")
    print(f"  M2 κ_N 变异系数: {df.kN.std()/abs(df.kN.mean()):.4f}")
    verdict = ("发生结构性转移（主导成分切换）" if n_dom_changes > 0
               else "未发生主导成分切换，呈平滑演进")
    print(f"  判定: {verdict}")

    out = {
        "definition": {
            "optimal_map": "x*(C) = (N*(C), D*(C), Q*(C))",
            "structural_indicator": "θ(C) = (lnN*, lnD*, Q*); s(C) = 成本占比向量",
            "structural_shift_point": ("存在 C* 使 θ'(C) 在 C* 处不连续，"
                                       "或主导成分 argmax(s(C)) 发生切换"),
            "identification_methods": ["M1 主导成分切换", "M2 弹性突变", "M3 Chinchilla比定性变化"],
        },
        "scan": {"L": L, "n_points": len(df),
                 "C_range": [float(df.C.min()), float(df.C.max())]},
        "M1_dominant_changes": [{"logC": float(r.logC), "C": float(r.C),
                                 "dominant": r.dominant,
                                 "shares": {"train": float(r.share_train),
                                            "Q": float(r.share_Q),
                                            "attn": float(r.share_attn)}}
                                for _, r in chg.iterrows()],
        "M2_elasticity": {"kN_mean": float(df.kN.mean()), "kN_std": float(df.kN.std()),
                          "kD_mean": float(df.kD.mean()), "kD_std": float(df.kD.std())},
        "M3_chinchilla_ratio": {"min": float(df.r_DN.min()), "max": float(df.r_DN.max()),
                                "mean": float(df.r_DN.mean())},
        "verdict": verdict,
        "table": df[["logC", "N", "D", "Q", "loss", "share_train", "share_Q",
                     "share_attn", "r_DN"]].to_dict(orient="records"),
    }
    with open(os.path.join(OUT, "q3_structural_shift.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_structural_shift.json")


if __name__ == "__main__":
    main()
