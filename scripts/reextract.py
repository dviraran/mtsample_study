"""
Re-extract orders from stored LLM plans using the updated extraction prompt.
Does NOT regenerate LLM plans — only re-runs the extraction + repricing.

Usage:
    python reextract.py --file m_claude-sonnet-3.5.json   # single file
    python reextract.py                                     # all files
"""

import json
import os
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
]


def reextract_and_reprice(result: dict, extractor, analyzer: CostAnalyzer) -> bool:
    """Re-extract orders and re-price a single result."""
    llm_plan = result.get("llm_plan", "")
    human_ap = result.get("human_ap", "")

    if not llm_plan or not human_ap:
        return False

    # Re-extract with updated prompt
    for attempt in range(3):
        try:
            result["llm_orders_a"] = extract_orders(llm_plan, extractor)
            result["human_orders_a"] = extract_orders(human_ap, extractor)
            break
        except Exception as e:
            if "429" in str(e):
                time.sleep(2 ** attempt * 5)
            else:
                return False

    # Re-price with Medicare
    for side, orders_key, dx_key, med_key, repriced_key in [
        ("human", "human_orders_a", "medicare_human_dx_cost", "medicare_human_med_cost", "medicare_human_orders"),
        ("llm", "llm_orders_a", "medicare_llm_dx_cost", "medicare_llm_med_cost", "medicare_llm_orders"),
    ]:
        orders = result.get(orders_key, [])
        dx_total = 0
        med_total = 0
        repriced = []
        for order in orders:
            cat = order.get("category", "")
            if cat in DIAGNOSTIC_CATEGORIES:
                priced = price_order(order.get("order", ""), analyzer, category=cat)
                priced["category"] = cat
                repriced.append(priced)
                dx_total += priced["medicare_price"]
            elif cat == "medication":
                med_total += order.get("monthly_cost_usd", 0)

        result[repriced_key] = repriced
        result[dx_key] = dx_total
        result[med_key] = med_total

    # Cost ratio
    h = result["medicare_human_dx_cost"]
    l = result["medicare_llm_dx_cost"]
    result["medicare_cost_ratio"] = l / h if h > 0 else (float("inf") if l > 0 else 1.0)

    return True


def main():
    parser = ArgumentParser()
    parser.add_argument("--file", help="Single file")
    args = parser.parse_args()

    results_dir = ROOT / "results" / "models_original_runs"

    print("Loading extractor and Medicare pricing...")
    extractor = CloudLLMClient(provider="openrouter", model="openai/gpt-4.1-mini")
    analyzer = CostAnalyzer(use_mock_extractor=True)
    print("Ready.\n")

    files = [args.file] if args.file else MAIN_FILES

    for fname in files:
        f = results_dir / fname
        if not f.exists():
            continue

        with open(f) as fh:
            data = json.load(fh)
        print(f"{fname}: {len(data)} results...", end=" ", flush=True)

        done = 0
        for r in data:
            if reextract_and_reprice(r, extractor, analyzer):
                done += 1
            # Save incrementally every 10
            if done % 10 == 0:
                with tempfile.NamedTemporaryFile("w", dir=f.parent, suffix=".tmp", delete=False) as out:
                    json.dump(data, out, indent=2, default=str)
                os.replace(out.name, f)

        # Final save
        with tempfile.NamedTemporaryFile("w", dir=f.parent, suffix=".tmp", delete=False) as out:
            json.dump(data, out, indent=2, default=str)
        os.replace(out.name, f)
        print(f"{done}/{len(data)} done")

    print("\nAll re-extraction complete.")


if __name__ == "__main__":
    main()
