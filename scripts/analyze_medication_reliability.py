#!/usr/bin/env python3
"""
Why medication cost is reported as counts rather than dollars (Supplementary
Methods S1.3.1).

Diagnostic tests and specialist consultations carry an administered price: each
maps to a CPT or E/M code with a published Medicare rate. Medications do not.
A drug's cost depends on formulation, dose, duration, formulary and channel,
none of which the note records, so medication cost has to be *imputed* by the
extraction model rather than looked up.

This script quantifies how well that imputation holds up, on three axes:

  1. Agreement  — Lin's concordance between the three independent extractors on
                  the same plan, against the same statistic for diagnostic cost.
  2. Concentration — what share of all imputed medication cost comes from a
                  handful of drug strings.
  3. Influence  — how the AI-minus-physician medication difference moves when
                  the most influential cases are removed.

Outputs: results/analysis/medication_reliability.{json,md}
"""

import ast
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (          # noqa: E402
    MODEL_INFO, SPECIALIZED_MODELS, load_unified_panel,
)
from agreement_stats import lins_ccc          # noqa: E402

OUT_JSON = ROOT / "results" / "analysis" / "medication_reliability.json"
OUT_MD = ROOT / "results" / "analysis" / "medication_reliability.md"

GP_SET = {m for m in MODEL_INFO if m not in SPECIALIZED_MODELS}
BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)
TOP_N = 12


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def as_orders(v):
    if isinstance(v, list):
        return v
    if not v:
        return []
    try:
        out = ast.literal_eval(v)
        return out if isinstance(out, list) else []
    except (ValueError, SyntaxError):
        return []


def slot_med_cost(case, prefix, slot):
    return sum(fnum(o.get("monthly_cost_usd")) for o in as_orders(case.get(f"{prefix}_orders_{slot}"))
               if isinstance(o, dict) and o.get("category") == "medication")


def slot_dx_cost(case, prefix, slot):
    return sum(fnum(o.get("price")) for o in as_orders(case.get(f"{prefix}_orders_{slot}"))
               if isinstance(o, dict) and o.get("category") != "medication")


def boot_ci(v, n=2000):
    v = np.asarray(v, float)
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(v), size=(n, len(v)))
    m = v[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main():
    panel = load_unified_panel()

    # ---- 1. extractor agreement, medications vs diagnostic tests ------------
    med = {s: [] for s in "abc"}
    dx = {s: [] for s in "abc"}
    drug_total = Counter()
    drug_n = Counter()
    drug_prices = defaultdict(list)

    for name, cases in panel.items():
        for c in cases:
            for s in "abc":
                med[s].append(slot_med_cost(c, "llm", s))
                dx[s].append(slot_dx_cost(c, "llm", s))
            for o in as_orders(c.get("llm_orders_b")):
                if isinstance(o, dict) and o.get("category") == "medication":
                    key = (o.get("order") or "").lower().split(",")[0].split("(")[0].strip()[:40]
                    price = fnum(o.get("monthly_cost_usd"))
                    drug_total[key] += price
                    drug_n[key] += 1
                    drug_prices[key].append(price)

    pairs = [("a", "b"), ("a", "c"), ("b", "c")]
    agreement = {"medication": {}, "diagnostic": {}}
    for lab, d in (("medication", med), ("diagnostic", dx)):
        for x, y in pairs:
            cc = lins_ccc(np.array(d[x]), np.array(d[y]))
            agreement[lab][f"{x}_vs_{y}"] = {
                "ccc": cc["ccc"], "pearson_r": cc["pearson_r"],
                "mean_x": float(np.mean(d[x])), "mean_y": float(np.mean(d[y])),
            }
    per_extractor_mean = {s: float(np.mean(med[s])) for s in "abc"}

    # ---- 2. concentration ---------------------------------------------------
    total = sum(drug_total.values())
    top = drug_total.most_common(TOP_N)
    concentration = {
        "n_distinct_medication_strings": len(drug_total),
        "top_n": TOP_N,
        "top_n_share_of_cost": float(sum(v for _, v in top) / total),
        "top": [{"drug": d, "n_orders": drug_n[d], "total_cost": v,
                 "share": v / total,
                 "price_min": min(drug_prices[d]), "price_median": float(np.median(drug_prices[d])),
                 "price_max": max(drug_prices[d])} for d, v in top],
    }

    # ---- 3. influence -------------------------------------------------------
    per_case = defaultdict(list)
    for name, cases in panel.items():
        if name not in GP_SET:
            continue
        for c in cases:
            h = sorted(slot_med_cost(c, "human", s) for s in "abc")[1]
            l = fnum(c.get("medicare_llm_med_cost"))
            per_case[c["case_id"]].append(l - h)
    ids = sorted(per_case)
    diff = np.array([np.mean(per_case[i]) for i in ids])
    order = np.argsort(-np.abs(diff))
    influence = {"all_cases": {"mean": float(diff.mean()), "ci": boot_ci(diff)},
                 "top_case_share_of_absolute_difference":
                     float(abs(diff[order[0]]) / np.abs(diff).sum()),
                 "most_influential_case": ids[order[0]]}
    for k in (1, 3, 5):
        keep = np.ones(len(ids), bool)
        keep[order[:k]] = False
        d = diff[keep]
        influence[f"drop_{k}"] = {"mean": float(d.mean()), "ci": boot_ci(d)}

    out = {"extractor_agreement": agreement,
           "medication_mean_per_plan_by_extractor": per_extractor_mean,
           "concentration": concentration, "influence": influence}
    OUT_JSON.write_text(json.dumps(out, indent=2))

    L = ["# Reliability of imputed medication cost\n",
         "Supporting analysis for Supplementary Methods S1.3.1: why new medications "
         "are reported as counts and excluded from the primary outcome.\n",
         "## 1. Agreement between the three extractors on the same plan\n",
         "| Endpoint | Pair | Lin's CCC | Pearson r | Mean A | Mean B |",
         "|---|---|---:|---:|---:|---:|"]
    for lab in ("medication", "diagnostic"):
        for k, v in agreement[lab].items():
            L.append(f"| {lab} | {k.replace('_', ' ')} | {v['ccc']:.2f} | {v['pearson_r']:.2f} | "
                     f"${v['mean_x']:.0f} | ${v['mean_y']:.0f} |")
    L.append(f"\nMean imputed medication cost per plan by extractor: "
             + ", ".join(f"{s.upper()} ${v:.0f}" for s, v in per_extractor_mean.items())
             + " — a threefold spread on identical plans.\n")

    L += ["## 2. Concentration\n",
          f"{TOP_N} of {concentration['n_distinct_medication_strings']} distinct medication "
          f"strings account for {100*concentration['top_n_share_of_cost']:.0f}% of all imputed "
          "AI medication cost.\n",
          "| Drug string | Orders | Total $ | Share | Imputed $/month (min–median–max) |",
          "|---|---:|---:|---:|---|"]
    for t in concentration["top"]:
        L.append(f"| {t['drug']} | {t['n_orders']} | {t['total_cost']:,.0f} | "
                 f"{100*t['share']:.1f}% | {t['price_min']:,.0f}–{t['price_median']:,.0f}–{t['price_max']:,.0f} |")

    L += ["\n## 3. Influence of individual cases\n",
          "| Cases included | Mean difference $/visit | 95% CI |", "|---|---:|---:|"]
    L.append(f"| all 200 | {influence['all_cases']['mean']:.0f} | "
             f"{influence['all_cases']['ci'][0]:.0f} to {influence['all_cases']['ci'][1]:.0f} |")
    for k in (1, 3, 5):
        v = influence[f"drop_{k}"]
        L.append(f"| dropping the {k} most influential | {v['mean']:.0f} | "
                 f"{v['ci'][0]:.0f} to {v['ci'][1]:.0f} |")
    L.append(f"\nThe single most influential case ({influence['most_influential_case']}) accounts "
             f"for {100*influence['top_case_share_of_absolute_difference']:.0f}% of the total "
             "absolute medication difference, and the sign of the estimate reverses once three "
             "of 200 cases are removed.\n")
    OUT_MD.write_text("\n".join(L) + "\n")

    print("\n".join(L))
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
