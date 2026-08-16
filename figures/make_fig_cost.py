#!/usr/bin/env python3
"""
Main-text cost figure (Figure 3A-D).

Built around the pre-specified primary outcome, with 95% confidence intervals
on every point estimate.

  (A) Total cost of recommended care per visit  <- primary outcome
  (B) Diagnostic tests, $/visit
  (C) Specialist consultations, n/visit
  (D) New medications, n/visit

All estimates and CIs are read from results/analysis/table1.json so the
figure, Table 1 and the text cannot drift apart.

Outputs: paper/figures/fig_cost.{pdf,png}
"""

import sys
import json
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import MODEL_INFO, FAMILY_COLORS   # noqa: E402

TABLE = ROOT / "results" / "analysis" / "table1.json"
OUT_DIR = ROOT / "paper" / "figures"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 10.5,
    "axes.facecolor": "white",
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#EEEEEE",
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})

PANELS = [
    ("total", "A", "Total cost of recommended care", "$ per visit", True),
    ("dx", "B", "Diagnostic tests", "$ per visit", True),
    ("consult_n", "C", "Specialist referrals", "Number per visit", False),
    ("med_n", "D", "New medications", "Number per visit", False),
]


def main():
    data = json.loads(TABLE.read_text())
    rows, physician = data["per_model"], data["physician"]

    fig = plt.figure(figsize=(16, 11))
    gs = gridspec.GridSpec(2, 2, wspace=0.30, hspace=0.30)

    for idx, (field, letter, title, xlabel, dollars) in enumerate(PANELS):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        keys = sorted(rows, key=lambda m: rows[m][field]["mean"])
        for i, m in enumerate(keys):
            e = rows[m][field]
            color = FAMILY_COLORS.get(rows[m]["family"], "#888")
            spec = rows[m]["specialized"]
            ax.barh(i, e["mean"], height=0.62, color=color,
                    alpha=0.55 if spec else 0.85,
                    edgecolor="#333" if spec else "white",
                    linewidth=0.9 if spec else 0.5,
                    hatch="///" if spec else None, zorder=2)
            ax.plot(e["ci"], [i, i], color="#333", lw=1.1, zorder=3)
            for b in e["ci"]:
                ax.plot([b, b], [i - 0.16, i + 0.16], color="#333", lw=1.1, zorder=3)

        p = physician[field]
        ax.axvspan(p["ci"][0], p["ci"][1], color="#E15759", alpha=0.10, zorder=1)
        ax.axvline(p["mean"], color="#E15759", lw=1.7, ls="--", zorder=4)
        txt = (f"physician ${p['mean']:.0f}" if dollars
               else f"physician {p['mean']:.2f}")
        # Above the plot area rather than at the foot of the axis, where it
        # collided with the lowest bar, and in a darker red than the reference
        # line so it stays legible against white (as in Figure 4).
        ax.text(p["mean"], len(keys) + 0.06, "  " + txt, color="#A4161A",
                fontsize=9.2, va="bottom", ha="left", fontweight="bold", zorder=5)

        ax.set_yticks(range(len(keys)))
        ax.set_yticklabels([rows[m]["label"] for m in keys], fontsize=8.6)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_title(f"{letter}    {title}", fontsize=12, fontweight="bold", loc="left")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylim(-0.8, len(keys) + 0.55)   # headroom for the physician label
        ax.set_xlim(0, max(rows[m][field]["ci"][1] for m in rows) * 1.06)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig_cost.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig_cost.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_DIR/'fig_cost.pdf'} / .png")


if __name__ == "__main__":
    main()
