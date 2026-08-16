#!/usr/bin/env python3
"""Generate supplementary Table S3 (guideline-currency sensitivity) as LaTeX,
recomputed on the UNIFIED 24-system panel (general-purpose models). No hardcoded
numbers. Writes results/analysis/supp_table3.tex.

Robustness check for the exclusion of temporally outdated physician plans. Because
the re-run unified panel covers only the 200-case primary cohort (the 20 excluded
outdated cases were not regenerated), the original "all 220" row cannot be
reproduced here. Instead we show that restricting to the cases both independent LLM
reviewers rated fully or mostly current (guideline-currency score 1-2) leaves the
AI-physician diagnostic-cost gap essentially unchanged (indeed marginally larger),
arguing against a purely temporal explanation. Guideline-currency scores are the
two-LLM review in data/guideline_currency_review.xlsx."""

import json
import statistics as st
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))
from generate_paper_figures import load_unified_panel, SPECIALIZED_MODELS

OUT = ROOT / "results/analysis/supp_table3.tex"

# ── guideline-currency scores per case (two LLM reviewers) ──
x = pd.read_excel(ROOT / "data/guideline_currency_review.xlsx")
x = x[["Case ID", "Claude Score", "Grok Score"]].dropna(subset=["Case ID"])
x["C"] = pd.to_numeric(x["Claude Score"], errors="coerce")
x["G"] = pd.to_numeric(x["Grok Score"], errors="coerce")
SCORE = {r["Case ID"]: (r["C"], r["G"]) for _, r in x.iterrows()}


def med_count(c, who):
    slots = [sum(1 for o in (c.get(f"{who}_orders_{s}") or [])
                 if o.get("category") == "medication")
             for s in "abc"]
    return st.median(slots)


def subset_stats(cases_by_model, keep):
    """GP-mean diagnostic-cost ratio, medication ratio, referral ratio over the
    cases passing `keep(case_id)`."""
    dx_ratios, l_med, h_med, l_ref, h_ref, n = [], [], [], [], [], None
    for m, cases in cases_by_model.items():
        cs = [c for c in cases if keep(c.get("case_id"))]
        if n is None:
            n = len(cs)
        hd = np.mean([c.get("medicare_human_dx_cost") or 0 for c in cs])
        ld = np.mean([c.get("medicare_llm_dx_cost") or 0 for c in cs])
        dx_ratios.append(ld / hd if hd else np.nan)
        l_med.append(np.mean([med_count(c, "llm") for c in cs]))
        h_med.append(np.mean([med_count(c, "human") for c in cs]))
        l_ref.append(np.mean([c.get("llm_referral_count") or 0 for c in cs]))
        h_ref.append(np.mean([c.get("human_referral_count") or 0 for c in cs]))
    # Ratios use the unrounded physician baseline. Dividing by the rounded,
    # display-precision baseline instead inflates the referral ratio to 5.8x
    # against the 5.6x the Results report from the same data.
    return {
        "n": n,
        "phys_med": float(np.mean(h_med)),
        "dx_ratio": float(np.nanmean(dx_ratios)),
        "med_ratio": float(np.mean(l_med) / np.mean(h_med)) if np.mean(h_med) else 0,
        "ref_ratio": float(np.mean(l_ref) / np.mean(h_ref)) if np.mean(h_ref) else 0,
    }


data = load_unified_panel()
gp = {m: cs for m, cs in data.items() if m not in SPECIALIZED_MODELS}

primary = subset_stats(gp, lambda cid: True)
current = subset_stats(gp, lambda cid: max(SCORE.get(cid, (9, 9))) <= 2)
n_gp = len(gp)


def row(label, s, shade=False):
    pre = r"\rowcolor{gray!8} " if shade else ""
    return (f"{pre}{label} & {s['n']} & {s['dx_ratio']:.1f}$\\times$ & "
            f"{s['med_ratio']:.1f}$\\times$ & {s['ref_ratio']:.1f}$\\times$ \\\\")


caption = (
    r"\caption{\textbf{Sensitivity Analysis: Robustness to Temporally Outdated "
    r"Physician Plans.} Mean diagnostic-cost ratio, medication ratio, and referral "
    r"ratio across the " + str(n_gp) + r" general-purpose LLMs of the unified panel, "
    r"recomputed on two case sets. The primary cohort excludes 20 cases whose "
    r"physician plans were significantly or substantially outdated (guideline-currency "
    r"score 4--5; e.g., pre-DOAC anticoagulation, pre-GLP-1 obesity management). The "
    r"current-plan subset further restricts to cases that \emph{both} independent LLM "
    r"guideline-currency reviewers (Claude and Grok) rated fully or mostly current "
    r"(score 1--2); this is the two-LLM currency review, distinct from the physician "
    r"appropriateness review. Restricting to current "
    r"physician plans leaves the diagnostic-cost gap essentially unchanged (indeed "
    r"marginally larger), arguing against a purely temporal explanation for the "
    r"AI--physician differential. The medication ratio is higher on the current-plan "
    r"subset because the excluded temporally-outdated cases are disproportionately "
    r"physician medication decisions (e.g., anticoagulation, obesity pharmacotherapy, "
    r"opioid analgesia), lowering the physician medication baseline in this subset "
    rf"({primary['phys_med']:.2f} to {current['phys_med']:.2f} per visit) while AI "
    r"medication counts are largely unchanged; the "
    r"rise is therefore a denominator effect, not more AI prescribing. The re-run "
    r"unified panel covers only the 200-case "
    r"cohort, so the original all-220 row (which required the excluded cases) is not "
    r"reproduced here.}")

L = [r"\begin{table}[h!]", r"\centering", r"\small",
     caption,
     r"\label{tab:guideline_sensitivity}",
     r"\begin{tabular}{l c c c c}", r"\toprule",
     r"\textbf{Subset} & \textbf{N} & \textbf{Dx Cost Ratio} & "
     r"\textbf{Medication Ratio} & \textbf{Referral Ratio} \\", r"\midrule",
     row("Primary cohort (outdated cases excluded)", primary),
     row("Current plans only (both LLM currency reviewers score 1--2)", current, shade=True),
     r"\bottomrule", r"\end{tabular}", r"\end{table}"]

OUT.write_text("\n".join(L) + "\n")
print(f"wrote {OUT}")
print(f"Primary  n={primary['n']}: dx {primary['dx_ratio']:.2f}x, "
      f"med {primary['med_ratio']:.2f}x, ref {primary['ref_ratio']:.2f}x")
print(f"Current  n={current['n']}: dx {current['dx_ratio']:.2f}x, "
      f"med {current['med_ratio']:.2f}x, ref {current['ref_ratio']:.2f}x")
