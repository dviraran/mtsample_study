#!/usr/bin/env python3
"""
The single pre-specified primary outcome.

The key outcome is the comparison of the cost of LLM-driven ordering — tests,
consultations and medications, in the aggregate — against the costs derived from
the physician's orders. Exactly one p-value is reported, for this outcome;
everything else is reported as point estimates with confidence limits.

Primary outcome
---------------
Per-visit TOTAL cost of recommended care = diagnostic tests (CY 2026 Medicare
PFS) + specialist consultations (Medicare new-patient E/M) + new medications
(30-day retail supply), for each case, averaged across the 20 general-purpose
systems, compared with the treating physician's plan on the same case.
Paired Wilcoxon signed-rank test over the 200 cases -> the one p-value.

Physician medication cost is not stored in results/models/, so it is computed
here from human_orders_{a,b,c} using exactly the rule applied to the AI side
(sum of monthly_cost_usd over medication-category orders; median of the three
independent extractions).

Outputs:
  results/analysis/primary_outcome.json
  results/analysis/primary_outcome.md
"""

import ast
import sys
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (           # noqa: E402
    MODEL_INFO, SPECIALIZED_MODELS, load_unified_panel,
)

VISIT_FILE = ROOT / "results" / "analysis" / "visit_type.json"
OUT_JSON = ROOT / "results" / "analysis" / "primary_outcome.json"
OUT_MD = ROOT / "results" / "analysis" / "primary_outcome.md"

GP_SET = {m for m in MODEL_INFO if m not in SPECIALIZED_MODELS}
BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)
N_BOOT = 2000


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def as_orders(v):
    """Order lists are stored either as JSON lists or as repr'd Python lists."""
    if isinstance(v, list):
        return v
    if not v:
        return []
    try:
        out = ast.literal_eval(v)
        return out if isinstance(out, list) else []
    except (ValueError, SyntaxError):
        return []


def med_total(orders):
    return sum(fnum(o.get("monthly_cost_usd", 0)) for o in orders
               if isinstance(o, dict) and o.get("category") == "medication")


def human_med_cost(case):
    """Median of the three independent extractions — the study's aggregation rule."""
    slots = [med_total(as_orders(case.get(f"human_orders_{s}"))) for s in "abc"]
    return float(sorted(slots)[1])


def components(case):
    """(physician, AI) component costs for one case."""
    h = {
        "dx": fnum(case.get("medicare_human_dx_cost")),
        "consult": fnum(case.get("human_referral_cost")),
        "med": human_med_cost(case),
    }
    l = {
        "dx": fnum(case.get("medicare_llm_dx_cost")),
        "consult": fnum(case.get("llm_referral_cost")),
        "med": fnum(case.get("medicare_llm_med_cost")),
    }
    # Primary outcome = diagnostic tests + specialist consultations. Medications
    # are excluded and reported as counts: their unit prices are not recorded in
    # the note and must be imputed by the extractor, the three extractors disagree
    # substantially on them (concordance 0.51-0.70, and a threefold spread in the
    # mean per plan), and the difference is dominated by a handful of high-cost
    # agents in single cases -- dropping the three most influential cases reverses
    # its sign. See analyze_medication_reliability.py.
    h["total"] = h["dx"] + h["consult"]
    l["total"] = l["dx"] + l["consult"]
    h["total_with_med"] = h["total"] + h["med"]
    l["total_with_med"] = l["total"] + l["med"]
    return h, l


def boot_ci(v, n_boot=N_BOOT):
    v = np.asarray(v, dtype=float)
    if len(v) < 2:
        return [float("nan"), float("nan")]
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(v), size=(n_boot, len(v)))
    m = v[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def describe(v):
    v = np.asarray(v, dtype=float)
    return {
        "mean": float(v.mean()),
        "mean_ci": boot_ci(v),
        "sd": float(v.std(ddof=1)),
        "median": float(np.median(v)),
        "iqr": [float(np.percentile(v, 25)), float(np.percentile(v, 75))],
    }


def main():
    panel = load_unified_panel()
    enc = {}
    if VISIT_FILE.exists():
        enc = {c["case_id"]: c["encounter_type"]
               for c in json.load(open(VISIT_FILE))["cases"]}

    # ---- per-case, per-model component costs --------------------------------
    # phys[case_id] is identical across models by construction; assert it.
    phys, ai = {}, {}
    for name, cases in panel.items():
        if name not in GP_SET:
            continue
        for c in cases:
            cid = c["case_id"]
            h, l = components(c)
            phys.setdefault(cid, []).append(h)
            ai.setdefault(cid, {})[name] = l

    case_ids = sorted(phys)
    # physician baseline: the per-model extractions of the same physician plan
    # differ slightly, so average them per case (the manuscript's convention).
    KEYS = ("dx", "consult", "med", "total", "total_with_med")
    phys_mean = {cid: {k: float(np.mean([d[k] for d in phys[cid]])) for k in KEYS}
                 for cid in case_ids}
    ai_mean = {cid: {k: float(np.mean([d[k] for d in ai[cid].values()])) for k in KEYS}
               for cid in case_ids}

    h_tot = np.array([phys_mean[c]["total"] for c in case_ids])
    l_tot = np.array([ai_mean[c]["total"] for c in case_ids])
    diff = l_tot - h_tot

    # ---- THE primary test (the only p-value in the paper) -------------------
    stat, p = wilcoxon(l_tot, h_tot)
    n_pos = int((diff > 0).sum())
    n_neg = int((diff < 0).sum())

    primary = {
        "definition": ("per-visit total cost of recommended care = diagnostic "
                       "tests + specialist consultations; AI value is the mean "
                       "across the 20 general-purpose systems; comparator is the "
                       "treating physician's plan on the same case. Medications "
                       "are excluded from the outcome and reported as counts"),
        "n_cases": len(case_ids),
        "n_systems_pooled": len(GP_SET),
        "test": "paired Wilcoxon signed-rank (two-sided)",
        "statistic": float(stat),
        "p_value": float(p),
        "cases_ai_higher": n_pos,
        "cases_ai_lower": n_neg,
        "physician": describe(h_tot),
        "ai": describe(l_tot),
        "difference": describe(diff),
        "ratio_of_means": float(l_tot.mean() / h_tot.mean()),
    }

    # ---- sensitivity: the same outcome with imputed medication cost added back
    hm = np.array([phys_mean[c]["total_with_med"] for c in case_ids])
    lm = np.array([ai_mean[c]["total_with_med"] for c in case_ids])
    sensitivity = {
        "definition": "primary outcome with imputed medication cost added back",
        "physician": describe(hm), "ai": describe(lm),
        "difference": describe(lm - hm),
        "ratio_of_means": float(lm.mean() / hm.mean()),
    }

    # ---- components (point estimates + CI only, no tests) -------------------
    comp = {}
    for k in ("dx", "consult", "med"):
        h = np.array([phys_mean[c][k] for c in case_ids])
        l = np.array([ai_mean[c][k] for c in case_ids])
        comp[k] = {
            "physician": describe(h),
            "ai": describe(l),
            "difference": describe(l - h),
            "ratio_of_means": float(l.mean() / h.mean()) if h.mean() else None,
        }

    # ---- per-system totals (point estimates + CI only) ----------------------
    per_model = {}
    for name, cases in sorted(panel.items()):
        h, l = [], []
        for c in cases:
            hh, ll = components(c)
            h.append(hh["total"])
            l.append(ll["total"])
        h, l = np.array(h), np.array(l)
        per_model[name] = {
            "label": MODEL_INFO[name]["label"],
            "specialized": name in SPECIALIZED_MODELS,
            "n": len(h),
            "phys_total_mean": float(h.mean()),
            "ai_total_mean": float(l.mean()),
            "ratio": float(l.mean() / h.mean()),
            "excess_mean": float((l - h).mean()),
            "excess_ci": boot_ci(l - h),
        }

    # ---- primary outcome restricted to first encounters --------------------
    strata = {}
    if enc:
        for s in ("first_encounter", "established_repeat"):
            ids = [c for c in case_ids if enc.get(c) == s]
            if not ids:
                continue
            h = np.array([phys_mean[c]["total"] for c in ids])
            l = np.array([ai_mean[c]["total"] for c in ids])
            strata[s] = {
                "n_cases": len(ids),
                "physician": describe(h),
                "ai": describe(l),
                "difference": describe(l - h),
                "ratio_of_means": float(l.mean() / h.mean()),
            }

    out = {"primary": primary, "sensitivity_with_medications": sensitivity,
           "components": comp, "per_model_total": per_model,
           "by_encounter_type": strata}
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # ---- report -------------------------------------------------------------
    L, A = [], None
    A = L.append
    A("# Primary outcome — total cost of recommended care\n")
    A("This is the **only** hypothesis test reported in the manuscript and "
      "supplement; every other quantity is a point estimate with a "
      "95% confidence interval.\n")
    A(f"**Definition.** {primary['definition']}.\n")
    A(f"**Result.** Physician ${primary['physician']['mean']:.0f}/visit "
      f"(95% CI ${primary['physician']['mean_ci'][0]:.0f}–"
      f"${primary['physician']['mean_ci'][1]:.0f}; median "
      f"${primary['physician']['median']:.0f}, IQR "
      f"${primary['physician']['iqr'][0]:.0f}–${primary['physician']['iqr'][1]:.0f}) "
      f"vs AI ${primary['ai']['mean']:.0f}/visit "
      f"(95% CI ${primary['ai']['mean_ci'][0]:.0f}–${primary['ai']['mean_ci'][1]:.0f}; "
      f"median ${primary['ai']['median']:.0f}, IQR "
      f"${primary['ai']['iqr'][0]:.0f}–${primary['ai']['iqr'][1]:.0f}).\n")
    p_str = "< 0.001" if primary["p_value"] < 0.001 else f"= {primary['p_value']:.3g}"
    A(f"Mean difference **${primary['difference']['mean']:.0f}/visit** "
      f"(95% CI ${primary['difference']['mean_ci'][0]:.0f}–"
      f"${primary['difference']['mean_ci'][1]:.0f}), ratio of means "
      f"**{primary['ratio_of_means']:.2f}×**; AI higher in "
      f"{primary['cases_ai_higher']}/{primary['n_cases']} cases, lower in "
      f"{primary['cases_ai_lower']}. Paired Wilcoxon signed-rank "
      f"**P {p_str}** (exact p = {primary['p_value']:.3g}).\n")
    A("## Components (point estimates only — no tests)\n")
    A("| Component | Physician mean (95% CI) | AI mean (95% CI) | Difference (95% CI) | Ratio |")
    A("|---|---:|---:|---:|---:|")
    names = {"dx": "Diagnostic tests", "consult": "Specialist consultations",
             "med": "New medications (imputed; excluded from the outcome)"}
    for k, lab in names.items():
        c = comp[k]
        A(f"| {lab} | ${c['physician']['mean']:.0f} "
          f"(${c['physician']['mean_ci'][0]:.0f}–${c['physician']['mean_ci'][1]:.0f}) | "
          f"${c['ai']['mean']:.0f} (${c['ai']['mean_ci'][0]:.0f}–${c['ai']['mean_ci'][1]:.0f}) | "
          f"${c['difference']['mean']:.0f} "
          f"(${c['difference']['mean_ci'][0]:.0f}–${c['difference']['mean_ci'][1]:.0f}) | "
          f"{c['ratio_of_means']:.2f}× |")
    A("")
    A("## Sensitivity: medications added back\n")
    A(f"Physician ${sensitivity['physician']['mean']:.0f} vs AI "
      f"${sensitivity['ai']['mean']:.0f}; difference "
      f"${sensitivity['difference']['mean']:.0f} "
      f"(95% CI ${sensitivity['difference']['mean_ci'][0]:.0f}-"
      f"${sensitivity['difference']['mean_ci'][1]:.0f}), ratio "
      f"{sensitivity['ratio_of_means']:.2f}x.\n")
    if strata:
        A("## Primary outcome by encounter type\n")
        A("| Stratum | n | Physician | AI | Difference (95% CI) | Ratio |")
        A("|---|---:|---:|---:|---:|---:|")
        for s, v in strata.items():
            A(f"| {s} | {v['n_cases']} | ${v['physician']['mean']:.0f} | "
              f"${v['ai']['mean']:.0f} | ${v['difference']['mean']:.0f} "
              f"(${v['difference']['mean_ci'][0]:.0f}–"
              f"${v['difference']['mean_ci'][1]:.0f}) | {v['ratio_of_means']:.2f}× |")
        A("")
    A("## Per-system total cost of recommended care\n")
    A("| System | Physician $/visit | AI $/visit | Ratio | Excess (95% CI) |")
    A("|---|---:|---:|---:|---:|")
    for m, v in sorted(per_model.items(), key=lambda kv: -kv[1]["ratio"]):
        star = " *" if v["specialized"] else ""
        A(f"| {v['label']}{star} | ${v['phys_total_mean']:.0f} | ${v['ai_total_mean']:.0f} | "
          f"{v['ratio']:.2f}× | ${v['excess_mean']:.0f} "
          f"(${v['excess_ci'][0]:.0f}–${v['excess_ci'][1]:.0f}) |")
    A("\n\\* specialized medical AI system")
    OUT_MD.write_text("\n".join(L) + "\n")

    print("\n".join(L))
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
