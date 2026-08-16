"""CONSORT-style case selection flow figure (Figure S1).

Reproduces the cascade from 4,999 MTSamples notes to 200 analysis cases.
Run: python figures/make_supp_consort.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "figures" / "supp_case_selection_consort.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ── Layout constants ─────────────────────────────────────────────────
FIG_W, FIG_H = 14, 18
ROW_H = 2.3          # vertical distance between main-column box centers
MAIN_BOX_H = 1.5     # main-column box height (taller for multi-line text)
MAIN_BOX_W = 7.6     # wider to fit long lines
MAIN_CX = 4.5        # main-column box center-x
EXCL_BOX_H = 1.7     # exclusion box height (sits in the gap between main boxes)
EXCL_BOX_W = 4.2
EXCL_CX = 11.0       # exclusion box center-x

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, 14)
ax.set_ylim(-0.5, FIG_H + 0.5)
ax.axis("off")

def box(cx, cy, w, h, text, facecolor="#E8F0FE", edgecolor="#1A73E8",
        fontsize=10, weight="normal"):
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                       boxstyle="round,pad=0.08,rounding_size=0.15",
                       linewidth=1.3, facecolor=facecolor, edgecolor=edgecolor)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight)

def arrow(x1, y1, x2, y2, color="#444"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", color=color,
                                 mutation_scale=16, linewidth=1.3,
                                 shrinkA=0, shrinkB=0))

# ── Main-column boxes (vertical center y values) ─────────────────────
# 7 boxes including the final green "duplicate pairs retained" box
main_top_y = 16.0
main_boxes = [
    ("MTSamples corpus\n"
     "n = 4,999 de-identified transcription samples\nacross 40 specialties"),
    ("Notes from the four AI-decision-support-\n"
     "relevant specialties: General Medicine,\n"
     "Consult–H&P, SOAP/Chart/Progress, Emergency\n(n = 1,016)"),
    "Transcription length > 200 characters\n(n = 1,007)",
    ("Clearly identifiable ASSESSMENT section,\n"
     "viable note split, outpatient visit\n(n = 315 candidate notes)"),
    "De-duplication of test–retest duplicates\n(n = 220 unique cases)",
    "Pre-registered guideline currency screen\n(n = 200 cases for primary analysis)",
    "92 duplicate pairs retained for\ntest–retest reliability assessment",  # 89 doubles + 3 triples = 92 groups (95 redundant copies)
]
main_y = [main_top_y - i * ROW_H for i in range(len(main_boxes))]

for i, (y, text) in enumerate(zip(main_y, main_boxes)):
    is_final = (i == len(main_boxes) - 1)
    box(MAIN_CX, y, MAIN_BOX_W, MAIN_BOX_H, text,
        facecolor="#F1F8E9" if is_final else "#E8F0FE",
        edgecolor="#689F38" if is_final else "#1A73E8",
        fontsize=9.5 if is_final else 10)

# Arrows between consecutive main boxes (bottom of i → top of i+1)
for i in range(len(main_boxes) - 1):
    y_src = main_y[i] - MAIN_BOX_H / 2
    y_dst = main_y[i + 1] + MAIN_BOX_H / 2
    arrow(MAIN_CX, y_src, MAIN_CX, y_dst)

# ── Exclusion boxes (centered in each inter-box gap) ─────────────────
# There are 5 exclusions, one between each pair of main steps for i = 0..4.
# Exclusion i sits in the gap between main_y[i] and main_y[i+1].
exclusions = [
    "Excluded: wrong specialty (n = 3,983)\n"
    "surgical subspecialties, radiology,\n"
    "pathology, dental, discharge summaries,\n"
    "office notes, etc.",
    "Excluded: transcription < 200 characters\n(n = 9)",
    "Excluded: no recognizable ASSESSMENT\n"
    "header, non-viable note split,\n"
    "or inpatient encounter\n(n ≈ 692)",
    "Removed: 95 test–retest duplicates\n"
    "(identical clinical text appearing 2–3 times)",
    "Removed: 20 cases with significantly\n"
    "outdated physician plans (pre-registered\n"
    "5-point rubric, two LLMs + physician reviewer,\n"
    "scored before any AI cost analysis)",
]

for i, text in enumerate(exclusions):
    gap_center_y = (main_y[i] + main_y[i + 1]) / 2
    box(EXCL_CX, gap_center_y, EXCL_BOX_W, EXCL_BOX_H, text,
        facecolor="#FFF4E5", edgecolor="#E07B00", fontsize=8.5)
    # Horizontal connector: tap off the main arrow at gap midpoint, go right
    arrow(MAIN_CX, gap_center_y, EXCL_CX - EXCL_BOX_W / 2, gap_center_y)

# ── Title ────────────────────────────────────────────────────────────
ax.text(7.0, FIG_H + 0.2, "Figure S1. Case Selection Flow",
        ha="center", fontsize=14, fontweight="bold")
ax.text(7.0, FIG_H - 0.3,
        "No case was excluded based on its content, the physician's plan, or any AI output.",
        ha="center", fontsize=9.5, style="italic", color="#555")

plt.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
print(f"saved: {OUT}")
