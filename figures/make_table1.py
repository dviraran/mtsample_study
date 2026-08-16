#!/usr/bin/env python3
"""
Table 1.

Emits the table as LaTeX (and a matching Markdown rendering) with one value per
cell, a unit of measure and an indicator of dispersion for every entry, and 95%
confidence intervals on every point estimate including new medications per visit.
The physician row carries an index of variance.

The table is organised around the primary outcome (total cost of recommended
care = diagnostic tests + specialist referrals).

Outputs:
  results/analysis/table1.json   per-model estimates with CIs
  results/analysis/table1.tex    LaTeX (booktabs), for manuscript.tex
  results/analysis/table1.md     Markdown, for review and the DOCX builder
"""

import sys
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (          # noqa: E402
    MODEL_INFO, SPECIALIZED_MODELS, load_unified_panel,
)

OUT_JSON = ROOT / "results" / "analysis" / "table1.json"
OUT_TEX = ROOT / "results" / "analysis" / "table1.tex"
OUT_MD = ROOT / "results" / "analysis" / "table1.md"
# body only (tabular environment, no table float or caption) — \input by
# paper/manuscript_R2.tex, which carries the caption so it stays with the text
OUT_BODY = ROOT / "results" / "analysis" / "table1_body.tex"

FAM_ORDER = ["GPT", "Claude", "Gemini", "Grok", "Llama", "Qwen", "DeepSeek"]
BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)
N_BOOT = 2000


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def boot_ci(v):
    v = np.asarray(v, dtype=float)
    if len(v) < 2:
        return [float("nan"), float("nan")]
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(v), size=(N_BOOT, len(v)))
    m = v[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def med_count(case, prefix):
    """Median across the three extractions, matching build_stats_df."""
    counts = []
    for slot in "abc":
        orders = case.get(f"{prefix}_orders_{slot}", []) or []
        counts.append(sum(1 for o in orders if isinstance(o, dict)
                          and o.get("category") == "medication"))
    return float(np.median(counts))


def arrays(cases):
    """Per-case endpoint arrays for one system: (physician dict, AI dict)."""
    h = {
        "dx": np.array([fnum(c.get("medicare_human_dx_cost")) for c in cases]),
        "consult_n": np.array([fnum(c.get("human_referral_count")) for c in cases]),
        "consult_cost": np.array([fnum(c.get("human_referral_cost")) for c in cases]),
        "med_n": np.array([med_count(c, "human") for c in cases]),
        "med_cost": np.array([fnum(c.get("medicare_human_med_cost")) for c in cases]),
    }
    l = {
        "dx": np.array([fnum(c.get("medicare_llm_dx_cost")) for c in cases]),
        "consult_n": np.array([fnum(c.get("llm_referral_count")) for c in cases]),
        "consult_cost": np.array([fnum(c.get("llm_referral_cost")) for c in cases]),
        "med_n": np.array([med_count(c, "llm") for c in cases]),
        "med_cost": np.array([fnum(c.get("medicare_llm_med_cost")) for c in cases]),
    }
    # Primary outcome = diagnostic tests + specialist referrals. Medication
    # cost is excluded (unit prices are imputed, not recorded, and the estimate is
    # unstable); medications are reported as counts instead.
    for d in (h, l):
        d["total"] = d["dx"] + d["consult_cost"]
    return h, l


def est(v, dollars=True):
    v = np.asarray(v, dtype=float)
    lo, hi = boot_ci(v)
    return {"mean": float(v.mean()), "ci": [lo, hi], "sd": float(v.std(ddof=1)),
            "median": float(np.median(v)),
            "iqr": [float(np.percentile(v, 25)), float(np.percentile(v, 75))],
            "dollars": dollars}


def fmt(e, dec=None):
    """'137 (118–158)' for dollars, '0.68 (0.55–0.82)' for counts."""
    d = 0 if e["dollars"] else 2
    d = dec if dec is not None else d
    pre = r"\$" if e["dollars"] else ""
    return f"{pre}{e['mean']:.{d}f} ({pre}{e['ci'][0]:.{d}f}--{pre}{e['ci'][1]:.{d}f})"


def fmt_md(e, dec=None):
    d = 0 if e["dollars"] else 2
    d = dec if dec is not None else d
    pre = "$" if e["dollars"] else ""
    return f"{pre}{e['mean']:.{d}f} ({pre}{e['ci'][0]:.{d}f}–{pre}{e['ci'][1]:.{d}f})"


def main():
    panel = load_unified_panel()
    rows = {}
    # The physician's plan is identical across systems; each system's file holds
    # its own extraction of it. The study-level physician baseline is therefore
    # the per-case mean across systems — the same quantity the primary-outcome
    # analysis uses, so the two agree exactly.
    phys_by_case = {}
    per_case = {}          # model -> field -> {case_id: value}, for group means

    for name, cases in panel.items():
        h, l = arrays(cases)
        for i, c in enumerate(cases):
            rec = phys_by_case.setdefault(c["case_id"], {})
            for k, v in h.items():
                rec.setdefault(k, []).append(v[i])
        per_case[name] = {k: {c["case_id"]: v[i] for i, c in enumerate(cases)}
                          for k, v in l.items()}
        rows[name] = {
            "label": MODEL_INFO[name]["label"],
            "family": MODEL_INFO[name]["family"],
            "gen": MODEL_INFO[name]["gen"],
            "specialized": name in SPECIALIZED_MODELS,
            "n": len(cases),
            "dx": est(l["dx"]),
            "consult_n": est(l["consult_n"], dollars=False),
            "med_n": est(l["med_n"], dollars=False),
            "total": est(l["total"]),
            "ratio_total": float(l["total"].mean() / h["total"].mean()),
            "ratio_dx": float(l["dx"].mean() / h["dx"].mean()),
            "excess_total": est(l["total"] - h["total"]),
        }
    case_ids = sorted(phys_by_case)
    h = {k: np.array([float(np.mean(phys_by_case[c][k])) for c in case_ids])
         for k in ("dx", "consult_n", "consult_cost", "med_n", "med_cost", "total")}
    physician = {
        "n": len(case_ids),
        "dx": est(h["dx"]),
        "consult_n": est(h["consult_n"], dollars=False),
        "med_n": est(h["med_n"], dollars=False),
        "total": est(h["total"]),
    }

    gp = [m for m in rows if not rows[m]["specialized"]]
    sp = [m for m in rows if rows[m]["specialized"]]
    gp.sort(key=lambda m: (FAM_ORDER.index(rows[m]["family"])
                           if rows[m]["family"] in FAM_ORDER else 99, rows[m]["gen"]))
    sp.sort(key=lambda m: rows[m]["label"])

    def group_mean(keys, field):
        """Mean over cases of the per-case mean across the group's systems.

        Averaging each system's own mean instead would weight systems that are
        missing a few cases differently, and would disagree with the
        primary-outcome analysis: for diagnostic tests the two differ by $0.15,
        enough to round to $177 rather than $176 and break the arithmetic of
        "$71 ... to $177 ... about $105 more" in the Results.
        """
        by_case = {}
        for m in keys:
            for cid, v in per_case[m][field].items():
                by_case.setdefault(cid, []).append(v)
        return float(np.mean([float(np.mean(v)) for v in by_case.values()]))

    groups = {
        "gp": {"keys": gp, "label": r"\textbf{Mean, 20 general-purpose systems}"},
        "sp": {"keys": sp, "label": r"\textbf{Mean, 4 specialized medical systems}"},
    }
    for g in groups.values():
        g["dx"] = group_mean(g["keys"], "dx")
        g["consult_n"] = group_mean(g["keys"], "consult_n")
        g["med_n"] = group_mean(g["keys"], "med_n")
        g["total"] = group_mean(g["keys"], "total")
        g["ratio_total"] = float(np.mean([rows[m]["ratio_total"] for m in g["keys"]]))

    OUT_JSON.write_text(json.dumps(
        {"per_model": rows, "physician": physician,
         "group_means": {k: {kk: vv for kk, vv in v.items() if kk != "keys"}
                         for k, v in groups.items()}},
        indent=2))

    # ---- LaTeX --------------------------------------------------------------
    CAPTION = (
        r"\textbf{Cost of care recommended by 24 AI systems and by the treating "
        r"physician across 200 clinical cases.} All values are per visit and are "
        r"means with 95\% confidence intervals from a 2,000-replicate case-level "
        r"bootstrap. Diagnostic tests are priced against the CY 2026 Medicare "
        r"Physician Fee Schedule and specialist referrals at the corresponding "
        r"Medicare new-patient evaluation and management code. Total cost of "
        r"recommended care, the primary outcome, is the sum of these two. New "
        r"medications are reported as counts and are not included in the total: "
        r"their unit prices are not recorded in the note and would have to be "
        r"imputed, and that imputation proved unreliable (\textbf{Supplementary "
        r"Methods \S S1.3}). Ratio is the system's mean total cost divided by the "
        r"treating physician's mean total cost on the same cases. The physician "
        r"rows report the same estimates for the treating physician's documented "
        r"plan, with the median and interquartile range given beneath the mean "
        r"because the distribution is strongly right-skewed: most visits generated "
        r"no diagnostic testing. CI denotes confidence interval; IQR, interquartile "
        r"range."
    )
    L = [r"\begin{table}[h!]", r"\centering", r"\footnotesize",
         r"\caption{" + CAPTION + "}", r"\label{tab:cost}",
         r"\begin{tabular}{l c c c c c}", r"\toprule",
         r"System & Diagnostic tests & Specialist & New medications & "
         r"Total cost of & Ratio to \\",
         r" & (\$/visit) & referrals & (n/visit) & recommended care & physician \\",
         r" & & (n/visit) & & (\$/visit) & \\",
         r"\midrule"]

    def tex_row(m):
        r = rows[m]
        return (f"{r['label']} & {fmt(r['dx'])} & {fmt(r['consult_n'])} & "
                f"{fmt(r['med_n'])} & {fmt(r['total'])} & "
                f"{r['ratio_total']:.2f}$\\times$ \\\\")

    for m in gp:
        L.append(tex_row(m))
    g = groups["gp"]
    L += [r"\midrule",
          (f"{g['label']} & \\${g['dx']:.0f} & {g['consult_n']:.2f} & "
           f"{g['med_n']:.2f} & \\${g['total']:.0f} & "
           f"{g['ratio_total']:.2f}$\\times$ \\\\"),
          r"\midrule"]
    for m in sp:
        L.append(tex_row(m))
    g = groups["sp"]
    L += [r"\midrule",
          (f"{g['label']} & \\${g['dx']:.0f} & {g['consult_n']:.2f} & "
           f"{g['med_n']:.2f} & \\${g['total']:.0f} & "
           f"{g['ratio_total']:.2f}$\\times$ \\\\"),
          r"\midrule"]
    p = physician
    L += [
        (r"\rowcolor{gray!8} \textbf{Treating physician}, mean (95\% CI) & "
         f"{fmt(p['dx'])} & {fmt(p['consult_n'])} & {fmt(p['med_n'])} & "
         f"{fmt(p['total'])} & 1.00$\\times$ (reference) \\\\"),
        (r"\rowcolor{gray!8} \quad median [IQR] & "
         f"\\${p['dx']['median']:.0f} [\\${p['dx']['iqr'][0]:.0f}--\\${p['dx']['iqr'][1]:.0f}] & "
         f"{p['consult_n']['median']:.2f} [{p['consult_n']['iqr'][0]:.2f}--{p['consult_n']['iqr'][1]:.2f}] & "
         f"{p['med_n']['median']:.2f} [{p['med_n']['iqr'][0]:.2f}--{p['med_n']['iqr'][1]:.2f}] & "
         f"\\${p['total']['median']:.0f} [\\${p['total']['iqr'][0]:.0f}--\\${p['total']['iqr'][1]:.0f}] & "
         r"-- \\"),
        r"\bottomrule", r"\end{tabular}", r"\end{table}",
    ]
    OUT_TEX.write_text("\n".join(L) + "\n")
    # body: strip the float wrapper and the caption/label, keep the tabular
    body = [ln for ln in L
            if not ln.startswith((r"\begin{table}", r"\end{table}", r"\caption{",
                                  r"\label{", r"\centering", r"\footnotesize"))]
    OUT_BODY.write_text("\n".join(body) + "\n")

    # ---- Markdown -----------------------------------------------------------
    M = ["# Table 1 — cost of recommended care\n",
         "All values per visit; mean (95% CI) from a 2,000-replicate case-level bootstrap.\n",
         "| System | Diagnostic tests ($/visit) | Specialist referrals (n/visit) | "
         "New medications (n/visit) | Total cost of recommended care ($/visit) | Ratio to physician |",
         "|---|---|---|---|---|---:|"]
    for m in gp:
        r = rows[m]
        M.append(f"| {r['label']} | {fmt_md(r['dx'])} | {fmt_md(r['consult_n'])} | "
                 f"{fmt_md(r['med_n'])} | {fmt_md(r['total'])} | {r['ratio_total']:.2f}× |")
    g = groups["gp"]
    M.append(f"| **Mean, 20 general-purpose systems** | ${g['dx']:.0f} | {g['consult_n']:.2f} | "
             f"{g['med_n']:.2f} | ${g['total']:.0f} | {g['ratio_total']:.2f}× |")
    for m in sp:
        r = rows[m]
        M.append(f"| {r['label']} | {fmt_md(r['dx'])} | {fmt_md(r['consult_n'])} | "
                 f"{fmt_md(r['med_n'])} | {fmt_md(r['total'])} | {r['ratio_total']:.2f}× |")
    g = groups["sp"]
    M.append(f"| **Mean, 4 specialized medical systems** | ${g['dx']:.0f} | {g['consult_n']:.2f} | "
             f"{g['med_n']:.2f} | ${g['total']:.0f} | {g['ratio_total']:.2f}× |")
    M.append(f"| **Treating physician**, mean (95% CI) | {fmt_md(p['dx'])} | "
             f"{fmt_md(p['consult_n'])} | {fmt_md(p['med_n'])} | {fmt_md(p['total'])} | "
             "1.00× (reference) |")
    M.append(f"| &nbsp;&nbsp;median [IQR] | "
             f"${p['dx']['median']:.0f} [${p['dx']['iqr'][0]:.0f}–${p['dx']['iqr'][1]:.0f}] | "
             f"{p['consult_n']['median']:.2f} [{p['consult_n']['iqr'][0]:.2f}–{p['consult_n']['iqr'][1]:.2f}] | "
             f"{p['med_n']['median']:.2f} [{p['med_n']['iqr'][0]:.2f}–{p['med_n']['iqr'][1]:.2f}] | "
             f"${p['total']['median']:.0f} [${p['total']['iqr'][0]:.0f}–${p['total']['iqr'][1]:.0f}] | — |")
    M.append(f"\nPhysician SD: diagnostic tests ${p['dx']['sd']:.0f}, "
             f"referrals {p['consult_n']['sd']:.2f}, medications {p['med_n']['sd']:.2f}, "
             f"total ${p['total']['sd']:.0f}.")
    OUT_MD.write_text("\n".join(M) + "\n")

    print("\n".join(M))
    print(f"\nwrote {OUT_JSON}\nwrote {OUT_TEX}\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
