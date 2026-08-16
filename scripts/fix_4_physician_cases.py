#!/usr/bin/env python3
"""
Surgical fix for 4 physician cases where extraction missed or mis-priced orders.

Each fix is applied across ALL model files (since human_orders_a/b/c are
replicated identically in every model file).

Case-specific reasoning:

MTS_0085 — Plan: "We will get follow-up labs today. ... arrange for a
  follow-up mammogram as recommended by the radiologist in six months"
  Extractor A matched "follow-up labs" → CMP $10.56. B and C failed CPT match.
  Patient has NIDDM, HTN, CAD, hyperlipidemia, hyperuricemia, anemia.
  "Follow-up labs" for this complex patient realistically = CMP + lipid + HbA1c
  + CBC. Conservative: just propagate A's $10.56 CMP to B and C (matching
  what A captured, no inflation).

MTS_0132 — Plan: "prescribe Lipitor ... plan to do a fasting lipid panel
  and CMP approximately 8 weeks" — lipid+CMP ORDERED today for 8 weeks out.
  All 3 extractors missed both. Add lipid panel ($13.44) + CMP ($10.56) = $24.00
  to all 3 extractors.

MTS_0544 — Plan: "Will check an H&H today."
  A matched → $2.37 (85018). B and C failed. Propagate A's price.

MTS_0840 — Plan: "We will go ahead and check MRI brain, and we will get
  the films later."  Context: essential tremor + torticollis workup.
  A matched MRI brain to 70553 (with+without contrast) → $316.97.
  B and C matched to 70558 which has no price.
  "MRI brain" unspecified for tremor — standard workup is without contrast
  (70551, $192.24). Using 70551 is more clinically honest, but for
  consistency with extractor A's decision, use $316.97.
  Decision: use the more conservative 70551 → $192.24 since plan does not
  specify contrast.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models_original_runs"

FIXES = {
    "MTS_0085": {
        "note": "propagate CMP $10.56 across b/c; already in a",
        "orders": [
            {"order": "follow-up labs", "category": "labs",
             "cpt_code": "80053", "price": 10.56, "source": "manual_fix"},
        ],
    },
    "MTS_0132": {
        "note": "add missing fasting lipid + CMP (ordered today for 8-week f/u)",
        "orders": [
            {"order": "fasting lipid panel (in 8 weeks)", "category": "labs",
             "cpt_code": "80061", "price": 13.44, "source": "manual_fix"},
            {"order": "comprehensive metabolic panel (in 8 weeks)", "category": "labs",
             "cpt_code": "80053", "price": 10.56, "source": "manual_fix"},
        ],
    },
    "MTS_0544": {
        "note": "propagate H&H $2.37 across b/c; already in a",
        "orders": [
            {"order": "Hematocrit and Hemoglobin (H&H)", "category": "labs",
             "cpt_code": "85018", "price": 2.37, "source": "manual_fix"},
        ],
    },
    "MTS_0840": {
        "note": "MRI brain unspecified — use 70551 (no contrast, $192.24) for tremor workup",
        "orders": [
            {"order": "MRI brain", "category": "imaging",
             "cpt_code": "70551", "price": 192.24, "source": "manual_fix"},
        ],
    },
}


def is_test(cat: str) -> bool:
    c = (cat or "").lower()
    return ("med" not in c) and any(k in c for k in
        {"lab", "laboratory", "labs", "imaging", "test", "procedure",
         "monitoring", "diagnostic", "screening"})


def apply_fix(case: dict, fix: dict) -> None:
    """Replace human_orders_{a,b,c} test orders with the corrected set,
    keeping any medication/referral orders intact."""
    for which in ["a", "b", "c"]:
        key = f"human_orders_{which}"
        existing = case.get(key, []) or []
        # Keep non-test orders (meds, referrals, etc.)
        non_test = [o for o in existing if not is_test(o.get("category", ""))]
        # Replace test orders with fix
        case[key] = non_test + [dict(o) for o in fix["orders"]]

    # Recompute median dx cost (sum of test prices in each extractor, then median)
    totals = []
    for which in ["a", "b", "c"]:
        total = sum(float(o.get("price", 0) or 0)
                    for o in (case.get(f"human_orders_{which}") or [])
                    if is_test(o.get("category", "")))
        totals.append(total)
    case["medicare_human_dx_cost"] = round(sorted(totals)[1], 2)


def main() -> None:
    for path in sorted(MODELS.glob("m_*.json")):
        # m_human.json is an aggregate — don't touch its pre-computed stats
        if path.stem == "m_human":
            continue
        with open(path) as f:
            data = json.load(f)
        changed = 0
        for c in data:
            if c["case_id"] in FIXES:
                apply_fix(c, FIXES[c["case_id"]])
                changed += 1
        if changed:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  {path.name}: {changed} cases fixed")

    # Verify
    print("\nVerification (any model file):")
    data = json.load(open(MODELS / "m_gpt-5.2.json"))
    for cid in FIXES:
        c = [x for x in data if x["case_id"] == cid][0]
        print(f"  {cid}: new dx_cost = ${c['medicare_human_dx_cost']}  ({FIXES[cid]['note']})")


if __name__ == "__main__":
    main()
