#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤5（借鉴 CodeBuddy 优点）：重复检测 + 分组熵权质量分 + Bootstrap

借鉴要点：
  ① 重复检测：按「域+id」识别重复记录，报告唯一文档数
  ② 分组熵权：22 指标归 6 组 → 组内中位数 → 组间熵权（避免同类评分器重复计权）
  ③ Bootstrap：文档簇级别 200 次重采样，给域级质量分条件置信区间
  ④ 重尾变换：计数指标 ln(1+x)；DSIR 全非正 → ln(1-x) 反向

输出：results/q1_quality_v2_*.json/csv
"""
import os, json, lzma
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
RAW = os.path.join(OUT, "q1_quality_raw_compressed.csv")

# ---- 6 大语义分组（借鉴 CodeBuddy 的分组思路）----
GROUPS = {
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
    "文本规模": ["rps_doc_word_count", "rps_doc_num_sentences", "rps_doc_mean_word_length"],
    "词汇丰富度": ["rps_doc_unigram_entropy", "rps_doc_frac_unique_words"],
}

# 方向（+1 越高越好 / -1 越低越好）
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
    """
    熵权法：X 为 (n, m) 非负矩阵（已归一化到 [0,1]）
    返回各列权重（和为1）。区分度为0的列权重置0。
    """
    n = X.shape[0]
    # 平移避免 0
    P = X.copy()
    P = P / P.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        E = -np.nansum(P * np.log(P + 1e-12), axis=0) / np.log(n)
    E = np.nan_to_num(E, nan=1.0)
    d = 1 - E                      # 差异系数
    d = np.where(d < 1e-8, 0.0, d)  # 常量列置0
    return d / d.sum() if d.sum() > 0 else np.ones(X.shape[1]) / X.shape[1]


def main():
    print("=" * 78)
    print("问题一 · 借鉴版：重复检测 + 分组熵权 + Bootstrap")
    print("=" * 78)

    df = pd.read_csv(RAW)
    print(f"  原始记录: {len(df)} 条")

    # ---------- ① 重复检测 ----------
    print("\n--- ① 重复检测（域+id）---")
    df["_dupkey"] = df["_domain"].astype(str) + "||" + df["id"].astype(str)
    n_total = len(df)
    n_unique = df["_dupkey"].nunique()
    n_dup = n_total - n_unique
    print(f"  总记录 {n_total}，唯一文档 {n_unique}，重复记录 {n_dup} ({n_dup/n_total:.2%})")
    # 仅按 id 去重（跨域同 id）
    n_unique_id = df["id"].nunique()
    print(f"  仅按 id 去重: {n_unique_id}")
    dup_info = {"n_total": int(n_total), "n_unique_domain_id": int(n_unique),
                "n_duplicate": int(n_dup), "dup_rate": float(n_dup / n_total),
                "n_unique_id_only": int(n_unique_id)}

    # ---------- ② 分组熵权质量分 ----------
    print("\n--- ② 分组熵权质量分 ---")
    all_metrics = [m for g in GROUPS.values() for m in g]

    # 重尾变换 + 方向统一 + MinMax
    V = pd.DataFrame(index=df.index)
    for m in all_metrics:
        x = df[m].astype(float).copy()
        if m.startswith("dsir_"):
            # DSIR 全为非正 → ln(1-x)，保留"原始DSIR越大越优"
            x = np.log1p(-x.clip(upper=0) + 1e-12)
        elif m in ("rps_doc_word_count", "rps_doc_num_sentences"):
            x = np.log1p(x.clip(lower=0))     # 计数指标重尾
        lo, hi = x.min(), x.max()
        z = (x - lo) / (hi - lo) if hi > lo else x * 0 + 0.5
        if DIRECTION.get(m, 1) < 0:
            z = 1 - z
        V[m] = z.fillna(z.median())
    print(f"  变换后范围: [{V.values.min():.3f}, {V.values.max():.3f}]")

    # 组内中位数
    G = pd.DataFrame(index=df.index)
    for g, ms in GROUPS.items():
        ms2 = [m for m in ms if m in V.columns]
        G[g] = V[ms2].median(axis=1)
    print(f"  组数: {len(G.columns)}")

    # 组间熵权
    w = entropy_weight(G.values)
    wmap = dict(zip(G.columns, w))
    print("\n  组间熵权:")
    for g, wv in sorted(wmap.items(), key=lambda x: -x[1]):
        print(f"    {g:14s} w={wv:.4f}")

    # 主质量分 S
    S = (G * w[None, :]).sum(axis=1)
    df["S"] = S.values
    print(f"\n  S 分布: mean={S.mean():.4f}, std={S.std():.4f}, "
          f"[{S.min():.4f}, {S.max():.4f}]")

    # 域级
    dom = df.groupby("_domain").agg(n=("S", "size"), S_mean=("S", "mean")).reset_index()
    print("\n  域级质量分（熵权）:")
    for _, r in dom.sort_values("S_mean", ascending=False).iterrows():
        print(f"    {r['_domain']:16s} n={int(r['n']):7d}  S={r['S_mean']:.4f}")

    # ---------- ③ Bootstrap 条件置信区间 ----------
    print("\n--- ③ Bootstrap 置信区间（文档簇级，200次）---")
    rng = np.random.default_rng(20260923)
    B = 200
    boot = {}
    # 文档簇 = dupkey
    for d, g in df.groupby("_domain"):
        if len(g) < 30:
            boot[d] = {"S_mean": float(g["S"].mean()), "ci_lo": None, "ci_hi": None,
                       "n": int(len(g)), "note": "样本不足，跳过bootstrap"}
            continue
        clusters = g.groupby("_dupkey")["S"].mean().values   # 簇级均值
        ncl = len(clusters)
        means = np.empty(B)
        for b in range(B):
            idx = rng.integers(0, ncl, ncl)
            means[b] = clusters[idx].mean()
        lo, hi = np.percentile(means, [2.5, 97.5])
        boot[d] = {"S_mean": float(g["S"].mean()), "ci_lo": float(lo), "ci_hi": float(hi),
                   "n": int(len(g)), "n_clusters": int(ncl)}
        print(f"    {d:16s} n={len(g):7d} 簇={ncl:6d}  S={g['S'].mean():.4f}  "
              f"95%CI=[{lo:.4f}, {hi:.4f}]")

    # ---------- 冲突分析（百分位秩法，借鉴 CodeBuddy）----------
    print("\n--- ④ 冲突识别（百分位秩 + 最大秩差）---")
    R = pd.DataFrame(index=df.index)
    n = len(df)
    for m in all_metrics:
        ranks = V[m].rank(method="average")
        R[m] = (ranks - 0.5) / n      # 百分位秩
    delta = R.max(axis=1) - R.min(axis=1)
    tau90 = delta.quantile(0.90)
    conflict = delta > tau90
    print(f"  最大秩差 δ: mean={delta.mean():.6f}, 90分位={tau90:.6f}")
    print(f"  ⭐ 冲突记录 {conflict.sum()} / {n} = {conflict.mean():.2%}")
    print(f"  ⚠️ 与 CodeBuddy 的 10.00% 对比（90分位规则决定，非独立发现）")

    df["_delta_rank"] = delta.values
    df["_conflict"] = conflict.values

    dc = df.groupby("_domain").agg(
        n=("_conflict", "size"), conflict_rate=("_conflict", "mean"),
        delta_mean=("_delta_rank", "mean")).reset_index()
    print("\n  分域冲突率:")
    for _, r in dc.sort_values("conflict_rate", ascending=False).iterrows():
        print(f"    {r['_domain']:16s} n={int(r['n']):7d}  冲突率={r['conflict_rate']:6.2%}")

    # ---------- 保存 ----------
    out = {
        "duplicate_detection": dup_info,
        "group_entropy_weights": {g: float(v) for g, v in wmap.items()},
        "S_stats": {"mean": float(S.mean()), "std": float(S.std()),
                    "min": float(S.min()), "max": float(S.max())},
        "domain_quality": dom.to_dict(orient="records"),
        "bootstrap": boot,
        "conflict": {"method": "百分位秩 + 最大秩差, 90分位阈值",
                     "tau90": float(tau90), "rate": float(conflict.mean()),
                     "n_conflict": int(conflict.sum()), "n": int(n)},
        "domain_conflict": dc.to_dict(orient="records"),
        "borrowed_from": "CodeBuddy 版：重复检测/分组熵权/bootstrap/百分位秩冲突",
    }
    with open(os.path.join(OUT, "q1_quality_v2.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    dom.to_csv(os.path.join(OUT, "q1_domain_quality_v2.csv"), index=False)
    dc.to_csv(os.path.join(OUT, "q1_domain_conflict_v2.csv"), index=False)
    pd.DataFrame([{"domain": k, **v} for k, v in boot.items()]).to_csv(
        os.path.join(OUT, "q1_bootstrap_ci.csv"), index=False)

    print(f"\n✅ 输出: results/q1_quality_v2.json, q1_domain_quality_v2.csv, "
          f"q1_domain_conflict_v2.csv, q1_bootstrap_ci.csv")


if __name__ == "__main__":
    main()
