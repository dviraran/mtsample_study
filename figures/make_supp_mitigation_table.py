#!/usr/bin/env python3
"""
Supplementary table: complete per-model mitigation results across the three prompts.
Each metric cell shows Standard / Cost-aware / Parsimonious. Emits a LaTeX tabular
(booktabs) and a markdown copy. Reads results/analysis/prompt_variants.json.

Output: results/analysis/supp_mitigation_table.tex  and  .md
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))
from generate_paper_figures import MODEL_INFO

JSON = ROOT / "results" / "analysis" / "prompt_variants.json"
TEX = ROOT / "results" / "analysis" / "supp_mitigation_table.tex"
MD = ROOT / "results" / "analysis" / "supp_mitigation_table.md"

ARMS = ["default", "costaware", "parsimonious"]
METRICS = [("ratio", "Dx-cost ratio", "{:.2f}"), ("concordance_pct", "Concordance (\\%)", "{:.0f}"),
           ("wrong_pct", "Wrong dx (\\%)", "{:.1f}"), ("ref_count", "Referrals", "{:.2f}"),
           ("med_count", "Medications", "{:.2f}")]


def main():
    data = json.load(open(JSON))
    models = [m for m in data if not m.startswith("_") and m in MODEL_INFO]
    models.sort(key=lambda m: -(data[m]["arms"]["default"].get("ratio") or 0))

    def cell(m, metric, fmt):
        vs = []
        for a in ARMS:
            v = data[m]["arms"][a].get(metric)
            vs.append(fmt.format(v) if v is not None else "--")
        return " / ".join(vs)

    # ── LaTeX ──
    L = [r"\begin{table}[ht]", r"\centering", r"\footnotesize",
         r"\caption{\textbf{Complete prompt-sensitivity (mitigation) results by model.} "
         r"Each cell shows \emph{Standard / Cost-aware / Parsimonious}. Dx-cost ratio is AI diagnostic "
         r"cost relative to the physician (Medicare); concordance and wrong-dx are 3-judge majority; "
         r"referrals and medications are mean counts per visit. Physician baselines: referrals 0.14, "
         r"medications 0.57 per visit.}",
         r"\label{tab:mitigation_full}",
         r"\begin{tabular}{l" + "c" * len(METRICS) + "}", r"\toprule",
         "Model & " + " & ".join(name for _, name, _ in METRICS) + r" \\", r"\midrule"]
    for m in models:
        L.append(MODEL_INFO[m]["label"] + " & " +
                 " & ".join(cell(m, k, f) for k, _, f in METRICS) + r" \\")
    ag = data.get("_aggregate", {})
    if ag:
        agg_cells = []
        for k, _, f in METRICS:
            key = {"ratio": "mean_ratio", "concordance_pct": "mean_concordance_pct",
                   "wrong_pct": "mean_wrong_pct"}.get(k)
            if key:
                agg_cells.append(" / ".join(f.format(ag[a][key]) for a in ARMS))
            else:
                agg_cells.append("--")   # ref/med means not in _aggregate
        L += [r"\midrule", r"\textbf{Mean} & " + " & ".join(agg_cells) + r" \\"]
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TEX.write_text("\n".join(L) + "\n")

    # ── Markdown copy ──
    M = ["| Model | " + " | ".join(n.replace("\\%", "%") for _, n, _ in METRICS) + " |",
         "|" + "---|" * (len(METRICS) + 1)]
    for m in models:
        M.append("| " + MODEL_INFO[m]["label"] + " | " +
                 " | ".join(cell(m, k, f) for k, _, f in METRICS) + " |")
    MD.write_text("\n".join(M) + "\n\n_Each cell: Standard / Cost-aware / Parsimonious._\n")
    print(f"wrote {TEX}\nwrote {MD}  ({len(models)} models)")


if __name__ == "__main__":
    main()
