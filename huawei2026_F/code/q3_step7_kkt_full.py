#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 补齐2：三方向完整 KKT 解析条件

题面/规范要求给出"三方向边际收益相等"的 KKT 解析条件。

拉格朗日函数（预算约束取等号，λ 为乘子）：
  Λ = L(N,D,Q) + λ[ C_tot(N,D,Q) − C ]

三方向一阶条件 ∂Λ/∂N = ∂Λ/∂D = ∂Λ/∂Q = 0：

  ∂L/∂N = −A·α·N^(−α−1)
  ∂C/∂N = 6D + η·D·L
  ⟹  A·α·N^(−α−1) = λ·D·(6 + ηL)                    ... (K1)

  ∂L/∂D = −B·β·D^(−β−1)
  ∂C/∂D = 6N + [g(Q)−g(Q0)] + η·N·L
  ⟹  B·β·D^(−β−1) = λ·[6N + (g(Q)−g(Q0)) + η·N·L]     ... (K2)

  ∂L/∂Q = −C·δ·(1−Q)^(δ−1)
  ∂C/∂Q = D·g'(Q)
  ⟹  C·δ·(1−Q)^(δ−1) = λ·D·g'(Q)                      ... (K3)

由 K1/K2 相除消去 λ，可得 N–D 的最优关系；由 K3 与 K1 相除可得 Q–N 关系。

输出：results/q3_kkt_full.json
"""
import os, json
import numpy as np
from scipy.optimize import brentq

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

g2 = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
p = g2["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ, DELTA = (p["E"], p["A"], p["alpha"], p["B"],
                                     p["beta"], p["C"], p["delta"])
ETA = 2e-4
g_pow = lambda Q: 5e9 * Q**4
gp_pow = lambda Q: 2e10 * Q**3      # g'(Q) for γ=5e9, λ=4
Q0 = 0.5


def main():
    print("=" * 78)
    print("问题三 · 补齐2：三方向完整 KKT 解析条件")
    print("=" * 78)

    print("\n拉格朗日函数:  Λ = L(N,D,Q) + λ[C_tot(N,D,Q) − C]")
    print("\n三方向一阶必要条件（取等号约束）:")
    print("  (K1) ∂Λ/∂N = 0 :  A·α·N^(−α−1) = λ·D·(6 + ηL)")
    print("  (K2) ∂Λ/∂D = 0 :  B·β·D^(−β−1) = λ·[6N + (g(Q)−g(Q0)) + ηNL]")
    print("  (K3) ∂Λ/∂Q = 0 :  C·δ·(1−Q)^(δ−1) = λ·D·g'(Q)")

    # ---- 由 K1/K2 消 λ 得 N-D 关系 ----
    print("\n" + "-" * 78)
    print("(A) 由 K1/K2 消去 λ，得到 N–D 的最优关系（L_ctx=8192, Q=1）")
    print("-" * 78)
    L = 8192

    def ratio_eq(N, D, Q):
        """K1/K2 相除后左右两侧之差"""
        lhs = (A_*ALPHA*N**(-ALPHA-1)) / (B_*BETA*D**(-BETA-1))
        rhs = (6 + ETA*L) / (6*N/D + (g_pow(Q)-g_pow(Q0))/D + ETA*L*N/D)
        return lhs - rhs

    # Q=1 时 g(Q)-g(Q0) 项
    Q = 1.0
    print(f"\n  理论推导：α≈β≈0.29 且数值接近，故 N 与 D 量级应相近（而非 20:1）")
    print(f"  数值验证（给定 N，解出最优 D）:")
    rows = []
    for N in [1e8, 1e9, 1e10, 1e11]:
        try:
            # 简化：在 Q=1 下，K1/K2 给出 N^α/D^β 关系
            # A·α·N^(-α-1) / (B·β·D^(-β-1)) = (6+ηL)/(6N/D + ηLN/D)
            f = lambda lD: (A_*ALPHA*N**(-ALPHA-1)) / (B_*BETA*(10**lD)**(-BETA-1)) \
                - (6+ETA*L) / (6*N/(10**lD) + ETA*L*N/(10**lD))
            lD = brentq(f, 5, 17)
            D = 10**lD
            rows.append({"N": N, "D_opt": float(D), "r_DN": float(D/N)})
            print(f"    N={N:.0e} → D_opt={D:.4e}  D/N={D/N:.4f}")
        except Exception as ex:
            print(f"    N={N:.0e} → 求解失败 {ex}")

    # ---- (B) Q 方向：解析说明 Q→1 ----
    print("\n" + "-" * 78)
    print("(B) Q 方向的 KKT (K3)：解析说明 Q*→1 的机理")
    print("-" * 78)
    print(f"\n  K3:  C·δ·(1−Q)^(δ−1) = λ·D·g'(Q)")
    print(f"  其中 C={CQ:.5f}, δ={DELTA:.5f}, δ−1={DELTA-1:.5f}")
    print(f"\n  左边 = C·δ·(1−Q)^(δ−1)：Q→1 时 (1−Q)^(−0.00948) → +∞")
    print(f"  右边 = λ·D·g'(Q)：g'(Q)=2×10¹⁰·Q³ 有限")
    print(f"\n  为使等式成立需要 λ → 0，即预算约束的『影子价格』趋于零，")
    print(f"  意味着在最优解处预算对质量维度的边际约束已完全松弛。")
    print(f"  ⟹ Q* 必然取上界（本题中 Q_max=1）")

    print(f"\n  数值验证 λ 随 Q 的变化:")
    for Qv in [0.5, 0.8, 0.9, 0.95, 0.99]:
        lhs = CQ*DELTA*(1-Qv)**(DELTA-1)
        print(f"    Q={Qv:.2f}: 左边(K3) = {lhs:.4e}  → 需 λ·D·g'(Q) 达到同量级")

    # ---- (C) 三方向边际收益完全形式的数值验证 ----
    print("\n" + "-" * 78)
    print("(C) 在最终最优解处验证三方向 KKT 条件（数值）")
    print("-" * 78)
    fl = json.load(open(os.path.join(OUT, "q3_flatness.json"), encoding="utf-8"))
    res = {}
    for bn, v in fl["final_recommended"].items():
        r = v["refined"]
        N, D, Q = r["N"], r["D"], r["Q"]
        # 边际收益（Loss 对各变量的偏导，取绝对值）
        dL_N = A_*ALPHA*N**(-ALPHA-1)
        dL_D = B_*BETA*D**(-BETA-1)
        dL_Q = CQ*DELTA*(1-Q)**(DELTA-1) if Q < 1 else float("inf")
        # 边际成本
        dC_N = D*(6 + ETA*L)
        dC_D = 6*N + (g_pow(Q)-g_pow(Q0)) + ETA*N*L
        dC_Q = D*gp_pow(Q)
        # 单位成本的边际收益（应三方向相等 = λ）
        lam_N = dL_N/dC_N if dC_N else np.nan
        lam_D = dL_D/dC_D if dC_D else np.nan
        lam_Q = dL_Q/dC_Q if (dC_Q and np.isfinite(dL_Q)) else np.nan
        res[bn] = {"N": N, "D": D, "Q": Q,
                   "dL_dN": float(dL_N), "dL_dD": float(dL_D),
                   "dL_dQ": float(dL_Q) if np.isfinite(dL_Q) else None,
                   "dC_dN": float(dC_N), "dC_dD": float(dC_D), "dC_dQ": float(dC_Q),
                   "lambda_N_eff": float(lam_N), "lambda_D_eff": float(lam_D),
                   "lambda_Q_eff": float(lam_Q) if np.isfinite(lam_Q) else None}
        print(f"\n  {bn}:  N={N/1e9:.4f}B D={D/1e9:.3f}B Q={Q:.4f}")
        print(f"    λ_eff(N) = |∂L/∂N|/(∂C/∂N) = {lam_N:.6e}")
        print(f"    λ_eff(D) = |∂L/∂D|/(∂C/∂D) = {lam_D:.6e}")
        if np.isfinite(lam_Q):
            print(f"    λ_eff(Q) = |∂L/∂Q|/(∂C/∂Q) = {lam_Q:.6e}")
        print(f"    → N 与 D 两方向的单位成本边际收益"
              f"{'一致 ✅' if abs(lam_N-lam_D)/max(lam_N,lam_D) < 0.05 else '不一致 ⚠️'}"
              f"（相对差 {abs(lam_N-lam_D)/max(lam_N,lam_D)*100:.3f}%）")

    out = {
        "lagrangian": "Λ = L(N,D,Q) + λ[C_tot(N,D,Q) − C]",
        "KKT_conditions": {
            "K1_N": "A·α·N^(−α−1) = λ·D·(6 + ηL)",
            "K2_D": "B·β·D^(−β−1) = λ·[6N + (g(Q)−g(Q0)) + ηNL]",
            "K3_Q": "C·δ·(1−Q)^(δ−1) = λ·D·g'(Q)",
        },
        "ND_relation": rows,
        "Q_mechanism": ("K3 中左边在 Q→1 时发散、右边有限，"
                        "故需 λ→0，即预算约束在质量维度上松弛，Q*→1"),
        "numerical_verification": res,
    }
    with open(os.path.join(OUT, "q3_kkt_full.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_kkt_full.json")


if __name__ == "__main__":
    main()
