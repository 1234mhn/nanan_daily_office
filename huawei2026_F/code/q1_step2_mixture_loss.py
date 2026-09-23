#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F题 问题一 · 步骤2：17域配比 → Loss 建模（含跨尺度验证与外推）

对应决策：
  1.2 质量加权：基础模型先拟合，若 ΔR²>0.05 则纳入质量项
  1.3 外推切换阈值 0.05
  1.4 只用 13 个有 Loss 的域（剔除 nih_exporter/enron_emails/europarl/philpapers）

输出：results/q1_mixture_*.json/csv
"""
import os, json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(BASE, "real_attachments", "A_data_value", "regmix_tables")
OUT = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# 17 个训练域（来自数据说明）
DOMAINS_17 = ["arxiv", "freelaw", "nih_exporter", "pubmed_central", "wikipedia_en",
              "dm_mathematics", "github", "philpapers", "stackexchange", "enron_emails",
              "gutenberg_pg_19", "pile_cc", "ubuntu_irc", "europarl", "hackernews",
              "pubmed_abstracts", "uspto_backgrounds"]
# 4 个无 Loss 列
NO_LOSS = {"nih_exporter", "enron_emails", "europarl", "philpapers"}
DOMAINS_13 = [d for d in DOMAINS_17 if d not in NO_LOSS]


def load_pair(mix_file, loss_file):
    m = pd.read_csv(os.path.join(ATT, mix_file))
    l = pd.read_csv(os.path.join(ATT, loss_file))
    return m, l


def get_mix_cols(m):
    return [c for c in m.columns if c.startswith("train_the_pile_")]


def get_loss_cols(l):
    return [c for c in l.columns if "val_loss" in c]


def to_domain_name(col):
    """train_the_pile_<domain> / metric/the_pile_<domain>_val_loss → <domain>"""
    s = col
    s = s.replace("metric/", "")
    s = s.replace("train_the_pile_", "")
    s = s.replace("the_pile_", "")
    s = s.replace("_val_loss", "")
    return s


def main():
    print("=" * 78)
    print("问题一 · 配比-Loss 建模（跨尺度验证 + 外推）")
    print("=" * 78)

    # ---- 载入 ----
    m_tr, l_tr = load_pair("train_mixture_1m.csv", "train_pile_loss_1m.csv")
    mix_cols = get_mix_cols(m_tr)
    loss_cols = get_loss_cols(l_tr)
    print(f"训练: 配比 {m_tr.shape}, Loss {l_tr.shape}")
    print(f"  配比列 {len(mix_cols)}: {[to_domain_name(c) for c in mix_cols]}")
    print(f"  Loss 列 {len(loss_cols)}: {[to_domain_name(c) for c in loss_cols]}")

    # 有 Loss 的域
    loss_domains = [to_domain_name(c) for c in loss_cols]
    keep_mix = [c for c in mix_cols if to_domain_name(c) in loss_domains]
    print(f"\n  Loss 域({len(loss_domains)}): {loss_domains}")
    print(f"  交集域（有配比且有Loss）: {len(keep_mix)} → {[to_domain_name(c) for c in keep_mix]}")

    # ---- 基础模型：L = b0 + sum bj*pj  (Ridge 处理共线性) ----
    Xtr = m_tr[keep_mix].values
    # 目标：平均 Loss（对 13 域 Loss 取均值作为整体 Loss 指标）
    Ytr_all = l_tr[loss_cols].values
    ytr = Ytr_all.mean(axis=1)

    model = Ridge(alpha=1.0)
    model.fit(Xtr, ytr)
    yhat = model.predict(Xtr)
    r2_tr = r2_score(ytr, yhat)
    rmse_tr = np.sqrt(mean_squared_error(ytr, yhat))
    print(f"\n[基础模型] 训练 R² = {r2_tr:.4f}, RMSE = {rmse_tr:.4f}")
    coefs = dict(zip([to_domain_name(c) for c in keep_mix], model.coef_))
    for k, v in sorted(coefs.items(), key=lambda x: -abs(x[1])):
        print(f"    {k:22s} {v:+.5f}")

    # ---- 跨尺度验证（1M/60M/1B）----
    print("\n--- 跨尺度验证（决策 1.3：阈值 0.05）---")
    val_results = []
    candidates = [
        ("test_mixture_1m.csv", "test_pile_loss_1m.csv", "1M"),
        ("test_mixture_60m.csv", "test_pile_loss_60m.csv", "60M"),
        ("test_mixture_1B.csv", "test_pile_loss_1B.csv", "1B"),
    ]
    for mf, lf, tag in candidates:
        try:
            mv, lv = load_pair(mf, lf)
        except Exception as e:
            print(f"  跳过 {tag}: {e}")
            continue
        mv_cols = [c for c in mv.columns if c.startswith("train_the_pile_")]
        keep_v = [c for c in mv_cols if to_domain_name(c) in loss_domains]
        Xv = mv[keep_v].values
        yv = lv[get_loss_cols(lv)].values.mean(axis=1)
        yhv = model.predict(Xv)
        r2 = r2_score(yv, yhv)
        rmse = np.sqrt(mean_squared_error(yv, yhv))
        mape = mean_absolute_percentage_error(yv, yhv)
        drop = r2_tr - r2
        need_switch = drop > 0.05
        val_results.append({"scale": tag, "n": len(yv), "R2": r2, "RMSE": rmse,
                            "MAPE": mape, "R2_drop_vs_train": drop,
                            "need_scale_model": bool(need_switch)})
        print(f"  {tag:4s} n={len(yv):4d}  R²={r2:+.4f} (Δ={drop:+.4f})  RMSE={rmse:.4f}  "
              f"MAPE={mape:.4%}  {'⚠️需切换' if need_switch else '✅可接受'}")

    # ---- 外推验证（10B/70B）----
    print("\n--- 外推验证（10B / 70B，标注为外推数据）---")
    ext_results = []
    for mf, lf, tag in [("est_mixture_10b.csv", "est_pile_loss_10b.csv", "10B"),
                        ("est_mixture_70b.csv", "est_pile_loss_70b.csv", "70B")]:
        try:
            mv, lv = load_pair(mf, lf)
        except Exception as e:
            print(f"  跳过 {tag}: {e}")
            continue
        mv_cols = [c for c in mv.columns if c.startswith("train_the_pile_")]
        keep_v = [c for c in mv_cols if to_domain_name(c) in loss_domains]
        Xv = mv[keep_v].values
        yv = lv[get_loss_cols(lv)].values.mean(axis=1)
        yhv = model.predict(Xv)
        r2 = r2_score(yv, yhv)
        rmse = np.sqrt(mean_squared_error(yv, yhv))
        ext_results.append({"scale": tag, "n": len(yv), "R2": r2, "RMSE": rmse,
                            "note": "外推数据（非直接观测）"})
        print(f"  {tag:4s} n={len(yv):4d}  R²={r2:+.4f}  RMSE={rmse:.4f}  [外推数据]")

    # ---- 残差诊断 ----
    resid = ytr - yhat
    sw = stats.shapiro(resid[:5000])  # Shapiro 限 5000
    print(f"\n--- 残差诊断（训练集）---")
    print(f"  Shapiro-Wilk: W={sw.statistic:.4f}, p={sw.pvalue:.4g}")
    print(f"  残差均值={resid.mean():.5f}, 标准差={resid.std():.5f}")

    # ---- 保存 ----
    out = {
        "decision_1_4": "仅用 13 个有 Loss 的域（剔除 nih_exporter/enron_emails/europarl/philpapers）",
        "n_domains_used": len(keep_mix),
        "domains_used": [to_domain_name(c) for c in keep_mix],
        "train": {"n": int(len(ytr)), "R2": r2_tr, "RMSE": rmse_tr,
                  "coefs": {k: float(v) for k, v in coefs.items()},
                  "intercept": float(model.intercept_)},
        "validation": val_results,
        "extrapolation": ext_results,
        "residual": {"shapiro_W": float(sw.statistic), "shapiro_p": float(sw.pvalue),
                     "mean": float(resid.mean()), "std": float(resid.std())},
        "decision_1_3_threshold": 0.05,
    }
    with open(os.path.join(OUT, "q1_mixture_loss_model.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    pd.DataFrame(val_results).to_csv(os.path.join(OUT, "q1_validation.csv"), index=False)
    pd.DataFrame(ext_results).to_csv(os.path.join(OUT, "q1_extrapolation.csv"), index=False)

    # 预测值 vs 实际值（画图用）
    pd.DataFrame({"actual": ytr, "pred": yhat}).to_csv(
        os.path.join(OUT, "q1_train_fit.csv"), index=False)

    print(f"\n✅ 输出: results/q1_mixture_loss_model.json, q1_validation.csv, "
          f"q1_extrapolation.csv, q1_train_fit.csv")


if __name__ == "__main__":
    main()
