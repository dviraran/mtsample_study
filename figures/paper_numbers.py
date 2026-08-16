#!/usr/bin/env python3
"""Single source of truth for every number cited in manuscript.tex.

Computes all numbers from the unified 24-system panel in results/models/m_*.json
(via generate_paper_figures.load_unified_panel, canonical n=200 filter); the
appropriateness sub-study is anchored to the original reviewed plans in
results/models_original_runs/. Writes:

  results/analysis/paper_numbers.json   — machine-readable
  results/analysis/paper_numbers.md     — human-readable table; diff this against
                                          manuscript.tex when updating numbers

Also importable: from paper_numbers import compute_all_numbers
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median

import numpy as np
from scipy.stats import wilcoxon, pearsonr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (
    EXCLUDED_CASES,
    MODEL_INFO,
    SPECIALIZED_MODELS,
    build_stats_df,
    load_all_models,
    load_unified_panel,
    majority_tier,
)

OUT_JSON = ROOT / "results" / "analysis" / "paper_numbers.json"
OUT_MD = ROOT / "results" / "analysis" / "paper_numbers.md"

# Net within-family generational change (oldest -> newest evaluated version), on the
# unified panel. Pro line only for Gemini (flash is a separate tier). DeepSeek is a
# variant pair (general vs reasoning), not a successive version.
VERSION_FAMILIES = [
    ("GPT", "gpt-4.1", "gpt-5.5"),
    ("Qwen", "qwen-2.5-72b", "qwen-3.7"),
    ("Gemini", "gemini-2.5-pro", "gemini-3.1-pro"),
    ("Grok", "grok-3", "grok-4.3"),
    ("Llama", "llama-3.3-70b", "llama4"),
    ("Claude", "claude-sonnet-3.5", "claude-opus-4.8"),
    ("DeepSeek", "deepseek-v3.2", "deepseek-r1"),
]

# Appropriateness-review data: 5 reviewed models mapped to their m_*.json keys
APPROP_XLSX = ROOT / "data" / "appropriateness_review.xlsx"
APPROP_MODELS = {
    "GPT-5.2":      "gpt-5.2",
    "Claude 4.5":   "claude-sonnet-4.5",
    "Gemini 3 Pro": "gemini-3-pro",
    "Grok 4.1":     "grok-4.1",
    "OpenEvidence": "openevidence",
}
# Shahar inserted a 'Score/Comment' column pair after each model's grok_score,
# then appended OpenEvidence at the very end (Score.4/Comment.4).
APPROP_SCORE_COLS = {
    "GPT-5.2":      "Score",
    "Claude 4.5":   "Score.1",
    "Gemini 3 Pro": "Score.2",
    "Grok 4.1":     "Score.3",
    "OpenEvidence": "Score.4",
}

GP_SET = {m for m in MODEL_INFO if m not in SPECIALIZED_MODELS}

COMMERCIAL_FACTOR = 2.0   # Fig 4 caption says "2x Medicare"
ANNUAL_VISITS = 883e6


def _is_test(cat: str) -> bool:
    c = (cat or "").lower()
    TEST_CATS = {"lab", "laboratory", "labs", "imaging", "test", "procedure",
                 "monitoring", "diagnostic", "screening"}
    return ("med" not in c) and any(k in c for k in TEST_CATS)


def slot_counts(case, prefix):
    return [len(case.get(f"{prefix}{s}", []) or []) for s in ("a", "b", "c")]


def compute_all_numbers(all_data: dict | None = None) -> dict:
    # Main result = the unified 24-system standard-prompt panel (results/models/).
    # The appropriateness sub-study (below) stays on the original reviewed plans
    # (results/models_original_runs/).
    if all_data is None:
        all_data = load_unified_panel()

    out = {}

    # ─── Per-model stats (n=200 each) ─────────────────────────────
    per_model = []
    for model, cases in all_data.items():
        if model not in MODEL_INFO:
            continue
        info = MODEL_INFO[model]
        h_dx = np.array([c.get("medicare_human_dx_cost") or 0 for c in cases])
        l_dx = np.array([c.get("medicare_llm_dx_cost") or 0 for c in cases])
        l_ref_count = [c.get("llm_referral_count") or 0 for c in cases]
        h_ref_count = [c.get("human_referral_count") or 0 for c in cases]

        # Diagnostic agreement — 3-judge majority (concordant / adjacent / discordant)
        tiers = [majority_tier(c) for c in cases]
        tiers = [t for t in tiers if t is not None]
        n_dx = len(tiers)
        correct = sum(1 for t in tiers if t == 2)
        related = sum(1 for t in tiers if t == 1)
        wrong = sum(1 for t in tiers if t == 0)
        acc = 100 * correct / n_dx if n_dx else 0
        related_pct = 100 * related / n_dx if n_dx else 0
        wrong_pct = 100 * wrong / n_dx if n_dx else 0

        # Medication counts — median across 3 extractor slots
        llm_meds = []
        human_meds = []
        for c in cases:
            l_slot = [sum(1 for o in (c.get(f"llm_orders_{s}") or []) if o.get("category") == "medication") for s in "abc"]
            h_slot = [sum(1 for o in (c.get(f"human_orders_{s}") or []) if o.get("category") == "medication") for s in "abc"]
            llm_meds.append(median(l_slot))
            human_meds.append(median(h_slot))

        over = int(np.sum(l_dx > h_dx))
        match = int(np.sum(l_dx == h_dx))
        under = int(np.sum(l_dx < h_dx))

        # Zero-physician subset
        zero_mask = h_dx == 0
        n_zero = int(zero_mask.sum())
        n_added = int(np.sum(l_dx[zero_mask] > 0)) if n_zero else 0
        pct_added = 100 * n_added / n_zero if n_zero else 0

        per_model.append({
            "model": model,
            "label": info["label"],
            "family": info["family"],
            "gen": info["gen"],
            "n": len(cases),
            "phys_dx_cost": float(h_dx.mean()),
            "llm_dx_cost": float(l_dx.mean()),
            "dx_ratio": float(l_dx.mean() / h_dx.mean()) if h_dx.mean() else 0,
            "dx_excess": float((l_dx - h_dx).mean()),
            "accuracy_pct": round(acc, 1),
            "related_pct": round(related_pct, 1),
            "wrong_pct": round(wrong_pct, 1),
            "llm_med_count": float(np.mean(llm_meds)),
            "phys_med_count": float(np.mean(human_meds)),
            "llm_ref_count": float(np.mean(l_ref_count)),
            "phys_ref_count": float(np.mean(h_ref_count)),
            "over": over, "match": match, "under": under,
            "n_zero_phys": n_zero,
            "pct_added_when_phys_zero": round(pct_added, 1),
        })
    out["per_model"] = per_model

    # ─── Aggregates used in Abstract / Results body ───────────────
    df_like = {r["model"]: r for r in per_model}
    gp_rows = [r for r in per_model if r["model"] in GP_SET]
    all_rows = per_model

    phys_avg = np.mean([r["phys_dx_cost"] for r in per_model])
    phys_med_count = np.mean([r["phys_med_count"] for r in per_model])
    phys_ref_count = np.mean([r["phys_ref_count"] for r in per_model])

    dx_ratios = [r["dx_ratio"] for r in all_rows]
    excesses = [r["dx_excess"] for r in all_rows]

    out["aggregate"] = {
        "n_cases_primary": per_model[0]["n"] if per_model else 0,
        "n_models_total": len(per_model),
        "n_models_gp": len(gp_rows),
        "n_models_specialized": len(all_rows) - len(gp_rows),
        "n_ai_physician_comparisons": len(per_model) * per_model[0]["n"] if per_model else 0,
        "phys_dx_cost_avg": round(phys_avg, 2),
        "phys_med_count": round(phys_med_count, 2),
        "phys_ref_count": round(phys_ref_count, 2),
        "dx_ratio_min": round(min(dx_ratios), 2),
        "dx_ratio_max": round(max(dx_ratios), 2),
        "dx_cost_min": round(min(r["llm_dx_cost"] for r in all_rows), 0),
        "dx_cost_max": round(max(r["llm_dx_cost"] for r in all_rows), 0),
        "dx_ratio_min_model": min(all_rows, key=lambda r: r["dx_ratio"])["label"],
        "dx_ratio_max_model": max(all_rows, key=lambda r: r["dx_ratio"])["label"],
        "mean_excess_gp_unweighted": round(float(np.mean([r["dx_excess"] for r in gp_rows])), 2),
        "med_count_min": round(min(r["llm_med_count"] for r in all_rows), 2),
        "med_count_max": round(max(r["llm_med_count"] for r in all_rows), 2),
        "med_ratio_max": round(max(r["llm_med_count"] / phys_med_count for r in all_rows), 1),
        "ref_count_min": round(min(r["llm_ref_count"] for r in all_rows), 2),
        "ref_count_max": round(max(r["llm_ref_count"] for r in all_rows), 2),
        "ref_ratio_min": round(min(r["llm_ref_count"] / phys_ref_count for r in all_rows), 1),
        "ref_ratio_max": round(max(r["llm_ref_count"] / phys_ref_count for r in all_rows), 1),
        "pct_added_min": round(min(r["pct_added_when_phys_zero"] for r in all_rows), 0),
        "pct_added_max": round(max(r["pct_added_when_phys_zero"] for r in all_rows), 0),
    }

    # ─── 67% zero-physician cases (from any model's view; physician is same) ──
    any_cases = all_data[next(iter(all_data))]
    h = np.array([c.get("medicare_human_dx_cost") or 0 for c in any_cases])
    n_zero = int((h == 0).sum())
    n_nonzero = int((h > 0).sum())
    out["aggregate"]["n_zero_phys_cases"] = n_zero
    out["aggregate"]["n_nonzero_phys_cases"] = n_nonzero
    out["aggregate"]["pct_zero_phys"] = round(100 * n_zero / len(h), 1)

    # NAMCS strata
    routine = (h == 0).sum()
    simple = ((h > 0) & (h <= 100)).sum()
    significant = (h > 100).sum()
    n = len(h)
    out["aggregate"]["namcs_strata_pct"] = {
        "routine_zero": round(100 * routine / n, 0),
        "simple_1_100": round(100 * simple / n, 0),
        "significant_gt100": round(100 * significant / n, 0),
    }

    # ─── Per-family version changes with paired Wilcoxon ──────────
    version_changes = []
    for fam, old_m, new_m in VERSION_FAMILIES:
        d_old = all_data.get(old_m, [])
        d_new = all_data.get(new_m, [])
        old_by = {c["case_id"]: c for c in d_old}
        new_by = {c["case_id"]: c for c in d_new}
        common = sorted(set(old_by) & set(new_by))
        old_c = np.array([old_by[c].get("medicare_llm_dx_cost") or 0 for c in common])
        new_c = np.array([new_by[c].get("medicare_llm_dx_cost") or 0 for c in common])
        h_old = np.array([old_by[c].get("medicare_human_dx_cost") or 0 for c in common])
        h_new = np.array([new_by[c].get("medicare_human_dx_cost") or 0 for c in common])
        try:
            _, p = wilcoxon(new_c, old_c)
        except ValueError:
            p = float("nan")
        fold_old = old_c.mean() / h_old.mean() if h_old.mean() else 0
        fold_new = new_c.mean() / h_new.mean() if h_new.mean() else 0
        pct = (fold_new - fold_old) / fold_old * 100 if fold_old else 0
        version_changes.append({
            "family": fam,
            "old_model": old_m,
            "new_model": new_m,
            "n": len(common),
            "fold_old": round(fold_old, 2),
            "fold_new": round(fold_new, 2),
            "pct_change": round(pct, 1),
            "p_value": round(p, 4) if p == p else None,
        })
    out["version_changes"] = version_changes

    # ─── Zero vs nonzero physician subset (Table S5 source) ──────
    subset = []
    for r in per_model:
        cases = all_data[r["model"]]
        zero = [c for c in cases if (c.get("medicare_human_dx_cost") or 0) == 0]
        nz = [c for c in cases if (c.get("medicare_human_dx_cost") or 0) > 0]
        z_l = float(np.mean([c.get("medicare_llm_dx_cost") or 0 for c in zero])) if zero else 0
        nz_h = float(np.mean([c.get("medicare_human_dx_cost") or 0 for c in nz])) if nz else 0
        nz_l = float(np.mean([c.get("medicare_llm_dx_cost") or 0 for c in nz])) if nz else 0
        nz_ratio = nz_l / nz_h if nz_h else 0
        subset.append({
            "model": r["model"],
            "label": r["label"],
            "zero_phys_ai_cost": round(z_l, 2),
            "nonzero_phys_phys_cost": round(nz_h, 2),
            "nonzero_phys_ai_cost": round(nz_l, 2),
            "nonzero_ratio": round(nz_ratio, 2),
        })
    out["subset_by_phys_ordering"] = subset
    gp_subset = [s for s in subset if s["model"] in GP_SET]
    out["aggregate"]["subset_zero_ai_mean"] = round(float(np.mean([s["zero_phys_ai_cost"] for s in gp_subset])), 2)
    out["aggregate"]["subset_nonzero_phys_mean"] = round(float(np.mean([s["nonzero_phys_phys_cost"] for s in gp_subset])), 2)
    out["aggregate"]["subset_nonzero_ratio_mean"] = round(float(np.mean([s["nonzero_ratio"] for s in gp_subset])), 2)
    out["aggregate"]["subset_nonzero_under_physician"] = sum(1 for s in gp_subset if s["nonzero_ratio"] < 1.0)

    # ─── Population projections ───────────────────────────────────
    # Match Figure 5 exactly: project only the six newest current-generation
    # flagships, using the same NAMCS-reweighted per-visit excess the figure plots
    # (excess_dx_weighted), so the min/max billions agree with the figure and text.
    FIG5_MODELS = {"gpt-5.5", "claude-opus-4.8", "qwen-3.7",
                   "gemini-3.1-pro", "grok-4.3", "deepseek-r1"}
    _wdf = build_stats_df(load_unified_panel())
    _wexcess = dict(zip(_wdf["model"], _wdf["excess_dx_weighted"]))
    projections = {}
    for adopt in (0.05, 0.10, 0.25):
        vals = []
        for r in per_model:
            if r["model"] not in FIG5_MODELS:
                continue
            excess = float(_wexcess.get(r["model"], r["dx_excess"]))
            v = excess * COMMERCIAL_FACTOR * ANNUAL_VISITS * adopt / 1e9
            vals.append((r["label"], v))
        vals.sort(key=lambda x: x[1])
        projections[f"{int(adopt*100)}_pct"] = {
            "min_billions": round(vals[0][1], 1),
            "min_model": vals[0][0],
            "max_billions": round(vals[-1][1], 1),
            "max_model": vals[-1][0],
            "per_model": vals,
        }
    out["projections"] = projections

    # ─── MTS_0100 exemplar (used in Figure 1 and caption) ─────────
    exemplars = {}
    for case_id in ["MTS_0100", "MTS_0334"]:
        for model_key in ["gpt-5.2"]:
            data = all_data.get(model_key, [])
            c = next((x for x in data if x.get("case_id") == case_id), None)
            if not c:
                continue

            # Compute test-category slot totals, taking median (as pipeline does)
            slot_tots = []
            slot_counts_list = []
            for s in "abc":
                orders = c.get(f"llm_orders_{s}", []) or []
                tests = [o for o in orders if _is_test(o.get("category", ""))]
                tot = sum(float(o.get("price") or 0) for o in tests)
                slot_tots.append(tot)
                slot_counts_list.append(len(tests))
            # median slot (stored medicare_llm_dx_cost should match)
            slot_tots_sorted = sorted(slot_tots)
            median_total = slot_tots_sorted[1]

            # Pick the slot whose total equals the median, for a representative ordering breakdown
            median_slot_idx = slot_tots.index(median_total) if median_total in slot_tots else 1
            orders = c.get(f"llm_orders_{'abc'[median_slot_idx]}", []) or []
            tests = [o for o in orders if _is_test(o.get("category", ""))]

            # Categorize tests
            def classify(name):
                s = (name or "").lower()
                if any(k in s for k in ["stress", "echo"]):
                    return "stress_echo"
                if any(k in s for k in ["x-ray", "xray", "radiograph", "lumbar", "film"]):
                    return "xray"
                if "dexa" in s or "bone density" in s:
                    return "dexa"
                return "lab"

            groups = {"stress_echo": [], "xray": [], "dexa": [], "lab": []}
            for o in tests:
                groups[classify(o.get("order", ""))].append(o)

            exemplars[f"{case_id}_{model_key}"] = {
                "stored_cost": c.get("medicare_llm_dx_cost"),
                "median_slot_total": round(median_total, 2),
                "n_tests_median_slot": len(tests),
                "stress_echo_cost": round(sum(float(o.get("price") or 0) for o in groups["stress_echo"]), 2),
                "xray_cost": round(sum(float(o.get("price") or 0) for o in groups["xray"]), 2),
                "dexa_cost": round(sum(float(o.get("price") or 0) for o in groups["dexa"]), 2),
                "lab_cost": round(sum(float(o.get("price") or 0) for o in groups["lab"]), 2),
                "n_labs": len(groups["lab"]),
                "phys_dx_cost": c.get("medicare_human_dx_cost"),
            }
        # physician breakdown for MTS_0100 (the CRP cost specifically)
        if case_id == "MTS_0100":
            data = all_data.get("gpt-5.2", [])
            c = next((x for x in data if x.get("case_id") == case_id), None)
            if c:
                for s in "abc":
                    orders = c.get(f"human_orders_{s}", []) or []
                    for o in orders:
                        if "crp" in (o.get("order") or "").lower() or "reactive protein" in (o.get("order") or "").lower():
                            exemplars[f"{case_id}_phys_crp"] = {
                                "cost": round(float(o.get("price") or 0), 2),
                                "cpt": o.get("cpt_code"),
                            }
                            break
                    if f"{case_id}_phys_crp" in exemplars:
                        break
    out["exemplars"] = exemplars

    # ─── Clinical appropriateness review (Table S4 source) ─────────
    # Anchored to the ORIGINAL reviewed plans (results/models_original_runs/), since Shahar
    # scored those specific AI outputs; the re-generated main panel does not match them.
    out["appropriateness"] = compute_appropriateness_numbers(load_all_models())

    # ─── Figure 1 exemplar: one case across physician + 3 prompt arms ─────
    # MTS_0481 (bronchiolitis, 2-month-old) with Grok 4.3: a textbook
    # Choosing Wisely case where AI over-orders viral testing the physician
    # appropriately omits, and the prompts dial it back toward the physician.
    out["fig1_exemplar"] = compute_fig1_exemplar("MTS_0481", "grok-4.3")

    return out


def compute_fig1_exemplar(case_id: str = "MTS_0109", model: str = "gpt-5.2") -> dict:
    """Figure 1 exemplar: physician vs AI under standard / cost-aware / parsimonious
    prompts on a single case, showing the cost-safety dial. Costs are the median of the
    three extraction slots (matching the pipeline); the representative order list is the
    median-cost slot. Read by figures/make_fig1.py (no hardcoded numbers there)."""
    DX_CATS = {"labs", "imaging", "procedure", "exam", "monitoring"}
    ARM_DIR = {"standard": "models", "costaware": "models_costaware",
               "parsimonious": "models_parsimonious"}

    def load_case(arm_dir):
        p = ROOT / "results" / arm_dir / f"m_{model}.json"
        if not p.exists():
            return None
        return next((r for r in json.loads(p.read_text()) if r.get("case_id") == case_id), None)

    def slot_tests(rec, side):
        """Return (median_total, representative_test_list, category_totals) for a plan side."""
        slot_tots, slot_orders = [], []
        for s in "abc":
            orders = rec.get(f"{side}_orders_{s}", []) or []
            tests = [o for o in orders if o.get("category") in DX_CATS]
            slot_tots.append(sum(float(o.get("price") or 0) for o in tests))
            slot_orders.append(tests)
        order = sorted(range(3), key=lambda i: slot_tots[i])
        mid = order[1]
        median_tot = slot_tots[mid]
        tests = slot_orders[mid]
        cat_tot = {}
        for o in tests:
            cat_tot[o.get("category")] = cat_tot.get(o.get("category"), 0) + float(o.get("price") or 0)
        order_list = [{"name": o.get("order", ""), "category": o.get("category"),
                       "price": round(float(o.get("price") or 0), 2)} for o in tests]
        return round(median_tot, 2), order_list, {k: round(v, 2) for k, v in cat_tot.items()}

    base = load_case("models")
    if base is None:
        return {}
    ph_cost, ph_orders, ph_cats = slot_tests(base, "human")
    ex = {
        "case_id": case_id, "model": model,
        "specialty": base.get("specialty", ""),
        "presentation": base.get("presentation", ""),
        "physician": {
            "dx_cost": round(base.get("medicare_human_dx_cost") or 0, 2),
            # diagnostic TESTS only (labs + imaging), excluding priced supportive
            # care (suctioning, observation/monitoring) for a clean Figure 1
            "dx_test_cost": round(ph_cats.get("labs", 0) + ph_cats.get("imaging", 0), 2),
            "dx_summary": base.get("human_dx_summary", ""),
            "n_tests": len(ph_orders), "orders": ph_orders, "category_totals": ph_cats,
        },
        "arms": {},
    }
    for arm, arm_dir in ARM_DIR.items():
        r = load_case(arm_dir)
        if r is None:
            continue
        cost, orders, cats = slot_tests(r, "llm")
        ex["arms"][arm] = {
            "dx_cost": round(r.get("medicare_llm_dx_cost") or 0, 2),
            "dx_test_cost": round(cats.get("labs", 0) + cats.get("imaging", 0), 2),
            "dx_summary": r.get("llm_dx_summary", ""),
            "n_tests": len(orders), "orders": orders, "category_totals": cats,
        }
    return ex


def compute_appropriateness_numbers(all_data: dict) -> dict:
    """Shahar's 200-case × 5-model scoring + per-case cost deltas from m_*.json.

    Produces per-model score distribution (%), unadjusted $/visit excess,
    strict-adjusted (score 1+2) and lenient-adjusted (score 1+2+3) excess, and
    5-model means. Scored cases always equal 200 (the primary-analysis cohort).
    Returns {} gracefully if the XLSX is missing.
    """
    if not APPROP_XLSX.exists():
        return {}
    try:
        import pandas as pd  # lazy import — keep paper_numbers importable without pandas
    except ImportError:
        return {}

    xlsx = pd.read_excel(APPROP_XLSX)
    per_model = []
    for pretty, stem in APPROP_MODELS.items():
        cases = {c["case_id"]: c for c in all_data.get(stem, [])}
        sub = xlsx[["case_id", APPROP_SCORE_COLS[pretty]]].dropna()
        sub = sub[sub["case_id"].isin(cases)].copy()
        sub["score"] = sub[APPROP_SCORE_COLS[pretty]].astype(int)
        sub["llm"]   = sub["case_id"].map(lambda cid: cases[cid]["medicare_llm_dx_cost"] or 0)
        sub["phys"]  = sub["case_id"].map(lambda cid: cases[cid]["medicare_human_dx_cost"] or 0)
        sub["delta"] = sub["llm"] - sub["phys"]
        n = len(sub)
        dist = {k: round((sub["score"] == k).mean() * 100, 1) for k in [1, 2, 3, 4]}
        unadj   = (sub["llm"].mean() - sub["phys"].mean())
        strict  = sub.loc[sub["score"].isin([1, 2]),    "delta"].sum() / n
        lenient = sub.loc[sub["score"].isin([1, 2, 3]), "delta"].sum() / n
        per_model.append({
            "model": pretty,
            "n": int(n),
            "score_pct_1": dist[1], "score_pct_2": dist[2],
            "score_pct_3": dist[3], "score_pct_4": dist[4],
            "pct_inappropriate": round(dist[1] + dist[2], 1),
            "pct_guideline_concordant": dist[4],
            "unadj_per_visit":   round(unadj,   2),
            "strict_per_visit":  round(strict,  2),
            "lenient_per_visit": round(lenient, 2),
            "pct_retained_strict":  round(strict  / unadj * 100, 1) if unadj else 0,
            "pct_retained_lenient": round(lenient / unadj * 100, 1) if unadj else 0,
        })
    # 5-model simple means (matching Table S4 "Mean of 5 systems" row)
    def mean_of(k): return round(sum(m[k] for m in per_model) / len(per_model), 1)
    def mean_of_dollar(k): return round(sum(m[k] for m in per_model) / len(per_model), 2)
    agg = {
        "n_models": len(per_model),
        "n_cases_per_model": per_model[0]["n"] if per_model else 0,
        "mean_pct_1": mean_of("score_pct_1"),
        "mean_pct_2": mean_of("score_pct_2"),
        "mean_pct_3": mean_of("score_pct_3"),
        "mean_pct_4": mean_of("score_pct_4"),
        "mean_pct_inappropriate":       mean_of("pct_inappropriate"),
        "mean_pct_guideline_concordant": mean_of("pct_guideline_concordant"),
        "mean_unadj":   mean_of_dollar("unadj_per_visit"),
        "mean_strict":  mean_of_dollar("strict_per_visit"),
        "mean_lenient": mean_of_dollar("lenient_per_visit"),
        # Headline retention % = ratio of mean-dollar values (matches Table S4 Mean row
        # and the "~78%" / "~25%" claims in the Results paragraph). Not the mean of
        # per-model ratios — those differ because models with small denominators skew.
        "pct_retained_strict":  round(
            mean_of_dollar("strict_per_visit")  / mean_of_dollar("unadj_per_visit") * 100, 1),
        "pct_retained_lenient": round(
            mean_of_dollar("lenient_per_visit") / mean_of_dollar("unadj_per_visit") * 100, 1),
        # inappropriate-fraction range across the 5 models (for the "15–30%" text)
        "inappropriate_min": round(min(m["pct_inappropriate"] for m in per_model), 1),
        "inappropriate_max": round(max(m["pct_inappropriate"] for m in per_model), 1),
        # guideline-concordant range (for the "12–23%" text)
        "concordant_min": round(min(m["pct_guideline_concordant"] for m in per_model), 1),
        "concordant_max": round(max(m["pct_guideline_concordant"] for m in per_model), 1),
    }
    return {"per_model": per_model, "aggregate": agg}


def write_outputs(data: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=2))
    # Markdown summary
    lines = ["# Paper Numbers (source of truth)",
             "",
             f"All numbers computed from `results/models/m_*.json` with n=200 filter.",
             ""]
    agg = data["aggregate"]
    lines += [
        "## Aggregates (used in Abstract / Results body)",
        "",
        f"- N cases (primary): **{agg['n_cases_primary']}**",
        f"- Total AI–physician comparisons: **{agg['n_ai_physician_comparisons']}** "
        f"({agg['n_models_total']} models × {agg['n_cases_primary']} cases)",
        f"- Physician avg dx cost: **${agg['phys_dx_cost_avg']:.2f}**",
        f"- Physician med count: **{agg['phys_med_count']:.2f}** / visit",
        f"- Physician ref count: **{agg['phys_ref_count']:.2f}** / visit",
        f"- Zero-phys cases: **{agg['n_zero_phys_cases']}/{agg['n_cases_primary']}** "
        f"(**{agg['pct_zero_phys']:.0f}%**)",
        f"- Nonzero-phys cases: **{agg['n_nonzero_phys_cases']}**",
        f"- dx_ratio range: **{agg['dx_ratio_min']:.2f}× – {agg['dx_ratio_max']:.2f}×** "
        f"({agg['dx_ratio_min_model']} → {agg['dx_ratio_max_model']})",
        f"- dx cost range: **${int(agg['dx_cost_min'])} – ${int(agg['dx_cost_max'])}** / visit",
        f"- GP mean excess (unweighted): **${agg['mean_excess_gp_unweighted']:.2f}** / visit",
        f"- Med count range: **{agg['med_count_min']} – {agg['med_count_max']}** (phys {agg['phys_med_count']:.2f}), "
        f"up to **{agg['med_ratio_max']:.1f}×** physician",
        f"- Ref count range: **{agg['ref_count_min']} – {agg['ref_count_max']}** "
        f"(**{agg['ref_ratio_min']:.1f}× – {agg['ref_ratio_max']:.1f}×**)",
        f"- pct-added (zero-phys subset): **{agg['pct_added_min']:.0f}% – {agg['pct_added_max']:.0f}%**",
        f"- NAMCS strata: routine {agg['namcs_strata_pct']['routine_zero']:.0f}%, "
        f"simple {agg['namcs_strata_pct']['simple_1_100']:.0f}%, "
        f"significant {agg['namcs_strata_pct']['significant_gt100']:.0f}%",
        f"- Subset (zero phys) AI mean: **${agg['subset_zero_ai_mean']:.0f}**",
        f"- Subset (nonzero phys) physician mean: **${agg['subset_nonzero_phys_mean']:.0f}**",
        f"- Subset (nonzero phys) mean ratio: **{agg['subset_nonzero_ratio_mean']:.2f}×**, "
        f"{agg['subset_nonzero_under_physician']}/{len([r for r in data['per_model'] if r['model'] in GP_SET])} GP models under physician",
        "",
    ]

    lines += ["## Per-model (Table 1 source)", "",
              "| Model | Concordant | Adjacent | Discordant | Dx cost | Dx fold | Med count | Med fold | Ref count | Ref fold |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in data["per_model"]:
        med_fold = r["llm_med_count"] / agg["phys_med_count"] if agg["phys_med_count"] else 0
        ref_fold = r["llm_ref_count"] / agg["phys_ref_count"] if agg["phys_ref_count"] else 0
        lines.append(
            f"| {r['label']} | {r['accuracy_pct']:.0f}% | {r['related_pct']:.0f}% | {r['wrong_pct']:.0f}% | "
            f"${r['llm_dx_cost']:.0f} | {r['dx_ratio']:.2f}× | "
            f"{r['llm_med_count']:.2f} | {med_fold:.1f}× | "
            f"{r['llm_ref_count']:.2f} | {ref_fold:.1f}× |"
        )

    lines += ["", "## Version changes (paired Wilcoxon, n=200 per family)", "",
              "| Family | Old | New | fold_old | fold_new | % change | p |",
              "|---|---|---|---:|---:|---:|---:|"]
    for v in data["version_changes"]:
        sign = "+" if v["pct_change"] > 0 else ""
        lines.append(
            f"| {v['family']} | {v['old_model']} | {v['new_model']} | {v['fold_old']:.2f}× | "
            f"{v['fold_new']:.2f}× | {sign}{v['pct_change']:.1f}% | {v['p_value']} |"
        )

    lines += ["", "## Population projections (commercial 2× Medicare, 883M visits)", "",
              "| Adoption | Min | Max |",
              "|---|---|---|"]
    for p in ["5_pct", "10_pct", "25_pct"]:
        pr = data["projections"][p]
        lines.append(
            f"| {p.replace('_pct','%')} | ${pr['min_billions']:.1f}B ({pr['min_model']}) "
            f"| ${pr['max_billions']:.1f}B ({pr['max_model']}) |"
        )

    lines += ["", "## Subset analysis (Table S5 source)", "",
              "| Model | Zero-phys: AI/visit | Nonzero: Phys | Nonzero: AI | Ratio |",
              "|---|---:|---:|---:|---:|"]
    for s in data["subset_by_phys_ordering"]:
        lines.append(
            f"| {s['label']} | ${s['zero_phys_ai_cost']:.0f} | "
            f"${s['nonzero_phys_phys_cost']:.0f} | ${s['nonzero_phys_ai_cost']:.0f} | "
            f"{s['nonzero_ratio']:.2f}× |"
        )

    appr = data.get("appropriateness", {})
    if appr:
        ag = appr["aggregate"]
        lines += [
            "", "## Clinical Appropriateness Review (Table S4 source)", "",
            f"- N cases × N models: **{ag['n_cases_per_model']} × {ag['n_models']} = "
            f"{ag['n_cases_per_model']*ag['n_models']} ratings**",
            f"- Mean score distribution: "
            f"**1={ag['mean_pct_1']}% / 2={ag['mean_pct_2']}% / "
            f"3={ag['mean_pct_3']}% / 4={ag['mean_pct_4']}%**",
            f"- Mean inappropriate (1+2): **{ag['mean_pct_inappropriate']}%** "
            f"(range {ag['inappropriate_min']}–{ag['inappropriate_max']}%)",
            f"- Mean guideline-concordant (4): **{ag['mean_pct_guideline_concordant']}%** "
            f"(range {ag['concordant_min']}–{ag['concordant_max']}%)",
            f"- Mean unadjusted $/visit excess: **${ag['mean_unadj']}** "
            f"(5-model mean; paper overall $71)",
            f"- Mean strict-adjusted (score 1+2): **${ag['mean_strict']}** "
            f"(**{ag['pct_retained_strict']}%** retained)",
            f"- Mean lenient-adjusted (score 1+2+3): **${ag['mean_lenient']}** "
            f"(**{ag['pct_retained_lenient']}%** retained)",
            "",
            "| Model | 1 | 2 | 3 | 4 | Unadj | Strict | Lenient |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for m in appr["per_model"]:
            lines.append(
                f"| {m['model']} | {m['score_pct_1']}% | {m['score_pct_2']}% | "
                f"{m['score_pct_3']}% | {m['score_pct_4']}% | "
                f"${m['unadj_per_visit']:.0f} | "
                f"${m['strict_per_visit']:.0f} ({m['pct_retained_strict']}%) | "
                f"${m['lenient_per_visit']:.0f} ({m['pct_retained_lenient']}%) |"
            )

    lines += ["", "## MTS_0100 exemplar (Figure 1 source)", ""]
    ex = data["exemplars"].get("MTS_0100_gpt-5.2", {})
    phys = data["exemplars"].get("MTS_0100_phys_crp", {})
    lines += [
        f"- GPT-5.2 stored total: **${ex.get('stored_cost')}**",
        f"- GPT-5.2 median-slot breakdown: stress/echo **${ex.get('stress_echo_cost')}**, "
        f"X-ray **${ex.get('xray_cost')}**, DEXA **${ex.get('dexa_cost')}**, "
        f"labs **${ex.get('lab_cost')}** (n={ex.get('n_labs')})",
        f"- Physician CRP cost: **${phys.get('cost')}** (CPT {phys.get('cpt')})",
        f"- Physician total dx cost (inc. colonoscopy): **${ex.get('phys_dx_cost')}**",
    ]

    OUT_MD.write_text("\n".join(lines))
    print(f"✓ wrote {OUT_JSON}")
    print(f"✓ wrote {OUT_MD}")


if __name__ == "__main__":
    data = compute_all_numbers()
    write_outputs(data)
