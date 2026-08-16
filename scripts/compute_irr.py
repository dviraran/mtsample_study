#!/usr/bin/env python3
"""
Inter-rater reliability for the appropriateness review.

Merges the second physician's completed blinded workbook with the hidden key and reviewer
1's scores, then reports, on the stratified subsample:
  - exact percent agreement on the 1-4 rubric
  - linear- and quadratic-weighted Cohen's kappa on the 1-4 ordinal scale
  - agreement + kappa on the clinically meaningful dichotomy
    inappropriate (score 1-2) vs defensible (score 3-4)

Weighted kappa is implemented directly (no sklearn dependency):
    kappa = 1 - (Σ d_ij O_ij) / (Σ d_ij E_ij)
with disagreement weights d_ij = |i-j| (linear) or (i-j)^2 (quadratic).

Usage:
  python scripts/compute_irr.py \
      --workbook data/reviewer2_blinded_workbook.xlsx --key data/reviewer2_key.csv
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def weighted_kappa(r1, r2, cats, kind="quadratic"):
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    O = np.zeros((k, k))
    for a, b in zip(r1, r2):
        O[idx[a], idx[b]] += 1
    n = O.sum()
    if n == 0:
        return None
    row = O.sum(1)
    col = O.sum(0)
    E = np.outer(row, col) / n
    d = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            d[i, j] = (i - j) ** 2 if kind == "quadratic" else abs(i - j)
    denom = (d * E).sum()
    return float(1 - (d * O).sum() / denom) if denom else 1.0


def gwet_ac2(r1, r2, cats, kind="quadratic"):
    """Gwet's AC2 agreement coefficient with ordinal weights.

    Unlike weighted kappa, the chance-agreement term does not multiply the two
    raters' marginals, so it is not deflated when ratings concentrate in a few
    categories (the 'kappa paradox'). Reduces to AC1 with identity weights.
    """
    q = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    O = np.zeros((q, q))
    for a, b in zip(r1, r2):
        O[idx[a], idx[b]] += 1
    n = O.sum()
    P = O / n
    w = np.array([[1 - ((i - j) ** 2) / (q - 1) ** 2 if kind == "quadratic"
                   else 1 - abs(i - j) / (q - 1) for j in range(q)] for i in range(q)])
    pa = (w * P).sum()
    pi = (P.sum(1) + P.sum(0)) / 2  # mean use of each category across raters
    pe = (w.sum() / (q * (q - 1))) * (pi * (1 - pi)).sum()
    return float((pa - pe) / (1 - pe)) if (1 - pe) else 1.0


def icc_2_1(r1, r2):
    """ICC(2,1), two-way random effects, single-rater, absolute agreement."""
    X = np.column_stack([r1, r2]).astype(float)
    n, k = X.shape
    gm = X.mean()
    ss_r = k * ((X.mean(1) - gm) ** 2).sum()
    ss_c = n * ((X.mean(0) - gm) ** 2).sum()
    ss_e = ((X - gm) ** 2).sum() - ss_r - ss_c
    msr = ss_r / (n - 1)
    msc = ss_c / (k - 1)
    mse = ss_e / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", default="data/reviewer2_blinded_workbook.xlsx")
    ap.add_argument("--key", default="data/reviewer2_key.csv")
    ap.add_argument("--sheet", default="Review")
    args = ap.parse_args()

    wb = pd.read_excel(ROOT / args.workbook, sheet_name=args.sheet)
    score_col = next((c for c in wb.columns if "score" in c.lower()), None)
    omit_col = next((c for c in wb.columns if "omission" in c.lower()), None)
    wb = wb.rename(columns={"Pair ID": "pair_id", score_col: "r2_score"})
    wb["r2_score"] = pd.to_numeric(wb["r2_score"], errors="coerce")
    wb["r2_omission"] = wb[omit_col] if omit_col else ""
    key = pd.read_csv(ROOT / args.key)

    m = key.merge(wb[["pair_id", "r2_score", "r2_omission"]], on="pair_id", how="inner").dropna(subset=["r2_score"])
    if m.empty:
        raise SystemExit("No completed second-reviewer scores found — has the workbook been filled in?")
    n_total = len(key)
    n_scored = len(m)
    print(f"scored {n_scored}/{n_total} pairs")

    r1 = m["reviewer1_score"].round().clip(1, 4).astype(int).tolist()
    r2 = m["r2_score"].round().clip(1, 4).astype(int).tolist()
    cats = [1, 2, 3, 4]

    exact = float(np.mean([a == b for a, b in zip(r1, r2)]))
    within1 = float(np.mean([abs(a - b) <= 1 for a, b in zip(r1, r2)]))
    kq = weighted_kappa(r1, r2, cats, "quadratic")
    kl = weighted_kappa(r1, r2, cats, "linear")

    # clinically meaningful dichotomy: inappropriate (1-2) vs defensible (3-4)
    d1 = [0 if s <= 2 else 1 for s in r1]
    d2 = [0 if s <= 2 else 1 for s in r2]
    dich_agree = float(np.mean([a == b for a, b in zip(d1, d2)]))
    dich_kappa = weighted_kappa(d1, d2, [0, 1], "linear")

    print(f"\n4-point rubric:")
    print(f"  exact agreement:            {100*exact:5.1f}%")
    print(f"  within-1 agreement:         {100*within1:5.1f}%")
    print(f"  linear-weighted kappa:      {kl:.3f}")
    print(f"  quadratic-weighted kappa:   {kq:.3f}")
    print(f"\ninappropriate(1-2) vs defensible(3-4):")
    print(f"  agreement:                  {100*dich_agree:5.1f}%")
    print(f"  Cohen's kappa:              {dich_kappa:.3f}")

    # ── Marginal-skew-robust agreement + association ───────────────────────
    # Ratings concentrate in tiers 3-4, which inflates weighted kappa's chance
    # term and deflates kappa (the "kappa paradox"). Gwet's AC2 corrects for this;
    # ICC(2,1) is reported as the interval-scale agreement (~ quadratic kappa);
    # Spearman/Kendall summarize ordinal ASSOCIATION (not agreement).
    ac2 = gwet_ac2(r1, r2, cats, "quadratic")
    icc = icc_2_1(r1, r2)
    try:
        from scipy.stats import spearmanr, kendalltau
        rho, rho_p = spearmanr(r1, r2)
        tau, tau_p = kendalltau(r1, r2)
        rho, rho_p, tau, tau_p = float(rho), float(rho_p), float(tau), float(tau_p)
    except Exception:
        rho = rho_p = tau = tau_p = None
    print(f"\nrobust to marginal skew / association:")
    print(f"  Gwet AC2 (quad-ordinal):    {ac2:.3f}")
    print(f"  ICC(2,1) abs. agreement:    {icc:.3f}")
    if rho is not None:
        print(f"  Spearman rho:               {rho:.3f} (p={rho_p:.4f})")
        print(f"  Kendall tau-b:              {tau:.3f} (p={tau_p:.4f})")

    # ── Directional analysis ──────────────────────────────────────────────
    # Higher score = reviewer judged the AI's (often comprehensive) orders as MORE
    # appropriate. If reviewer 2 (less experienced) systematically scores higher /
    # flags fewer plans as inappropriate, that is directional leniency toward AI
    # over-ordering, not random disagreement, and supports the hypothesis that
    # less-experienced clinicians are more accepting of AI-recommended workup.
    mean1, mean2 = float(np.mean(r1)), float(np.mean(r2))
    inappro1 = float(np.mean([s <= 2 for s in r1]))  # rated clearly-unnec/debatable
    inappro2 = float(np.mean([s <= 2 for s in r2]))
    higher = float(np.mean([b > a for a, b in zip(r1, r2)]))
    lower = float(np.mean([b < a for a, b in zip(r1, r2)]))
    # paired Wilcoxon signed-rank on the score difference (if scipy available)
    try:
        from scipy.stats import wilcoxon
        diffs = [b - a for a, b in zip(r1, r2)]
        wp = float(wilcoxon(diffs).pvalue) if any(d != 0 for d in diffs) else 1.0
    except Exception:
        wp = None
    print(f"\ndirectional (does reviewer 2 rate AI plans as more appropriate?):")
    print(f"  mean score  reviewer1={mean1:.2f}  reviewer2={mean2:.2f}  diff={mean2-mean1:+.2f}")
    print(f"  inappropriate-rate (1-2)  reviewer1={100*inappro1:.0f}%  reviewer2={100*inappro2:.0f}%")
    print(f"  reviewer2 scored higher on {100*higher:.0f}% of plans, lower on {100*lower:.0f}%")
    if wp is not None:
        print(f"  Wilcoxon signed-rank p (score difference) = {wp:.4f}")

    # ── Boundary reshuffle: is the disagreement one-directional? ──────────────
    # Of the plans reviewer 1 flagged inappropriate (1-2), how many did reviewer 2
    # upgrade to defensible (3-4), and vice versa. If leniency were systematic the
    # flow would be one-way (r1-flagged -> r2-upgraded) with little reverse flow.
    r1_flag_n = sum(s <= 2 for s in r1)
    r1flag_r2up = sum(1 for a, b in zip(r1, r2) if a <= 2 and b >= 3)
    r2_flag_n = sum(s <= 2 for s in r2)
    r2flag_r1up = sum(1 for a, b in zip(r1, r2) if b <= 2 and a >= 3)
    print(f"\nboundary reshuffle (inappropriate<->defensible):")
    print(f"  reviewer1 flagged {r1_flag_n}; reviewer2 upgraded {r1flag_r2up} of them to defensible")
    print(f"  reviewer2 flagged {r2_flag_n}; reviewer1 upgraded {r2flag_r1up} of them to defensible")

    # ── Omission column: reviewer 2's independent under-ordering judgment ─────
    def yn(x):
        s = "" if pd.isna(x) else str(x).strip()
        if not s:
            return "blank"
        return "Y" if s[:1].lower() == "y" else ("N" if s[:1].lower() == "n" else "other")
    om_flags = [yn(x) for x in m["r2_omission"]]
    om_y = om_flags.count("Y")
    om_n = om_flags.count("N")
    om_blank = om_flags.count("blank") + om_flags.count("other")
    print(f"\nomission (reviewer2 judged AI UNDER-ordered / missed something):")
    print(f"  Y={om_y}  N={om_n}  blank/other={om_blank}  ->  flagged under-ordering on "
          f"{100*om_y/max(1,om_y+om_n):.0f}% of scorable plans")

    out = {
        "n_scored": n_scored, "n_total": n_total,
        "rubric4": {"exact_agreement": exact, "within1_agreement": within1,
                    "linear_weighted_kappa": kl, "quadratic_weighted_kappa": kq},
        "dichotomy": {"agreement": dich_agree, "cohens_kappa": dich_kappa},
        "robust_agreement": {
            "gwet_ac2_quadratic": ac2, "icc_2_1": icc,
            "spearman_rho": rho, "spearman_p": rho_p,
            "kendall_tau_b": tau, "kendall_p": tau_p,
        },
        "directional": {
            "mean_reviewer1": mean1, "mean_reviewer2": mean2,
            "mean_diff_r2_minus_r1": mean2 - mean1,
            "inappropriate_rate_reviewer1": inappro1,
            "inappropriate_rate_reviewer2": inappro2,
            "pct_r2_higher": higher, "pct_r2_lower": lower,
            "wilcoxon_p": wp,
        },
        "boundary_reshuffle": {
            "reviewer1_flagged_n": int(r1_flag_n),
            "reviewer1_flagged_upgraded_by_r2": int(r1flag_r2up),
            "reviewer2_flagged_n": int(r2_flag_n),
            "reviewer2_flagged_upgraded_by_r1": int(r2flag_r1up),
        },
        "omission_reviewer2": {"Y": om_y, "N": om_n, "blank_or_other": om_blank,
                               "under_order_rate": om_y / max(1, om_y + om_n)},
    }
    outp = ROOT / "results" / "analysis" / "irr.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(outp, "w"), indent=2)
    print(f"\nwrote {outp}")


if __name__ == "__main__":
    main()
