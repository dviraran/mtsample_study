#!/usr/bin/env python3
"""Generate supplementary Table S6 (complete prompt-sensitivity / mitigation results)
as LaTeX, recomputed on the CANONICAL basis so the default arm matches Table 1.

For every model present in all three arms (default / cost-aware / parsimonious) with
at least MIN_CASES cases per arm, each arm is loaded with the same dedup-by-presentation
and 20-outdated-case exclusion as the unified panel (load_unified_panel). Metrics:
  - Dx-cost ratio  = mean(arm AI diagnostic cost) / fixed per-model physician baseline
                     (mean physician diagnostic cost over that model's default-arm cohort),
                     so the default arm reproduces Table 1 exactly.
  - Concordance / Wrong dx = 3-judge majority (same as Table 1).
  - Medications    = median medication-order count across the 3 extractor slots
                     (same definition as Table 1's medication count).
  - Referrals      = median referral-order count across the 3 extractor slots
                     (order-extraction method, identical across arms). NOTE: the unified
                     panel's Table 1 referral count uses an additional LLM referral pass
                     that filters non-counting referrals, so default-arm referrals here
                     read marginally higher than Table 1; the column is for the
                     within-model arm comparison.

Writes results/analysis/supp_table6.tex and .md.
"""

import glob
import json
import os
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))
from generate_paper_figures import EXCLUDED_CASES, MODEL_INFO, majority_tier

ARMS = ["default", "costaware", "parsimonious"]
MIN_CASES = 150
TEX = ROOT / "results/analysis/supp_table6.tex"
MD = ROOT / "results/analysis/supp_table6.md"


def load_arm(arm):
    """{model: [deduped cohort cases]} for one arm (same filter as load_unified_panel)."""
    out = {}
    for f in sorted(glob.glob(str(ROOT / "results" / ("models" if arm == "default" else f"models_{arm}") / "m_*.json"))):
        m = os.path.basename(f).replace("m_", "").replace(".json", "")
        if m not in MODEL_INFO:
            continue
        seen, uniq = set(), []
        for c in json.load(open(f)):
            if c.get("case_id") in EXCLUDED_CASES:
                continue
            p = c.get("presentation")
            if p in seen:
                continue
            seen.add(p)
            uniq.append(c)
        out[m] = uniq
    return out


def med_count(c):
    slots = [sum(1 for o in (c.get(f"llm_orders_{s}") or [])
                 if o.get("category") == "medication")
             for s in "abc"]
    return st.median(slots) if slots else 0


def ref_count(c):
    slots = [sum(1 for o in (c.get(f"llm_orders_{s}") or []) if o.get("category") == "referral")
             for s in "abc"]
    return st.median(slots) if slots else 0


def arm_stats(cases):
    """Ratio uses this arm's OWN cases for both AI and physician means (numerator and
    denominator over the same cases). For the default arm this is the full 200-case
    cohort, so the ratio reproduces Table 1; for arms missing a few cases the per-case
    physician comparator is unchanged."""
    ai = np.array([c.get("medicare_llm_dx_cost") or 0 for c in cases], dtype=float)
    ph = np.array([c.get("medicare_human_dx_cost") or 0 for c in cases], dtype=float)
    tiers = [t for t in (majority_tier(c) for c in cases) if t is not None]
    n_dx = len(tiers)
    return {
        "n": len(cases),
        "ratio": float(ai.mean() / ph.mean()) if ph.mean() else None,
        "concordance_pct": 100 * sum(t == 2 for t in tiers) / n_dx if n_dx else None,
        "wrong_pct": 100 * sum(t == 0 for t in tiers) / n_dx if n_dx else None,
        "med_count": float(np.mean([med_count(c) for c in cases])),
        "ref_count": float(np.mean([ref_count(c) for c in cases])),
    }


def main():
    armdata = {a: load_arm(a) for a in ARMS}
    models = [m for m in armdata["default"]
              if all(m in armdata[a] and len(armdata[a][m]) >= MIN_CASES for a in ARMS)]

    results = {}
    for m in models:
        results[m] = {a: arm_stats(armdata[a][m]) for a in ARMS}

    models.sort(key=lambda m: -(results[m]["default"]["ratio"] or 0))

    # Canonical mitigation JSON (same structure as the legacy prompt_variants.json)
    # so Figure 4 and supp_mitigation_orders read the SAME numbers as this table.
    canon = {m: {"arms": {a: results[m][a] for a in ARMS}} for m in models}
    (ROOT / "results/analysis/mitigation_canonical.json").write_text(json.dumps(canon, indent=2))

    METRICS = [("ratio", "Dx-cost ratio", "{:.2f}"), ("concordance_pct", "Concordance (\\%)", "{:.0f}"),
               ("wrong_pct", "Discordant (\\%)", "{:.1f}"), ("med_count", "Medications", "{:.2f}"),
               ("ref_count", "Referrals", "{:.2f}")]

    def cell(m, key, fmt):
        return " / ".join(fmt.format(results[m][a][key]) if results[m][a][key] is not None else "--"
                          for a in ARMS)

    L = [r"\begin{table}[ht]", r"\centering", r"\footnotesize",
         r"\caption{\textbf{Complete prompt-sensitivity (mitigation) results by model.} "
         r"Each cell shows \emph{Standard / Cost-aware / Parsimonious}. Metrics are recomputed on the "
         r"same 200-case cohort, diagnostic pricing, and 3-judge majority concordance as the main panel, "
         r"with each plan compared against the same per-case physician comparator, so the Standard arm "
         r"reproduces \textbf{Table~1}. Dx-cost ratio is mean AI diagnostic cost relative to the "
         r"physician; medications and referrals are median order counts per visit across the three "
         r"extractors. Referral counts use the structured order-extraction method (identical across "
         r"arms); the main-panel referral figures additionally apply an LLM referral pass that filters "
         r"non-counting referrals, so Standard-arm referrals here read marginally higher than "
         r"\textbf{Table~1}.}",
         r"\label{tab:mitigation_full}",
         r"\begin{tabular}{l" + "c" * len(METRICS) + "}", r"\toprule",
         "Model & " + " & ".join(n for _, n, _ in METRICS) + r" \\", r"\midrule"]
    for m in models:
        L.append(MODEL_INFO[m]["label"] + " & " + " & ".join(cell(m, k, f) for k, _, f in METRICS) + r" \\")
    # mean row
    agg = []
    for k, _, f in METRICS:
        agg.append(" / ".join(f.format(st.mean(results[m][a][k] for m in models
                                                if results[m][a][k] is not None)) for a in ARMS))
    L += [r"\midrule", r"\textbf{Mean} & " + " & ".join(agg) + r" \\",
          r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TEX.write_text("\n".join(L) + "\n")

    M = ["| Model | " + " | ".join(n.replace("\\%", "%") for _, n, _ in METRICS) + " |",
         "|" + "---|" * (len(METRICS) + 1)]
    for m in models:
        M.append("| " + MODEL_INFO[m]["label"] + " | " + " | ".join(cell(m, k, f) for k, _, f in METRICS) + " |")
    MD.write_text("\n".join(M) + "\n\n_Each cell: Standard / Cost-aware / Parsimonious._\n")

    print(f"wrote {TEX}\nwrote {MD}  ({len(models)} models)")
    g = results.get("gpt-5.5")
    if g:
        print(f"check GPT-5.5 default: ratio={g['default']['ratio']:.2f} (Table 1: 3.2), "
              f"conc={g['default']['concordance_pct']:.0f}% (88), meds={g['default']['med_count']:.2f} (1.19), "
              f"refs={g['default']['ref_count']:.2f} (Table1 0.54)")


if __name__ == "__main__":
    main()
