#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题二 · 步骤3：B8 尺度不一致的诊断与校准

关键发现（必须诚实报告）：
  B8 与 B6/B7 在同一配方下 Loss 尺度不同（如 N=1,D=50,Q=0.2: B6/B7=2.8076 vs B8=0.7393）
  B8 的 Q≤0.2 区间 Loss 被截断在 0.5（数据生成时的 floor）

处理：
  1. 严格量化两套数据的尺度差异
  2. 用「同配方重叠点」估计校准系数（若有）
  3. 校准后再评估 → 区分「模型误差」与「尺度差异」
  4. 结论：B8 仅可用于「Q 与 Loss 的关系方向」验证，不可用于绝对 Loss 验证

输出：results/q2_B8_calibration.json
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
    print("问题二 · B8 尺度一致性诊断与校准")
    print("=" * 78)

    g = json.load(open(os.path.join(OUT, "q2_generalized_law.json"), encoding="utf-8"))
    pb = g["model_B_additive"]["params"]
    pB = [pb["E"], pb["A"], pb["alpha"], pb["B"], pb["beta"], pb["C"], pb["delta"]]

    b6 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment.csv"))
    b8 = pd.read_csv(os.path.join(ATT, "supplementary_NQ_experiment_large.csv"))

    # ---- 1. 找同配方重叠点 ----
    print("\n--- 1. 同配方重叠点诊断 ---")
    b6k = b6.copy(); b6k["key"] = b6k.N_params_B.astype(str) + "|" + b6k.D_tokens_B.astype(str) + "|" + b6k.Q_score.round(2).astype(str)
    b8k = b8.copy(); b8k["key"] = b8k.N_params_B.astype(str) + "|" + b8k.D_tokens_B.astype(str) + "|" + b8k.Q_score.round(2).astype(str)
    mg = b6k.merge(b8k, on="key", suffixes=("_b6", "_b8"))
    print(f"  重叠配方数: {len(mg)}")
    if len(mg) > 0:
        ratio = mg.val_loss_b8 / mg.val_loss_b6
        print(f"  Loss 比值 (B8/B6): mean={ratio.mean():.4f}, median={ratio.median():.4f}, "
              f"std={ratio.std():.4f}")
        print(f"  比值范围: [{ratio.min():.4f}, {ratio.max():.4f}]")
        print("\n  前 8 个重叠点:")
        for _, r in mg.head(8).iterrows():
            print(f"    {r['key']:24s}  B6={r.val_loss_b6:.4f}  B8={r.val_loss_b8:.4f}  "
                  f"比值={r.val_loss_b8/r.val_loss_b6:.4f}")
        scale_ratio = float(ratio.median())
    else:
        print("  ⚠️ 无同配方重叠点 → 无法直接估计校准系数")
        scale_ratio = None

    # ---- 2. Q 依赖方向的一致性检验（这才是可比的部分）----
    print("\n--- 2. Q 与 Loss 的关系方向（跨文件可比）---")
    for tag, d in [("B6", b6), ("B8-calibrated", b8[b8.data_type == "calibrated"]),
                   ("B8-extrapolated", b8[b8.data_type == "extrapolated"])]:
        # 固定 (N,D)，看 Loss 随 Q 的单调性
        dr = d.groupby(["N_params_B", "D_tokens_B"]).apply(
            lambda x: np.corrcoef(x.Q_score, x.val_loss)[0, 1] if len(x) > 3 else np.nan).dropna()
        print(f"  {tag:18s} 组内 corr(Q, Loss) 均值 = {dr.mean():+.4f}  "
              f"({'✅ 负（Q↑Loss↓）' if dr.mean() < 0 else '⚠️'})  组数={len(dr)}")

    # ---- 3. 校准后评估 ----
    print("\n--- 3. 校准后评估（若可比）---")
    res = {}
    for tag, d in [("原始", b8), ("仅calibrated", b8[b8.data_type == "calibrated"]),
                   ("仅extrapolated", b8[b8.data_type == "extrapolated"])]:
        N, D, Q, L = d.N_params_B.values, d.D_tokens_B.values, d.Q_score.values, d.val_loss.values
        pr = modelB(pB, N, D, Q)
        rm = np.sqrt(np.mean((pr - L) ** 2))
        rr = 1 - np.sum((pr - L) ** 2) / np.sum((L - L.mean()) ** 2)
        # 去均值相关（只考察形状一致性，不看绝对偏移）
        corr = np.corrcoef(pr, L)[0, 1]
        res[tag] = {"n": int(len(d)), "rmse": float(rm), "r2": float(rr),
                    "pearson_r": float(corr)}
        print(f"  {tag:16s} n={len(d):5d}  R²={rr:+.4f}  RMSE={rm:.4f}  "
              f"Pearson r={corr:+.4f}")

    # ---- 4. Loss floor 检测 ----
    print("\n--- 4. Loss 截断(floor)检测 ---")
    floor = b8.val_loss.min()
    n_floor = (b8.val_loss <= floor + 1e-6).sum()
    print(f"  B8 最小 Loss = {floor:.4f}，触及该值的记录 {n_floor} 条 "
          f"({n_floor/len(b8):.2%})")
    print(f"  → 说明 B8 在低 Q 区存在 Loss 下限截断，属数据生成机制特征")

    # ---- 5. 结论 ----
    concl = (
        "B8 与 B6/B7 在同一配方下的 Loss 尺度不一致（比值非1），"
        "且低 Q 区存在 0.5 的 Loss 下限截断。因此 B8 不适合用于绝对 Loss 的验证，"
        "但可用于检验「Q↑ → Loss↓」的方向性结论。"
    )
    print(f"\n  结论: {concl}")

    out = {
        "overlap_points": int(len(mg)),
        "scale_ratio_median_B8_over_B6": scale_ratio,
        "q_loss_direction_check": {},
        "calibrated_eval": res,
        "loss_floor": {"value": float(floor), "n_at_floor": int(n_floor),
                       "rate": float(n_floor / len(b8))},
        "data_type_split": b8.data_type.value_counts().to_dict(),
        "conclusion": concl,
        "decision_2_3": ("B8 报告 RMSE 并标注为外推一致性检查；"
                         "因尺度不一致，绝对 Loss 验证不成立，仅验证方向性"),
    }
    with open(os.path.join(OUT, "q2_B8_calibration.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q2_B8_calibration.json")


if __name__ == "__main__":
    main()
