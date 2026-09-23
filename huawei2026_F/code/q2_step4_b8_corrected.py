#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题二 · 步骤4：B8 的 Q 反向编码诊断 → 统一口径后验证

铁证（步骤3）：
  B6/B7: corr(Q, Loss) = -0.925  (Q↑ → Loss↓，符合质量定义)
  B8:    corr(Q, Loss) = +0.995  (Q↑ → Loss↑，与质量定义相反!)

结论：B8 的 Q_score 在数值上与 B6/B7 语义相反。
     处理：对 B8 采用 Q' = 1 - Q 后再验证。
     这是必须明确标注的数据口径问题，不是模型缺陷。

输出：results/q2_B8_corrected.json
"""
import os, json
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "B_scaling_laws")
OUT = os.path.join(BASE, "results")


def modelB(p, N, D, Q):
    E, A, alpha, B, beta, C, delta = p
    return E + A / N**alpha + B / D**beta + C * (1 - Q) ** delta


def main():
    print("=" * 78)
    print("问题二 · B8 的 Q 反向编码诊断与统一验证")
    print("=" * 78)

    g = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
    pb = g["model_B_additive"]["params"]
    pB = [pb["E"], pb["A"], pb["alpha"], pb["B"], pb["beta"], pb["C"], pb["delta"]]

    b6 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment.csv"))
    b8 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment_large.csv"))

    # ---- 1. 铁证：Q 与 Loss 的组内相关性 ----
    print("\n--- 1. Q-Loss 相关性（固定 N,D 的组内相关）---")
    for tag, d in [("B6/B7 (主拟合)", b6), ("B8 (外部验证)", b8)]:
        dr = d.groupby(["N_params_B", "D_tokens_B"]).apply(
            lambda x: np.corrcoef(x.Q_score, x.val_loss)[0, 1] if len(x) > 3 else np.nan).dropna()
        dr2 = d.groupby(["N_params_B", "D_tokens_B"]).apply(
            lambda x: np.corrcoef(1 - x.Q_score, x.val_loss)[0, 1] if len(x) > 3 else np.nan).dropna()
        print(f"  {tag:16s} corr(Q,L)={dr.mean():+.4f}   corr(1-Q,L)={dr2.mean():+.4f}")

    print("\n  ⚠️ 诊断：B8 的 Q_score 与 B6/B7 语义相反（数值正向=低质量）")
    print("     处理：B8 采用 Q' = 1 - Q")

    # ---- 2. 反向修正后验证 ----
    print("\n--- 2. 反向修正后验证 ---")
    b8c = b8.copy()
    b8c["Q_fixed"] = 1 - b8c.Q_score
    res = {}
    for tag, d, qcol in [("B8 原始Q", b8, "Q_score"),
                         ("B8 修正Q'=1-Q", b8c, "Q_fixed")]:
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d[ qcol].values, d.val_loss.values
        pr = modelB(pB, N, D, Q)
        rm = np.sqrt(np.mean((pr - L) ** 2))
        rr = 1 - np.sum((pr - L) ** 2) / np.sum((L - L.mean()) ** 2)
        corr = np.corrcoef(pr, L)[0, 1]
        res[tag] = {"rmse": float(rm), "r2": float(rr), "pearson_r": float(corr)}
        print(f"  {tag:16s} R²={rr:+.4f}  RMSE={rm:.4f}  Pearson r={corr:+.4f}")

    # ---- 3. 但尺度仍不一致 → 检查 scale-free 指标 ----
    print("\n--- 3. 尺度无关的一致性检验（Pearson r / 秩相关）---")
    print("  R² 对绝对尺度敏感；Pearson r 与 Spearman 只考察形状一致性")
    from scipy import stats
    for tag, d, qcol in [("B8 修正Q'", b8c, "Q_fixed")]:
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d[qcol].values, d.val_loss.values
        pr = modelB(pB, N, D, Q)
        sp = stats.spearmanr(pr, L)
        print(f"  {tag:16s} Pearson r={np.corrcoef(pr,L)[0,1]:+.4f}  "
              f"Spearman ρ={sp.statistic:+.4f} (p={sp.pvalue:.2e})")

    # ---- 4. 分 data_type ----
    print("\n--- 4. 按 data_type 分层（修正Q后）---")
    for dt in ["calibrated", "extrapolated"]:
        d = b8c[b8c.data_type == dt]
        if len(d) == 0: continue
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d.Q_fixed.values, d.val_loss.values
        pr = modelB(pB, N, D, Q)
        print(f"  {dt:14s} n={len(d):5d}  Pearson r={np.corrcoef(pr,L)[0,1]:+.4f}  "
              f"R²={1-np.sum((pr-L)**2)/np.sum((L-L.mean())**2):+.4f}")

    # ---- 5. 结论 ----
    concl = (
        "B8 的 Q_score 语义与 B6/B7 相反（corr(Q,Loss)=+0.99 vs -0.93），"
        "需以 Q'=1-Q 统一口径；统一后 Pearson r 显著改善。"
        "但两套数据绝对 Loss 尺度仍不同（B8 有 0.5 下限截断），"
        "故 B8 仅用于方向性与形状一致性验证，不作绝对 Loss 验证。"
    )
    print(f"\n  结论: {concl}")

    out = {
        "evidence": {
            "B6B7_corr_Q_L": -0.9248,
            "B8_corr_Q_L": +0.9954,
            "diagnosis": "B8 的 Q_score 为反向编码（数值正向对应低质量）",
        },
        "correction": "Q' = 1 - Q",
        "B8_original_eval": res.get("B8 原始Q"),
        "B8_corrected_eval": res.get("B8 修正Q'=1-Q"),
        "scale_note": "B8 存在 0.5 Loss 下限截断，绝对尺度不可比",
        "conclusion": concl,
        "decision_2_3": "B8 报告 RMSE/相关系数并标注为外推一致性检查，降结论强度",
    }
    with open(os.path.join(OUT, "q2_B8_corrected.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q2_B8_corrected.json")


if __name__ == "__main__":
    main()
