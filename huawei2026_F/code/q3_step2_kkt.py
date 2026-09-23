#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 步骤2：KKT 分析与"Q是否真的拉满"的严格验证

疑点：主求解中 Q 全部顶到 1.0，与陷阱描述的"Q*=1 质量拉满"表面一致。
      但陷阱说这是 FALSE。需要严格判断：
      - 是求解器问题（搜索陷入边界），还是真实最优？
      - 用 KKT 条件验证

分析思路：
  约束 g(N,D,Q) = 6ND + D[g(Q)-g(Q0)] + ηNDL - C ≤ 0
  拉格朗日 L = Loss + λ·(cost - C)
  KKT 必要条件：
    ∂Loss/∂N = -λ·∂cost/∂N
    ∂Loss/∂D = -λ·∂cost/∂D
    ∂Loss/∂Q = -λ·∂cost/∂Q     ← 若 Q 在内点

  关键：∂Loss/∂Q = -C_q·δ(1-Q)^(δ-1) < 0（Q 越大 Loss 越小）
        ∂cost/∂Q = D·g'(Q) > 0（Q 越大成本越高）
        当 Q→1 时，(1-Q)^(δ-1) → +∞（δ=0.99<1），所以 ∂Loss/∂Q → -∞
        → 只要预算允许，Q 必然趋向 1！

  这是 δ<1 导致的数学性质：质量提升的边际收益在 Q→1 时发散。
  所以 Q*=1 在成本函数尺度相对较小时是"真最优"，但需说明其现实局限。

输出：results/q3_kkt_analysis.json
"""
import os, json
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

g2 = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
_p = g2["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ, DELTA = (_p["E"], _p["A"], _p["alpha"], _p["B"],
                                     _p["beta"], _p["C"], _p["delta"])
ETA = 2e-4


def analyze(C, L, gQ, gQ0, D_val, Q_pct):
    """
    在给定 D 和 Q 分位下，考察质量边际收益 vs 边际成本
    """
    # 质量项成本：D[g(Q)-g(Q0)]
    return None


def main():
    print("=" * 78)
    print("问题三 · Q 最优性的 KKT 严格分析")
    print("=" * 78)

    print(f"\n标度律质量项: C_q·(1-Q)^δ,  C_q={CQ:.5f},  δ={DELTA:.5f}")
    print(f"  注意 δ = {DELTA:.5f} < 1")
    print(f"\n质量提升的边际收益: ∂Loss/∂Q = -C_q·δ·(1-Q)^(δ-1)")
    print(f"  当 Q→1 时, (1-Q)^(δ-1) → +∞  (因为 δ-1 = {DELTA-1:.5f} < 0)")
    print(f"  → 边际收益在 Q→1 处发散（趋于无穷大）")

    print(f"\n质量提升的边际成本: ∂cost/∂Q = D·g'(Q)")
    for nm, gp in [("指数型 γe^(λQ)", lambda Q: 1e7*6.0*np.exp(6.0*Q)),
                   ("幂函数型 γQ^λ", lambda Q: 5e9*4.0*Q**3),
                   ("对数渐进型 γln(1+λQ)", lambda Q: 2e9*10.0/(1+10.0*Q))]:
        vals = [gp(q) for q in [0.5, 0.8, 0.9, 0.95, 0.99]]
        print(f"  {nm:22s}: g'(0.5)={vals[0]:.3e}, g'(0.9)={vals[2]:.3e}, g'(0.99)={vals[4]:.3e}")

    print(f"\n结论推导:")
    print(f"  边际收益 → ∞，边际成本有限 → KKT 条件在 Q<1 时无法满足")
    print(f"  → Q*=1 是【真最优】，不是求解器问题")
    print(f"  但这是 δ<1 的数学性质导致的，须在论文中说明现实局限：")
    print(f"     (a) 实际中质量不可能达到理论完美 (Q=1)；")
    print(f"     (b) 应引入质量上界 Q_max<1 或更陡的成本函数做敏感性分析。")

    # ---- 验证：加入质量上界后的最优 ----
    print("\n" + "=" * 78)
    print("敏感性：引入质量上界 Q_max < 1 后的最优配置")
    print("=" * 78)

    from scipy.optimize import minimize

    def solve_with_qmax(C_budget, L, gfun, Q0, Qmax, seed=20260923):
        rng = np.random.default_rng(seed)
        best = None
        bounds = [(1e5, 1e14), (1e6, 1e16), (Q0 + 1e-6, Qmax)]

        def cost(x):
            N, D, Q = x
            return 6*N*D + D*max(gfun(Q)-gfun(Q0), 0) + ETA*N*D*L

        def loss(x):
            N, D, Q = x
            return E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA

        for _ in range(200):
            N0 = 10**rng.uniform(6, 11)
            x0 = np.array([N0, 20*N0, rng.uniform(Q0, Qmax)])
            for _t in range(60):
                if cost(x0) <= C_budget: break
                x0[:2] *= 0.5
            try:
                r = minimize(loss, x0, method="SLSQP", bounds=bounds,
                             constraints=[{"type": "ineq", "fun": lambda x: C_budget - cost(x)}],
                             options={"maxiter": 500, "ftol": 1e-12})
                if r.success and (best is None or r.fun < best.fun):
                    best = r
            except Exception:
                pass
        return best

    g_pow = lambda Q: 5e9 * Q**4
    res = {}
    for Qmax in [1.0, 0.95, 0.90, 0.80, 0.70]:
        row = {}
        for bn, Cb in [("低", 1e19), ("中", 1e22), ("高", 1e24)]:
            r = solve_with_qmax(Cb, 8192, g_pow, 0.5, Qmax)
            if r is None: continue
            N, D, Q = r.x
            row[bn] = {"N": float(N), "D": float(D), "Q": float(Q),
                       "loss": float(E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA),
                       "at_bound": bool(abs(Q - Qmax) < 1e-4)}
        res[f"Qmax={Qmax}"] = row
        print(f"\n  Q_max = {Qmax}")
        for bn in ["低", "中", "高"]:
            if bn in row:
                v = row[bn]
                tag = "← 顶到上界" if v["at_bound"] else "← 内点解"
                print(f"    {bn}: N={v['N']/1e9:8.4f}B D={v['D']/1e9:10.4f}B "
                      f"Q={v['Q']:.4f} Loss={v['loss']:.4f} {tag}")

    out = {
        "kkt_conclusion": {
            "delta": DELTA,
            "marginal_benefit": "∂Loss/∂Q = -C_q·δ(1-Q)^(δ-1) → -∞ as Q→1",
            "marginal_cost": "∂cost/∂Q = D·g'(Q) finite",
            "verdict": "Q*=1 在无质量上界时是真最优（非求解器缺陷）",
            "reason": "δ<1 使质量边际收益在 Q→1 处发散",
            "remedy": "引入 Q_max<1 或更陡成本函数做敏感性分析",
        },
        "qmax_sensitivity": res,
    }
    with open(os.path.join(OUT, "q3_kkt_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_kkt_analysis.json")


if __name__ == "__main__":
    main()
