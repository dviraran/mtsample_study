#!/usr/bin/env python3
"""
Main-text prompt-mitigation figure (Figure 3); the referral and medication
panels are in the supplement.

Ratio of the primary outcome, the per-visit total cost of recommended care
(diagnostic tests plus specialist consultations), to the treating physician
under the three prompts, with 95% confidence intervals from a case-level
bootstrap.

Consultations in the two mitigation arms were extracted and priced by
scripts/extract_referrals.py on those directories, the identical pipeline and
extractor used for the standard arm, so all three arms are measured the same
way.

Outputs: paper/figures/fig_prompt_arms.{pdf,png}
         results/analysis/prompt_arms.json
"""

import sys
import json
import glob
import os
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

OUT_DIR = ROOT / "paper" / "figures"
OUT_JSON = ROOT / "results" / "analysis" / "prompt_arms.json"

# Guard: the mitigation arms only carry priced consultations after
# scripts/extract_referrals.py has been run on those directories.
REQUIRED_FIELD = "llm_referral_cost"

ARMS = [
    ("default", "Standard prompt", "#C0392B", "results/models"),
    ("costaware", "Cost-aware prompt", "#E67E22", "results/models_costaware"),
    ("parsimonious", "Parsimonious-but-safe prompt", "#27AE60", "results/models_parsimonious"),
]
SELECT = ["gpt-5.5", "claude-opus-4.8", "gemini-3.1-pro",
          "grok-4.3", "qwen-3.7", "deepseek-r1"]

BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)
N_BOOT = 2000


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def load_arm(dirname, keep_ids):
    """model -> {case_id: (physician dx cost, AI dx cost)} restricted to the cohort."""
    out = {}
    for fpath in sorted(glob.glob(str(ROOT / dirname / "m_*.json"))):
        name = os.path.basename(fpath).replace("m_", "").replace(".json", "")
        if name not in MODEL_INFO:
            continue
        seen, rec = set(), {}
        missing = 0
        for c in json.load(open(fpath)):
            cid = c.get("case_id")
            if cid in EXCLUDED_CASES or cid not in keep_ids:
                continue
            p = c.get("presentation")
            if p in seen:
                continue
            seen.add(p)
            if REQUIRED_FIELD not in c:
                missing += 1
            rec[cid] = (fnum(c.get("medicare_human_dx_cost")) + fnum(c.get("human_referral_cost")),
                        fnum(c.get("medicare_llm_dx_cost")) + fnum(c.get("llm_referral_cost")))
        if missing:
            sys.exit(f"{dirname}/{os.path.basename(fpath)}: {missing} cases lack "
                     f"'{REQUIRED_FIELD}'. Run:\n"
                     f"  /usr/bin/python3 scripts/extract_referrals.py --dir {dirname}")
        out[name] = rec
    return out


def ratio_ci(pairs):
    """Bootstrap CI for the ratio of means, resampling cases."""
    h = np.array([p[0] for p in pairs])
    l = np.array([p[1] for p in pairs])
    if not len(h) or h.mean() == 0:
        return float("nan"), [float("nan")] * 2
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(h), size=(N_BOOT, len(h)))
    hm, lm = h[idx].mean(axis=1), l[idx].mean(axis=1)
    ok = hm > 0
    r = lm[ok] / hm[ok]
    return float(l.mean() / h.mean()), [float(np.percentile(r, 2.5)),
                                        float(np.percentile(r, 97.5))]


def main():
    keep_ids = {c["case_id"] for c in next(iter(load_unified_panel().values()))}
    arms = {key: load_arm(d, keep_ids) for key, _, _, d in ARMS}

    models = [m for m in SELECT
              if all(m in arms[k] and arms[k][m] for k, *_ in ARMS)]
    if not models:
        sys.exit("no models present in all three prompt arms")

    stats = {}
    for m in models:
        stats[m] = {}
        for key, label, _, _ in ARMS:
            ids = sorted(arms[key][m])
            r, ci = ratio_ci([arms[key][m][i] for i in ids])
            stats[m][key] = {"n": len(ids), "ratio": r, "ci": ci}

    fig, ax = plt.subplots(figsize=(13, 6))
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Helvetica Neue", "Helvetica",
                                             "Arial", "DejaVu Sans"]})
    n_arm = len(ARMS)
    gw, bw = 0.78, 0.78 / n_arm

    for ai, (key, label, color, _) in enumerate(ARMS):
        xs, hs, los, his = [], [], [], []
        for mi, m in enumerate(models):
            s = stats[m][key]
            x = mi - gw / 2 + bw * (ai + 0.5)
            xs.append(x)
            hs.append(s["ratio"])
            los.append(s["ratio"] - s["ci"][0])
            his.append(s["ci"][1] - s["ratio"])
        ax.bar(xs, hs, width=bw * 0.92, color=color, alpha=0.88,
               edgecolor="white", linewidth=0.6, label=label, zorder=2)
        ax.errorbar(xs, hs, yerr=[los, his], fmt="none", ecolor="#333",
                    elinewidth=1.1, capsize=2.5, zorder=3)
        # label above the upper confidence bound, not the bar, so the whisker
        # does not run through the digits
        for x, h, hi in zip(xs, hs, his):
            ax.text(x, h + hi + 0.08, f"{h:.1f}", ha="center", va="bottom",
                    fontsize=8.6, color="#333")

    ax.axhline(1.0, color="#333", lw=1.5, ls="--", zorder=4)
    ax.text(-0.48, 1.04, "treating physician", fontsize=9.5,
            va="bottom", ha="left", color="#333", fontweight="bold")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([MODEL_INFO[m]["label"] for m in models], fontsize=11)
    ax.set_ylabel("Total cost of recommended care relative to the\n"
                  "treating physician (ratio of means, 95% CI)", fontsize=11)
    ax.set_ylim(0, max(s[k]["ci"][1] for s in stats.values()
                       for k, *_ in ARMS) * 1.12)
    ax.legend(frameon=False, fontsize=10, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, 1.11))
    ax.grid(axis="y", color="#EEEEEE", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig_prompt_arms.pdf", bbox_inches="tight")
    fig.savefig(OUT_DIR / "fig_prompt_arms.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Panel-wide means across systems run through all three arms on the full
    # cohort. OpenEvidence has no API and was administered manually on a
    # 10-case subset only (Figure S8), so the coverage threshold excludes it
    # from the panel mean rather than letting 10 cases weigh as 200.
    MIN_CASES = 150
    allm = [m for m in arms["default"]
            if all(len(arms[k].get(m, {})) >= MIN_CASES for k, *_ in ARMS)]
    panel_means = {}
    for key, *_ in ARMS:
        rs = []
        for m in allm:
            ids = sorted(arms[key][m])
            r, _ = ratio_ci([arms[key][m][i] for i in ids])
            rs.append(r)
        panel_means[key] = {"n_models": len(rs), "mean_ratio": float(np.mean(rs)),
                            "range": [float(np.min(rs)), float(np.max(rs))]}

    OUT_JSON.write_text(json.dumps({"per_model": stats,
                                    "panel_means": panel_means}, indent=2))
    print(json.dumps(panel_means, indent=2))
    print(f"wrote {OUT_DIR/'fig_prompt_arms.pdf'}\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
