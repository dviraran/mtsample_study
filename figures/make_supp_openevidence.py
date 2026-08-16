#!/usr/bin/env python3
"""Supplementary Figure: OpenEvidence parsimonious-prompt sub-study (10 hand-picked cases).

OpenEvidence has no API, so the parsimonious-and-safe prompt was run manually through the
web interface on 10 deliberately hand-picked cases (5 high-acuity / can't-miss, 5
lower-acuity / defensible) to probe cost-vs-safety behavior at the extremes. The same
extraction (3 extractors, median) -> Medicare pricing -> concordance pipeline was applied.

Standard-prompt OpenEvidence values come from the unified panel (results/models/);
parsimonious values from results/models_parsimonious/. These 10 cases are illustrative, NOT
a representative sample; no aggregate ratio is implied.

Key point (Results, mitigation): the parsimonious prompt cuts routine/low-acuity ordering
far more than high-acuity can't-miss ordering, while diagnostic concordance is preserved.

Panel A: per-case standard vs parsimonious diagnostic cost (dumbbell), grouped by acuity.
Panel B: mean diagnostic cost by acuity stratum, standard vs parsimonious, with % reduction.

Output: paper/figures/supp_openevidence.{png,pdf}
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "axes.facecolor": "white",
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#EEEEEE",
    "grid.linewidth": 0.8,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 300,
})

# Hand-picked cases with their acuity stratum and a short clinical label
# (from data/openevidence_manual_prompts.md / openevidence_prompt_variants_report.md)
CASES = [
    # high-acuity / can't-miss
    ("MTS_0449", "high", "ER pathologic hip fracture (melanoma mets)"),
    ("MTS_0239", "high", "Newly dx high-risk acute leukemia"),
    ("MTS_0582", "high", "Rapid dementia: CJD vs autoimmune enceph."),
    ("MTS_0481", "high", "2-month-old bronchiolitis (peds ER)"),
    ("MTS_0305", "high", "Probable acute ischemic stroke"),
    # lower-acuity / defensible
    ("MTS_0974", "low", "Obesity / T2DM, complication risk"),
    ("MTS_0159", "low", "Bell's palsy (vs stroke can't-miss)"),
    ("MTS_0255", "low", "Right-sided weakness (stroke-like)"),
    ("MTS_0019", "low", "Sleep disruption complaint"),
    ("MTS_0600", "low", "Possible reactive arthritis"),
]

ACUITY_COLOR = {"high": "#B84040", "low": "#3B8FD2"}
ACUITY_LABEL = {"high": "High-acuity / can't-miss (n=5)",
                "low": "Lower-acuity / defensible (n=5)"}
STD_COLOR = "#999999"


def load_indexed(arm):
    d = json.load(open(ROOT / "results" / ("models" if arm == "default" else f"models_{arm}") / "m_openevidence.json"))
    return {c["case_id"]: c for c in d}


def main():
    de = load_indexed("default")
    pa = load_indexed("parsimonious")

    rows = []
    for cid, acuity, label in CASES:
        std = de[cid]["medicare_llm_dx_cost"]
        par = pa[cid]["medicare_llm_dx_cost"]
        rows.append((cid, acuity, label, std, par))

    # order rows: high block then low block, each sorted by standard cost descending
    rows.sort(key=lambda r: (0 if r[1] == "high" else 1, -r[3]))

    fig = plt.figure(figsize=(15, 7))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.0, 1.0], wspace=0.32)

    # ── Panel A: per-case dumbbell, standard -> parsimonious ──
    ax = fig.add_subplot(gs[0])
    y = np.arange(len(rows))[::-1]   # first row at top
    for yi, (cid, acuity, label, std, par) in zip(y, rows):
        col = ACUITY_COLOR[acuity]
        ax.plot([std, par], [yi, yi], color=col, lw=2.2, alpha=0.55, zorder=2,
                solid_capstyle="round")
        ax.scatter(std, yi, s=70, color=STD_COLOR, edgecolor="white", linewidth=0.8,
                   zorder=3)
        ax.scatter(par, yi, s=85, color=col, edgecolor="white", linewidth=0.8, zorder=4)
        # % change label, placed clear of the markers (left of the pair, or
        # right of it when the pair sits near $0 to avoid clipping at the axis)
        if std > 0:
            pct = 100 * (par - std) / std
            txt = f"{pct:+.0f}%"
        else:
            txt = ""
        if txt:
            lo, hi = min(std, par), max(std, par)
            if lo < 320:                       # near the left edge -> label to the right
                ax.text(hi + 45, yi, txt, ha="left", va="center", fontsize=8.5,
                        color=col, fontweight="bold")
            else:
                ax.text(lo - 45, yi, txt, ha="right", va="center", fontsize=8.5,
                        color=col, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{label}" for (_, _, label, _, _) in rows], fontsize=9)
    ax.set_xlabel("OpenEvidence diagnostic cost per case ($)", fontsize=11)
    ax.set_xlim(-120, max(r[3] for r in rows) * 1.10)
    ax.set_title("A   Standard vs parsimonious prompt, per case",
                 fontsize=12.5, fontweight="bold", loc="left", pad=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)

    # divider between strata blocks
    n_high = sum(1 for r in rows if r[1] == "high")
    div = y[n_high - 1] - 0.5
    ax.axhline(div, color="#CCCCCC", lw=1.0, ls="--", zorder=1)
    ax.text(ax.get_xlim()[1], y[0] + 0.05, "HIGH-ACUITY", ha="right", va="bottom",
            fontsize=8.5, color=ACUITY_COLOR["high"], fontweight="bold")
    ax.text(ax.get_xlim()[1], y[n_high] + 0.05, "LOWER-ACUITY", ha="right", va="bottom",
            fontsize=8.5, color=ACUITY_COLOR["low"], fontweight="bold")

    # legend for the two markers
    h_std = ax.scatter([], [], s=70, color=STD_COLOR, edgecolor="white",
                       label="Standard prompt")
    h_high = ax.scatter([], [], s=85, color=ACUITY_COLOR["high"], edgecolor="white",
                        label="Parsimonious (high-acuity)")
    h_low = ax.scatter([], [], s=85, color=ACUITY_COLOR["low"], edgecolor="white",
                       label="Parsimonious (lower-acuity)")
    ax.legend(handles=[h_std, h_high, h_low], fontsize=8.8,
              loc="center right", bbox_to_anchor=(1.0, 0.30), framealpha=0.96)

    # ── Panel B: mean cost by stratum, standard vs parsimonious ──
    axb = fig.add_subplot(gs[1])
    strata = ["high", "low"]
    means = {}
    for s in strata:
        sub = [r for r in rows if r[1] == s]
        means[s] = (np.mean([r[3] for r in sub]), np.mean([r[4] for r in sub]))
    x = np.arange(len(strata))
    bw = 0.34
    for i, s in enumerate(strata):
        std_m, par_m = means[s]
        axb.bar(i - bw / 2, std_m, bw, color=STD_COLOR, alpha=0.92,
                edgecolor="white", label="Standard" if i == 0 else None)
        axb.bar(i + bw / 2, par_m, bw, color=ACUITY_COLOR[s], alpha=0.92,
                edgecolor="white", label="Parsimonious" if i == 0 else None)
        axb.text(i - bw / 2, std_m + 25, f"${std_m:.0f}", ha="center", fontsize=9,
                 color="#444")
        axb.text(i + bw / 2, par_m + 25, f"${par_m:.0f}", ha="center", fontsize=9,
                 color="#444", fontweight="bold")
        red = 100 * (std_m - par_m) / std_m
        axb.annotate(f"-{red:.0f}%", xy=(i, max(std_m, par_m) + 120),
                     ha="center", fontsize=11, fontweight="bold",
                     color=ACUITY_COLOR[s])
    axb.set_xticks(x)
    axb.set_xticklabels(["High-acuity\n(n=5)", "Lower-acuity\n(n=5)"], fontsize=10)
    axb.set_ylabel("Mean diagnostic cost per case ($)", fontsize=11)
    axb.set_ylim(0, max(m[0] for m in means.values()) * 1.30)
    axb.set_title("B   Parsimony cuts low-acuity ordering hardest",
                  fontsize=12.5, fontweight="bold", loc="left", pad=10)
    axb.spines[["top", "right"]].set_visible(False)
    axb.legend(fontsize=9, loc="upper right", framealpha=0.96)
    axb.grid(axis="y", color="#EEEEEE", lw=0.8, zorder=0)

    fig.suptitle(
        "OpenEvidence sub-study: parsimonious prompting trims low-acuity workup more than "
        "high-acuity can't-miss workup",
        fontsize=13, fontweight="bold", y=0.99)

    for fmt in ("png", "pdf"):
        fig.savefig(OUT_DIR / f"supp_openevidence.{fmt}", dpi=300,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)
    hi_red = 100 * (means["high"][0] - means["high"][1]) / means["high"][0]
    lo_red = 100 * (means["low"][0] - means["low"][1]) / means["low"][0]
    print(f"wrote supp_openevidence  high-acuity mean ${means['high'][0]:.0f}->"
          f"${means['high'][1]:.0f} (-{hi_red:.0f}%); low-acuity mean "
          f"${means['low'][0]:.0f}->${means['low'][1]:.0f} (-{lo_red:.0f}%)")


if __name__ == "__main__":
    main()
