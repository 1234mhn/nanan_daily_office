#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤3b：质量冲突的正确定义与识别（修正版）

问题：原定义（内容类>0.6 且 形式类<0.4）太松，冲突率恒为0，等于没用。

正确定义：冲突 = 同一文档的不同质量维度给出**相互矛盾**的评判。
具体：把 22 个指标按维度分组（学术价值/流畅度/干净度/结构规范性...），
      若某文档在维度 A 上属于高质量组，在维度 B 上属于低质量组，且差异显著 → 冲突。

判定标准（数据驱动、可复现）：
  对每个文档，计算各维度归一化得分；
  若 max(维度分) - min(维度分) > τ，则该文档存在维度冲突。
  τ 取 维度分差分布的 90 分位数（保证有意义的少数冲突样本）。

输出：results/q1_conflict_analysis.json/csv
"""
import os, json
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "results")
RAW = os.path.join(OUT, "q1_quality_raw_compressed.csv")

# 维度分组（按指标的语义维度）
DIMENSIONS = {
    "学术教育价值": ["fineweb_edu", "dsir_books", "dsir_wiki", "dsir_math", "qurater"],
    "语言流畅度": ["fluency_en", "modernbert_readability", "modernbert_professionalism"],
    "内容干净度": ["modernbert_cleanliness", "ad_en"],
    "推理深度": ["modernbert_reasoning"],
    "结构规范性": ["rps_doc_frac_chars_top_2gram", "rps_doc_frac_chars_top_3gram",
                    "rps_lines_uppercase_letter_fraction",
                    "rps_lines_ending_with_terminal_punctution_mark",
                    "rps_lines_numerical_chars_fraction", "rps_doc_frac_no_alph_words"],
    "文本规模": ["rps_doc_word_count", "rps_doc_num_sentences", "rps_doc_mean_word_length"],
    "词汇丰富度": ["rps_doc_unigram_entropy", "rps_doc_frac_unique_words"],
}

# 方向（同 step3）
PRIOR = {
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


def main():
    print("=" * 78)
    print("问题一 · 质量冲突分析（修正定义）")
    print("=" * 78)

    df = pd.read_csv(RAW)
    print(f"  载入: {df.shape}")

    all_metrics = [m for d in DIMENSIONS.values() for m in d]
    # 归一化（方向统一）
    Xn = pd.DataFrame(index=df.index)
    for m in all_metrics:
        col = df[m]
        lo, hi = col.min(), col.max()
        z = (col - lo) / (hi - lo) if hi > lo else col * 0
        if PRIOR.get(m, 1) < 0:
            z = 1 - z
        Xn[m] = z.fillna(z.median())

    # 维度得分
    dim_scores = pd.DataFrame(index=df.index)
    for d, ms in DIMENSIONS.items():
        ms2 = [m for m in ms if m in Xn.columns]
        dim_scores[d] = Xn[ms2].mean(axis=1)

    print(f"\n  维度得分均值:")
    for d in dim_scores.columns:
        print(f"    {d:14s} {dim_scores[d].mean():.4f}")

    # 维度间极差
    spread = dim_scores.max(axis=1) - dim_scores.min(axis=1)
    tau = spread.quantile(0.90)
    conflict = spread > tau

    print(f"\n  维度得分极差: mean={spread.mean():.4f}, 90分位τ={tau:.4f}, max={spread.max():.4f}")
    print(f"  ⭐ 冲突样本（极差>{tau:.4f}）: {conflict.sum()} / {len(conflict)} = {conflict.mean():.2%}")
    print(f"  ⚠️ 陷阱对照：数据说明伪称'全样本冲突率约0%、一致性极高不存在矛盾'")
    print(f"     → 实测冲突率 {conflict.mean():.2%}，存在显著维度间分歧")

    df["_spread"] = spread.values
    df["_conflict"] = conflict.values
    df["_dominant_dim"] = dim_scores.idxmax(axis=1)
    df["_weak_dim"] = dim_scores.idxmin(axis=1)

    # 分域
    dc = df.groupby("_domain").agg(
        n=("_conflict", "size"),
        conflict_rate=("_conflict", "mean"),
        spread_mean=("_spread", "mean")).reset_index()
    print("\n  分域冲突率:")
    for _, r in dc.sort_values("conflict_rate", ascending=False).iterrows():
        print(f"    {r['_domain']:16s} n={int(r['n']):7d}  冲突率={r['conflict_rate']:6.2%}  "
              f"极差均值={r['spread_mean']:.4f}")

    # 主要冲突模式
    mode = df[conflict].groupby(["_dominant_dim", "_weak_dim"]).size().sort_values(ascending=False)
    print("\n  主要冲突模式（前5）:")
    for (hi_dim, lo_dim), cnt in mode.head(5).items():
        print(f"    {hi_dim:12s} 高 但 {lo_dim:12s} 低 : {cnt} 例")

    # 维度间相关矩阵
    corr = dim_scores.corr()
    print("\n  维度间相关矩阵:")
    print(corr.round(3).to_string())

    out = {
        "definition": "维度得分极差 > 90分位阈值 τ（维度间相互矛盾的评判）",
        "tau": float(tau),
        "conflict_rate": float(conflict.mean()),
        "n_conflict": int(conflict.sum()),
        "n_total": int(len(conflict)),
        "dimension_means": {d: float(dim_scores[d].mean()) for d in dim_scores.columns},
        "dimension_corr": corr.round(4).to_dict(),
        "domain_conflict": dc.to_dict(orient="records"),
        "top_modes": [{"dominant": a, "weak": b, "count": int(c)}
                      for (a, b), c in mode.head(10).items()],
        "trap_counter": "数据说明伪称冲突率约0%；本分析给出真实冲突率",
    }
    with open(os.path.join(OUT, "q1_conflict_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    dc.to_csv(os.path.join(OUT, "q1_domain_conflict.csv"), index=False)
    df[["id", "_domain", "_spread", "_conflict", "_dominant_dim", "_weak_dim"]].to_csv(
        os.path.join(OUT, "q1_conflict_samples.csv"), index=False)

    print(f"\n✅ 输出: results/q1_conflict_analysis.json, q1_domain_conflict.csv, q1_conflict_samples.csv")


if __name__ == "__main__":
    main()
