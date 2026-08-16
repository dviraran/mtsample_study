#!/usr/bin/env python3
"""Generate supplementary Table S5 (AI diagnostic cost by physician ordering
behavior) as LaTeX from paper_numbers.json. No hardcoded numbers. Writes
results/analysis/supp_table5.tex (to \\input into supplement.tex).

Cases are split on whether the treating physician ordered any diagnostic tests:
"Follow-up" (physician $0) vs "Active workup" (physician > $0). Values come from
paper_numbers' subset_by_phys_ordering / aggregate, computed on the unified panel."""

import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "figures"))
from generate_paper_figures import MODEL_INFO  # family/gen/label (single source)

PN = json.loads((ROOT / "results/analysis/paper_numbers.json").read_text())
OUT = ROOT / "results/analysis/supp_table5.tex"

ag = PN["aggregate"]
sub = {s["model"]: s for s in PN["subset_by_phys_ordering"]}
pm = {r["model"]: r for r in PN["per_model"]}
n_zero = ag["n_zero_phys_cases"]
n_nz = ag["n_nonzero_phys_cases"]
phys_active = ag["subset_nonzero_phys_mean"]

FAM_ORDER = ["GPT", "Claude", "Gemini", "Grok", "Llama", "Qwen", "DeepSeek"]
SPEC = ["openevidence", "medgemma-4b", "medgemma-27b", "meditron"]
SPEC_SET = set(SPEC)

gp = [m for m in sub if m not in SPEC_SET and m in MODEL_INFO]
gp.sort(key=lambda m: (FAM_ORDER.index(MODEL_INFO[m]["family"])
                       if MODEL_INFO[m]["family"] in FAM_ORDER else 99,
                       MODEL_INFO[m]["gen"]))

gp_mean_ratio = st.mean(pm[m]["dx_ratio"] for m in gp if m in pm)


def row(m, shade):
    s = sub[m]
    pre = r"\rowcolor{gray!8} " if shade else ""
    return (f"{pre}{s['label']} & \\${s['zero_phys_ai_cost']:.0f} & & "
            f"\\${s['nonzero_phys_ai_cost']:.0f} & {s['nonzero_ratio']:.2f}$\\times$ \\\\")


L = [r"\begin{table}[p]", r"\centering", r"\small",
     r"\caption{\textbf{Subset Analysis: AI Diagnostic Cost Ratios by Physician "
     r"Ordering Behavior.} Cases stratified by whether the treating physician ordered "
     rf"any diagnostic tests. In the {n_zero} cases where physicians ordered no tests "
     rf"(\$0), AI systems generated \${min(s['zero_phys_ai_cost'] for s in sub.values()):.0f}"
     rf"--{max(s['zero_phys_ai_cost'] for s in sub.values()):.0f} per visit from a zero "
     rf"baseline. In the {n_nz} cases where physicians did order tests (mean "
     rf"\${phys_active:.0f}/visit), the overall cost ratio collapses from "
     rf"{gp_mean_ratio:.1f}$\times$ to {ag['subset_nonzero_ratio_mean']:.1f}$\times$, "
     rf"with {ag['subset_nonzero_under_physician']} of {ag['n_models_gp']} general-purpose "
     r"models ordering less than the physician. This shows that the primary driver of AI "
     r"excess is adding tests to visits where the physician ordered no diagnostic workup.}",
     r"\label{tab:phys_ordering}",
     r"\begin{tabular}{l c c c c}", r"\toprule",
     rf"\textbf{{Model}} & \multicolumn{{2}}{{c}}{{\textbf{{Follow-up (n={n_zero})}}}} & "
     rf"\multicolumn{{2}}{{c}}{{\textbf{{Active workup (n={n_nz})}}}} \\",
     r"\cmidrule(lr){2-3} \cmidrule(lr){4-5}",
     r" & AI \$/visit & & AI \$/visit & Ratio \\", r"\midrule"]

for i, m in enumerate(gp):
    L.append(row(m, shade=(i % 2 == 1)))
L.append(r"\midrule")
for i, m in enumerate(SPEC):
    if m in sub:
        L.append(row(m, shade=(i % 2 == 1)))
L += [r"\midrule",
      (rf"\rowcolor{{gray!8}} \textbf{{Mean ({ag['n_models_gp']} GP)}} & "
       rf"\textbf{{\${ag['subset_zero_ai_mean']:.0f}}} & & "
       rf"\textbf{{\${st.mean(sub[m]['nonzero_phys_ai_cost'] for m in gp):.0f}}} & "
       rf"\textbf{{{ag['subset_nonzero_ratio_mean']:.2f}$\times$}} \\"),
      rf"Physician & \$0 & & \${phys_active:.0f} & 1.0$\times$ \\",
      r"\bottomrule", r"\end{tabular}", r"\end{table}"]

OUT.write_text("\n".join(L) + "\n")
print(f"wrote {OUT}  ({len(gp)} GP + {sum(1 for m in SPEC if m in sub)} specialized)")
print(f"Follow-up n={n_zero}, Active workup n={n_nz}, "
      f"nonzero ratio {ag['subset_nonzero_ratio_mean']:.2f}x, "
      f"{ag['subset_nonzero_under_physician']} of {ag['n_models_gp']} under physician")
