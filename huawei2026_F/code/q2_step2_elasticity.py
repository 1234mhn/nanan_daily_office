#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题二 · 步骤2：外部验证的正确口径 + 尺度调整 + 弹性分析

发现：B8 的 N 达 700B、D 达 2000B，远超训练集（N≤12B, D≤600B），
      Loss 低至 0.5（训练最低 2.0）→ 属真外推，R² 为负是必然。

正确做法（决策 1.3 思路移植 + 诚实报告）：
  1. 区分 B8 的「插值区」（落在训练范围内）与「外推区」（超出）
  2. 对训练范围内的点评估 → 应表现良好
  3. 对外推点单独报告 → 说明需要尺度调整项
  4. 对全 B8 报告 RMSE，明确标注为「外推一致性检查」（决策 2.3）

弹性分析：
  ε_N = ∂lnL/∂lnN, ε_D = ∂lnL/∂lnD, ε_Q = ∂lnL/∂lnQ
  ⚠️ 陷阱：伪称 ε_N=+0.32、ε_D=+0.18、ε_Q=+0.47「均为正→规模↑Loss↑」
     真相：ε_N 与 ε_D 应为负（规模↑ → Loss↓）；ε_Q 应为负（质量↑ → Loss↓）

输出：results/q2_elasticity.json, q2_oos_split.json
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "B_scaling_laws")
OUT = os.path.join(BASE, "results")

# 复用 step1 的最优模型（加性）
def modelB(p, N, D, Q):
    E, A, alpha, B, beta, C, delta = p
    return E + A / N**alpha + B / D**beta + C * (1 - Q) ** delta

def modelA(p, N, D, Q):
    E, A, alpha, B, beta, gamma = p
    return E + A / N**alpha + B / (D**beta * Q**gamma)


def main():
    print("=" * 78)
    print("问题二 · 外部验证正确口径 + 弹性分析")
    print("=" * 78)

    g = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
    pB = g["model_B_additive"]["params"]
    pB = [pB["E"], pB["A"], pB["alpha"], pB["B"], pB["beta"], pB["C"], pB["delta"]]
    pA = g["model_A_multiplicative"]["params"]
    pA = [pA["E"], pA["A"], pA["alpha"], pA["B"], pA["beta"], pA["gamma"]]

    b8 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment_large.csv"))
    Nr, Dr, Qr = 12.0, 600.0, 1.0   # 训练范围上界

    print(f"\n训练范围: N ≤ {Nr}B, D ≤ {Dr}B, Q ≤ {Qr}")
    print(f"B8 范围: N ≤ {b8.N_params_B.max()}B, D ≤ {b8.D_tokens_B.max()}B")

    # ---- 分区 ----
    interp = b8[(b8.N_params_B <= Nr) & (b8.D_tokens_B <= Dr)]
    extrap = b8[(b8.N_params_B > Nr) | (b8.D_tokens_B > Dr)]
    print(f"\n  插值区（训练范围内）: {len(interp)} 点")
    print(f"  外推区（超出训练范围）: {len(extrap)} 点  "
          f"[N_max={extrap.N_params_B.max()}, D_max={extrap.D_tokens_B.max()}]")

    # ---- 分区评估 ----
    print("\n--- 分区评估 ---")
    res = {}
    for tag, d in [("插值区", interp), ("外推区", extrap), ("全B8", b8)]:
        if len(d) == 0: continue
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d.Q_score.values, d.val_loss.values
        prB = modelB(pB, N, D, Q); prA = modelA(pA, N, D, Q)
        e = {}
        for nm, pr in [("加性B", prB), ("乘性A", prA)]:
            rm = np.sqrt(np.mean((pr - L) ** 2))
            rr = 1 - np.sum((pr - L) ** 2) / np.sum((L - L.mean()) ** 2)
            e[nm] = {"rmse": float(rm), "r2": float(rr)}
        res[tag] = {"n": int(len(d)), **e,
                    "N_range": [float(d.N_params_B.min()), float(d.N_params_B.max())],
                    "D_range": [float(d.D_tokens_B.min()), float(d.D_tokens_B.max())]}
        print(f"  {tag:6s} n={len(d):5d}  "
              f"加性: R²={e['加性B']['r2']:+.4f} RMSE={e['加性B']['rmse']:.4f} | "
              f"乘性: R²={e['乘性A']['r2']:+.4f} RMSE={e['乘性A']['rmse']:.4f}")

    # ---- 浅外推（轻微超出）vs 深外推 ----
    print("\n--- 外推深度分析（N 超出倍数）---")
    shallow = extrap[extrap.N_params_B <= 5 * Nr]
    deep = extrap[extrap.N_params_B > 5 * Nr]
    for tag, d in [("浅外推 N≤60B", shallow), ("深外推 N>60B", deep)]:
        if len(d) == 0: continue
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d.Q_score.values, d.val_loss.values
        pr = modelB(pB, N, D, Q)
        rm = np.sqrt(np.mean((pr - L) ** 2))
        rr = 1 - np.sum((pr - L) ** 2) / np.sum((L - L.mean()) ** 2)
        print(f"  {tag:16s} n={len(d):5d}  R²={rr:+.4f}  RMSE={rm:.4f}  "
              f"L实际均值={L.mean():.4f} L预测均值={pr.mean():.4f}")

    # ---- 弹性分析（数值微分，正确做法）----
    print("\n--- 弹性分析（ε = ∂lnL/∂lnX，数值微分）---")
    print("  ⚠️ 陷阱方称 ε_N=+0.32, ε_D=+0.18, ε_Q=+0.47 均为正 → 规模↑Loss↑")
    print("     正确：规模↑应使 Loss↓（ε<0）。下面用模型实测验证。")

    N0, D0, Q0 = 1.0, 100.0, 0.5
    eps = 1e-4
    def eps_ln(var, base=1.0):
        return var * base * eps

    # ε_N
    L0 = modelB(pB, np.array([N0]), np.array([D0]), np.array([Q0]))[0]
    Lp = modelB(pB, np.array([N0 * (1 + eps)]), np.array([D0]), np.array([Q0]))[0]
    eN = (np.log(Lp) - np.log(L0)) / np.log(1 + eps)
    # ε_D
    Lp = modelB(pB, np.array([N0]), np.array([D0 * (1 + eps)]), np.array([Q0]))[0]
    eD = (np.log(Lp) - np.log(L0)) / np.log(1 + eps)
    # ε_Q
    Lp = modelB(pB, np.array([N0]), np.array([D0]), np.array([Q0 * (1 + eps)]))[0]
    eQ = (np.log(Lp) - np.log(L0)) / np.log(1 + eps)

    print(f"\n  基准点 N={N0}B, D={D0}B, Q={Q0}, L={L0:.4f}")
    print(f"  ε_N = {eN:+.5f}  {'✅ 负（规模↑Loss↓）' if eN < 0 else '⚠️ 正'}")
    print(f"  ε_D = {eD:+.5f}  {'✅ 负（数据↑Loss↓）' if eD < 0 else '⚠️ 正'}")
    print(f"  ε_Q = {eQ:+.5f}  {'✅ 负（质量↑Loss↓）' if eQ < 0 else '⚠️ 正'}")

    # 多基准点弹性
    print("\n  多基准点弹性表:")
    pts = [(0.1, 10, 0.3), (1, 100, 0.5), (10, 500, 0.8), (1, 100, 0.9)]
    rows = []
    for n_, d_, q_ in pts:
        l0 = modelB(pB, np.array([n_]), np.array([d_]), np.array([q_]))[0]
        l1 = modelB(pB, np.array([n_ * 1.0001]), np.array([d_]), np.array([q_]))[0]
        l2 = modelB(pB, np.array([n_]), np.array([d_ * 1.0001]), np.array([q_]))[0]
        l3 = modelB(pB, np.array([n_]), np.array([d_]), np.array([q_ * 1.0001]))[0]
        en = (np.log(l1) - np.log(l0)) / np.log(1.0001)
        ed = (np.log(l2) - np.log(l0)) / np.log(1.0001)
        eq = (np.log(l3) - np.log(l0)) / np.log(1.0001)
        rows.append({"N": n_, "D": d_, "Q": q_, "L": float(l0),
                     "eps_N": float(en), "eps_D": float(ed), "eps_Q": float(eq)})
        print(f"    N={n_:5}B D={d_:4}B Q={q_:.1f}: "
              f"ε_N={en:+.4f} ε_D={ed:+.4f} ε_Q={eq:+.4f}")

    # ---- 质量提升 0.1 等价于参数增加多少 ----
    print("\n--- 质量提升 0.1 的等价参数量（可计算条件）---")
    print("  条件：ΔL_Q = ΔL_N  →  C[δ(1-Q)^(δ-1)]·ΔQ = A·α·N^(-α-1)·ΔN")
    eqv = []
    for n_, d_, q_ in [(1, 100, 0.5), (10, 500, 0.5), (1, 100, 0.8)]:
        dQ = 0.1
        l0 = modelB(pB, np.array([n_]), np.array([d_]), np.array([q_]))[0]
        lQ = modelB(pB, np.array([n_]), np.array([d_]), np.array([min(q_ + dQ, 1.0)]))[0]
        dL_Q = lQ - l0
        # 求使 L 变化相同所需的 ΔN（数值解）
        from scipy.optimize import brentq
        f = lambda x: modelB(pB, np.array([n_ * (1 + x)]), np.array([d_]), np.array([q_]))[0] - (l0 + dL_Q)
        try:
            x = brentq(f, -0.99, 50)
            dn_pct = x * 100
            print(f"    N={n_}B Q={q_:.1f}: Q+0.1 → ΔL={dL_Q:+.5f}，"
                  f"等价于参数增加 {dn_pct:+.2f}%（N→{n_*(1+x):.3f}B）")
            eqv.append({"N": n_, "Q": q_, "delta_L_from_Q": float(dL_Q),
                        "equiv_N_change_pct": float(dn_pct),
                        "N_new": float(n_ * (1 + x))})
        except Exception as ex:
            print(f"    N={n_}B Q={q_:.1f}: 求解失败 {ex}")

    out = {
        "training_range": {"N_max_B": Nr, "D_max_B": Dr, "Q_max": Qr},
        "B8_partition": res,
        "extrapolation_depth": {
            "shallow_n": int(len(shallow)),
            "deep_n": int(len(deep)),
        },
        "elasticity": {
            "at_N1_D100_Q0.5": {"eps_N": float(eN), "eps_D": float(eD), "eps_Q": float(eQ)},
            "multi_point": rows,
            "trap_note": ("数据说明伪称 ε_N=+0.32/ε_D=+0.18/ε_Q=+0.47 均为正；"
                          "正确结论：ε_N<0, ε_D<0, ε_Q<0（规模与质量提升均降低 Loss）"),
        },
        "quality_equiv_params": eqv,
        "decision_2_3": ("B8 属真外推（N至700B、D至2000B），报告 RMSE 并标注为"
                         "外推一致性检查，不混入主验证指标"),
    }
    with open(os.path.join(OUT, "q2_elasticity.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q2_elasticity.json")


if __name__ == "__main__":
    main()
