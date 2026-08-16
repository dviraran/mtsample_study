#!/usr/bin/env python3
"""
Generates the two agreement figures using Lin's concordance
correlation coefficient and Bland-Altman plots.

  supp_test_retest.{pdf,png}         (Figure S5) - 92 duplicate case pairs
  supp_extractor_agreement.{pdf,png} (Figure S6) - 3 LLM extractors

Also writes results/analysis/agreement_stats.json so paper_numbers.py and the
supplement text can cite the same values.

Usage:  /usr/bin/python3 figures/make_supp_agreement.py
"""

import os
import sys
import glob
import json
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (          # noqa: E402
    MODEL_INFO, FAMILY_COLORS, load_unified_panel,
)
from agreement_stats import lins_ccc, bland_altman, format_ccc   # noqa: E402

OUT_DIR = ROOT / "paper" / "figures"
STATS_OUT = ROOT / "results" / "analysis" / "agreement_stats.json"

AI_COLOR = "#4393C3"
PHYS_COLOR = "#E8834A"
EXTRACTOR_NAMES = {"a": "GPT-4.1-mini", "b": "Claude Haiku", "c": "Gemini Flash"}

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
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 300,
})


def _save(fig, stem):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {stem}.pdf / .png")


def _ba_panel(ax, ba, color, title, unit="$"):
    """Draw one Bland-Altman panel from a bland_altman() result."""
    ax.scatter(ba["mean"], ba["diff"], c=color, alpha=0.40, s=22,
               edgecolors="none", rasterized=True)
    ax.axhline(ba["bias"], color="#333", lw=1.4)
    ax.axhline(ba["loa_upper"], color="#E15759", lw=1.1, ls="--")
    ax.axhline(ba["loa_lower"], color="#E15759", lw=1.1, ls="--")
    ax.axhline(0, color="#999", lw=0.8, ls=":")
    xmax = float(np.max(ba["mean"])) if len(ba["mean"]) else 1
    ax.text(xmax, ba["bias"], f" bias {ba['bias']:+.0f}", fontsize=8,
            va="bottom", ha="right", color="#333")
    ax.text(xmax, ba["loa_upper"], f" +1.96 SD {ba['loa_upper']:+.0f}", fontsize=8,
            va="bottom", ha="right", color="#E15759")
    ax.text(xmax, ba["loa_lower"], f" -1.96 SD {ba['loa_lower']:+.0f}", fontsize=8,
            va="top", ha="right", color="#E15759")
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=6)
    ax.set_xlabel(f"Mean of the two measurements ({unit})", fontsize=9)
    ax.set_ylabel(f"Difference ({unit})", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ══════════════════════════════════════════════════════════════════════
# S9 — test-retest on 92 duplicate case pairs
# ══════════════════════════════════════════════════════════════════════
def test_retest():
    """Duplicate presentations live in results/models_original_runs/ (the
    pre-dedup 315-case files); results/models/ is already deduped to 200."""
    per_model, best, best_ccc = {}, None, -np.inf

    for fpath in sorted(glob.glob(str(ROOT / "results" / "models_original_runs" / "m_*.json"))):
        model = os.path.basename(fpath).replace("m_", "").replace(".json", "")
        if model not in MODEL_INFO or model == "openevidence":
            continue
        with open(fpath) as f:
            raw = json.load(f)
        if not raw or "presentation" not in raw[0]:
            continue

        pres = {}
        for c in raw:
            pres.setdefault(c["presentation"], []).append(
                float(c.get("medicare_llm_dx_cost") or 0))
        pairs = [(v[0], v[1]) for v in pres.values() if len(v) >= 2]
        if len(pairs) < 10:
            continue

        x = np.array([p[0] for p in pairs])
        y = np.array([p[1] for p in pairs])
        cc = lins_ccc(x, y)
        ba = bland_altman(x, y)
        per_model[model] = {
            "n_pairs": len(pairs),
            **{k: v for k, v in cc.items() if k != "n"},
            "bland_altman": {k: v for k, v in ba.items()
                             if k not in ("mean", "diff")},
        }
        if cc["ccc"] > best_ccc:
            best_ccc, best = cc["ccc"], (model, x, y, cc, ba)

    order = sorted(per_model, key=lambda m: per_model[m]["ccc"])

    fig = plt.figure(figsize=(15, 6.5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.15, 1], wspace=0.28)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    for i, m in enumerate(order):
        d = per_model[m]
        color = FAMILY_COLORS.get(MODEL_INFO[m]["family"], "#888")
        ax1.barh(i, d["ccc"], color=color, alpha=0.85, height=0.62,
                 edgecolor="white", linewidth=0.5)
        if "ccc_ci" in d:
            ax1.plot(d["ccc_ci"], [i, i], color="#444", lw=1.2, zorder=3)
            ax1.plot([d["ccc_ci"][0]] * 2, [i - .13, i + .13], color="#444", lw=1.2)
            ax1.plot([d["ccc_ci"][1]] * 2, [i - .13, i + .13], color="#444", lw=1.2)
        ax1.text(max(d["ccc"], d.get("ccc_ci", [0, 0])[1]) + 0.015, i,
                 f"{d['ccc']:.2f}", fontsize=8.5, va="center",
                 fontweight="bold", color="#333")

    ax1.set_yticks(np.arange(len(order)))
    ax1.set_yticklabels([MODEL_INFO[m]["label"] for m in order], fontsize=9.5)
    ax1.set_xlabel("Lin's concordance correlation coefficient (95% CI)", fontsize=10.5)
    ax1.set_xlim(0, 1.05)
    ax1.set_title("A    Test–retest concordance\n(duplicate clinical presentations)",
                  fontsize=12, fontweight="bold", loc="left")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    if best:
        m, x, y, cc, ba = best
        _ba_panel(ax2, ba, FAMILY_COLORS.get(MODEL_INFO[m]["family"], "#888"),
                  f"B    Bland–Altman, {MODEL_INFO[m]['label']} "
                  f"({format_ccc(cc)}, n = {len(x)} pairs)")

    _save(fig, "supp_test_retest")
    return {"per_model": per_model,
            "best_model": best[0] if best else None,
            "n_models": len(per_model)}


# ══════════════════════════════════════════════════════════════════════
# S10 — inter-extractor agreement
# ══════════════════════════════════════════════════════════════════════
def _slot_cost(orders):
    if not orders:
        return 0.0
    return float(sum((o.get("price", 0) or 0) for o in orders
                     if isinstance(o, dict) and o.get("category") != "medication"))


def extractor_agreement():
    panel = load_unified_panel()
    rows = {"AI": {"a": [], "b": [], "c": []},
            "Physician": {"a": [], "b": [], "c": []}}
    for cases in panel.values():
        for case in cases:
            for side, pre in (("AI", "llm"), ("Physician", "human")):
                vals = {s: _slot_cost(case.get(f"{pre}_orders_{s}", [])) for s in "abc"}
                if any(v > 0 for v in vals.values()):
                    for s in "abc":
                        rows[side][s].append(vals[s])

    pairs = [("a", "b"), ("a", "c"), ("b", "c")]
    stats = {}

    fig = plt.figure(figsize=(17, 10))
    gs = gridspec.GridSpec(2, 3, wspace=0.28, hspace=0.34,
                           left=0.075, right=0.97, top=0.90, bottom=0.07)

    for r, (side, color) in enumerate((("AI", AI_COLOR), ("Physician", PHYS_COLOR))):
        stats[side] = {}
        for c, (p, q) in enumerate(pairs):
            x = np.array(rows[side][p])
            y = np.array(rows[side][q])
            cc = lins_ccc(x, y)
            ba = bland_altman(x, y)
            stats[side][f"{p}_vs_{q}"] = {
                **{k: v for k, v in cc.items()},
                "bland_altman": {k: v for k, v in ba.items()
                                 if k not in ("mean", "diff")},
            }
            ax = fig.add_subplot(gs[r, c])
            _ba_panel(ax, ba, color,
                      f"{side}: {EXTRACTOR_NAMES[p]} vs {EXTRACTOR_NAMES[q]}\n"
                      f"{format_ccc(cc)}")

    fig.text(0.017, 0.70, "AI plans", fontsize=14, fontweight="bold",
             color=AI_COLOR, rotation=90, va="center", ha="center")
    fig.text(0.017, 0.28, "Physician plans", fontsize=14, fontweight="bold",
             color=PHYS_COLOR, rotation=90, va="center", ha="center")
    fig.suptitle("Inter-extractor agreement (Bland–Altman, with Lin's concordance)",
                 fontsize=14, fontweight="bold", x=0.075, ha="left", y=0.965)

    _save(fig, "supp_extractor_agreement")
    return stats


def main():
    print("Test–retest (Figure S9):")
    tr = test_retest()
    print("Inter-extractor (Figure S10):")
    ex = extractor_agreement()

    STATS_OUT.parent.mkdir(parents=True, exist_ok=True)
    STATS_OUT.write_text(json.dumps({"test_retest": tr, "extractor": ex},
                                    indent=2, default=float))
    print(f"\nwrote {STATS_OUT}")

    # console summary for the supplement text
    ccs = {m: d["ccc"] for m, d in tr["per_model"].items()}
    lo, hi = min(ccs.values()), max(ccs.values())
    lo_m = min(ccs, key=ccs.get)
    hi_m = max(ccs, key=ccs.get)
    print(f"\ntest–retest CCC range: {lo:.2f} ({MODEL_INFO[lo_m]['label']}) "
          f"– {hi:.2f} ({MODEL_INFO[hi_m]['label']})")
    for side in ("AI", "Physician"):
        vals = [d["ccc"] for d in ex[side].values()]
        rs = [d["pearson_r"] for d in ex[side].values()]
        print(f"{side:10s} extractor CCC {min(vals):.2f}–{max(vals):.2f} "
              f"(Pearson r {min(rs):.2f}–{max(rs):.2f})")


if __name__ == "__main__":
    main()
