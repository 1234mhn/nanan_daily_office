#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤6（借鉴版续）：稳健性检验 + 二阶交互模型

借鉴要点：
  ⑤ 排序一致性检验（Kendall τ_b / Spearman ρ）：主模型 vs 替代评价方案
  ⑥ 去除"文本形态组"的敏感性对照（词数/句数不是普适质量真值）
  ⑦ 二阶交互模型：136 个 p_i p_j 项 + 岭回归 + 5折CV + 配对 bootstrap

输出：results/q1_robustness_v2.json, q1_quadratic_model.json
"""
import os, json
import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
RGT = os.path.join(BASE, "real_attachments", "A_data_value", "regmix_tables")

# 复用 v2 的分组（剔除文本规模组作为敏感性对照）
GROUPS_FULL = {
    "教育与知识": ["fineweb_edu", "dsir_books", "dsir_wiki", "dsir_math", "qurater",
                   "modernbert_reasoning"],
    "语言与清洁": ["fluency_en", "modernbert_cleanliness", "modernbert_readability",
                   "modernbert_professionalism"],
    "无广告": ["ad_en"],
    "重复与字符结构": ["rps_doc_frac_chars_top_2gram", "rps_doc_frac_chars_top_3gram",
                       "rps_lines_uppercase_letter_fraction",
                       "rps_lines_numerical_chars_fraction",
                       "rps_lines_ending_with_terminal_punctution_mark",
                       "rps_doc_frac_no_alph_words"],
    "词汇丰富度": ["rps_doc_unigram_entropy", "rps_doc_frac_unique_words"],
    "文本规模": ["rps_doc_word_count", "rps_doc_num_sentences", "rps_doc_mean_word_length"],
}
DIRECTION = {
    "fineweb_edu": +1, "fluency_en": +1, "modernbert_cleanliness": +1,
    "modernbert_readability": +1, "modernbert_reasoning": +1,
    "modernbert_professionalism": +1, "dsir_books": +1, "dsir_wiki": +1,
    "dsir_math": +1, "qurater": +1, "ad_en": -1,
    "rps_doc_frac_no_alph_words": -1, "rps_doc_frac_chars_top_2gram": -1,
    "rps_doc_frac_chars_top_3gram": -1, "rps_lines_uppercase_letter_fraction": -1,
    "rps_lines_numerical_chars_fraction": -1,
    "rps_doc_word_count": +1, "rps_doc_num_sentences": +1,
    "rps_doc_unigram_entropy": +1, "rps_doc_frac_unique_words": -1,
    "rps_doc_mean_word_length": +1,
    "rps_lines_ending_with_terminal_punctution_mark": -1,
}


def entropy_weight(X):
    n = X.shape[0]
    P = X / (X.sum(axis=0, keepdims=True) + 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        E = -np.nansum(P * np.log(P + 1e-12), axis=0) / np.log(n)
    E = np.nan_to_num(E, nan=1.0)
    d = np.where((1 - E) < 1e-8, 0.0, 1 - E)
    return d / d.sum() if d.sum() > 0 else np.ones(X.shape[1]) / X.shape[1]


def score_domains(df, groups):
    all_m = [m for g in groups.values() for m in g]
    V = pd.DataFrame(index=df.index)
    for m in all_m:
        x = df[m].astype(float).copy()
        if m.startswith("dsir_"):
            x = np.log1p(-x.clip(upper=0) + 1e-12)
        elif m in ("rps_doc_word_count", "rps_doc_num_sentences"):
            x = np.log1p(x.clip(lower=0))
        lo, hi = x.min(), x.max()
        z = (x - lo) / (hi - lo) if hi > lo else x * 0 + 0.5
        if DIRECTION.get(m, 1) < 0:
            z = 1 - z
        V[m] = z.fillna(z.median())
    G = pd.DataFrame(index=df.index)
    for g, ms in groups.items():
        G[g] = V[[m for m in ms if m in V.columns]].median(axis=1)
    w = entropy_weight(G.values)
    S = (G * w[None, :]).sum(axis=1)
    dom = df.assign(S=S).groupby("_domain")["S"].mean()
    return dom, dict(zip(G.columns, w))


def dn(c):
    return (c.replace("metric/", "").replace("train_the_pile_", "")
            .replace("the_pile_", "").replace("_val_loss", ""))


def main():
    print("=" * 78)
    print("问题一 · 稳健性检验 + 二阶交互模型")
    print("=" * 78)

    df = pd.read_csv(os.path.join(OUT, "q1_quality_raw_compressed.csv"))
    # 排除扩展集重复（A2_arxiv/A3_github 与 arxiv/github 重复），用去重后的七域
    print(f"  载入 {len(df)} 条")

    # ---- ⑤ 排序一致性：主方案 vs 替代方案 ----
    print("\n--- ⑤ 排序一致性检验（Kendall τ_b / Spearman ρ）---")

    def rank_of(dom_series):
        return dom_series.sort_values(ascending=False)

    main_dom, main_w = score_domains(df, GROUPS_FULL)
    # 替代1：去除文本规模组
    g_nof = {k: v for k, v in GROUPS_FULL.items() if k != "文本规模"}
    alt1_dom, _ = score_domains(df, g_nof)
    # 替代2：等权（不做熵权）
    all_m = [m for g in GROUPS_FULL.values() for m in g]
    V = pd.DataFrame(index=df.index)
    for m in all_m:
        x = df[m].astype(float)
        lo, hi = x.min(), x.max()
        z = (x - lo) / (hi - lo) if hi > lo else x * 0 + 0.5
        if DIRECTION.get(m, 1) < 0:
            z = 1 - z
        V[m] = z.fillna(z.median())
    alt2_dom = V.mean(axis=1).groupby(df["_domain"]).mean()

    # 对齐共同域
    common = sorted(set(main_dom.index) & set(alt1_dom.index) & set(alt2_dom.index))
    comparisons = []
    for name, alt in [("去文本规模组", alt1_dom), ("等权平均", alt2_dom)]:
        a = main_dom[common].values
        b = alt[common].values
        tau, _ = stats.kendalltau(a, b)
        rho, _ = stats.spearmanr(a, b)
        comparisons.append({"alt": name, "kendall_tau_b": float(tau), "spearman_rho": float(rho)})
        print(f"    vs {name:12s}: Kendall τ_b={tau:.4f}  Spearman ρ={rho:.4f}")

    print(f"\n  主方案域排序: {' > '.join(rank_of(main_dom)[:5].index)}...")

    # ---- ⑥ 配比模型（系数和=0 约束）----
    print("\n--- ⑥ 线性配比模型（系数和=0，借鉴 CodeBuddy 的可识别约束）---")
    m1 = pd.read_csv(os.path.join(RGT, "train_mixture_1m.csv"))
    l1 = pd.read_csv(os.path.join(RGT, "train_pile_loss_1m.csv"))
    loss_domains = [dn(c) for c in l1.columns if "_val_loss" in c]
    mc = [c for c in m1.columns if c.startswith("train_the_pile_") and dn(c) in loss_domains]
    lc = [c for c in l1.columns if "_val_loss" in c and dn(c) in loss_domains]
    P = m1[mc].values
    L = l1[lc].values.mean(axis=1)
    print(f"  训练: {P.shape[0]} 组 × {P.shape[1]} 域")

    # 中心化（等价于系数和=0 约束）
    Pm = P.mean(axis=0); Lm = L.mean()
    Pc = P - Pm; Lc = L - Lm
    beta, *_ = np.linalg.lstsq(Pc, Lc, rcond=None)
    # 系数和=0 约束：把 beta 平移到均值为0（对中心化预测等价）
    beta = beta - beta.mean()
    a0 = Lm - Pm @ beta
    print(f"  截距 a0 = {a0:.4f}（综合 Loss 基准）")
    print(f"  系数和 = {beta.sum():.6e}（约束验证，应≈0）")
    r2_lin = r2_score(L, Pc @ beta + Lm)
    print(f"  训练 R² = {r2_lin:.4f}")
    coef_lin = dict(zip([dn(c) for c in mc], beta.tolist()))

    # 一阶转移效应（1个百分点）
    print("\n  最有利转移方向（1个百分点，点估计）:")
    trans = []
    names = [dn(c) for c in mc]
    for i, j in combinations(range(len(names)), 2):
        # 从 j 转到 i 的 ΔLoss = beta_i - beta_j
        dl = beta[i] - beta[j]
        trans.append({"from": names[j], "to": names[i], "delta_loss": float(dl)})
        trans.append({"from": names[i], "to": names[j], "delta_loss": float(-dl)})
    trans.sort(key=lambda x: x["delta_loss"])
    for t in trans[:3]:
        print(f"    {t['from']:18s} → {t['to']:18s}  ΔLoss={t['delta_loss']:+.5f}")

    # ---- ⑦ 二阶交互模型 ----
    print("\n--- ⑦ 二阶交互模型（136 项 + 岭回归 + 5折CV）---")
    pairs = list(combinations(range(P.shape[1]), 2))
    X2 = np.hstack([P] + [(P[:, i] * P[:, j])[:, None] for i, j in pairs])
    print(f"  特征: 线性 {P.shape[1]} + 二阶 {len(pairs)} = {X2.shape[1]}")

    kf = KFold(n_splits=5, shuffle=True, random_state=20260924)
    from sklearn.preprocessing import StandardScaler
    alphas = [0.01, 0.1, 1, 10, 100, 1000]

    def cv_rmse(X, y, use_ridge=True):
        errs = []
        for tr, te in kf.split(X):
            sc = StandardScaler().fit(X[tr])
            Xtr, Xte = sc.transform(X[tr]), sc.transform(X[te])
            if use_ridge:
                mdl = RidgeCV(alphas=alphas).fit(Xtr, y[tr])
            else:
                mdl = Ridge(alpha=0.0).fit(Xtr, y[tr])
            errs.append(np.sqrt(mean_squared_error(y[te], mdl.predict(Xte))))
        return np.mean(errs)

    cv_lin = cv_rmse(P, L, True)
    cv_quad = cv_rmse(X2, L, True)
    print(f"  5折CV RMSE: 线性={cv_lin:.4f}  二阶={cv_quad:.4f}  "
          f"改善={cv_lin-cv_quad:+.4f} ({(cv_lin-cv_quad)/cv_lin:.2%})")

    # 同尺度 1M 检验集
    mv = pd.read_csv(os.path.join(RGT, "test_mixture_1m.csv"))
    lv = pd.read_csv(os.path.join(RGT, "test_pile_loss_1m.csv"))
    mcv = [c for c in mv.columns if c.startswith("train_the_pile_") and dn(c) in loss_domains]
    lcv = [c for c in lv.columns if "_val_loss" in c and dn(c) in loss_domains]
    Pv = mv[mcv].values; Lv = lv[lcv].values.mean(axis=1)
    X2v = np.hstack([Pv] + [(Pv[:, i] * Pv[:, j])[:, None] for i, j in pairs])

    sc1 = StandardScaler().fit(P); sc2 = StandardScaler().fit(X2)
    scv2 = StandardScaler().fit(X2v)
    mdl1 = RidgeCV(alphas=alphas).fit(sc1.transform(P), L)
    mdl2 = RidgeCV(alphas=alphas).fit(sc2.transform(X2), L)
    pr1 = mdl1.predict(sc1.transform(Pv))
    pr2 = mdl2.predict(scv2.transform(X2v))
    print(f"\n  1M 检验集:")
    print(f"    线性 R²={r2_score(Lv,pr1):.4f}  RMSE={np.sqrt(mean_squared_error(Lv,pr1)):.4f}")
    print(f"    二阶 R²={r2_score(Lv,pr2):.4f}  RMSE={np.sqrt(mean_squared_error(Lv,pr2)):.4f}")

    # 配对 bootstrap 检验 RMSE 差
    rng = np.random.default_rng(20260924)
    diffs = []
    e1 = (Lv - pr1) ** 2; e2 = (Lv - pr2) ** 2
    for _ in range(500):
        idx = rng.integers(0, len(Lv), len(Lv))
        diffs.append(np.sqrt(e2[idx].mean()) - np.sqrt(e1[idx].mean()))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    print(f"    RMSE差(二阶-线性) 95%CI = [{lo:+.4f}, {hi:+.4f}]  "
          f"{'✅二阶更优' if hi < 0 else '⚠️不显著'}")

    # ---- 保存 ----
    out = {
        "robustness": {"comparisons": comparisons,
                       "main_ranking": rank_of(main_dom).to_dict(),
                       "group_weights": {k: float(v) for k, v in main_w.items()}},
        "linear_model": {"intercept": float(a0), "coef_sum": float(beta.sum()),
                         "r2_train": float(r2_lin), "coefs": coef_lin,
                         "top_transfers": trans[:5]},
        "quadratic_model": {"n_features": int(X2.shape[1]), "n_pairs": len(pairs),
                            "cv_rmse_linear": float(cv_lin), "cv_rmse_quad": float(cv_quad),
                            "improvement": float(cv_lin - cv_quad),
                            "test_1m_linear_r2": float(r2_score(Lv, pr1)),
                            "test_1m_quad_r2": float(r2_score(Lv, pr2)),
                            "rmse_diff_ci": [float(lo), float(hi)]},
        "borrowed_from": "CodeBuddy：排序一致性/系数和=0约束/二阶交互+配对bootstrap",
    }
    with open(os.path.join(OUT, "q1_robustness_v2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 输出: results/q1_robustness_v2.json")


if __name__ == "__main__":
    main()
