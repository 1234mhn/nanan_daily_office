#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题三 · 步骤1：算力约束下的资源优化（核心求解）

模型（严格依据题面公式）：
  决策变量: N (参数个数), D (训练Token数), Q (数据质量)
  外生变量: L_ctx (上下文长度, 依据 C7), p (领域配比, 取自问题一/二)

  目标:  min Loss(N,D,Q) = E + A/N^α + B/D^β + C_q·(1-Q)^δ   ← 问题二广义标度律
  约束:  C_train + C_Q + C_attn ≤ C
         C_train = 6ND
         C_Q     = D·[g(Q) − g(Q₀)]⁺
         C_attn  = η·N·D·L_ctx,  η = 2e-4
         N,D > 0,  Q ∈ (0,1]

  预算档位: C ∈ {10^19, 10^22, 10^24} FLOPs
  成本函数: 指数型 / 幂函数型 / 对数渐进型（附录 B 参数）

单位约定（重要）：
  N 用「参数个数」(不是 B)，D 用「Token 数」(不是 B)
  因为 C = 6ND 中 N、D 是原始个数
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from itertools import product

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
C7 = os.path.join(BASE, "real_attachments", "C_efficiency_evolution",
                  "model_architecture_metadata.csv")

# ---- 问题二广义标度律参数（加性模型，主模型）----
g = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
_p = g["model_B_additive"]["params"]
E, A_, ALPHA, B_, BETA, CQ_, DELTA = (_p["E"], _p["A"], _p["alpha"],
                                     _p["B"], _p["beta"], _p["C"], _p["delta"])
print(f"标度律参数: E={E:.5f} A={A_:.4f} α={ALPHA:.5f} B={B_:.4f} β={BETA:.5f} "
      f"C={CQ_:.5f} δ={DELTA:.5f}")

ETA = 2e-4
L_CRIT = 6 / ETA          # 临界上下文长度 = 30000

# ---- 成本函数（附录 B）----
def g_exp(Q, gamma=1e7, lam=6.0):
    return gamma * np.exp(lam * Q)

def g_pow(Q, gamma=5e9, lam=4.0):
    return gamma * Q ** lam

def g_log(Q, gamma=2e9, lam=10.0):
    return gamma * np.log(1 + lam * Q)

COST_FUNCS = {"指数型": g_exp, "幂函数型": g_pow, "对数渐进型": g_log}


def loss_fn(N, D, Q):
    return E + A_ / N**ALPHA + B_ / D**BETA + CQ_ * (1 - Q) ** DELTA


def make_constraint(gfun, Q0, L, C_budget):
    def total_cost(x):
        N, D, Q = x
        c_train = 6 * N * D
        c_q = D * max(gfun(Q) - gfun(Q0), 0.0)
        c_attn = ETA * N * D * L
        return c_train + c_q + c_attn - C_budget
    return total_cost


def solve_one(C_budget, L, gfun, Q0=0.5, n_starts=300, seed=20260923):
    """对给定预算和 L 求最优 (N,D,Q)"""
    rng = np.random.default_rng(seed)
    # 变量用对数尺度搜索 N, D；Q 在 (Q0,1]
    best = None
    bounds = [(1e5, 1e14), (1e6, 1e16), (Q0 + 1e-6, 1.0)]
    cons = [{"type": "ineq", "fun": lambda x: -make_constraint(gfun, Q0, L, C_budget)(x)}]

    # 解析估计起点：Chinchilla 比例 D ≈ 20N
    for _ in range(n_starts):
        # 先估算 N 的合理量级
        n_scale = rng.uniform(-2, 2)
        N0 = 10 ** (rng.uniform(6, 11) + n_scale)
        D0 = 20 * N0
        Q0s = rng.uniform(Q0, 1.0)
        x0 = np.array([N0, D0, Q0s])
        # 投影到可行域内
        try:
            for _t in range(60):
                if make_constraint(gfun, Q0, L, C_budget)(x0) <= 0:
                    break
                x0[:2] *= 0.5
        except Exception:
            continue
        try:
            r = minimize(lambda x: loss_fn(x[0], x[1], x[2]), x0, method="SLSQP",
                         bounds=bounds, constraints=cons,
                         options={"maxiter": 500, "ftol": 1e-12})
            if r.success and (best is None or r.fun < best.fun):
                best = r
        except Exception:
            pass
    return best


def main():
    print("=" * 78)
    print("问题三 · 算力约束下的资源优化")
    print("=" * 78)
    print(f"临界上下文长度 L_crit = 6/η = {L_CRIT:.0f}")

    # ---- C7 的上下文长度取值 ----
    c7 = pd.read_csv(C7)
    Ls = sorted(c7["max_position_embeddings"].dropna().unique())
    print(f"\nC7 上下文长度取值: {Ls}")

    budgets = {"低": 1e19, "中": 1e22, "高": 1e24}
    Q0 = 0.5

    # ---- 主分析：幂函数型（决策 3.2 = B）----
    print("\n" + "=" * 78)
    print("主结果：幂函数型成本（决策 3.2 选 B）")
    print("=" * 78)
    main_results = {}
    for bname, Cb in budgets.items():
        row = {}
        print(f"\n--- 预算 {bname}: C = {Cb:.0e} FLOPs ---")
        for L in Ls:
            r = solve_one(Cb, L, g_pow, Q0)
            if r is None:
                print(f"  L={L:>7}: 求解失败")
                continue
            N, D, Q = r.x
            Lv = loss_fn(N, D, Q)
            ct = 6 * N * D
            cq = D * max(g_pow(Q) - g_pow(Q0), 0)
            ca = ETA * N * D * L
            row[str(L)] = {"N": float(N), "D": float(D), "Q": float(Q),
                           "loss": float(Lv), "C_train": float(ct),
                           "C_Q": float(cq), "C_attn": float(ca),
                           "attn_share": float(ca / Cb),
                           "train_share": float(ct / Cb), "Q_share": float(cq / Cb)}
            print(f"  L={L:>7}: N={N/1e9:8.4f}B  D={D/1e9:10.4f}B  Q={Q:.4f}  "
                  f"Loss={Lv:.4f}  [训练{ct/Cb:5.1%} 质量{cq/Cb:5.1%} 注意力{ca/Cb:5.1%}]")
        main_results[bname] = row

    # ---- 成本函数对比（决策 3.2：三种都做敏感性分析）----
    print("\n" + "=" * 78)
    print("成本函数对比（L=8192, 三种成本函数）")
    print("=" * 78)
    cost_compare = {}
    for q0 in [0.5, 0.7]:
        for fname, f in COST_FUNCS.items():
            row = {}
            for bname, Cb in budgets.items():
                r = solve_one(Cb, 8192, f, q0)
                if r is None:
                    row[bname] = None; continue
                N, D, Q = r.x
                row[bname] = {"N": float(N), "D": float(D), "Q": float(Q),
                              "loss": float(loss_fn(N, D, Q))}
            cost_compare[f"{fname}_Q0={q0}"] = row
            if q0 == 0.5:
                print(f"\n  [Q0={q0}] {fname}")
                for bname in budgets:
                    if row[bname]:
                        v = row[bname]
                        print(f"    {bname}: N={v['N']/1e9:8.4f}B D={v['D']/1e9:10.4f}B "
                              f"Q={v['Q']:.4f} Loss={v['loss']:.4f}")

    # ---- 保存 ----
    out = {
        "model": {
            "loss": "L = E + A/N^α + B/D^β + C(1-Q)^δ",
            "loss_params": {"E": E, "A": A_, "alpha": ALPHA, "B": B_,
                            "beta": BETA, "C": CQ_, "delta": DELTA},
            "cost": {"train": "6ND", "quality": "D[g(Q)-g(Q0)]+",
                     "attn": "η N D L,  η=2e-4"},
            "L_crit": float(L_CRIT),
        },
        "C7_context_values": [int(x) for x in Ls],
        "Q0": Q0,
        "main_power_law": main_results,
        "cost_function_comparison": cost_compare,
        "cost_func_params": {"指数型": {"gamma": 1e7, "lambda": 6.0, "form": "γe^(λQ)"},
                             "幂函数型": {"gamma": 5e9, "lambda": 4.0, "form": "γQ^λ"},
                             "对数渐进型": {"gamma": 2e9, "lambda": 10.0,
                                            "form": "γln(1+λQ)"}},
    }
    with open(os.path.join(OUT, "q3_optimization.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q3_optimization.json")


if __name__ == "__main__":
    main()
