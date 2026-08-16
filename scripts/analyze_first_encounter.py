#!/usr/bin/env python3
"""
Re-run the primary cost analysis stratified by encounter type
(first encounter vs established/repeat visit).

Requires results/analysis/visit_type.json (scripts/classify_visit_type.py).

Outputs:
  results/analysis/first_encounter_analysis.json
  results/analysis/first_encounter_analysis.md
"""

import sys
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (           # noqa: E402
    MODEL_INFO, SPECIALIZED_MODELS, load_unified_panel,
)

VISIT_FILE = ROOT / "results" / "analysis" / "visit_type.json"
OUT_JSON = ROOT / "results" / "analysis" / "first_encounter_analysis.json"
OUT_MD = ROOT / "results" / "analysis" / "first_encounter_analysis.md"

GP_SET = {m for m in MODEL_INFO if m not in SPECIALIZED_MODELS}
# The last two are robustness checks on the classification itself: cases all three
# judges called a first encounter, and emergency-department visits, which are
# first encounters by definition regardless of how the judges labelled them.
STRATA = ["all", "first_encounter", "established_repeat", "indeterminate",
          "first_encounter_unanimous", "emergency_department"]
BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)
N_BOOT = 2000


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def case_arrays(cases):
    """(physician dx cost, AI dx cost) arrays for a list of case records."""
    h = np.array([fnum(c.get("medicare_human_dx_cost")) for c in cases])
    l = np.array([fnum(c.get("medicare_llm_dx_cost")) for c in cases])
    return h, l


def boot_ci(vals_per_case, n_boot=N_BOOT):
    """Case-level bootstrap CI of the mean."""
    v = np.asarray(vals_per_case, dtype=float)
    if len(v) < 2:
        return (float("nan"), float("nan"))
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def main():
    if not VISIT_FILE.exists():
        sys.exit(f"missing {VISIT_FILE} — run scripts/classify_visit_type.py first")

    vt = json.load(open(VISIT_FILE))
    enc = {c["case_id"]: c["encounter_type"] for c in vt["cases"]}
    prior_res = {c["case_id"]: c["prior_results_in_note"] for c in vt["cases"]}
    membership = {}
    for c in vt["cases"]:
        m = {"all", c["encounter_type"]}
        if c["encounter_type"] == "first_encounter" and c["unanimous"]:
            m.add("first_encounter_unanimous")
        if c["setting"] == "emergency_department":
            m.add("emergency_department")
        membership[c["case_id"]] = m

    def in_stratum(case_id, s):
        return s in membership.get(case_id, {"all"})

    panel = load_unified_panel()
    print(f"loaded {len(panel)} systems; visit types for {len(enc)} cases")

    # ---- per-model, per-stratum -------------------------------------------
    per_model = {}
    # pooled per-case excess, keyed by stratum: {case_id: [excess across GP models]}
    pooled = {s: {} for s in STRATA}

    for name, cases in sorted(panel.items()):
        rec = {}
        for s in STRATA:
            sub = [c for c in cases if in_stratum(c["case_id"], s)]
            if not sub:
                continue
            h, l = case_arrays(sub)
            excess = l - h
            rec[s] = {
                "n": len(sub),
                "phys_mean": float(h.mean()),
                "ai_mean": float(l.mean()),
                "ratio": float(l.mean() / h.mean()) if h.mean() else float("nan"),
                "excess_mean": float(excess.mean()),
                "excess_ci": boot_ci(excess),
                "phys_zero_pct": float(100 * (h == 0).mean()),
                "ai_added_when_phys_zero_pct": (
                    float(100 * (l[h == 0] > 0).mean()) if (h == 0).any() else float("nan")
                ),
            }
            if name in GP_SET:
                for c, e in zip(sub, excess):
                    pooled[s].setdefault(c["case_id"], []).append(e)
        per_model[name] = rec

    # ---- pooled across the 20 general-purpose systems ----------------------
    # Cluster bootstrap over cases: resample cases, average the per-case
    # across-model mean excess. Matches the manuscript's aggregate CI method.
    pooled_stats = {}
    for s in STRATA:
        if not pooled[s]:
            continue
        ids = sorted(pooled[s])
        per_case_mean = np.array([np.mean(pooled[s][i]) for i in ids])
        lo, hi = boot_ci(per_case_mean)
        # physician baseline in this stratum (same for every model; take one)
        ref = next(iter(panel.values()))
        sub = [c for c in ref if in_stratum(c["case_id"], s)]
        h, _ = case_arrays(sub)
        gp_ratios = [per_model[m][s]["ratio"] for m in GP_SET
                     if s in per_model.get(m, {})]
        pooled_stats[s] = {
            "n_cases": len(ids),
            "phys_mean": float(h.mean()),
            "phys_median": float(np.median(h)),
            "phys_sd": float(h.std(ddof=1)),
            "phys_iqr": [float(np.percentile(h, 25)), float(np.percentile(h, 75))],
            "phys_zero_pct": float(100 * (h == 0).mean()),
            "gp_mean_excess": float(per_case_mean.mean()),
            "gp_mean_excess_ci": [lo, hi],
            "gp_mean_ratio": float(np.mean(gp_ratios)),
            "gp_ratio_range": [float(np.min(gp_ratios)), float(np.max(gp_ratios))],
            "n_gp_models_above_phys": int(sum(r > 1 for r in gp_ratios)),
            "n_gp_models": len(gp_ratios),
        }

    # ---- prior-results cross-tab (the editor's mechanism) ------------------
    ref = next(iter(panel.values()))
    xtab = {}
    for s in STRATA:
        sub = [c for c in ref if in_stratum(c["case_id"], s)]
        if not sub:
            continue
        pr = np.array([bool(prior_res.get(c["case_id"], False)) for c in sub])
        h, _ = case_arrays(sub)
        xtab[s] = {
            "n": len(sub),
            "pct_note_reports_prior_results": float(100 * pr.mean()),
            "phys_mean_cost_with_prior_results": float(h[pr].mean()) if pr.any() else None,
            "phys_mean_cost_without": float(h[~pr].mean()) if (~pr).any() else None,
        }

    out = {
        "visit_type_summary": vt["summary"],
        "pooled": pooled_stats,
        "per_model": per_model,
        "prior_results_crosstab": xtab,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # ---- markdown report ---------------------------------------------------
    L = []
    A = L.append
    A("# First-encounter vs repeat-visit sensitivity analysis\n")
    A("Encounter type assigned by 3-judge majority vote "
      "(GPT-4.1-mini, Claude Sonnet 4.5, Gemini 2.5 Flash) on the "
      "clinical presentation only.\n")
    vs = vt["summary"]
    A("## Cohort composition\n")
    A(f"- First encounter: **{vs['encounter_type']['first_encounter']} "
      f"({vs['encounter_type_pct']['first_encounter']}%)**")
    A(f"- Established / repeat visit: **{vs['encounter_type']['established_repeat']} "
      f"({vs['encounter_type_pct']['established_repeat']}%)**")
    A(f"- Indeterminate: **{vs['encounter_type']['indeterminate']} "
      f"({vs['encounter_type_pct']['indeterminate']}%)**")
    A(f"- Unanimous across all three judges: {vs['unanimous']}/{vs['n_cases']}; "
      f"no majority (tie): {vs['needs_adjudication']}")
    A(f"- Pairwise raw agreement: " +
      ", ".join(f"{k} {v:.0%}" for k, v in vs["pairwise_agreement"].items()))
    A(f"- Setting: " + ", ".join(f"{k} {v}" for k, v in sorted(vs["setting"].items())))
    A("")
    A("## Pooled result by stratum (20 general-purpose systems)\n")
    A("| Stratum | n cases | Physician $/visit (mean) | median [IQR] | % $0 visits | "
      "AI mean excess $/visit (95% CI) | mean ratio | ratio range | models > physician |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for s in STRATA:
        if s not in pooled_stats:
            continue
        p = pooled_stats[s]
        A(f"| {s} | {p['n_cases']} | ${p['phys_mean']:.0f} | "
          f"${p['phys_median']:.0f} [{p['phys_iqr'][0]:.0f}–{p['phys_iqr'][1]:.0f}] | "
          f"{p['phys_zero_pct']:.0f}% | "
          f"${p['gp_mean_excess']:.0f} (${p['gp_mean_excess_ci'][0]:.0f}–"
          f"${p['gp_mean_excess_ci'][1]:.0f}) | {p['gp_mean_ratio']:.2f}× | "
          f"{p['gp_ratio_range'][0]:.2f}–{p['gp_ratio_range'][1]:.2f}× | "
          f"{p['n_gp_models_above_phys']}/{p['n_gp_models']} |")
    A("")
    A("## Per-model, first encounters vs repeat visits\n")
    A("| System | n first | Phys $ | AI $ | ratio | excess (95% CI) | "
      "n repeat | Phys $ | AI $ | ratio | excess (95% CI) |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for m in sorted(per_model, key=lambda k: MODEL_INFO[k]["label"]):
        f = per_model[m].get("first_encounter")
        r = per_model[m].get("established_repeat")
        if not f or not r:
            continue
        A(f"| {MODEL_INFO[m]['label']} | {f['n']} | ${f['phys_mean']:.0f} | "
          f"${f['ai_mean']:.0f} | {f['ratio']:.2f}× | ${f['excess_mean']:.0f} "
          f"(${f['excess_ci'][0]:.0f}–${f['excess_ci'][1]:.0f}) | "
          f"{r['n']} | ${r['phys_mean']:.0f} | ${r['ai_mean']:.0f} | "
          f"{r['ratio']:.2f}× | ${r['excess_mean']:.0f} "
          f"(${r['excess_ci'][0]:.0f}–${r['excess_ci'][1]:.0f}) |")
    A("")
    A("## Does the note itself carry prior results?\n")
    A("| Stratum | n | % notes reporting prior test results | Phys $/visit if prior results | if not |")
    A("|---|---:|---:|---:|---:|")
    for s, x in xtab.items():
        a = f"${x['phys_mean_cost_with_prior_results']:.0f}" if x["phys_mean_cost_with_prior_results"] is not None else "—"
        b = f"${x['phys_mean_cost_without']:.0f}" if x["phys_mean_cost_without"] is not None else "—"
        A(f"| {s} | {x['n']} | {x['pct_note_reports_prior_results']:.0f}% | {a} | {b} |")
    OUT_MD.write_text("\n".join(L) + "\n")

    print("\n".join(L[:40]))
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
