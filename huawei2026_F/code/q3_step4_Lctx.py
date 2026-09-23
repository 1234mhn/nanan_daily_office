#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 步骤4：上下文长度 L_ctx 敏感性分析

题面要求：
  "L_ctx 的可行取值须依据 C7，须解析给出使注意力开销与训练开销相当的
   临界值 L_ctx^crit = 6/η，并在其可行取值上完成敏感性分析。"

理论：
  C_train = 6ND,  C_attn = ηNDL
  令二者相当: 6ND = ηNDL  →  L = 6/η = 6/2e-4 = 30000

C7 可行取值: 2048, 4096, 8192, 32768, 131072
注意: 32768 和 131072 都超过 L_crit=30000 → 注意力开销超过训练开销

输出：results/q3_Lctx_sensitivity.json
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import minimize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")

g2 = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
_p = g2["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ, DELTA = (_p["E"], _p["A"], _p["alpha"], _p["B"],
                                     _p["beta"], _p["C"], _p["delta"])
ETA = 2e-4
L_CRIT = 6 / ETA
g_pow = lambda Q: 5e9 * Q**4


def solve(C_budget, L, Q0=0.5, n_starts=120, seed=20260923):
    rng = np.random.default_rng(seed)
    best = None
    bounds = [(1e4, 1e15), (1e5, 1e17), (Q0 + 1e-6, 1.0)]

    def cost(x):
        N, D, Q = x
        return 6*N*D + D*max(g_pow(Q)-g_pow(Q0), 0) + ETA*N*D*L

    def loss(x):
        N, D, Q = x
        return E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA

    for _ in range(n_starts):
        N0 = 10**rng.uniform(5, 12)
        x0 = np.array([N0, 20*N0, rng.uniform(Q0, 1.0)])
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
    print("问题三 · 上下文长度 L_ctx 敏感性分析")
    print("=" * 78)
    print(f"\n临界值解析: C_train = 6ND = C_attn = ηNDL  →  L_crit = 6/η = {L_CRIT:.0f}")

    c7 = pd.read_csv(os.path.join(BASE, "real_attachments", "C_efficiency_evolution",
                                  "model_architecture_metadata.csv"))
    Ls = [int(x) for x in sorted(c7.max_position_embeddings.dropna().unique())]
    print(f"C7 可行取值: {Ls}")
    print(f"  {'超临界' if Ls[-1] > L_CRIT else ''}: "
          f"{[L for L in Ls if L > L_CRIT]} 超过 L_crit")

    # ---- 1. 注意力/训练 比值随 L 变化 ----
    print("\n--- 1. C_attn / C_train = L/L_crit 理论比值 ---")
    ratio_tbl = []
    for L in Ls:
        rt = L / L_CRIT
        ratio_tbl.append({"L": L, "ratio_attn_train": rt,
                          "attn_over_train": "超过" if rt > 1 else "未超过"})
        print(f"  L={L:>7}: C_attn/C_train = L/L_crit = {rt:.6f}  "
              f"{'⚠️ 注意力 > 训练' if rt > 1 else '✅ 训练 > 注意力'}")

    # ---- 2. 各预算下最优配置随 L 的变化 ----
    print("\n--- 2. 各预算下最优配置随 L 变化 ---")
    res = {}
    for bn, Cb in [("低(1e19)", 1e19), ("中(1e22)", 1e22), ("高(1e24)", 1e24)]:
        row = {}
        print(f"\n  预算 {bn}:")
        print(f"    {'L':>8} {'N(B)':>10} {'D(B)':>12} {'Q':>7} {'Loss':>8} "
              f"{'训练%':>7} {'质量%':>7} {'注意力%':>8}")
        for L in Ls:
            r = solve(Cb, L)
            if r is None: continue
            N, D, Q = r.x
            ct = 6*N*D; cq = D*max(g_pow(Q)-g_pow(0.5), 0); ca = ETA*N*D*L
            tot = ct+cq+ca
            lv = E + A_/N**ALPHA + B_/D**BETA + CQ*(1-Q)**DELTA
            row[str(L)] = {"N": float(N), "D": float(D), "Q": float(Q),
                           "loss": float(lv), "share_train": float(ct/tot),
                           "share_Q": float(cq/tot), "share_attn": float(ca/tot)}
            print(f"    {L:>8} {N/1e9:>10.4f} {D/1e9:>12.3f} {Q:>7.4f} {lv:>8.4f} "
                  f"{ct/tot*100:>7.2f} {cq/tot*100:>7.2f} {ca/tot*100:>8.2f}")
        res[bn] = row

    # ---- 3. Loss 随 L 的劣化 ----
    print("\n--- 3. 长上下文的 Loss 代价（相对 L=2048）---")
    for bn in res:
        base = res[bn].get("2048")
        if not base: continue
        print(f"  {bn}:")
        for L in Ls:
            v = res[bn].get(str(L))
            if v:
                print(f"    L={L:>7}: Loss={v['loss']:.4f}  "
                      f"Δ={v['loss']-base['loss']:+.5f}  "
                      f"({(v['loss']-base['loss'])/base['loss']*100:+.3f}%)")

    out = {
        "L_crit_analytic": {"formula": "L_crit = 6/η", "eta": ETA,
                            "value": float(L_CRIT),
                            "derivation": "6ND = ηNDL → L = 6/η"},
        "C7_feasible_values": Ls,
        "attention_over_train_ratio": ratio_tbl,
        "opt_by_budget_and_L": res,
    }
    with open(os.path.join(OUT, "q3_Lctx_sensitivity.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_Lctx_sensitivity.json")


if __name__ == "__main__":
    main()
