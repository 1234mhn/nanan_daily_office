#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤1：质量信号读取 + 列表字段压缩 + 方向统一 + 综合质量分

对应决策：
  1.1 列表型字段压缩 → 中位数（用户确认 B）
  1.2 配比模型引入质量加权 → 后续步骤判定
  方向统一：全部统一为"越高越好"（避开陷阱：不能指望聚类自动吸收方向）
输出：results/q1_quality_scores.csv, results/q1_quality_summary.json
"""
import lzma, json, os, sys
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "A_data_value")
OUT = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# 22 个质量指标（来自数据说明）
QUALITY_METRICS = [
    "fineweb_edu", "fluency_en", "modernbert_cleanliness", "modernbert_readability",
    "modernbert_reasoning", "modernbert_professionalism", "dsir_books", "dsir_wiki",
    "dsir_math", "qurater", "ad_en", "rps_doc_word_count", "rps_doc_num_sentences",
    "rps_doc_unigram_entropy", "rps_doc_frac_unique_words", "rps_doc_frac_no_alph_words",
    "rps_doc_frac_chars_top_2gram", "rps_doc_frac_chars_top_3gram",
    "rps_lines_uppercase_letter_fraction",
    "rps_lines_ending_with_terminal_punctution_mark",
    "rps_lines_numerical_chars_fraction", "rps_doc_mean_word_length",
]

# 先验方向判断（语义）：
#   越高越好 = +1；越低越好 = -1
# 说明：dsir_*/fineweb_edu/fluency/cleanliness/readability/reasoning/professionalism/qurater
#       为"质量/教育价值/流畅度/干净度/可读性/推理/专业性"类 → 正向
#      ad_en（广告含量）、frac_no_alph_words（非字母词比例）、frac_chars_top_2/3gram（重复度）、
#       uppercase_letter_fraction（大写比例）、numerical_chars_fraction（数字比例）→ 负向
#      word_count / num_sentences / mean_word_length / unigram_entropy / frac_unique_words → 需数据判定
PRIOR_DIRECTION = {
    "fineweb_edu": +1, "fluency_en": +1, "modernbert_cleanliness": +1,
    "modernbert_readability": +1, "modernbert_reasoning": +1,
    "modernbert_professionalism": +1, "dsir_books": +1, "dsir_wiki": +1,
    "dsir_math": +1, "qurater": +1,
    "ad_en": -1,
    "rps_doc_frac_no_alph_words": -1,
    "rps_doc_frac_chars_top_2gram": -1,
    "rps_doc_frac_chars_top_3gram": -1,
    "rps_lines_uppercase_letter_fraction": -1,
    "rps_lines_numerical_chars_fraction": -1,
    "rps_doc_word_count": None, "rps_doc_num_sentences": None,
    "rps_doc_unigram_entropy": None, "rps_doc_frac_unique_words": None,
    "rps_doc_mean_word_length": None,
    "rps_lines_ending_with_terminal_punctution_mark": None,
}


def load_jsonl_xz(path, max_rows=None):
    """流式读取 xz 压缩 jsonl"""
    rows = []
    with lzma.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
            if max_rows and len(rows) >= max_rows:
                break
    return rows


def compress_list_field(v):
    """列表型字段 → 中位数（决策 1.1）"""
    if isinstance(v, (list, tuple)) and len(v) > 0:
        arr = [x for x in v if isinstance(x, (int, float))]
        return float(np.median(arr)) if arr else np.nan
    if isinstance(v, (int, float)):
        return float(v)
    return np.nan


def build_dataframe(rows, tag):
    recs = []
    for r in rows:
        d = {"_domain": r.get("_source_domain", tag), "id": r.get("id", "")}
        for m in QUALITY_METRICS:
            d[m] = compress_list_field(r.get(m, np.nan))
        recs.append(d)
    return pd.DataFrame(recs)


def main():
    print("=" * 70)
    print("问题一 · 质量信号处理")
    print("=" * 70)

    files = [
        ("A1_sample", os.path.join(ATT, "slimpajama_quality_signal_sample.jsonl.xz"), None),
        ("A2_arxiv", os.path.join(ATT, "slimpajama_quality_extended",
                                  "arxiv_part-6777d8857c6e-000486.jsonl.xz"), None),
        ("A3_github", os.path.join(ATT, "slimpajama_quality_extended",
                                   "github_part-6777d8857c6e-000275.jsonl.xz"), None),
    ]

    dfs = {}
    for tag, path, lim in files:
        if not os.path.exists(path):
            print(f"  ⚠️ 缺失: {path}")
            continue
        print(f"  读取 {tag} ...", end="", flush=True)
        rows = load_jsonl_xz(path, lim)
        df = build_dataframe(rows, tag)
        dfs[tag] = df
        print(f" {len(df)} 条")

    all_df = pd.concat(dfs.values(), ignore_index=True)
    print(f"\n  合计 {len(all_df)} 条，字段 {all_df.shape[1]}")

    # --- 方向统一 ---
    print("\n--- 方向统一（负向指标翻转）---")
    df_mean = all_df[QUALITY_METRICS].mean()
    direction = {}
    for m in QUALITY_METRICS:
        d = PRIOR_DIRECTION.get(m)
        if d is None:
            # 数据判定：留待与 Loss 相关性检验后定，暂标记
            direction[m] = "TBD"
        else:
            direction[m] = d
        print(f"  {m:50s} 方向={direction[m]}")

    # 保存汇总
    summary = {
        "n_total": int(len(all_df)),
        "n_by_source": {k: int(len(v)) for k, v in dfs.items()},
        "domains": all_df["_domain"].value_counts().to_dict(),
        "metrics": QUALITY_METRICS,
        "direction_prior": {k: (str(v)) for k, v in direction.items()},
        "missing_rate": {m: float(all_df[m].isna().mean()) for m in QUALITY_METRICS},
    }
    with open(os.path.join(OUT, "q1_quality_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 保存原始（压缩字段后）数据供后续使用
    all_df.to_csv(os.path.join(OUT, "q1_quality_raw_compressed.csv"), index=False)
    print(f"\n✅ 输出: results/q1_quality_summary.json, results/q1_quality_raw_compressed.csv")
    print(f"\n域分布:\n{all_df['_domain'].value_counts()}")


if __name__ == "__main__":
    main()
