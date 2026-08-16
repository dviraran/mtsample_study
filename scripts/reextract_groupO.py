#!/usr/bin/env python3
"""
Re-extract the "Group O" standard-prompt systems for the unified panel.

Group O = systems that were NOT re-run under the new prompt arms because they are
either withdrawn from their API (Claude 3.5 Sonnet, the original Gemini 3 Pro, Grok 3)
or simply not re-queried (Grok 4.1; OpenEvidence, which has no API). They still belong
in the *standard-prompt* (main) panel. To make their diagnostic-cost numbers comparable
to the 18 re-run models, we take each system's SAVED assessment-and-plan text from the
canonical results/models/m_*.json and re-extract orders + diagnoses with the CURRENT
three-extractor set (gpt-4.1-mini, claude-haiku-4.5, gemini-2.5-flash) — identical to
scripts/run_prompt_variants.py. No regeneration occurs (the model outputs are fixed),
so this removes only the extractor-pipeline drift, not the original generation behavior.

Output mirrors the unified-panel schema and is written to results/models/ so
the standard-prompt panel lives in one place. Pricing is applied afterwards by
scripts/price_arms.py and concordance by scripts/judge_dx.py (all three judges), exactly
as for the 18 re-run models.

Usage
-----
  python scripts/reextract_groupO.py --models grok-4.1 --limit 5     # pilot
  python scripts/reextract_groupO.py --all
"""

import sys
import os
import json
import argparse
import tempfile
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulations"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "figures"))

from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)

from pipeline.cloud_llm_client import CloudLLMClient
from run_study import extract_orders, extract_diagnoses
from run_prompt_variants import load_cohort, med_total, REFERENCE_BASELINE

# Group O: the standard-prompt-only systems. All read their saved llm_plan from
# results/models_original_runs/ and write a default-arm record to results/models/.
GROUP_O = ["openevidence", "grok-4.1", "gemini-3-pro", "claude-sonnet-3.5", "grok-3"]

# Identical to run_prompt_variants.py main(): gemini-2.0-flash-001 (removed from
# OpenRouter) was replaced by its live successor google/gemini-2.5-flash.
EXTRACTOR_SPECS = [
    ("openai", "gpt-4.1-mini"),
    ("openrouter", "anthropic/claude-haiku-4.5"),
    ("openrouter", "google/gemini-2.5-flash"),
]

DIAGNOSTIC_CATEGORIES = {"labs", "imaging", "procedure", "exam", "monitoring"}
_write_lock = threading.Lock()


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as out:
            json.dump(data, out, indent=2, default=str)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


def build_record(case, saved_plan, model_name, extractors):
    """Re-extract one saved plan (no generation). Pricing/judging added downstream."""
    ex_a, ex_b, ex_c = extractors
    dx_info = extract_diagnoses(saved_plan, ex_a)
    orders_a = extract_orders(saved_plan, ex_a)
    orders_b = extract_orders(saved_plan, ex_b)
    orders_c = extract_orders(saved_plan, ex_c)
    llm_med_cost = sorted([med_total(orders_a), med_total(orders_b), med_total(orders_c)])[1]
    return {
        "case_id": case["case_id"],
        "sample_name": case["sample_name"],
        "specialty": case["specialty"],
        "presentation": case["presentation"],
        "model": model_name,
        "prompt_arm": "default",
        # fixed physician baseline (same reference comparator as the 18 re-run models)
        "human_ap": case["human_ap"],
        "human_diagnoses": case["human_diagnoses"],
        "human_dx_summary": case["human_dx_summary"],
        "human_orders_a": case["human_orders_a"],
        "human_orders_b": case["human_orders_b"],
        "human_orders_c": case["human_orders_c"],
        "human_referrals": case["human_referrals"],
        "human_referral_count": case["human_referral_count"],
        "human_referral_cost": case["human_referral_cost"],
        "medicare_human_dx_cost": case["medicare_human_dx_cost"],
        # re-extracted AI side from SAVED plan text (RAW orders; priced by price_arms.py)
        "llm_plan": saved_plan,
        "llm_diagnoses": dx_info["diagnoses"],
        "llm_dx_summary": dx_info["summary"],
        "llm_orders_a": orders_a,
        "llm_orders_b": orders_b,
        "llm_orders_c": orders_c,
        "medicare_llm_med_cost": llm_med_cost,
    }


def run_model(model_name, cohort, extractors, workers, limit):
    canon = ROOT / "results" / "models_original_runs" / f"m_{model_name}.json"
    if not canon.exists():
        print(f"  [{model_name}] canonical file missing: {canon}"); return
    saved = {r["case_id"]: r.get("llm_plan", "") for r in json.load(open(canon)) if r.get("case_id")}

    out_dir = ROOT / "results" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"m_{model_name}.json"

    results, done = [], set()
    if out_file.exists():
        try:
            results = json.load(open(out_file))
            done = {r["case_id"] for r in results}
        except Exception:
            results, done = [], set()

    todo = [c for c in cohort
            if c["case_id"] not in done and saved.get(c["case_id"])]
    if limit:
        todo = todo[:limit]
    print(f"[{model_name}] {len(done)} done, {len(todo)} to re-extract "
          f"({sum(1 for c in cohort if saved.get(c['case_id']))} have saved plans)", flush=True)
    if not todo:
        return

    completed = 0

    def task(case):
        try:
            return build_record(case, saved[case["case_id"]], model_name, extractors)
        except Exception as e:
            print(f"    ERROR {case['case_id']}: {e}", flush=True)
            return None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed({ex.submit(task, c): c for c in todo}):
            rec = fut.result()
            completed += 1
            if rec is not None:
                with _write_lock:
                    results.append(rec)
                    if completed % 10 == 0 or completed == len(todo):
                        atomic_write(out_file, results)
                        print(f"    [{model_name}] {completed}/{len(todo)}", flush=True)
    atomic_write(out_file, results)
    print(f"  [{model_name}] wrote {len(results)} records -> {out_file}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", help="comma-separated subset of Group O (default: all)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    models = GROUP_O if (args.all or not args.models) else [m.strip() for m in args.models.split(",")]
    for m in models:
        if m not in GROUP_O:
            raise SystemExit(f"{m!r} not in Group O: {GROUP_O}")

    cohort = load_cohort(REFERENCE_BASELINE)
    print(f"Cohort: {len(cohort)} cases (fixed physician baseline: {REFERENCE_BASELINE})")
    print(f"Group O models: {models}\n")

    # Health-check each extractor before spending calls.
    for prov, mid in EXTRACTOR_SPECS:
        try:
            CloudLLMClient(provider=prov, model=mid).generate("reply OK", max_tokens=8, temperature=0)
        except Exception as e:
            raise SystemExit(f"Extractor health check FAILED for {prov}/{mid}: {e}")
    print("Extractor health check passed.\n", flush=True)
    extractors = tuple(CloudLLMClient(provider=p, model=m) for p, m in EXTRACTOR_SPECS)

    for m in models:
        run_model(m, cohort, extractors, args.workers, args.limit)

    print("\nDone. Next: price_arms.py --arms default --models <these>, "
          "then judge_dx.py (gpt-4.1-mini/claude/gemini) on results/models for these.")


if __name__ == "__main__":
    main()
