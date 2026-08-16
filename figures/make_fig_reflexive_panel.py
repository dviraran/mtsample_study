#!/usr/bin/env python3
"""
Main-text figure: the reflexive screening panel AI systems suggest on visits
where the treating physician ordered no diagnostic workup.

For each commonly suggested test the figure reports the across-system spread
rather than a single pooled frequency: every one of the 24 systems is plotted,
with the panel mean and the interquartile range across systems, as an index of
variance among the systems.

Panel A: the ten most frequently suggested tests on $0-physician visits, mean
         across systems with IQR and per-system points.
Panel B: number of diagnostic tests suggested per encounter, per system, versus
         the physician — showing both the level and the spread of the
         "kitchen-sink" tail.

Outputs: paper/figures/fig_reflexive_panel.{pdf,png}
         results/analysis/reflexive_panel.json
"""

import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (          # noqa: E402
    MODEL_INFO, SPECIALIZED_MODELS, FAMILY_COLORS, load_unified_panel,
)

OUT_DIR = ROOT / "paper" / "figures"
OUT_JSON = ROOT / "results" / "analysis" / "reflexive_panel.json"

DX_CATS = {"labs", "imaging", "procedure", "monitoring", "exam"}
TOP_N = 10

CPT_CANON = {
    "85025": "CBC", "80053": "Comprehensive metabolic panel",
    "83036": "Hemoglobin A1c", "84443": "TSH", "80048": "Basic metabolic panel",
    "80061": "Lipid panel", "85652": "ESR", "82607": "Vitamin B12",
    "86140": "C-reactive protein", "82947": "Fasting glucose",
    "71046": "Chest X-ray", "71020": "Chest X-ray", "81003": "Urinalysis",
    "81001": "Urinalysis", "93000": "Electrocardiogram",
    "80076": "Hepatic function panel", "82746": "Folate", "84439": "Free T4",
    "82728": "Ferritin",
}

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
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def label_for(key, desc_counter):
    if key.startswith("cpt:"):
        code = key[4:]
        if code in CPT_CANON:
            return CPT_CANON[code]
    common = desc_counter.most_common(1)
    return common[0][0].title() if common else key


def collect():
    """Per-system suggestion rates on $0-physician visits, and tests/encounter."""
    panel = load_unified_panel()
    # system -> test key -> n visits suggesting it; system -> n $0 visits
    per_sys_test = defaultdict(Counter)
    per_sys_zero = Counter()
    desc_of = defaultdict(Counter)
    pooled = Counter()
    tests_per_enc = {}
    phys_tests_per_enc = []

    for model, cases in panel.items():
        if model not in MODEL_INFO:
            continue
        counts = []
        for c in cases:
            l_orders = [o for o in (c.get("llm_orders_b") or [])
                        if isinstance(o, dict) and o.get("category") in DX_CATS]
            h_orders = [o for o in (c.get("human_orders_b") or [])
                        if isinstance(o, dict) and o.get("category") in DX_CATS]
            counts.append(len(l_orders))
            phys_tests_per_enc.append(len(h_orders))

            if (c.get("medicare_human_dx_cost") or 0) != 0:
                continue
            per_sys_zero[model] += 1
            seen = set()
            for o in l_orders:
                desc = (o.get("order") or "").strip()
                if not desc or desc.lower() == "none":
                    continue
                code = o.get("cpt_code")
                key = f"cpt:{code}" if code else desc.lower()
                desc_of[key][desc.lower()] += 1
                if key not in seen:
                    seen.add(key)
                    per_sys_test[model][key] += 1
                    pooled[key] += 1
        tests_per_enc[model] = np.array(counts, dtype=float)

    return (panel, per_sys_test, per_sys_zero, desc_of, pooled,
            tests_per_enc, np.array(phys_tests_per_enc, dtype=float))


def main():
    (panel, per_sys_test, per_sys_zero, desc_of, pooled,
     tests_per_enc, phys_tests) = collect()

    systems = [m for m in panel if m in MODEL_INFO]
    top = [k for k, _ in pooled.most_common(TOP_N)]

    # per-system % of $0-physician visits on which the test was suggested
    rates = {}
    for key in top:
        vals = []
        for m in systems:
            z = per_sys_zero[m]
            if z:
                vals.append(100 * per_sys_test[m][key] / z)
        rates[key] = np.array(vals)

    order = sorted(top, key=lambda k: rates[k].mean())

    fig = plt.figure(figsize=(15.5, 7.2))
    gs = gridspec.GridSpec(1, 2, wspace=0.30, width_ratios=[1.25, 1])

    # ── Panel A ───────────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[0])
    for i, key in enumerate(order):
        v = rates[key]
        q1, q3 = np.percentile(v, [25, 75])
        ax.barh(i, v.mean(), height=0.55, color="#4393C3", alpha=0.30,
                edgecolor="none", zorder=1)
        ax.plot([q1, q3], [i, i], color="#1F5F8B", lw=3.2, solid_capstyle="butt",
                zorder=2)
        ax.scatter(v, np.full_like(v, i) + RNG_JITTER[:len(v)], s=13,
                   color="#1F5F8B", alpha=0.55, edgecolors="none", zorder=3)
        ax.plot([v.mean()], [i], marker="D", ms=6, color="#0B3954", zorder=4)
        ax.text(max(v.max(), q3) + 1.5, i, f"{v.mean():.0f}%", fontsize=9,
                va="center", color="#333", fontweight="bold")

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([label_for(k, desc_of[k]) for k in order], fontsize=10)
    ax.set_xlabel("Visits on which the test was suggested (%)\n"
                  "of visits where the treating physician ordered no workup",
                  fontsize=10)
    ax.set_title("A    The reflexive screening panel",
                 fontsize=12.5, fontweight="bold", loc="left")
    ax.set_xlim(0, max(r.max() for r in rates.values()) * 1.14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ── Panel B ───────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    means = {m: tests_per_enc[m].mean() for m in systems}
    order2 = sorted(systems, key=lambda m: means[m])
    for i, m in enumerate(order2):
        v = tests_per_enc[m]
        q1, q3 = np.percentile(v, [25, 75])
        color = FAMILY_COLORS.get(MODEL_INFO[m]["family"], "#888")
        ax2.plot([q1, q3], [i, i], color=color, lw=3.0, alpha=0.55,
                 solid_capstyle="butt", zorder=2)
        ax2.plot([v.mean()], [i], marker="o", ms=6.5, color=color,
                 markeredgecolor="white", markeredgewidth=0.8, zorder=3)
        if m in SPECIALIZED_MODELS:
            ax2.plot([v.mean()], [i], marker="D", ms=9, mfc="none",
                     mec="#333", mew=0.9, zorder=4)

    pm = phys_tests.mean()
    ax2.axvline(pm, color="#E15759", lw=1.6, ls="--", zorder=1)
    ax2.text(pm, len(order2) - 0.2, f"  physician {pm:.1f}", color="#E15759",
             fontsize=9.5, va="top", fontweight="bold")
    ax2.set_yticks(range(len(order2)))
    ax2.set_yticklabels([MODEL_INFO[m]["label"] for m in order2], fontsize=9)
    ax2.set_xlabel("Diagnostic tests suggested per encounter\n"
                   "(mean, with interquartile range across the 200 cases)",
                   fontsize=10)
    ax2.set_title("B    Volume of suggested testing, by system",
                  fontsize=12.5, fontweight="bold", loc="left")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig_reflexive_panel.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig_reflexive_panel.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    out = {
        "n_systems": len(systems),
        "n_zero_physician_visits_per_system": dict(per_sys_zero),
        "physician_tests_per_encounter_mean": float(phys_tests.mean()),
        "tests_per_encounter": {
            MODEL_INFO[m]["label"]: {
                "mean": float(tests_per_enc[m].mean()),
                "iqr": [float(np.percentile(tests_per_enc[m], 25)),
                        float(np.percentile(tests_per_enc[m], 75))],
            } for m in systems},
        "top_tests": [
            {
                "label": label_for(k, desc_of[k]),
                "mean_pct": float(rates[k].mean()),
                "sd_pct": float(rates[k].std(ddof=1)),
                "iqr_pct": [float(np.percentile(rates[k], 25)),
                            float(np.percentile(rates[k], 75))],
                "range_pct": [float(rates[k].min()), float(rates[k].max())],
            } for k in order[::-1]],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))

    print("Top suggested tests on $0-physician visits (mean % of visits, across-system spread):")
    for t in out["top_tests"]:
        print(f"  {t['label']:34s} {t['mean_pct']:5.1f}%  "
              f"IQR {t['iqr_pct'][0]:.0f}–{t['iqr_pct'][1]:.0f}  "
              f"range {t['range_pct'][0]:.0f}–{t['range_pct'][1]:.0f}")
    print(f"\nphysician tests/encounter {out['physician_tests_per_encounter_mean']:.2f}")
    print(f"wrote {OUT_DIR/'fig_reflexive_panel.pdf'}\nwrote {OUT_JSON}")


# small deterministic jitter so overlapping per-system points stay readable
RNG_JITTER = np.linspace(-0.16, 0.16, 24)
np.random.default_rng(7).shuffle(RNG_JITTER)


if __name__ == "__main__":
    main()
