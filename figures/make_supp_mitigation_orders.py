#!/usr/bin/env python3
"""
Supplementary figure: what the mitigation prompts do to specialist CONSULTATIONS
and MEDICATIONS, per system. Companion to the main mitigation figure (Figure 3),
which covers the primary outcome.

Counts are read from the three prompt-arm directories directly rather than from
results/analysis/mitigation_canonical.json, so that consultations use the same
LLM referral pass (specialty classification plus filtering of non-counting
referrals) as Table 1 and Figure 3. That pass has now been run on all three arms
(scripts/extract_referrals.py --dir results/models_{costaware,parsimonious}),
which removes the arm-versus-main-panel discrepancy the earlier version carried.

Physician baselines are computed from the same records, not hardcoded.

Output: paper/figures/supp_mitigation_orders.{pdf,png}
"""

import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))
from generate_paper_figures import (          # noqa: E402
    MODEL_INFO, EXCLUDED_CASES, load_unified_panel,
)

OUT = ROOT / "paper" / "figures" / "supp_mitigation_orders.png"

ARMS = [("default", "Standard", "#C0392B", "results/models"),
        ("costaware", "Cost-aware", "#E67E22", "results/models_costaware"),
        ("parsimonious", "Parsimonious", "#27AE60", "results/models_parsimonious")]
MIN_CASES = 150          # excludes OpenEvidence, run manually on 10 cases only


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def med_count(case, prefix):
    """Median across the three extractions, matching Table 1."""
    counts = []
    for slot in "abc":
        orders = case.get(f"{prefix}_orders_{slot}", []) or []
        counts.append(sum(1 for o in orders if isinstance(o, dict)
                          and o.get("category") == "medication"))
    return float(np.median(counts))


def load_arm(dirname, keep_ids):
    out = {}
    for fpath in sorted(glob.glob(str(ROOT / dirname / "m_*.json"))):
        name = os.path.basename(fpath).replace("m_", "").replace(".json", "")
        if name not in MODEL_INFO:
            continue
        seen, rows = set(), []
        for c in json.load(open(fpath)):
            cid = c.get("case_id")
            if cid in EXCLUDED_CASES or cid not in keep_ids:
                continue
            p = c.get("presentation")
            if p in seen:
                continue
            seen.add(p)
            if "llm_referral_count" not in c:
                sys.exit(f"{dirname}/{os.path.basename(fpath)} lacks 'llm_referral_count'.\n"
                         f"Run: /usr/bin/python3 scripts/extract_referrals.py --dir {dirname}")
            rows.append({
                "ref": fnum(c.get("llm_referral_count")),
                "med": med_count(c, "llm"),
                "h_ref": fnum(c.get("human_referral_count")),
                "h_med": med_count(c, "human"),
            })
        if len(rows) >= MIN_CASES:
            out[name] = rows
    return out


def main():
    keep_ids = {c["case_id"] for c in next(iter(load_unified_panel().values()))}
    arms = {k: load_arm(d, keep_ids) for k, _, _, d in ARMS}
    models = sorted(set.intersection(*(set(arms[k]) for k, *_ in ARMS)))
    if not models:
        sys.exit("no systems present in all three arms")

    val = {k: {m: {"ref": float(np.mean([r["ref"] for r in arms[k][m]])),
                   "med": float(np.mean([r["med"] for r in arms[k][m]]))}
               for m in models} for k, *_ in ARMS}
    # Physician baseline is read from Table 1's own output rather than recomputed,
    # so the figure and the table cannot disagree. Table 1 averages within case
    # across systems and then across cases; pooling over (system, case) pairs
    # instead gives a marginally different value (0.59 vs 0.58 medications), which
    # would read as an inconsistency between table and figure.
    t1 = json.loads((ROOT / "results" / "analysis" / "table1.json").read_text())
    phys = {"ref": t1["physician"]["consult_n"]["mean"],
            "med": t1["physician"]["med_n"]["mean"]}

    models.sort(key=lambda m: val["default"][m]["ref"])

    fig, axes = plt.subplots(1, 2, figsize=(14, max(6, 0.42 * len(models))), sharey=True)
    bh = 0.26
    panels = [("ref", "A   Specialist referrals per visit"),
              ("med", "B   New medications per visit")]
    for ax, (metric, title) in zip(axes, panels):
        for i, m in enumerate(models):
            for j, (key, label, color, _) in enumerate(ARMS):
                ax.barh(i + (1 - j) * bh, val[key][m][metric], height=bh * 0.92,
                        color=color, alpha=0.9, edgecolor="white", linewidth=0.5,
                        label=label if i == 0 else None)
        ax.axvline(phys[metric], ls="--", color="#333", lw=1.2, alpha=0.7, zorder=0)
        ax.text(phys[metric], len(models) - 0.3, f" physician {phys[metric]:.2f}",
                fontsize=8.5, color="#555", ha="left", va="bottom")
        ax.set_yticks(range(len(models)))
        ax.set_yticklabels([MODEL_INFO[m]["label"] for m in models], fontsize=9)
        ax.set_xlabel("Count per visit", fontsize=10.5)
        ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=9, loc="lower right", framealpha=0.95)
    fig.suptitle("Mitigation prompts also reduce referrals, but not medications",
                 fontsize=13.5, fontweight="bold", y=1.005)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    fig.savefig(str(OUT).replace(".png", ".pdf"), bbox_inches="tight")

    print(f"wrote {OUT}  ({len(models)} systems)")
    print(f"physician: referrals {phys['ref']:.2f}, medications {phys['med']:.2f} per visit")
    for k, label, *_ in ARMS:
        print(f"  {label:13s} referrals {np.mean([val[k][m]['ref'] for m in models]):.2f}"
              f"   medications {np.mean([val[k][m]['med'] for m in models]):.2f}")


if __name__ == "__main__":
    main()
