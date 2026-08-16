#!/usr/bin/env python3
"""
Preview the UNIFIED standard-prompt panel.

Builds the new Table 1 numbers from results/models/ (the re-run models +
the 5 re-extracted Group O systems = 23 systems), using:
  - dx cost ratio   = mean(medicare_llm_dx_cost) / mean(medicare_human_dx_cost)
                      (single fixed physician baseline, ~$71, shared by all systems)
  - concordance     = 3-JUDGE MAJORITY of {dx_match_v2 (gpt-4.1-mini), dx_claude
                      (sonnet-4.5), dx_gemini (2.5-flash)}; tiers concordant /
                      adjacent / discordant; 3-way tie -> ordinal middle (adjacent)
  - medications     = mean over cases of median-across-3-slots medication-order count
  - referrals       = mean over cases of median-across-3-slots referral-order count
                      (PROVISIONAL: structured referral-category orders, not the
                      canonical two-pass definite-referral extraction)

This is a REVIEW artifact (shown to Dvir before refactoring the canonical pipeline).
It does not write into paper_numbers.json.

Usage:
  python scripts/build_unified_panel.py
  python scripts/build_unified_panel.py --json results/analysis/unified_panel_preview.json
"""

import json
import glob
import os
import argparse
import statistics
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
DX_CATS = {"labs", "imaging", "procedure", "exam", "monitoring"}
SPECIALIZED = {"openevidence", "medgemma-4b", "medgemma-27b", "meditron"}

# label -> ordinal tier (discordant=0, adjacent=1, concordant=2)
TIER = {"correct": 2, "correct_plus": 2, "related": 1, "wrong": 0}


def majority_tier(rec):
    """3-judge majority tier; 3-way tie -> ordinal middle."""
    ts = [TIER[rec[f]] for f in ("dx_match_v2", "dx_claude", "dx_gemini")
          if rec.get(f) in TIER]
    if not ts:
        return None
    c = Counter(ts)
    top, n = c.most_common(1)[0]
    if n == 1 and len(c) == len(ts):       # all distinct -> middle
        return sorted(ts)[len(ts) // 2]
    return top


def med_count(rec):
    counts = [sum(1 for o in (rec.get(f"llm_orders_{s}") or [])
                  if o.get("category") == "medication" and (o.get("monthly_cost_usd", 0) or 0) > 0)
              for s in "abc"]
    return statistics.median(counts) if counts else 0


def ref_count(rec):
    counts = [sum(1 for o in (rec.get(f"llm_orders_{s}") or []) if o.get("category") == "referral")
              for s in "abc"]
    return statistics.median(counts) if counts else 0


def load_unified():
    """All m_*.json in results/models/, deduped by presentation (cohort is pre-filtered)."""
    out = {}
    for f in sorted(glob.glob(str(ROOT / "results" / "models" / "m_*.json"))):
        m = os.path.basename(f)[2:-5]
        if m == "human":
            continue
        seen, uniq = set(), []
        for r in json.load(open(f)):
            p = r.get("presentation")
            if p and p in seen:
                continue
            seen.add(p)
            uniq.append(r)
        out[m] = uniq
    return out


def panel_row(recs):
    ai = [r.get("medicare_llm_dx_cost", 0) or 0 for r in recs]
    ph = [r.get("medicare_human_dx_cost", 0) or 0 for r in recs]
    ai_m, ph_m = statistics.mean(ai), statistics.mean(ph)
    tiers = [majority_tier(r) for r in recs]
    tiers = [t for t in tiers if t is not None]
    nj = len(tiers)
    conc = 100 * sum(t == 2 for t in tiers) / nj if nj else None
    adj = 100 * sum(t == 1 for t in tiers) / nj if nj else None
    disc = 100 * sum(t == 0 for t in tiers) / nj if nj else None
    return {
        "n": len(recs), "n_judged": nj,
        "ai_dx": round(ai_m, 1), "phys_dx": round(ph_m, 1),
        "dx_ratio": round(ai_m / ph_m, 2) if ph_m else None,
        "concordant_pct": round(conc) if conc is not None else None,
        "adjacent_pct": round(adj) if adj is not None else None,
        "discordant_pct": round(disc) if disc is not None else None,
        "med_count": round(statistics.mean([med_count(r) for r in recs]), 2),
        "ref_count": round(statistics.mean([ref_count(r) for r in recs]), 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(ROOT / "results" / "analysis" / "unified_panel_preview.json"))
    args = ap.parse_args()

    data = load_unified()
    rows = {m: panel_row(recs) for m, recs in data.items()}

    hdr = f"{'model':20s} {'n':>4} {'AI$':>6} {'ratio':>6} {'conc':>5} {'adj':>4} {'disc':>5} {'meds':>5} {'refs':>5}"
    print(hdr); print("-" * len(hdr))
    gp_ratios, gp_conc = [], []
    for m in sorted(rows, key=lambda x: (x in SPECIALIZED, x)):
        r = rows[m]
        tag = " [spec]" if m in SPECIALIZED else ""
        print(f"{m:20s} {r['n']:>4} {r['ai_dx']:>6} {str(r['dx_ratio']):>6} "
              f"{str(r['concordant_pct']):>5} {str(r['adjacent_pct']):>4} {str(r['discordant_pct']):>5} "
              f"{r['med_count']:>5} {r['ref_count']:>5}{tag}")
        if m not in SPECIALIZED:
            if r["dx_ratio"] is not None: gp_ratios.append(r["dx_ratio"])
            if r["concordant_pct"] is not None: gp_conc.append(r["concordant_pct"])

    print("-" * len(hdr))
    print(f"GENERAL-PURPOSE mean (n={len(gp_ratios)}): "
          f"dx_ratio={statistics.mean(gp_ratios):.2f}x  concordance={statistics.mean(gp_conc):.0f}%")
    all_ratios = [r["dx_ratio"] for r in rows.values() if r["dx_ratio"] is not None]
    print(f"ALL {len(rows)} systems: dx_ratio range {min(all_ratios):.2f}-{max(all_ratios):.2f}x, "
          f"mean {statistics.mean(all_ratios):.2f}x")

    agg = {
        "n_systems": len(rows),
        "gp_mean_dx_ratio": round(statistics.mean(gp_ratios), 3),
        "gp_mean_concordance_pct": round(statistics.mean(gp_conc), 1),
        "phys_baseline": round(statistics.mean([r["phys_dx"] for r in rows.values()]), 1),
    }
    out = {"models": rows, "_aggregate": agg}
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    json.dump(out, open(args.json, "w"), indent=2)
    print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
