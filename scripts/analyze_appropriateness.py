#!/usr/bin/env python3
"""
Consolidate Shahar's physician appropriateness reviews from all 3 batches and
compute the full-cohort (200-case) distribution plus stratified analyses.

Inputs (all in ./data):
  - physician_review_שחר.xlsx            (batch 1: 41 cases, stratified)
  - physician_review_cases_batch2_shahar.xlsx (batch 2: 59 random - columns SWAPPED)
  - physician_review_cases_batch3_shahar.xlsx (batch 3: 103 random)
  - review_master_200.csv                (cohort of 200 cases post guideline screen)

3 case_ids from batch 1 (MTS_0013, MTS_0380, MTS_0971) were later excluded
by the guideline-currency screen and do not appear in review_master_200.

Batch 2 has reviewer_score and reviewer_notes columns swapped (numeric score
landed in reviewer_notes, free-text landed in reviewer_score). Batch 1 uses
half-scores (2.5, 3.5) when reviewer was between two tiers.

Output: results/analysis/appropriateness_full.json + printed summary.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)


def load_batch1() -> pd.DataFrame:
    df = pd.read_excel(DATA / "physician_review_שחר.xlsx")
    df = df[["case_id", "reviewer_score", "reviewer_notes"]].copy()
    df["batch"] = "batch1_stratified"
    df["score_raw"] = df["reviewer_score"]
    df["notes"] = df["reviewer_notes"]
    return df[["case_id", "batch", "score_raw", "notes"]]


def load_batch2() -> pd.DataFrame:
    df = pd.read_excel(DATA / "physician_review_cases_batch2_shahar.xlsx")
    # Columns are swapped — numeric score is in reviewer_notes, free text in reviewer_score
    df = df[["case_id", "reviewer_score", "reviewer_notes"]].copy()
    df["batch"] = "batch2_random"
    df["score_raw"] = df["reviewer_notes"]
    df["notes"] = df["reviewer_score"]
    return df[["case_id", "batch", "score_raw", "notes"]]


def load_batch3() -> pd.DataFrame:
    df = pd.read_excel(DATA / "physician_review_cases_batch3_shahar.xlsx")
    df = df[["case_id", "reviewer_score", "reviewer_notes"]].copy()
    df["batch"] = "batch3_random"
    df["score_raw"] = df["reviewer_score"]
    df["notes"] = df["reviewer_notes"]
    return df[["case_id", "batch", "score_raw", "notes"]]


def bucket(score: float) -> str | None:
    if pd.isna(score):
        return None
    # Half-scores: round up (the stricter interpretation — bucket 2.5 as
    # "debatable/defensive" rounded to 3 = reasonable-given-context; bucket 3.5
    # as guideline-concordant). This matches how half-scores were used: shahar
    # used 2.5 when hovering between debatable (2) and reasonable (3), and we
    # follow the charitable interpretation used in the paper appendix.
    s = round(float(score) + 0.01)  # .5 rounds up deterministically
    if s == 1:
        return "clearly_unnecessary"
    if s == 2:
        return "debatable_defensive"
    if s == 3:
        return "reasonable_given_context"
    if s == 4:
        return "guideline_concordant"
    return None


def fmt_dist(df: pd.DataFrame, label: str) -> dict:
    total = len(df)
    counts = df["bucket"].value_counts().to_dict()
    order = [
        "clearly_unnecessary",
        "debatable_defensive",
        "reasonable_given_context",
        "guideline_concordant",
    ]
    pct = {k: 100 * counts.get(k, 0) / total if total else 0.0 for k in order}
    print(f"\n{label}  (n={total})")
    for k in order:
        n = counts.get(k, 0)
        print(f"  {k:<28} {n:>3}  ({pct[k]:>5.1f}%)")
    inappropriate = pct["clearly_unnecessary"] + pct["debatable_defensive"]
    defensible = pct["reasonable_given_context"] + pct["guideline_concordant"]
    print(f"  ────────────────────────")
    print(f"  Inappropriate (1+2):         {inappropriate:>5.1f}%")
    print(f"  Defensible (3+4):            {defensible:>5.1f}%")
    return {
        "n": total,
        "counts": {k: int(counts.get(k, 0)) for k in order},
        "pct": {k: round(pct[k], 2) for k in order},
        "inappropriate_pct": round(inappropriate, 2),
        "defensible_pct": round(defensible, 2),
    }


def main() -> None:
    b1 = load_batch1()
    b2 = load_batch2()
    b3 = load_batch3()
    all_reviews = pd.concat([b1, b2, b3], ignore_index=True)

    # Sanity: ensure no case_id duplicated across batches
    dup = all_reviews["case_id"].duplicated()
    assert not dup.any(), f"Duplicates across batches: {all_reviews.loc[dup, 'case_id'].tolist()}"

    # Parse scores (batch 2 score_raw arrives as int, batch 1 has halves)
    all_reviews["score"] = pd.to_numeric(all_reviews["score_raw"], errors="coerce")
    all_reviews["bucket"] = all_reviews["score"].map(bucket)

    print("="*70)
    print("APPROPRIATENESS REVIEW — CONSOLIDATED ANALYSIS")
    print("="*70)
    print(f"\nBatches loaded:")
    for name, df in [("batch1_stratified", b1), ("batch2_random", b2), ("batch3_random", b3)]:
        n_scored = pd.to_numeric(df["score_raw"], errors="coerce").notna().sum()
        print(f"  {name:<22} total={len(df):>3}  scored={n_scored}")

    # Full set (all 203 reviews including 3 pre-exclusion)
    _ = fmt_dist(all_reviews.dropna(subset=["bucket"]), "ALL REVIEWS (pre guideline-currency screen)")

    # Cohort-restricted: exclude 3 cases not in the 200-case study cohort
    master = pd.read_csv(DATA / "review_master_200.csv")
    in_cohort = all_reviews[all_reviews["case_id"].isin(master["case_id"])].copy()
    print(f"\nExcluded (not in 200-case cohort — guideline currency screen): "
          f"{sorted(set(all_reviews['case_id']) - set(master['case_id']))}")

    full = fmt_dist(in_cohort.dropna(subset=["bucket"]), "PRIMARY: 200-case cohort")

    # ── Stratified analyses ───────────────────────────────────────────
    cohort = in_cohort.merge(master, on="case_id", how="left")

    # Random-only (batch 2 + batch 3), to replicate the paper's "non-stratified"
    # sensitivity analysis but with the larger n
    rand_only = cohort[cohort["batch"].isin(["batch2_random", "batch3_random"])].dropna(subset=["bucket"])
    random_dist = fmt_dist(rand_only, "SENSITIVITY: random-sampled only (batch 2+3)")

    # Paper's published 97-case set (batch 1 minus 3 excluded, + batch 2)
    paper_set = cohort[cohort["batch"].isin(["batch1_stratified", "batch2_random"])].dropna(subset=["bucket"])
    paper_dist = fmt_dist(paper_set, "REPRODUCE PAPER: 97-case (batch 1+2)")

    # Batch 3 on its own
    b3_cohort = cohort[cohort["batch"] == "batch3_random"].dropna(subset=["bucket"])
    b3_dist = fmt_dist(b3_cohort, "BATCH 3 ONLY (new 103 cases)")

    # ── Stratify by physician ordered zero diagnostic tests (the 68% "zero-plan" cases) ─
    cohort["physician_zero"] = cohort["physician_cost"] == 0
    zero = cohort[cohort["physician_zero"]].dropna(subset=["bucket"])
    nonzero = cohort[~cohort["physician_zero"]].dropna(subset=["bucket"])
    zero_dist = fmt_dist(zero, "STRATIFIED: physician ordered ZERO diagnostics")
    nonzero_dist = fmt_dist(nonzero, "STRATIFIED: physician ordered ≥1 diagnostic")

    # ── Stratify by CCI tier (diagnostic consensus) ─
    tier_dists = {}
    for tier in ["high", "moderate", "low"]:
        sub = cohort[cohort["cci_tier"] == tier].dropna(subset=["bucket"])
        if len(sub):
            tier_dists[tier] = fmt_dist(sub, f"STRATIFIED: CCI tier = {tier}")

    # ── Stratify by specialty ─
    spec_dists = {}
    for sp in sorted(cohort["specialty"].dropna().unique()):
        sub = cohort[cohort["specialty"] == sp].dropna(subset=["bucket"])
        if len(sub):
            spec_dists[sp] = fmt_dist(sub, f"STRATIFIED: specialty = {sp}")

    # ── Link appropriateness score to AI excess cost ─
    print("\n" + "="*70)
    print("AI EXCESS COST BY APPROPRIATENESS BUCKET")
    print("="*70)
    excess_by_bucket = {}
    labeled = cohort.dropna(subset=["bucket"])
    for b in [
        "clearly_unnecessary",
        "debatable_defensive",
        "reasonable_given_context",
        "guideline_concordant",
    ]:
        sub = labeled[labeled["bucket"] == b]
        if len(sub):
            stats = {
                "n": len(sub),
                "mean_excess": round(sub["ai_excess_cost"].mean(), 2),
                "median_excess": round(sub["ai_excess_cost"].median(), 2),
                "mean_ai_cost": round(sub["mean_ai_cost"].mean(), 2),
                "mean_physician_cost": round(sub["physician_cost"].mean(), 2),
            }
            excess_by_bucket[b] = stats
            print(f"  {b:<28} n={stats['n']:>3}  "
                  f"mean_excess=${stats['mean_excess']:>7.0f}  "
                  f"median=${stats['median_excess']:>6.0f}  "
                  f"AI=${stats['mean_ai_cost']:>6.0f}  phys=${stats['mean_physician_cost']:>5.0f}")

    # Cohort-wide excess cost driven by each bucket:
    # treat excess as "appropriate" if bucket ∈ {3,4}, else "waste"
    print("\n" + "="*70)
    print("SHARE OF TOTAL EXCESS COST BY APPROPRIATENESS")
    print("="*70)
    total_excess = labeled["ai_excess_cost"].clip(lower=0).sum()
    for b in ["clearly_unnecessary", "debatable_defensive",
              "reasonable_given_context", "guideline_concordant"]:
        sub = labeled[labeled["bucket"] == b]
        share = 100 * sub["ai_excess_cost"].clip(lower=0).sum() / total_excess if total_excess else 0
        print(f"  {b:<28} share of positive excess = {share:>5.1f}%")
    inappropriate_sum = (
        labeled[labeled["bucket"].isin(["clearly_unnecessary", "debatable_defensive"])]
        ["ai_excess_cost"].clip(lower=0).sum()
    )
    print(f"\n  Inappropriate (1+2) share of excess cost: "
          f"{100 * inappropriate_sum / total_excess:.1f}%")

    # ── Save full results ─
    summary = {
        "full_200_cohort": full,
        "random_only_batch2_3": random_dist,
        "paper_published_97": paper_dist,
        "batch3_only": b3_dist,
        "physician_zero_diag": zero_dist,
        "physician_nonzero_diag": nonzero_dist,
        "by_cci_tier": tier_dists,
        "by_specialty": spec_dists,
        "excess_by_bucket": excess_by_bucket,
        "batch_totals": {
            "batch1_stratified": int(len(b1)),
            "batch2_random": int(len(b2)),
            "batch3_random": int(len(b3)),
            "excluded_by_guideline_screen": sorted(
                set(all_reviews["case_id"]) - set(master["case_id"])
            ),
        },
    }
    outpath = OUT / "appropriateness_full.json"
    with open(outpath, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {outpath}")

    # Also save the per-case merged table so we can slice further
    per_case = cohort[[
        "case_id", "batch", "score", "bucket", "notes",
        "specialty", "cci_tier", "cci_score", "physician_cost",
        "mean_ai_cost", "ai_excess_cost", "physician_dx", "ai_consensus_dx",
    ]].copy()
    per_case_path = OUT / "appropriateness_per_case.csv"
    per_case.to_csv(per_case_path, index=False)
    print(f"Saved: {per_case_path}")


if __name__ == "__main__":
    main()
