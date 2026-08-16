"""
Re-extract orders B and C from stored LLM plans using the updated extraction prompt.
This gives us 3 independent extractions (A already done by reextract.py) for median-of-3.

Usage:
    python reextract_bc.py                                # all files
    python reextract_bc.py --file m_gpt-4.1.json          # single file
    python reextract_bc.py --file m_gpt-4.1.json --slot c # just extractor C
"""

import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from argparse import ArgumentParser

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "simulations"))
sys.path.insert(0, str(ROOT.parent / "malpractice"))

from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)

from pipeline.cloud_llm_client import CloudLLMClient
from cost.analyzer import CostAnalyzer
from run_study import extract_orders, DIAGNOSTIC_CATEGORIES
from reprice_medicare import price_order


MAIN_FILES = [
    'm_claude-sonnet-3.5.json', 'm_claude-sonnet-4.5.json',
    'm_gemini-2.5-pro.json', 'm_gemini-3-pro.json',
    'm_gpt-4.1.json', 'm_gpt-5.2.json',
    'm_grok-3.json', 'm_grok-4.1.json',
    'm_llama-3.3-70b.json', 'm_llama4.json',
    'm_qwen-2.5-72b.json', 'm_qwen3.json',
    'm_deepseek-r1.json', 'm_deepseek-v3.2.json',
    'm_medgemma-4b.json',
    'm_meditron.json',
    'm_openevidence.json',
]


def extract_and_price_slot(result: dict, slot: str, extractor, analyzer: CostAnalyzer) -> bool:
    """Re-extract orders for slot B or C and price with Medicare."""
    llm_plan = result.get("llm_plan", "")
    human_ap = result.get("human_ap", "")

    if not llm_plan and not human_ap:
        return False

    orders_key_h = f"human_orders_{slot}"
    orders_key_l = f"llm_orders_{slot}"

    # Extract with retries
    for attempt in range(5):
        try:
            if human_ap:
                result[orders_key_h] = extract_orders(human_ap, extractor)
            if llm_plan:
                result[orders_key_l] = extract_orders(llm_plan, extractor)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 2 ** attempt * 5
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    ERROR: {e}")
                return False

    # Price medications from this slot
    for side, orders_key in [("human", orders_key_h), ("llm", orders_key_l)]:
        orders = result.get(orders_key, [])
        dx_total = 0
        med_total = 0
        for order in orders:
            cat = order.get("category", "")
            if cat in DIAGNOSTIC_CATEGORIES:
                priced = price_order(order.get("order", ""), analyzer, category=cat)
                order["cpt_code"] = priced.get("cpt_code")
                order["price"] = priced.get("medicare_price", 0)
                order["source"] = priced.get("match_method", "")
                dx_total += priced.get("medicare_price", 0)
            elif cat == "medication":
                med_total += order.get("monthly_cost_usd", 0)

        # Store per-slot costs for later median calculation
        result[f"{side}_dx_cost_{slot}"] = dx_total
        result[f"{side}_med_cost_{slot}"] = med_total

    return True


def update_medicare_median(result: dict):
    """Recompute medicare costs as median of slots A, B, C."""
    for side in ["human", "llm"]:
        for cost_type in ["dx", "med"]:
            costs = []
            for slot in ["a", "b", "c"]:
                key = f"{side}_{cost_type}_cost_{slot}"
                val = result.get(key)
                if val is not None:
                    costs.append(float(val))

            if len(costs) >= 2:
                median_val = statistics.median(costs)
                result[f"medicare_{side}_{cost_type}_cost"] = median_val

    # Update ratio
    h = result.get("medicare_human_dx_cost", 0)
    l = result.get("medicare_llm_dx_cost", 0)
    result["medicare_cost_ratio"] = l / h if h > 0 else (float("inf") if l > 0 else 1.0)


def main():
    parser = ArgumentParser()
    parser.add_argument("--file", help="Single file to process")
    parser.add_argument("--slot", choices=["a", "b", "c", "bc", "abc"], default="bc",
                        help="Which slot(s) to re-extract")
    args = parser.parse_args()

    results_dir = ROOT / "results" / "models_original_runs"

    print("Loading extractor and Medicare pricing...")
    extractor = CloudLLMClient(provider="openrouter", model="openai/gpt-4.1-mini")
    analyzer = CostAnalyzer(use_mock_extractor=True)
    # Warm up RAG index
    analyzer.rag.search("CBC", top_k=1, threshold=0.5)
    print("Ready.\n")

    slots = list(args.slot)  # "bc" -> ["b", "c"]
    files = [args.file] if args.file else MAIN_FILES

    for fname in files:
        f = results_dir / fname
        if not f.exists():
            print(f"  {fname}: NOT FOUND, skipping")
            continue

        with open(f) as fh:
            data = json.load(fh)
        print(f"{fname}: {len(data)} results")

        for slot in slots:
            print(f"  Extracting slot {slot.upper()}...", flush=True)
            done = 0
            for i, r in enumerate(data):
                if extract_and_price_slot(r, slot, extractor, analyzer):
                    done += 1

                # Progress + incremental save every 20
                if (i + 1) % 20 == 0:
                    print(f"    {i+1}/{len(data)}...", flush=True)
                    with tempfile.NamedTemporaryFile("w", dir=f.parent, suffix=".tmp", delete=False) as out:
                        json.dump(data, out, indent=2, default=str)
                    os.replace(out.name, f)

            print(f"    {done}/{len(data)} extracted")

        # Now compute median of A, B, C for all
        print(f"  Computing median costs...", flush=True)
        for r in data:
            update_medicare_median(r)

        # Final save
        with tempfile.NamedTemporaryFile("w", dir=f.parent, suffix=".tmp", delete=False) as out:
            json.dump(data, out, indent=2, default=str)
        os.replace(out.name, f)
        print(f"  Saved.\n")

    print("All re-extraction complete.")


if __name__ == "__main__":
    main()
