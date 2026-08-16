#!/usr/bin/env python3
"""
Extract and price specialist referrals from LLM cost study results.

Two-pass approach:
  1. Structured: Pull referrals already captured in orders_a (category="referral")
  2. LLM-based: Extract referrals from plan text to catch ones missed by order extraction

Only DEFINITE referrals (being placed now) are costed.
Conditional, already-seeing, and vague referrals are logged but not costed.

Usage:
    python extract_referrals.py                     # All model files
    python extract_referrals.py --file m_gpt-4.1.json
    python extract_referrals.py --dry-run           # Preview without saving
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
SIMULATIONS_DIR = ROOT / "simulations"
sys.path.insert(0, str(SIMULATIONS_DIR))

from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)

from pipeline.cloud_llm_client import CloudLLMClient

# ============================================================================
# SPECIALTY NORMALIZATION
# ============================================================================

SPECIALTY_MAP = {
    # Cardiology
    "cardiology": "Cardiology",
    "cardiac": "Cardiology",
    "electrophysiology": "Cardiology",
    "heart": "Cardiology",
    "cardiovascular": "Cardiology",
    # Dermatology
    "dermatology": "Dermatology",
    "derm": "Dermatology",
    "skin": "Dermatology",
    # Endocrinology
    "endocrinology": "Endocrinology",
    "endocrine": "Endocrinology",
    "diabetes": "Endocrinology",
    # Gastroenterology
    "gastroenterology": "Gastroenterology",
    "gi": "Gastroenterology",
    "hepatology": "Gastroenterology",
    "gastrointestinal": "Gastroenterology",
    # Hematology/Oncology
    "hematology": "Hematology/Oncology",
    "oncology": "Hematology/Oncology",
    "heme/onc": "Hematology/Oncology",
    "hematology/oncology": "Hematology/Oncology",
    "neuro-oncology": "Hematology/Oncology",
    "radiation oncology": "Hematology/Oncology",
    # Neurology
    "neurology": "Neurology",
    "neuro": "Neurology",
    "neurologist": "Neurology",
    # Neurosurgery
    "neurosurgery": "Neurosurgery",
    "neurosurgeon": "Neurosurgery",
    "brain surgery": "Neurosurgery",
    # Nutrition/Dietetics
    "nutrition": "Nutrition/Dietetics",
    "dietitian": "Nutrition/Dietetics",
    "dietetics": "Nutrition/Dietetics",
    "nutritionist": "Nutrition/Dietetics",
    "registered dietitian": "Nutrition/Dietetics",
    "rd": "Nutrition/Dietetics",
    "nutrition/dietetics": "Nutrition/Dietetics",
    "dietary": "Nutrition/Dietetics",
    # Orthopedics
    "orthopedics": "Orthopedics",
    "ortho": "Orthopedics",
    "orthopedic": "Orthopedics",
    "hand specialist": "Orthopedics",
    "hand surgery": "Orthopedics",
    "hand surgeon": "Orthopedics",
    "sports medicine": "Orthopedics",
    # Pain Management
    "pain management": "Pain Management",
    "pain specialist": "Pain Management",
    "pain clinic": "Pain Management",
    "pain medicine": "Pain Management",
    # Physical Therapy / Rehab
    "physical therapy": "Physical Therapy",
    "pt": "Physical Therapy",
    "occupational therapy": "Physical Therapy",
    "ot": "Physical Therapy",
    "rehabilitation": "Physical Therapy",
    "rehab": "Physical Therapy",
    "pm&r": "Physical Therapy",
    "physical medicine": "Physical Therapy",
    "hand therapy": "Physical Therapy",
    "pulmonary rehabilitation": "Physical Therapy",
    # Psychiatry / Behavioral Health
    "psychiatry": "Psychiatry",
    "behavioral health": "Psychiatry",
    "mental health": "Psychiatry",
    "psychology": "Psychiatry",
    "psychologist": "Psychiatry",
    "cbt-i": "Psychiatry",
    "cognitive behavioral therapy": "Psychiatry",
    "sex therapist": "Psychiatry",
    # Pulmonology
    "pulmonology": "Pulmonology",
    "pulmonary": "Pulmonology",
    "respiratory": "Pulmonology",
    # Rheumatology
    "rheumatology": "Rheumatology",
    "rheumatologist": "Rheumatology",
    # Surgery
    "surgery": "Surgery",
    "general surgery": "Surgery",
    "vascular surgery": "Surgery",
    "bariatric surgery": "Surgery",
    "bariatric": "Surgery",
    "surgical": "Surgery",
    # Urology
    "urology": "Urology",
    "urologist": "Urology",
    # Allergy/Immunology
    "allergy": "Allergy/Immunology",
    "immunology": "Allergy/Immunology",
    "allergist": "Allergy/Immunology",
    "allergy/immunology": "Allergy/Immunology",
    # ENT
    "ent": "ENT",
    "otolaryngology": "ENT",
    # Nephrology
    "nephrology": "Nephrology",
    "renal": "Nephrology",
    "nephrologist": "Nephrology",
    # Infectious Disease
    "infectious disease": "Infectious Disease",
    "id": "Infectious Disease",
    # Sleep Medicine
    "sleep medicine": "Sleep Medicine",
    "sleep specialist": "Sleep Medicine",
    "sleep": "Sleep Medicine",
    # Social Work
    "social work": "Social Work",
    "case management": "Social Work",
    "social worker": "Social Work",
    # Substance Abuse / Addiction
    "addiction medicine": "Substance Abuse",
    "otp": "Substance Abuse",
    "methadone clinic": "Substance Abuse",
    "opioid treatment program": "Substance Abuse",
    "substance abuse": "Substance Abuse",
    "addiction": "Substance Abuse",
    # Smoking Cessation
    "tobacco treatment": "Smoking Cessation",
    "smoking cessation": "Smoking Cessation",
    "quitline": "Smoking Cessation",
    # Wound/Ostomy
    "wound care": "Wound/Ostomy Care",
    "ostomy nurse": "Wound/Ostomy Care",
    "wound/ostomy": "Wound/Ostomy Care",
    # Podiatry
    "podiatry": "Podiatry",
    "podiatrist": "Podiatry",
    # Dental
    "dental": "Dental",
    "dentist": "Dental",
    # Ophthalmology
    "ophthalmology": "Ophthalmology",
    "ophthalmologist": "Ophthalmology",
    "eye": "Ophthalmology",
    # Primary Care (generally should not count as referral)
    "primary care": "Primary Care",
    "pcp": "Primary Care",
}


def normalize_specialty(raw: str) -> str:
    """Normalize a specialty string to a canonical name."""
    raw_lower = raw.lower().strip()
    # Direct match
    if raw_lower in SPECIALTY_MAP:
        return SPECIALTY_MAP[raw_lower]
    # Substring match
    for key, canonical in SPECIALTY_MAP.items():
        if key in raw_lower or raw_lower in key:
            return canonical
    return raw.strip().title()


# ============================================================================
# MEDICARE PRICING FOR REFERRALS
# ============================================================================

# A referral generates a new patient visit at the specialist.
# Specialty-specific evaluation codes where they exist; otherwise new patient E/M.
REFERRAL_PRICING = {
    # Specialty-specific evaluation codes
    "Physical Therapy":       {"cpt": "97161", "price": 97.86,  "desc": "PT evaluation low complex 20 min"},
    "Nutrition/Dietetics":    {"cpt": "97802", "price": 36.74,  "desc": "Medical nutrition therapy initial"},
    "Psychiatry":             {"cpt": "90792", "price": 202.08, "desc": "Psychiatric diagnostic eval w/ med services"},
    # Complex specialist referrals — new patient high complexity
    "Neurosurgery":           {"cpt": "99205", "price": 236.81, "desc": "Office new patient high complexity 60 min"},
    "Hematology/Oncology":    {"cpt": "99205", "price": 236.81, "desc": "Office new patient high complexity 60 min"},
    "Surgery":                {"cpt": "99205", "price": 236.81, "desc": "Office new patient high complexity 60 min"},
    # Non-physician services
    "Smoking Cessation":      {"cpt": "99407", "price": 30.00,  "desc": "Smoking cessation counseling 3-10 min"},
    "Social Work":            {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"},
    "Wound/Ostomy Care":      {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"},
    "Substance Abuse":        {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"},
    "Dental":                 {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"},
    "Primary Care":           {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"},
}

# Default: new patient moderate complexity visit
DEFAULT_REFERRAL_PRICE = {"cpt": "99204", "price": 177.36, "desc": "Office new patient moderate complexity 45 min"}


def price_referral(specialty: str) -> dict:
    """Get Medicare price for a referral to a given specialty."""
    return REFERRAL_PRICING.get(specialty, DEFAULT_REFERRAL_PRICE)


# ============================================================================
# LLM-BASED REFERRAL EXTRACTION
# ============================================================================

REFERRAL_EXTRACT_PROMPT = """\
Extract ALL specialist referrals mentioned in this clinical plan text.

For each referral, provide:
1. "specialty": The medical specialty being referred to (e.g., "Cardiology", "Physical Therapy")
2. "quote": The exact phrase from the text (keep it short, max 120 chars)
3. "type": One of:
   - "DEFINITE": Referral is being placed/ordered NOW ("Refer to cardiology", "PT evaluation ordered", "Consult neurosurgery")
   - "CONDITIONAL": Depends on future events ("If symptoms persist, refer to...", "Consider GI consult if...")
   - "ALREADY_SEEING": Continuing existing specialist care ("Continue with oncology", "Return to hematology", "Follow up with existing cardiologist")
   - "VAGUE": Non-committal ("May benefit from", "Could consider seeing")

Rules:
- "Refer to X" / "Referral to X" / "Consult X" / "X consultation" = DEFINITE
- "If/when/should [condition], refer/consult" = CONDITIONAL
- "Continue/return/follow up with [existing specialist]" = ALREADY_SEEING
- "Consider/may benefit/might want to see" = VAGUE
- Do NOT extract: follow-up with the same physician, diagnostic test orders (EMG, imaging), medication recommendations
- Do NOT count "refer for [test]" (e.g., "refer for EMG") as a specialist referral — that's a test order

Return a JSON array. If no referrals found, return [].

Text:
{plan_text}

Return ONLY the JSON array."""


def extract_referrals_llm(plan_text: str, llm: CloudLLMClient) -> list[dict]:
    """Extract referrals from plan text using LLM."""
    prompt = REFERRAL_EXTRACT_PROMPT.format(plan_text=plan_text[:3000])
    for attempt in range(5):
        try:
            response = llm.generate(prompt, max_tokens=2048, temperature=0.0)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 2 ** attempt * 5
                time.sleep(wait)
            else:
                raise

    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if text.startswith("json"):
        text = text[4:].strip()

    try:
        referrals = json.loads(text)
        if not isinstance(referrals, list):
            return []
        result = []
        for item in referrals:
            if isinstance(item, dict) and "specialty" in item:
                result.append({
                    "specialty": item.get("specialty", "Unknown"),
                    "quote": item.get("quote", "")[:150],
                    "type": item.get("type", "DEFINITE"),
                })
        return result
    except json.JSONDecodeError:
        print(f"Warning: failed to parse LLM referral response")
        return []


# ============================================================================
# MERGE STRUCTURED + LLM REFERRALS
# ============================================================================

def get_structured_referrals(orders_a: list[dict]) -> list[dict]:
    """Pull referrals already captured in orders_a with category='referral'."""
    referrals = []
    for order in orders_a:
        if order.get("category") == "referral":
            referrals.append({
                "specialty": order.get("order", "Unknown"),
                "quote": order.get("order", ""),
                "type": "DEFINITE",  # orders_a referrals are definitively ordered
                "source": "structured",
            })
    return referrals


def deduplicate_referrals(structured: list[dict], llm_extracted: list[dict]) -> list[dict]:
    """Merge structured and LLM-extracted referrals, deduplicating by specialty."""
    # Start with LLM-extracted (they have better specialty labels)
    # Add structured ones only if their specialty isn't already covered
    seen_specialties = set()
    merged = []

    for ref in llm_extracted:
        specialty = normalize_specialty(ref["specialty"])
        key = specialty.lower()
        if key not in seen_specialties:
            seen_specialties.add(key)
            merged.append({
                **ref,
                "specialty": specialty,
                "source": ref.get("source", "llm"),
            })

    for ref in structured:
        # Try to normalize the order text as a specialty
        specialty = normalize_specialty(ref["specialty"])
        key = specialty.lower()
        if key not in seen_specialties:
            seen_specialties.add(key)
            merged.append({
                **ref,
                "specialty": specialty,
                "source": "structured",
            })

    return merged


def process_referrals(orders_a: list[dict], plan_text: str, llm: CloudLLMClient) -> list[dict]:
    """Full referral extraction: structured + LLM, deduplicated and priced."""
    structured = get_structured_referrals(orders_a)
    llm_extracted = extract_referrals_llm(plan_text, llm)
    merged = deduplicate_referrals(structured, llm_extracted)

    # Price only DEFINITE referrals
    for ref in merged:
        if ref["type"] == "DEFINITE":
            pricing = price_referral(ref["specialty"])
            ref["cpt_code"] = pricing["cpt"]
            ref["medicare_price"] = pricing["price"]
            ref["cpt_description"] = pricing["desc"]
        else:
            ref["cpt_code"] = None
            ref["medicare_price"] = 0
            ref["cpt_description"] = None

    return merged


# ============================================================================
# MAIN
# ============================================================================

def process_case(case: dict, llm: CloudLLMClient) -> dict:
    """Extract and price referrals for both human and LLM plans in a case."""
    # Human referrals
    human_orders_a = case.get("human_orders_a", [])
    human_ap = case.get("human_ap", "")
    human_referrals = process_referrals(human_orders_a, human_ap, llm)

    # LLM referrals
    llm_orders_a = case.get("llm_orders_a", [])
    llm_plan = case.get("llm_plan", "")
    llm_referrals = process_referrals(llm_orders_a, llm_plan, llm)

    # Compute costs (DEFINITE only)
    human_ref_cost = sum(r["medicare_price"] for r in human_referrals if r["type"] == "DEFINITE")
    llm_ref_cost = sum(r["medicare_price"] for r in llm_referrals if r["type"] == "DEFINITE")

    human_definite = [r for r in human_referrals if r["type"] == "DEFINITE"]
    llm_definite = [r for r in llm_referrals if r["type"] == "DEFINITE"]

    return {
        "human_referrals": human_referrals,
        "llm_referrals": llm_referrals,
        "human_referral_cost": human_ref_cost,
        "llm_referral_cost": llm_ref_cost,
        "human_referral_count": len(human_definite),
        "llm_referral_count": len(llm_definite),
    }


def main():
    parser = ArgumentParser(description="Extract and price referrals from LLM cost study results")
    parser.add_argument("--file", help="Single result file (e.g., m_gpt-4.1.json)")
    parser.add_argument("--dir", default="results/models",
                        help="results dir with m_*.json (e.g. results/models or results/models_parsimonious)")
    parser.add_argument("--models", help="comma-separated model keys (default: all m_*.json in dir)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--force", action="store_true", help="Re-extract even if already done")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers")
    args = parser.parse_args()

    results_dir = (ROOT / args.dir) if not os.path.isabs(args.dir) else Path(args.dir)

    # Initialize extraction LLM
    print("Initializing extraction LLM (GPT-4.1-mini)...")
    llm = CloudLLMClient(provider="openai", model="gpt-4.1-mini")

    if args.file:
        files = [results_dir / args.file]
    elif args.models:
        files = [results_dir / f"m_{m.strip()}.json" for m in args.models.split(",")]
    else:
        files = sorted(results_dir.glob("m_*.json"))

    grand_stats = {}

    for f in files:
        if not f.exists():
            print(f"  {f.name}: not found, skipping")
            continue

        try:
            with open(f) as fh:
                results = json.load(fh)
        except Exception:
            print(f"  {f.name}: corrupt JSON, skipping")
            continue

        n = len(results)
        model_name = results[0].get("model", f.stem) if results else f.stem
        print(f"\n{'='*70}")
        print(f"{f.name}: {n} cases (model: {model_name})")
        print(f"{'='*70}")

        # Check if already done (key on llm_referrals, the field THIS script produces;
        # human_referrals may already be present from the cohort copy in arm files)
        if not args.force and results and "llm_referrals" in results[0]:
            already = sum(1 for r in results if "llm_referrals" in r)
            print(f"  Already processed ({already}/{n}). Use --force to re-extract.")
            # Still collect stats
            for r in results:
                if "human_referral_cost" in r:
                    if model_name not in grand_stats:
                        grand_stats[model_name] = {
                            "n": 0, "human_ref_cost": 0, "llm_ref_cost": 0,
                            "human_ref_count": 0, "llm_ref_count": 0,
                        }
                    grand_stats[model_name]["n"] += 1
                    grand_stats[model_name]["human_ref_cost"] += r.get("human_referral_cost", 0)
                    grand_stats[model_name]["llm_ref_cost"] += r.get("llm_referral_cost", 0)
                    grand_stats[model_name]["human_ref_count"] += r.get("human_referral_count", 0)
                    grand_stats[model_name]["llm_ref_count"] += r.get("llm_referral_count", 0)
            continue

        # Process cases with parallelism
        processed = 0
        errors = 0

        def process_one(idx_case):
            idx, case = idx_case
            try:
                return idx, process_case(case, llm)
            except Exception as e:
                return idx, {"error": str(e)}

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_one, (i, r)): i for i, r in enumerate(results)}
            for future in as_completed(futures):
                idx, ref_data = future.result()
                if "error" in ref_data:
                    errors += 1
                    print(f"  [{idx+1}/{n}] ERROR: {ref_data['error']}")
                    continue

                results[idx].update(ref_data)
                processed += 1

                # Progress
                if processed % 20 == 0 or processed == n:
                    case = results[idx]
                    h_count = ref_data["human_referral_count"]
                    l_count = ref_data["llm_referral_count"]
                    h_cost = ref_data["human_referral_cost"]
                    l_cost = ref_data["llm_referral_cost"]
                    print(f"  [{processed}/{n}] {case['case_id']}: human={h_count} referrals (${h_cost:.0f}), llm={l_count} (${l_cost:.0f})")

        print(f"\n  Done: {processed} processed, {errors} errors")

        # Collect stats
        if model_name not in grand_stats:
            grand_stats[model_name] = {
                "n": 0, "human_ref_cost": 0, "llm_ref_cost": 0,
                "human_ref_count": 0, "llm_ref_count": 0,
            }
        for r in results:
            if "human_referral_cost" in r:
                grand_stats[model_name]["n"] += 1
                grand_stats[model_name]["human_ref_cost"] += r.get("human_referral_cost", 0)
                grand_stats[model_name]["llm_ref_cost"] += r.get("llm_referral_cost", 0)
                grand_stats[model_name]["human_ref_count"] += r.get("human_referral_count", 0)
                grand_stats[model_name]["llm_ref_count"] += r.get("llm_referral_count", 0)

        # Save
        if not args.dry_run:
            tmp_fd = tempfile.NamedTemporaryFile(
                mode="w", dir=f.parent, suffix=".tmp", delete=False
            )
            try:
                json.dump(results, tmp_fd, indent=2, default=str)
                tmp_fd.close()
                os.replace(tmp_fd.name, f)
            except BaseException:
                tmp_fd.close()
                os.unlink(tmp_fd.name)
                raise
            print(f"  Saved to {f.name}")
        else:
            print(f"  [DRY RUN] Would save to {f.name}")

    # Print grand summary
    print(f"\n{'='*70}")
    print("REFERRAL COST SUMMARY")
    print(f"{'='*70}")
    print(f"{'Model':<25s} {'N':>4s} {'Avg H$':>8s} {'Avg L$':>8s} {'Excess':>8s} {'H Refs':>7s} {'L Refs':>7s} {'Ratio':>7s}")
    print(f"{'-'*25} {'-'*4} {'-'*8} {'-'*8} {'-'*8} {'-'*7} {'-'*7} {'-'*7}")

    for model in sorted(grand_stats.keys()):
        s = grand_stats[model]
        n = s["n"]
        if n == 0:
            continue
        avg_h = s["human_ref_cost"] / n
        avg_l = s["llm_ref_cost"] / n
        excess = avg_l - avg_h
        h_refs = s["human_ref_count"] / n
        l_refs = s["llm_ref_count"] / n
        ratio = avg_l / avg_h if avg_h > 0 else float("inf")
        print(f"{model:<25s} {n:>4d} ${avg_h:>6.0f} ${avg_l:>6.0f} ${excess:>6.0f} {h_refs:>6.2f} {l_refs:>6.2f} {ratio:>6.2f}x")


if __name__ == "__main__":
    main()
