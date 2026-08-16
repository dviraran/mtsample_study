#!/usr/bin/env python3
"""Supplementary Figure S5: Specialist Referral Analysis.

Rebuilds supp_referral_analysis.png with 3 panels:
  A — Referral volume by specialty for AI (mean across 17 models) vs. physician
  B — Fold-change in AI referrals relative to physician by specialty
  C — Referral rate per case for each model (with physician baseline)

Reads current data from results/models/m_*.json with the same 200-case filter
as generate_paper_figures.py (load_all_models).
"""
from __future__ import annotations

import sys
from collections import defaultdict, Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "figures"))

from generate_paper_figures import (
    FAMILY_COLORS,
    MODEL_INFO,
    SPECIALIZED_MODELS,
    load_unified_panel,
)

OUT_DIR = ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Specialty normalization — collapse variants into canonical buckets
SPECIALTY_NORMALIZE = {
    "physical therapy": "Physical Therapy",
    "physical therapist": "Physical Therapy",
    "pt": "Physical Therapy",
    "orthopedics": "Orthopedics",
    "orthopaedics": "Orthopedics",
    "orthopedic surgery": "Orthopedics",
    "neurology": "Neurology",
    "neurosurgery": "Neurosurgery",
    "cardiology": "Cardiology",
    "gastroenterology": "Gastroenterology",
    "gi": "Gastroenterology",
    "psychiatry": "Psychiatry",
    "psychology": "Psychology",
    "dermatology": "Dermatology",
    "endocrinology": "Endocrinology",
    "urology": "Urology",
    "ophthalmology": "Ophthalmology",
    "ent": "ENT",
    "otolaryngology": "ENT",
    "pulmonology": "Pulmonology",
    "nephrology": "Nephrology",
    "rheumatology": "Rheumatology",
    "oncology": "Oncology",
    "nutrition": "Nutrition/Dietetics",
    "dietetics": "Nutrition/Dietetics",
    "dietitian": "Nutrition/Dietetics",
    "social work": "Social Work",
    "pain management": "Pain Management",
    "pain": "Pain Management",
    "obgyn": "OB/GYN",
    "ob/gyn": "OB/GYN",
    "obstetrics": "OB/GYN",
    "gynecology": "OB/GYN",
    "occupational therapy": "Occupational Therapy",
    "ot": "Occupational Therapy",
    "speech therapy": "Speech Therapy",
    "speech-language": "Speech Therapy",
    "allergy": "Allergy/Immunology",
    "immunology": "Allergy/Immunology",
    "infectious disease": "Infectious Disease",
    "id": "Infectious Disease",
    "hematology": "Hematology",
    "vascular": "Vascular Surgery",
    "surgery": "General Surgery",
}


def normalize_specialty(s: str) -> str:
    if not s:
        return "Other"
    s = s.strip().lower()
    # longest-match lookup
    for key in sorted(SPECIALTY_NORMALIZE, key=len, reverse=True):
        if key in s:
            return SPECIALTY_NORMALIZE[key]
    return s.title() if len(s) <= 25 else "Other"


def collect_referrals(all_data: dict):
    """Return per-specialty counts for AI (aggregate across 17 models/200 cases each)
    and physician (once, 200 cases)."""
    ai_counts = Counter()
    phys_counts = Counter()
    n_cases_per_model = {}
    n_phys_cases = None

    for model, cases in all_data.items():
        n_cases_per_model[model] = len(cases)
        for c in cases:
            for ref in c.get("llm_referrals", []) or []:
                if ref.get("type") == "DEFINITE":
                    spec = normalize_specialty(ref.get("specialty", ""))
                    ai_counts[spec] += 1
        # Only count physician referrals once (they should be identical across models,
        # but m_human.json is the canonical source if present)
        if model == list(all_data)[0]:
            n_phys_cases = len(cases)
            for c in cases:
                for ref in c.get("human_referrals", []) or []:
                    if ref.get("type") == "DEFINITE":
                        spec = normalize_specialty(ref.get("specialty", ""))
                        phys_counts[spec] += 1

    return ai_counts, phys_counts, n_cases_per_model, n_phys_cases


def per_model_ref_rate(all_data: dict) -> list[tuple[str, float, int]]:
    """Return list of (model_label, referrals_per_case, gen) for the model ordering in panel C."""
    rows = []
    for model, cases in all_data.items():
        if model not in MODEL_INFO:
            continue
        total = sum(len([r for r in (c.get("llm_referrals") or []) if r.get("type") == "DEFINITE"]) for c in cases)
        rate = total / len(cases) if cases else 0
        rows.append((model, MODEL_INFO[model]["label"], MODEL_INFO[model]["family"], rate))
    return rows


def main():
    print("Loading data…")
    all_data = load_unified_panel()
    n_models = len(all_data)
    # n=200 is guaranteed by load_all_models filter

    ai_counts, phys_counts, n_cases_per_model, n_phys_cases = collect_referrals(all_data)

    # Panel A: top specialties by AI volume. Normalize AI to per-case per-model for fair display.
    specialties = set(ai_counts) | set(phys_counts)
    rows = []
    for spec in specialties:
        ai_per_case = ai_counts[spec] / (n_models * n_phys_cases)
        phys_per_case = phys_counts[spec] / n_phys_cases if n_phys_cases else 0
        rows.append((spec, ai_per_case, phys_per_case))
    rows.sort(key=lambda r: r[1], reverse=True)
    top = rows[:12]

    # ── Figure: 3 panels horizontally ──
    fig = plt.figure(figsize=(20, 7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 1.0, 1.1], wspace=0.45)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    })

    # ── Panel A: Referral volume by specialty (AI mean vs physician) ──
    ax_a = fig.add_subplot(gs[0])
    labels_a = [r[0] for r in top]
    ai_vals = [r[1] for r in top]
    ph_vals = [r[2] for r in top]
    y = np.arange(len(labels_a))
    height = 0.36
    ax_a.barh(y - height / 2, ai_vals, height,
              label=f"AI (mean of {n_models} systems)",
              color="#4070B0", alpha=0.85, edgecolor="white", linewidth=0.5)
    ax_a.barh(y + height / 2, ph_vals, height, label="Physician", color="#C8A428",
              alpha=0.85, edgecolor="white", linewidth=0.5)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(labels_a, fontsize=10)
    ax_a.invert_yaxis()
    ax_a.set_xlabel("Referrals per Case", fontsize=11)
    ax_a.set_title("A    Referral Volume by Specialty", fontsize=13,
                   fontweight="bold", loc="left", pad=10)
    ax_a.legend(fontsize=9, loc="lower right")
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)
    ax_a.set_axisbelow(True)

    # ── Panel B: Fold-change (AI/physician) per specialty ──
    ax_b = fig.add_subplot(gs[1])
    fold_rows = []
    for spec, ai_r, ph_r in top:
        if ph_r > 0:
            fold = ai_r / ph_r
            label = spec
        else:
            fold = None  # no physician referrals — flag separately
            label = spec + "*"
        fold_rows.append((spec, label, fold, ai_r, ph_r))
    # Sort: finite folds first (by magnitude), then infinite ones
    finite = [r for r in fold_rows if r[2] is not None]
    infinite = [r for r in fold_rows if r[2] is None]
    finite.sort(key=lambda r: r[2], reverse=True)
    ordered = finite + infinite

    y_b = np.arange(len(ordered))
    for i, (spec, label, fold, ai_r, ph_r) in enumerate(ordered):
        if fold is not None:
            ax_b.barh(i, fold, color="#B84040", alpha=0.85, edgecolor="white", linewidth=0.5)
            ax_b.text(fold + 0.1, i, f"{fold:.1f}×", fontsize=9,
                      va="center", fontweight="bold", color="#333")
        else:
            # No physician referrals — show as a capped bar + note
            ax_b.barh(i, 1.0, color="#CCCCCC", alpha=0.6, hatch="//",
                      edgecolor="#888", linewidth=0.5)
            ax_b.text(0.02, i, f"(phys = 0, AI = {ai_r:.2f}/case)",
                      fontsize=8, va="center", color="#333", style="italic")
    ax_b.axvline(x=1.0, color="#333", linestyle="--", lw=1.0, alpha=0.7, zorder=0)
    ax_b.set_yticks(y_b)
    ax_b.set_yticklabels([r[1] for r in ordered], fontsize=10)
    ax_b.invert_yaxis()
    ax_b.set_xlabel("Fold-change (AI / Physician)", fontsize=11)
    ax_b.set_title("B    Fold-change by Specialty", fontsize=13,
                   fontweight="bold", loc="left", pad=10)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)
    ax_b.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)
    ax_b.set_axisbelow(True)
    ax_b.text(0.01, -0.15, "* physician ordered no referrals in this specialty",
              transform=ax_b.transAxes, fontsize=8, color="#666", style="italic")

    # ── Panel C: Per-model referral rate ──
    ax_c = fig.add_subplot(gs[2])
    model_rows = per_model_ref_rate(all_data)
    model_rows.sort(key=lambda r: r[3])
    y_c = np.arange(len(model_rows))
    phys_ref_rate = sum(phys_counts.values()) / n_phys_cases if n_phys_cases else 0.14

    for i, (model, label, family, rate) in enumerate(model_rows):
        color = FAMILY_COLORS.get(family, "#888")
        is_spec = model in SPECIALIZED_MODELS
        ax_c.barh(i, rate, color=color, alpha=0.5 if is_spec else 0.85,
                  edgecolor=color if is_spec else "white",
                  linewidth=1.5 if is_spec else 0.5)
        ax_c.text(rate + 0.02, i, f"{rate:.2f}", fontsize=9, va="center",
                  fontweight="normal" if is_spec else "bold", color="#333")

    ax_c.axvline(x=phys_ref_rate, color="#333", linestyle="--", lw=1.1, alpha=0.7, zorder=0)
    ax_c.text(phys_ref_rate, -1.4, f"Physician: {phys_ref_rate:.2f}/case",
              ha="center", fontsize=9, fontweight="bold", color="#555",
              bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFDE7",
                        edgecolor="#E0C97F", alpha=0.95))
    ax_c.set_yticks(y_c)
    ax_c.set_yticklabels([r[1] for r in model_rows], fontsize=10)
    ax_c.set_xlabel("Avg Referrals per Case", fontsize=11)
    ax_c.set_title("C    Referral Rate by Model", fontsize=13,
                   fontweight="bold", loc="left", pad=10)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)
    ax_c.grid(axis="x", color="#EEEEEE", lw=0.8, zorder=0)
    ax_c.set_axisbelow(True)
    ax_c.set_ylim(-1.8, len(model_rows) - 0.3)

    # Save
    fig.savefig(OUT_DIR / "supp_referral_analysis.png", dpi=300,
                bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_DIR / "supp_referral_analysis.pdf", bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print(f"✓ supp_referral_analysis saved to {OUT_DIR}")

    # Also print summary to console
    print(f"\nTop specialties (per-case):")
    for spec, ai_r, ph_r in top[:8]:
        fc = f"{ai_r/ph_r:.1f}×" if ph_r > 0 else "phys=0"
        print(f"  {spec:<22} AI={ai_r:.3f}  Phys={ph_r:.3f}  {fc}")
    print(f"\nPhysician total referral rate: {phys_ref_rate:.2f}/case "
          f"(N={n_phys_cases})")


if __name__ == "__main__":
    main()
