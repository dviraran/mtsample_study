#!/usr/bin/env python3
"""Supplementary Figure: Three-judge concordance agreement and absence of own-family bias.

Diagnostic concordance for every system in the
24-system unified panel (results/models/) was independently classified by three
LLM judges from different developers:
  dx_match_v2 = GPT-4.1-mini (OpenAI)
  dx_claude   = Claude Sonnet 4.5 (Anthropic)
  dx_gemini   = Gemini 2.5 Flash (Google)
Concordance = correct + correct_plus on the cases judged into a valid tier.

Panel A: per-system concordance under each of the three judges (systems sorted by mean).
         Judges differ in overall severity but track each other across systems.
Panel B: own-family EXCESS self-bias by judge family. EXCESS = (own-family concordance
         premium under the own judge) minus (that judge's uniform severity offset over
         ALL systems). EXCESS near zero means no self-favoritism beyond uniform severity.

Mirrors scripts/analyze_judge_leniency.py methodology, extended to the 24-system panel.
Output: paper/figures/supp_judge_agreement.{png,pdf}
"""
from __future__ import annotations

import sys
import statistics
import itertools
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))
import generate_paper_figures as gpf

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

# judge field -> (developer family, display label, bar color)
JUDGES = {
    "dx_match_v2": ("OpenAI", "GPT-4.1-mini (OpenAI)", "#66A61E"),
    "dx_claude":   ("Anthropic", "Claude Sonnet 4.5 (Anthropic)", "#E8834A"),
    "dx_gemini":   ("Google", "Gemini 2.5 Flash (Google)", "#3B8FD2"),
}
# MODEL_INFO 'family' -> developer family used for the own-family-bias test
DEV = {
    "Claude": "Anthropic", "GPT": "OpenAI", "Gemini": "Google", "Grok": "xAI",
    "Llama": "Meta", "Qwen": "Qwen", "DeepSeek": "DeepSeek",
    "OpenEvidence": "OpenEvidence", "MedGemma": "Google", "Meditron": "Meditron",
}
CONCORDANT = {"correct", "correct_plus"}
VALID = {"correct", "correct_plus", "related", "wrong"}


def concord(cases, field):
    judged = [r for r in cases if r.get(field) in VALID]
    if not judged:
        return None
    return 100.0 * sum(r[field] in CONCORDANT for r in judged) / len(judged)


def main():
    ad = gpf.load_unified_panel()
    models = list(ad.keys())
    tab = {m: {j: concord(ad[m], j) for j in JUDGES} for m in models}
    fam = {m: DEV[gpf.MODEL_INFO[m]["family"]] for m in models}

    # judge severity (mean concordance across systems)
    jmean = {j: statistics.mean([tab[m][j] for m in models if tab[m][j] is not None])
             for j in JUDGES}

    # sort systems by mean concordance over the three judges (ascending -> read up)
    def sys_mean(m):
        vs = [tab[m][j] for j in JUDGES if tab[m][j] is not None]
        return statistics.mean(vs) if vs else 0
    models_sorted = sorted(models, key=sys_mean)

    # ── Figure layout: A (tall, per-system) + B (compact, excess bias) ──
    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.32)

    # ── Panel A: per-system concordance under each judge ──
    ax = fig.add_subplot(gs[0])
    y = np.arange(len(models_sorted))
    bh = 0.26
    for k, (field, (jf, lab, color)) in enumerate(JUDGES.items()):
        vals = [tab[m][field] if tab[m][field] is not None else 0 for m in models_sorted]
        ax.barh(y + (1 - k) * bh, vals, height=bh * 0.92, color=color, alpha=0.9,
                edgecolor="white", linewidth=0.4, label=lab, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([gpf.MODEL_INFO[m]["label"] for m in models_sorted], fontsize=9)
    ax.set_ylim(-0.6, len(models_sorted) - 0.1)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Diagnostic concordance (%)", fontsize=11)
    ax.set_title("A   Per-system concordance under three independent judges",
                 fontsize=12.5, fontweight="bold", loc="left", pad=10)
    ax.legend(fontsize=9, loc="lower right", framealpha=0.96, title="Judge (developer)",
              title_fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)

    # severity reference lines (mean concordance per judge)
    for field, (jf, lab, color) in JUDGES.items():
        ax.axvline(jmean[field], color=color, ls=":", lw=1.3, alpha=0.85, zorder=2)
    ax.text(0.5, 1.005,
            f"Judge mean (severity):  GPT {jmean['dx_match_v2']:.0f}%   "
            f"Claude {jmean['dx_claude']:.0f}%   Gemini {jmean['dx_gemini']:.0f}%",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=8.6, color="#555")

    # ── Panel B: own-family EXCESS self-bias ──
    axb = fig.add_subplot(gs[1])

    def offset(field, subset):
        vals = []
        for m in subset:
            others = [tab[m][j] for j in JUDGES if j != field and tab[m][j] is not None]
            if tab[m][field] is not None and others:
                vals.append(tab[m][field] - statistics.mean(others))
        return statistics.mean(vals) if vals else None

    rows = []
    for field, (jf, lab, color) in JUDGES.items():
        fam_models = [m for m in models if fam[m] == jf]
        fam_prem = offset(field, fam_models)
        gen_prem = offset(field, models)
        if fam_prem is None or gen_prem is None:
            continue
        rows.append((jf, color, len(fam_models), fam_prem - gen_prem))

    yb = np.arange(len(rows))
    # ±5 pp "no material bias" band
    axb.axvspan(-5, 5, color="#E8F4EA", alpha=0.9, zorder=0)
    axb.axvline(0, color="#333", lw=1.1, alpha=0.8, zorder=1)
    for i, (jf, color, nfam, exc) in enumerate(rows):
        axb.barh(i, exc, height=0.5, color=color, alpha=0.9, edgecolor="white",
                 linewidth=0.6, zorder=3)
        ha = "left" if exc >= 0 else "right"
        dx = 0.25 if exc >= 0 else -0.25
        axb.text(exc + dx, i, f"{exc:+.1f} pp", va="center", ha=ha,
                 fontsize=10, fontweight="bold", color="#333", zorder=4)
    axb.set_yticks(yb)
    axb.set_yticklabels([f"{jf}\n(judge, n={n})" for jf, _, n, _ in rows], fontsize=10)
    axb.set_ylim(-0.6, len(rows) - 0.4)
    axb.set_xlim(-10, 10)
    axb.set_xlabel("Own-family excess concordance bias (pp)", fontsize=11)
    axb.set_title("B   Own-family bias after removing judge severity",
                  fontsize=12.5, fontweight="bold", loc="left", pad=10)
    axb.spines[["top", "right"]].set_visible(False)
    axb.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)
    axb.text(0.5, -0.085, "shaded band: |bias| < 5 pp (no material self-favoritism)",
             transform=axb.transAxes, ha="center", va="top", fontsize=8.6,
             color="#3C7A4A", style="italic")

    # cross-judge correlation note (per-system concordance tracks together)
    rs = []
    for a, b in itertools.combinations(JUDGES, 2):
        xs = [tab[m][a] for m in models]
        ys = [tab[m][b] for m in models]
        rs.append(pearsonr(xs, ys)[0])
    axb.text(0.74, 0.86,
             "Judges differ in overall\nseverity, not in ranking:\n"
             "per-system concordance is\nhighly correlated across\n"
             f"judges (pairwise\nr = {min(rs):.2f} to {max(rs):.2f}).",
             transform=axb.transAxes, ha="center", va="center", fontsize=8.8,
             color="#444",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFFDE7",
                       edgecolor="#E0C97F", alpha=0.95))

    fig.suptitle(
        "Concordance classification is robust to judge choice and shows no own-family bias",
        fontsize=13.5, fontweight="bold", y=0.98)

    for fmt in ("png", "pdf"):
        fig.savefig(OUT_DIR / f"supp_judge_agreement.{fmt}", dpi=300,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote supp_judge_agreement  (systems={len(models)}, "
          f"severity GPT={jmean['dx_match_v2']:.0f}% Claude={jmean['dx_claude']:.0f}% "
          f"Gemini={jmean['dx_gemini']:.0f}%)")
    for jf, _, n, exc in rows:
        print(f"  {jf:10} excess self-bias {exc:+.1f} pp (n_family={n})")
    print(f"  cross-judge r = {min(rs):.2f}–{max(rs):.2f}")


if __name__ == "__main__":
    main()
