#!/usr/bin/env python3
"""
Prompt variants for the prompt-sensitivity experiment.

Three plan-generation prompts, applied to the same 200-case cohort and the same
extraction / Medicare-pricing / diagnostic-judge pipeline as the main study:

  - DEFAULT      : byte-identical to the original study's PLAN_PROMPT
                   (scripts/run_study.py). Used for the "default re-run" arm, which
                   anchors the within-model comparison and serves as a reproducibility
                   check against the published results/models/ figures.
  - PARSIMONIOUS : the editors' specification — name the three most likely diagnoses
                   with a per-diagnosis plan, explicitly include "can't-miss" dangerous
                   diagnoses that must not be missed, and practice resource-conscious
                   (Choosing Wisely) care.
  - COSTAWARE    : the DEFAULT prompt plus a single appended cost-aware instruction — isolates the marginal effect of a
                   one-line cost nudge from the fuller parsimonious-plus-safe framing.

These strings are frozen and quoted verbatim in Appendix 1 of the revised manuscript.
Run `python scripts/prompt_variants.py` to print them.
"""

# ---------------------------------------------------------------------------
# DEFAULT — must remain byte-identical to PLAN_PROMPT in scripts/run_study.py
# ---------------------------------------------------------------------------
PLAN_PROMPT_DEFAULT = """\
You are the physician seeing this patient in a real-world clinical setting. \
Below is the clinical note from this visit containing the history, exam findings, \
and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
{presentation}

Write the ASSESSMENT AND PLAN section now."""


# ---------------------------------------------------------------------------
# PARSIMONIOUS + SAFE — the editors' specification
#   (1) three most likely diagnoses, each with a differential plan;
#   (2) explicitly include less-likely "can't-miss" dangerous diagnoses;
#   (3) resource-constrained health system / Choosing Wisely framing.
# ---------------------------------------------------------------------------
PLAN_PROMPT_PARSIMONIOUS = """\
You are the physician seeing this patient in a real-world clinical setting that has \
LIMITED financial and technical resources: diagnostic tests, advanced imaging, and \
specialist referrals are scarce and costly and should be used only when their result \
would change management. Practice in the spirit of the Choosing Wisely campaign, \
delivering high-value, parsimonious care that avoids low-yield testing while never \
missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and \
available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, \
structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death \
or serious harm if missed, and that must therefore be actively considered or excluded \
(for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and \
management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" \
diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are \
unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them \
only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
{presentation}

Write the ASSESSMENT AND PLAN section now."""


# ---------------------------------------------------------------------------
# COST-AWARE — DEFAULT prompt + a single appended cost-aware instruction.
# Constructed from PLAN_PROMPT_DEFAULT so the two are identical except for the nudge.
# ---------------------------------------------------------------------------
_COSTAWARE_NUDGE = (
    " Order laboratory tests, imaging studies, medications, referrals, and procedures "
    "only when they are clinically necessary and cost-effective; avoid low-value care "
    "that is unlikely to change management."
)
PLAN_PROMPT_COSTAWARE = PLAN_PROMPT_DEFAULT.replace(
    "Write the ASSESSMENT AND PLAN section now.",
    "Practice cost-conscious, high-value care:" + _COSTAWARE_NUDGE
    + "\n\nWrite the ASSESSMENT AND PLAN section now.",
)


PROMPTS = {
    "default": PLAN_PROMPT_DEFAULT,
    "parsimonious": PLAN_PROMPT_PARSIMONIOUS,
    "costaware": PLAN_PROMPT_COSTAWARE,
}


if __name__ == "__main__":
    for name, tmpl in PROMPTS.items():
        print("=" * 78)
        print(f"PROMPT: {name}")
        print("=" * 78)
        print(tmpl)
        print()
