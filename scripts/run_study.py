#!/usr/bin/env python3
"""
LLM Cost Dynamics Study — Direct Note Completion.

For each clinical note with a PLAN section:
1. Split the note into PRESENTATION (everything before PLAN) and HUMAN_PLAN
2. Give the LLM the PRESENTATION and ask it to write a PLAN
3. Extract and price diagnostic orders from both plans
4. Compare costs

No simulation engine needed — same input, compare output.

Usage:
    python run_study.py                        # 10 cases, 3 models
    python run_study.py --limit 50             # 50 cases
    python run_study.py --model claude-sonnet   # single model
    python run_study.py --list                 # preview available cases
"""

import json
import sys
import os
import re
import time
import fcntl
import tempfile
from pathlib import Path
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
SIMULATIONS_DIR = ROOT / "simulations"
sys.path.insert(0, str(SIMULATIONS_DIR))

from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)

from pipeline.cloud_llm_client import CloudLLMClient
from pipeline.utils.cpt_lookup import lookup_cpt

MODELS = {
    # OpenAI:       old → new
    "gpt-4.1": ("openrouter", "openai/gpt-4.1"),
    "gpt-5.2": ("openrouter", "openai/gpt-5.2"),
    # Anthropic:    old → new
    "claude-sonnet-3.5": ("openrouter", "anthropic/claude-3.5-sonnet"),
    "claude-sonnet-4.5": ("openrouter", "anthropic/claude-sonnet-4.5"),
    # Google:       old → new
    "gemini-2.5-pro": ("openrouter", "google/gemini-2.5-pro"),
    "gemini-3-pro": ("openrouter", "google/gemini-3-pro-preview"),
    # xAI:          old → new
    "grok-3": ("openrouter", "x-ai/grok-3"),
    "grok-4.1": ("openrouter", "x-ai/grok-4.1-fast"),
    # Meta:         old → new
    "llama-3.3-70b": ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
    "llama4": ("openrouter", "meta-llama/llama-4-maverick"),
    # Qwen:         old → new
    "qwen-2.5-72b": ("openrouter", "qwen/qwen-2.5-72b-instruct"),
    "qwen3": ("openrouter", "qwen/qwen3-235b-a22b"),
    # DeepSeek:     old → new
    "deepseek-r1": ("openrouter", "deepseek/deepseek-r1"),
    "deepseek-v3.2": ("openrouter", "deepseek/deepseek-chat-v3-0324"),
    # Medical LLMs
    "medgemma-4b": ("dr7", "medgemma-4b-it"),
    "meditron": ("dr7", "meditron"),
}

PLAN_PROMPT = """\
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

EXTRACT_PROMPT = """\
Extract individual medical orders that the physician is DEFINITELY placing NOW from this clinical assessment and plan.
Return a JSON array of objects with "order", "category", and for medications include "monthly_cost_usd" (estimated US retail cost for a 30-day supply of the generic version).

Categories: "labs", "imaging", "procedure", "exam", "monitoring", "medication", "referral", "follow_up", "other"

ONLY extract orders the physician is definitively placing. Do NOT extract:
- Records requests ("obtain previous results", "get records from", "fax report", "review prior imaging")
- Conditional/contingent orders ("consider if", "may need if", "if symptoms persist", "if not already done", "if indicated")
- Medication management of EXISTING medications ("continue", "hold", "titrate", "adjust dose", "maintain current", "taper", "wean", "resume", "keep on")
- Dose adjustments to existing medications ("increase dose", "reduce dose", "decrease to", "uptitrate", "change dose")
- Medication discontinuations ("discontinue", "stop", "hold", "d/c")
- Past results being reported ("showed", "negative for", "was normal", "revealed", "demonstrated")
- Patient education ("counsel patient", "educate", "advise on", "instruct on lifestyle")
- Monitoring instructions without a specific test ("watch for", "monitor for signs of", "observe for")
- Follow-up scheduling ("follow up in 2 weeks", "return in", "recheck in", "schedule appointment")
- One-time administrations already given during the visit ("immunizations given today", "administered in office", "injected today")
- IV fluids and inpatient-only treatments ("IV fluids", "heparin drip", "IV normal saline") — these are not outpatient prescriptions

For truly NEW outpatient medication prescriptions only, DO extract them with monthly_cost_usd as the outpatient retail cost for a 30-day supply.
For vaccines: only extract if being ORDERED for future administration, not if already given. Use the one-time cost, not monthly.
For specific monitoring tests (e.g., "daily CBC", "blood pressure check"), DO extract them.

Text:
{plan_text}

Return ONLY a JSON array. Example:
[{{"order": "CBC", "category": "labs"}}, {{"order": "Chest X-ray", "category": "imaging"}}, {{"order": "Lisinopril 10mg daily", "category": "medication", "monthly_cost_usd": 4}}]"""

DIAGNOSIS_EXTRACT_PROMPT = """\
Extract the primary diagnosis or assessment from this clinical assessment and plan section.
Return a JSON object with:
- "diagnoses": array of diagnosis strings (most important first)
- "summary": one-sentence clinical impression

Text:
{ap_text}

Return ONLY the JSON object."""

DIAGNOSTIC_CATEGORIES = {"labs", "imaging", "procedure", "exam", "monitoring"}

# Filter out inpatient/hospital notes — we want office visits only
INPATIENT_MARKERS = [
    "postoperative", "post-op", "pod #", "pod#", "day #", "day#",
    "admitted", "discharge summary", "inpatient", "icu ",
    "hospital day", "postoperative day",
]


# ============================================================================
# NOTE SPLITTING
# ============================================================================

SPLIT_MARKERS = [
    "ASSESSMENT AND PLAN:",
    "ASSESSMENT/PLAN:",
    "ASSESSMENT:",
    "A/P:",
]


def split_note(text: str):
    """Split a clinical note into (presentation, assessment_and_plan).

    Splits at the ASSESSMENT section so the LLM must produce both
    the assessment/diagnosis AND the plan — same as the human doctor.
    """
    text_upper = text.upper()
    for marker in SPLIT_MARKERS:
        idx = text_upper.find(marker)
        if idx >= 0:
            presentation = text[:idx].strip()
            assessment_plan = text[idx:].strip()
            if len(presentation) > 100 and len(assessment_plan) > 20:
                return presentation, assessment_plan
    return None


# ============================================================================
# DATA LOADING
# ============================================================================

def load_cases(limit: int = None, start: int = 0) -> list[dict]:
    """Load cases from existing result files (already processed 315 cases)."""
    results_dir = ROOT / "results" / "models_original_runs"

    # Try CSV first, fall back to existing results
    csv_path = SIMULATIONS_DIR / "case-data" / "mtsamples" / "raw" / "mtsamples.csv"
    if csv_path.exists():
        import pandas as pd
        df = pd.read_csv(csv_path)
        df["medical_specialty"] = df["medical_specialty"].str.strip()
        pc_specs = [
            "General Medicine",
            "Consult - History and Phy.",
            "SOAP / Chart / Progress Notes",
            "Emergency Room Reports",
        ]
        filtered = df[df["medical_specialty"].isin(pc_specs)]
        filtered = filtered[filtered["transcription"].str.len() > 200].reset_index(drop=True)
        cases = []
        for idx, row in filtered.iterrows():
            result = split_note(row["transcription"])
            if result is None:
                continue
            presentation, plan = result
            combined = (presentation + " " + row.get("sample_name", "")).lower()
            if any(marker in combined for marker in INPATIENT_MARKERS):
                continue
            cases.append({
                "case_id": f"MTS_{idx:04d}",
                "sample_name": row.get("sample_name", "").strip(),
                "specialty": row["medical_specialty"],
                "presentation": presentation,
                "human_ap": plan,
                "full_text": row["transcription"],
            })
    else:
        # Load from existing result files
        ref_file = None
        for f in sorted(results_dir.glob("m_*.json")):
            if f.stat().st_size > 100000:
                ref_file = f
                break
        if ref_file is None:
            raise FileNotFoundError("No CSV or existing result files found to load cases from")
        with open(ref_file) as f:
            ref_results = json.load(f)
        seen = set()
        cases = []
        for r in ref_results:
            cid = r["case_id"]
            if cid in seen:
                continue
            seen.add(cid)
            cases.append({
                "case_id": cid,
                "sample_name": r.get("sample_name", ""),
                "specialty": r.get("specialty", ""),
                "presentation": r["presentation"],
                "human_ap": r["human_ap"],
            })

    # Flag duplicates as test-retest pairs
    seen_ap = {}
    for c in cases:
        key = c["human_ap"][:200]
        if key in seen_ap:
            c["is_retest"] = True
            c["retest_of"] = seen_ap[key]
        else:
            seen_ap[key] = c["case_id"]
            c["is_retest"] = False
            c["retest_of"] = None

    cases = cases[start:]
    if limit:
        cases = cases[:limit]
    return cases


# ============================================================================
# LLM PLAN GENERATION
# ============================================================================

def generate_plan(presentation: str, provider: str, model: str) -> str:
    """Ask an LLM to write a PLAN given the presentation."""
    llm = CloudLLMClient(provider=provider, model=model)
    prompt = PLAN_PROMPT.format(presentation=presentation)
    for attempt in range(5):
        try:
            return llm.generate(prompt, max_tokens=4096, temperature=0.3)
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 2 ** attempt * 5
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


# ============================================================================
# ORDER EXTRACTION & PRICING
# ============================================================================

def extract_orders(plan_text: str, llm: CloudLLMClient) -> list[dict]:
    """Extract categorized orders from a plan using LLM."""
    prompt = EXTRACT_PROMPT.format(plan_text=plan_text)
    for attempt in range(5):
        try:
            response = llm.generate(prompt)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 2 ** attempt * 5
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if text.startswith("json"):
        text = text[4:].strip()

    try:
        orders = json.loads(text)
        if not isinstance(orders, list):
            return []
        result = []
        for item in orders:
            if isinstance(item, str):
                result.append({"order": item, "category": "other"})
            elif isinstance(item, dict):
                entry = {
                    "order": item.get("order", ""),
                    "category": item.get("category", "other"),
                }
                if item.get("monthly_cost_usd") is not None:
                    try:
                        entry["monthly_cost_usd"] = float(item["monthly_cost_usd"])
                    except (ValueError, TypeError):
                        pass
                result.append(entry)
        return result
    except json.JSONDecodeError:
        print(f"Warning: failed to parse LLM response")
        return []


def extract_diagnoses(ap_text: str, llm: CloudLLMClient) -> dict:
    """Extract diagnoses from an assessment & plan section."""
    prompt = DIAGNOSIS_EXTRACT_PROMPT.format(ap_text=ap_text[:2000])
    for attempt in range(5):
        try:
            response = llm.generate(prompt)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 2 ** attempt * 5
                time.sleep(wait)
            else:
                return {"diagnoses": [], "summary": ""}

    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if text.startswith("json"):
        text = text[4:].strip()

    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return {
                "diagnoses": result.get("diagnoses", []),
                "summary": result.get("summary", ""),
            }
    except json.JSONDecodeError:
        print(f"Warning: failed to parse LLM response for diagnosis extraction")
    return {"diagnoses": [], "summary": ""}


def price_orders(orders: list[dict], llm: CloudLLMClient) -> list[dict]:
    """Price orders via CPT lookup (rule-based + LLM fallback). Returns diagnostic only."""
    dx_orders = [o for o in orders if o["category"] in DIAGNOSTIC_CATEGORIES]
    priced = []
    for o in dx_orders:
        result = lookup_cpt(o["order"]) or lookup_cpt(o["order"], use_llm=True, llm_client=llm)
        if result:
            priced.append({
                **o,
                "cpt_code": result["cpt_code"],
                "price": result["price"],
                "source": result.get("source", "unknown"),
            })
        else:
            priced.append({**o, "cpt_code": None, "price": 0, "source": "unmatched"})
    return priced


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = ArgumentParser(description="LLM Cost Dynamics — Direct Note Completion Study")
    parser.add_argument("--limit", type=int, default=10, help="Number of cases")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--model", help="Single model (default: all 3)")
    parser.add_argument("--list", action="store_true", help="Preview cases and exit")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers per model")
    parser.add_argument("--output", default="note_completion_results.json", help="Output filename")
    args = parser.parse_args()

    cases = load_cases(limit=args.limit, start=args.start)
    print(f"Loaded {len(cases)} cases with PLAN sections\n")

    if args.list:
        for c in cases:
            plan_preview = c["human_ap"][:80].replace("\n", " ")
            print(f"  {c['case_id']:10s} {c['sample_name'][:35]:35s} | {plan_preview}")
        return

    models = {args.model: MODELS[args.model]} if args.model else MODELS
    # Triple extractors for inter-rater reliability (use median)
    extractor_a = CloudLLMClient(provider="openai", model="gpt-4.1-mini")
    extractor_b = CloudLLMClient(provider="openrouter", model="anthropic/claude-haiku-4.5")
    extractor_c = CloudLLMClient(provider="openrouter", model="google/gemini-2.0-flash-001")

    # Load existing results to skip completed case+model pairs
    output_file = ROOT / "results" / "analysis" / args.output
    all_results = []
    done_pairs = set()
    if output_file.exists():
        try:
            with open(output_file) as fh:
                all_results = json.load(fh)
            done_pairs = {(r["case_id"], r["model"]) for r in all_results}
            print(f"Resuming: {len(done_pairs)} case-model pairs already done")
        except (json.JSONDecodeError, OSError, Exception) as e:
            print(f"Warning: could not load checkpoint: {e}")

    for case in cases:
        case_id = case["case_id"]

        # Re-read done pairs (another worker may have updated)
        if output_file.exists():
            try:
                with open(output_file) as fh:
                    done_pairs = {(r["case_id"], r["model"]) for r in json.load(fh)}
            except (json.JSONDecodeError, OSError, Exception) as e:
                print(f"Warning: could not load checkpoint: {e}")
        # Skip if all models for this case are done
        models_todo = {m: v for m, v in models.items() if (case_id, m) not in done_pairs}
        if not models_todo:
            continue

        print(f"{'─'*70}")
        print(f"{case_id}: {case['sample_name'][:50]} ({len(models_todo)} models remaining)")

        # Extract human diagnosis
        human_dx_info = extract_diagnoses(case["human_ap"], extractor_a)
        print(f"  Human dx: {', '.join(human_dx_info['diagnoses'][:3])}")

        # Extract and price HUMAN plan — triple extraction, take median
        human_orders_a = extract_orders(case["human_ap"], extractor_a)
        human_orders_b = extract_orders(case["human_ap"], extractor_b)
        human_orders_c = extract_orders(case["human_ap"], extractor_c)
        human_priced_a = price_orders(human_orders_a, extractor_a)
        human_priced_b = price_orders(human_orders_b, extractor_b)
        human_priced_c = price_orders(human_orders_c, extractor_c)
        human_dx_cost_a = sum(o["price"] for o in human_priced_a)
        human_dx_cost_b = sum(o["price"] for o in human_priced_b)
        human_dx_cost_c = sum(o["price"] for o in human_priced_c)
        human_dx_cost = sorted([human_dx_cost_a, human_dx_cost_b, human_dx_cost_c])[1]  # median
        human_all_count = len(human_orders_a)
        human_med_costs = sorted([
            sum(o.get("monthly_cost_usd", 0) for o in human_orders_a if o["category"] == "medication"),
            sum(o.get("monthly_cost_usd", 0) for o in human_orders_b if o["category"] == "medication"),
            sum(o.get("monthly_cost_usd", 0) for o in human_orders_c if o["category"] == "medication"),
        ])
        human_med_cost = human_med_costs[1]  # median

        print(f"  Human: dx=${human_dx_cost:.0f} med=${human_med_cost:.0f} (A:${human_dx_cost_a:.0f} B:${human_dx_cost_b:.0f} C:${human_dx_cost_c:.0f})")

        # Generate and price LLM plans
        for model_name, (provider, model_id) in models_todo.items():
            print(f"  {model_name}...")
            try:
                llm_plan = generate_plan(case["presentation"], provider, model_id)
                if not llm_plan:
                    print(f"    Empty response — skipping")
                    continue
            except Exception as e:
                print(f"    ERROR: {e}")
                continue

            # Extract LLM diagnosis
            llm_dx_info = extract_diagnoses(llm_plan, extractor_a)
            print(f"    Dx: {', '.join(llm_dx_info['diagnoses'][:3])}")

            # Triple extraction for LLM orders, take median
            llm_orders_a = extract_orders(llm_plan, extractor_a)
            llm_orders_b = extract_orders(llm_plan, extractor_b)
            llm_orders_c = extract_orders(llm_plan, extractor_c)
            llm_priced_a = price_orders(llm_orders_a, extractor_a)
            llm_priced_b = price_orders(llm_orders_b, extractor_b)
            llm_priced_c = price_orders(llm_orders_c, extractor_c)
            llm_dx_cost_a = sum(o["price"] for o in llm_priced_a)
            llm_dx_cost_b = sum(o["price"] for o in llm_priced_b)
            llm_dx_cost_c = sum(o["price"] for o in llm_priced_c)
            llm_dx_cost = sorted([llm_dx_cost_a, llm_dx_cost_b, llm_dx_cost_c])[1]  # median
            llm_all_count = len(llm_orders_a)
            # Medication costs (median of 3 extractors)
            llm_med_costs = sorted([
                sum(o.get("monthly_cost_usd", 0) for o in llm_orders_a if o["category"] == "medication"),
                sum(o.get("monthly_cost_usd", 0) for o in llm_orders_b if o["category"] == "medication"),
                sum(o.get("monthly_cost_usd", 0) for o in llm_orders_c if o["category"] == "medication"),
            ])
            llm_med_cost = llm_med_costs[1]  # median

            ratio = llm_dx_cost / human_dx_cost if human_dx_cost > 0 else (
                float("inf") if llm_dx_cost > 0 else 1.0
            )

            print(f"    A:${llm_dx_cost_a:.0f} B:${llm_dx_cost_b:.0f} C:${llm_dx_cost_c:.0f} → median ${llm_dx_cost:.0f} (ratio: {ratio:.2f}x)")

            all_results.append({
                "case_id": case_id,
                "sample_name": case["sample_name"],
                "specialty": case.get("specialty", ""),
                "presentation": case["presentation"],
                "model": model_name,
                "human_ap": case["human_ap"],
                "human_diagnoses": human_dx_info["diagnoses"],
                "human_dx_summary": human_dx_info["summary"],
                "human_orders_a": human_priced_a,
                "human_orders_b": human_priced_b,
                "human_orders_c": human_priced_c,
                "human_dx_cost_a": human_dx_cost_a,
                "human_dx_cost_b": human_dx_cost_b,
                "human_dx_cost_c": human_dx_cost_c,
                "human_dx_cost": human_dx_cost,
                "human_med_cost": human_med_cost,
                "human_all_count": human_all_count,
                "llm_plan": llm_plan,
                "llm_diagnoses": llm_dx_info["diagnoses"],
                "llm_dx_summary": llm_dx_info["summary"],
                "llm_orders_a": llm_priced_a,
                "llm_orders_b": llm_priced_b,
                "llm_orders_c": llm_priced_c,
                "llm_dx_cost_a": llm_dx_cost_a,
                "llm_dx_cost_b": llm_dx_cost_b,
                "llm_dx_cost_c": llm_dx_cost_c,
                "llm_dx_cost": llm_dx_cost,
                "llm_med_cost": llm_med_cost,
                "llm_all_count": llm_all_count,
                "cost_ratio": ratio,
            })

        # Incremental save after each case — atomic read-merge-write with lock
        output_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file = output_file.with_suffix(".lock")
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                # Re-read file AFTER acquiring lock (another worker may have written)
                existing = {}
                if output_file.exists():
                    try:
                        with open(output_file) as fh:
                            for r in json.load(fh):
                                existing[(r["case_id"], r["model"])] = r
                    except (json.JSONDecodeError, OSError, Exception) as e:
                        print(f"Warning: could not load checkpoint: {e}")
                # Merge our results
                for r in all_results:
                    existing[(r["case_id"], r["model"])] = r
                # Atomic write: write to temp file then replace
                fd, tmp_path = tempfile.mkstemp(
                    dir=str(output_file.parent), suffix=".tmp"
                )
                try:
                    with os.fdopen(fd, "w") as tmp_f:
                        json.dump(list(existing.values()), tmp_f, indent=2, default=str)
                    os.replace(tmp_path, str(output_file))
                except BaseException:
                    os.unlink(tmp_path)
                    raise
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

    # ========================================
    # SUMMARY
    # ========================================
    if not all_results:
        print("\nNo results.")
        return

    print(f"\n{'='*70}")
    print("RESULTS — DIAGNOSTIC ORDERS ONLY")
    print(f"{'='*70}")

    print(f"\n{'Case':<12} {'Model':<18} {'LLM$':>7} {'Human$':>8} {'Ratio':>7}")
    print("─" * 55)
    for r in sorted(all_results, key=lambda x: (x["case_id"], x["model"])):
        ratio_str = f"{r['cost_ratio']:.2f}x" if r["cost_ratio"] != float("inf") else "  inf"
        print(f"{r['case_id']:<12} {r['model']:<18} ${r['llm_dx_cost']:>5.0f} "
              f"${r['human_dx_cost']:>6.0f} {ratio_str:>7}")

    # Model averages
    print(f"\n{'Model':<18} {'Avg LLM$':>9} {'Avg Human$':>11} {'Median Ratio':>13} {'N':>4}")
    print("─" * 58)
    by_model = {}
    for r in all_results:
        by_model.setdefault(r["model"], []).append(r)

    for model, comps in sorted(by_model.items()):
        avg_llm = sum(c["llm_dx_cost"] for c in comps) / len(comps)
        avg_human = sum(c["human_dx_cost"] for c in comps) / len(comps)
        finite_ratios = [c["cost_ratio"] for c in comps
                        if c["cost_ratio"] != float("inf") and c["human_dx_cost"] > 0]
        if finite_ratios:
            finite_ratios.sort()
            median_ratio = finite_ratios[len(finite_ratios) // 2]
        else:
            median_ratio = 0
        print(f"{model:<18} ${avg_llm:>7.0f} ${avg_human:>9.0f} {median_ratio:>12.2f}x {len(comps):>4}")

    # Over-ordering breakdown
    print(f"\n{'Model':<18} {'Added tests':>12} {'Matched':>9} {'Fewer tests':>12} {'Avg added$':>11}")
    print("─" * 65)
    for model, comps in sorted(by_model.items()):
        added = sum(1 for c in comps if c["llm_dx_cost"] > c["human_dx_cost"])
        matched = sum(1 for c in comps if c["llm_dx_cost"] == c["human_dx_cost"])
        fewer = sum(1 for c in comps if c["llm_dx_cost"] < c["human_dx_cost"])
        excess = [c["llm_dx_cost"] - c["human_dx_cost"] for c in comps if c["llm_dx_cost"] > c["human_dx_cost"]]
        avg_excess = sum(excess) / len(excess) if excess else 0
        print(f"{model:<18} {added:>12} {matched:>9} {fewer:>12} ${avg_excess:>9.0f}")

    # Cost impact projection
    print(f"\n{'='*70}")
    print("COST IMPACT PROJECTION")
    print(f"{'='*70}")
    all_excess = [r["llm_dx_cost"] - r["human_dx_cost"] for r in all_results]
    avg_excess_per_visit = sum(all_excess) / len(all_excess) if all_excess else 0
    print(f"  Avg excess diagnostic cost per visit: ${avg_excess_per_visit:.2f}")
    print(f"  At 1M AI-influenced visits/year:      ${avg_excess_per_visit * 1_000_000:,.0f}")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
