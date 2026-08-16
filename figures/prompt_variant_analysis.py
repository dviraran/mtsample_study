#!/usr/bin/env python3
"""
Decision-gate analysis for the prompt-sensitivity experiment.

Reads the arm result dirs (results/models_<arm>/m_*.json) produced by
scripts/run_prompt_variants.py + priced by scripts/price_arms.py + judged by
scripts/judge_dx.py, and reports, per model and per arm:

  - mean AI diagnostic cost (Medicare) and ratio to the fixed physician baseline
  - % change vs the default arm (the prompt effect)
  - diagnostic concordance % (correct + correct_plus, from dx_match_v2)
  - mean diagnostic test / medication / referral counts per visit

No numbers are hardcoded; everything is read from the arm dirs. Also writes a machine
-readable summary to results/analysis/prompt_variants.json.

Usage:
  python figures/prompt_variant_analysis.py [--arms default,parsimonious,costaware]
"""

import json
import glob
import argparse
import statistics
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DIAG = {"labs", "imaging", "procedure", "exam", "monitoring"}
CONCORDANT = {"correct", "correct_plus"}


def dedup(records):
    seen, out = set(), []
    for r in records:
        p = r.get("presentation", "")
        if p and p not in seen:
            seen.add(p)
            out.append(r)
    return out


def slot_count(rec, cats, slot="a"):
    return sum(1 for o in rec.get(f"llm_orders_{slot}", []) if o.get("category") in cats)


def summarize(records):
    recs = dedup(records)
    n = len(recs)
    ai = [r.get("medicare_llm_dx_cost", 0) or 0 for r in recs]
    ph = [r.get("medicare_human_dx_cost", 0) or 0 for r in recs]
    judged = [r.get("dx_match_v2") for r in recs if r.get("dx_match_v2") in
              {"correct", "correct_plus", "related", "wrong"}]
    cc = Counter(judged)
    n_j = len(judged)
    labs = [slot_count(r, {"labs"}) for r in recs]
    imaging = [slot_count(r, {"imaging"}) for r in recs]
    dx_orders = [slot_count(r, DIAG) for r in recs]
    meds = [slot_count(r, {"medication"}) for r in recs]
    refs = [slot_count(r, {"referral"}) for r in recs]
    mean = lambda x: statistics.mean(x) if x else 0.0
    return {
        "n": n,
        "ai_cost": mean(ai),
        "phys_cost": mean(ph),
        "ratio": (mean(ai) / mean(ph)) if mean(ph) else None,
        "n_judged": n_j,
        "concordance_pct": (100 * sum(cc[k] for k in CONCORDANT) / n_j) if n_j else None,
        "match_breakdown": dict(cc),
        "dx_orders": mean(dx_orders),
        "labs": mean(labs),
        "imaging": mean(imaging),
        "meds": mean(meds),
        "referrals": mean(refs),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="default,parsimonious,costaware")
    args = ap.parse_args()
    arms = [a.strip() for a in args.arms.split(",")]

    # discover models present in any arm
    models = set()
    for arm in arms:
        for f in glob.glob(str(ROOT / "results" / ("models" if arm == "default" else f"models_{arm}") / "m_*.json")):
            models.add(Path(f).stem.replace("m_", ""))
    models = sorted(models)

    summary = {}
    print(f"\n{'model':18s} {'arm':13s} {'n':>4} {'AI$':>7} {'ratio':>6} {'Δvs def':>8} "
          f"{'concord%':>9} {'#dx':>5} {'#med':>5} {'#ref':>5}")
    print("-" * 92)
    for m in models:
        summary[m] = {}
        default_cost = None
        for arm in arms:
            f = ROOT / "results" / ("models" if arm == "default" else f"models_{arm}") / f"m_{m}.json"
            if not f.exists():
                continue
            s = summarize(json.load(open(f)))
            summary[m][arm] = s
            if arm == "default":
                default_cost = s["ai_cost"]
            dpct = (100 * (s["ai_cost"] - default_cost) / default_cost
                    if default_cost else None)
            ratio_s = f"{s['ratio']:.2f}" if s["ratio"] is not None else "-"
            dpct_s = f"{dpct:+.0f}%" if dpct is not None else ""
            conc_s = f"{s['concordance_pct']:.0f}%" if s["concordance_pct"] is not None else "-"
            print(f"{m:18s} {arm:13s} {s['n']:4d} {s['ai_cost']:7.1f} "
                  f"{ratio_s:>6} {dpct_s:>8} {conc_s:>9} "
                  f"{s['dx_orders']:5.1f} {s['meds']:5.1f} {s['referrals']:5.1f}")
        print()

    outdir = ROOT / "results" / "analysis"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "prompt_variants.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"wrote {outdir / 'prompt_variants.json'}")


if __name__ == "__main__":
    main()
