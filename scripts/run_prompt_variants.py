#!/usr/bin/env python3
"""
Prompt-sensitivity experiment for the GENERATION step.

Generates AI assessment-and-plans under three prompt arms (default / parsimonious /
costaware; see scripts/prompt_variants.py) on the SAME 200-case cohort and extracts
orders with the SAME three LLM extractors as the main study. Output mirrors the
canonical results/models/m_*.json schema.

Pricing is intentionally NOT done here. Generation is expensive/stochastic; pricing is
cheap/deterministic and is applied separately by scripts/price_arms.py (which mirrors
the canonical reprice_medicare -> canonical_cpt_override -> median pipeline). This lets
pricing be refined without re-querying the models. Diagnostic concordance is added by
scripts/judge_dx.py.

Design notes
------------
- Only the AI side is generated/extracted per arm. The physician baseline is fixed:
  case metadata (presentation, human_ap) and the physician side (human_orders_{a,b,c},
  medicare_human_dx_cost, etc.) are copied verbatim from the canonical reference file
  (default m_gpt-4.1.json) so the comparator is identical across every model and arm.
- The "default" arm re-runs the byte-identical original prompt; comparing its priced AI
  cost to the published results/models/ values is a reproducibility check.

Usage
-----
  python scripts/run_prompt_variants.py --models gpt-4.1 --arms default --limit 5   # pilot
  python scripts/run_prompt_variants.py --all-models --arms default,parsimonious,costaware
"""

import sys
import os
import json
import time
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
from prompt_variants import PROMPTS

# The dr7.ai key (for MedGemma/Meditron) lives in benchmarking/.env; the copy in ~/.env
# is stale. Set it explicitly AFTER the dotenv loads above so it wins at call time.
_bench_env = Path("~/Documents/benchmarking/.env").expanduser()
if _bench_env.exists():
    from dotenv import dotenv_values
    _dr7 = dotenv_values(_bench_env).get("DR7AI_API")
    if _dr7:
        os.environ["DR7AI_API"] = _dr7

DIAGNOSTIC_CATEGORIES = {"labs", "imaging", "procedure", "exam", "monitoring"}

# Model registry for the new arm. Keys match canonical model keys where they exist
# (so the canonical physician baseline and published comparisons line up); new
# frontier models get fresh keys. Verified live on OpenRouter 2026-06-01.
NEW_ARM_MODELS = {
    # live originals (re-runnable)
    "gpt-4.1":            ("openrouter", "openai/gpt-4.1"),
    "gpt-5.2":            ("openrouter", "openai/gpt-5.2"),
    "claude-sonnet-4.5":  ("openrouter", "anthropic/claude-sonnet-4.5"),
    "gemini-2.5-pro":     ("openrouter", "google/gemini-2.5-pro"),
    "llama-3.3-70b":      ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
    "llama4":             ("openrouter", "meta-llama/llama-4-maverick"),
    "qwen-2.5-72b":       ("openrouter", "qwen/qwen-2.5-72b-instruct"),
    "qwen3":              ("openrouter", "qwen/qwen3-235b-a22b"),
    "deepseek-r1":        ("openrouter", "deepseek/deepseek-r1"),
    "deepseek-v3.2":      ("openrouter", "deepseek/deepseek-chat-v3-0324"),
    # new frontier (fresh)
    "qwen-3.7":           ("openrouter", "qwen/qwen3.7-plus"),  # newest Qwen flagship (2026-06)
    "grok-4.3":           ("openrouter", "x-ai/grok-4.3"),
    "claude-opus-4.8":    ("openrouter", "anthropic/claude-opus-4.8"),
    "gemini-3.5-flash":   ("openrouter", "google/gemini-3.5-flash"),
    "gemini-3.1-pro":     ("openrouter", "google/gemini-3.1-pro-preview"),  # successor to retired gemini-3-pro
    # GPT-5.5 via the OpenAI API directly (not on OpenRouter); reasoning model, so it
    # uses max_completion_tokens and the default temperature (see cloud_llm_client).
    "gpt-5.5":            ("openai", "gpt-5.5"),
    # Specialized medical models via dr7.ai (key from benchmarking/.env)
    "medgemma-4b":        ("dr7", "medgemma-4b-it"),
    "medgemma-27b":       ("dr7", "medgemma-27b-it"),
    "meditron":           ("dr7", "meditron"),
}

REFERENCE_BASELINE = "gpt-4.1"  # canonical file whose physician side defines the comparator


def med_total(orders):
    return sum(o.get("monthly_cost_usd", 0) for o in orders if o.get("category") == "medication")


_TRANSIENT = ("429", "connection", "reset", "timed out", "timeout", "broken", "502", "503", "504")


def _is_transient(e):
    s = str(e).lower()
    return any(t in s for t in _TRANSIENT)


def _retry(fn, attempts=6):
    """Retry a network call on transient errors (429, connection resets, timeouts, 5xx)."""
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            if _is_transient(e) and i < attempts - 1:
                time.sleep(min(2 ** i * 4, 60))
            else:
                raise


def generate_plan_arm(presentation, provider, model_id, arm):
    """Generate an assessment & plan under the given prompt arm (transient-error backoff)."""
    llm = CloudLLMClient(provider=provider, model=model_id)
    prompt = PROMPTS[arm].format(presentation=presentation)
    return _retry(lambda: llm.generate(prompt, max_tokens=4096, temperature=0.3))


def load_cohort(reference):
    """Load the N=200 cohort + reference physician baseline from canonical results."""
    import generate_paper_figures as gpf
    all_data = gpf.load_all_models()
    if reference not in all_data:
        raise SystemExit(f"reference model {reference!r} not found in results/models/")
    cohort = []
    for r in all_data[reference]:
        cohort.append({
            "case_id": r["case_id"],
            "sample_name": r.get("sample_name", ""),
            "specialty": r.get("specialty", ""),
            "presentation": r["presentation"],
            "human_ap": r["human_ap"],
            "human_diagnoses": r.get("human_diagnoses", []),
            "human_dx_summary": r.get("human_dx_summary", ""),
            "human_orders_a": r.get("human_orders_a", []),
            "human_orders_b": r.get("human_orders_b", []),
            "human_orders_c": r.get("human_orders_c", []),
            "human_referrals": r.get("human_referrals", []),
            "human_referral_count": r.get("human_referral_count", 0),
            "human_referral_cost": r.get("human_referral_cost", 0),
            "medicare_human_dx_cost": r.get("medicare_human_dx_cost", 0),
        })
    return cohort


def build_record(case, model_name, provider, model_id, arm, extractors):
    """Generate + extract one case for one model/arm. Pricing is done later."""
    ex_a, ex_b, ex_c = extractors
    llm_plan = generate_plan_arm(case["presentation"], provider, model_id, arm)
    if not llm_plan:
        return None

    dx_info = _retry(lambda: extract_diagnoses(llm_plan, ex_a))
    orders_a = _retry(lambda: extract_orders(llm_plan, ex_a))
    orders_b = _retry(lambda: extract_orders(llm_plan, ex_b))
    orders_c = _retry(lambda: extract_orders(llm_plan, ex_c))
    llm_med_cost = sorted([med_total(orders_a), med_total(orders_b), med_total(orders_c)])[1]

    return {
        "case_id": case["case_id"],
        "sample_name": case["sample_name"],
        "specialty": case["specialty"],
        "presentation": case["presentation"],
        "model": model_name,
        "prompt_arm": arm,
        # fixed physician baseline (copied from reference canonical file; already priced)
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
        # freshly generated AI side under this prompt arm (RAW orders; priced by price_arms.py)
        "llm_plan": llm_plan,
        "llm_diagnoses": dx_info["diagnoses"],
        "llm_dx_summary": dx_info["summary"],
        "llm_orders_a": orders_a,
        "llm_orders_b": orders_b,
        "llm_orders_c": orders_c,
        "medicare_llm_med_cost": llm_med_cost,
        # medicare_llm_dx_cost / dx_match_v2 added by price_arms.py / judge_dx.py
    }


def atomic_write(path, data):
    tmp = tempfile.NamedTemporaryFile(mode="w", dir=path.parent, suffix=".tmp", delete=False)
    try:
        json.dump(data, tmp, indent=2, default=str)
        tmp.close()
        os.replace(tmp.name, path)
    except BaseException:
        tmp.close()
        os.unlink(tmp.name)
        raise


def run_model_arm(model_name, provider, model_id, arm, cohort, extractors, workers):
    out_dir = ROOT / "results" / f"models_{arm}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"m_{model_name}.json"

    results, done = [], set()
    if out_file.exists():
        try:
            results = json.load(open(out_file))
            done = {r["case_id"] for r in results}
        except Exception:
            results, done = [], set()

    todo = [c for c in cohort if c["case_id"] not in done]
    print(f"[{arm}/{model_name}] {len(done)} done, {len(todo)} to generate", flush=True)
    if not todo:
        return out_file

    lock = threading.Lock()
    completed = 0

    def task(case):
        try:
            return build_record(case, model_name, provider, model_id, arm, extractors)
        except Exception as e:
            print(f"    ERROR {case['case_id']}: {e}", flush=True)
            return None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed({ex.submit(task, c): c for c in todo}):
            rec = fut.result()
            completed += 1
            if rec is not None:
                with lock:
                    results.append(rec)
                    if completed % 10 == 0 or completed == len(todo):
                        atomic_write(out_file, results)
                        n_dx = sum(1 for o in rec["llm_orders_a"]
                                   if o.get("category") in DIAGNOSTIC_CATEGORIES)
                        print(f"    [{arm}/{model_name}] {completed}/{len(todo)} "
                              f"(last {rec['case_id']}: {n_dx} dx orders)", flush=True)
    atomic_write(out_file, results)
    return out_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", help="comma-separated model keys")
    ap.add_argument("--all-models", action="store_true", help="use the full NEW_ARM_MODELS set")
    ap.add_argument("--arms", default="default,parsimonious,costaware")
    ap.add_argument("--limit", type=int, default=0, help="limit cases (0 = all 200)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--reference", default=REFERENCE_BASELINE)
    ap.add_argument("--list-models", action="store_true")
    args = ap.parse_args()

    if args.list_models:
        for k, v in NEW_ARM_MODELS.items():
            print(f"  {k:20s} {v[1]}")
        return

    if args.all_models:
        models = dict(NEW_ARM_MODELS)
    elif args.models:
        models = {}
        for k in args.models.split(","):
            k = k.strip()
            if k not in NEW_ARM_MODELS:
                raise SystemExit(f"unknown model key {k!r}; see --list-models")
            models[k] = NEW_ARM_MODELS[k]
    else:
        raise SystemExit("specify --models or --all-models")

    arms = [a.strip() for a in args.arms.split(",")]
    for a in arms:
        if a not in PROMPTS:
            raise SystemExit(f"unknown arm {a!r}; choices: {list(PROMPTS)}")

    cohort = load_cohort(args.reference)
    if args.limit:
        cohort = cohort[:args.limit]
    print(f"Cohort: {len(cohort)} cases (reference baseline: {args.reference})")
    print(f"Models: {list(models)}")
    print(f"Arms:   {arms}\n")

    # Three extractors (median-of-3). NOTE: the original study used
    # google/gemini-2.0-flash-001, which OpenRouter has since removed (HTTP 404);
    # replaced with its live successor google/gemini-2.5-flash. gpt-4.1-mini and
    # claude-haiku-4.5 are unchanged from the main study.
    extractor_specs = [
        ("openai", "gpt-4.1-mini"),
        ("openrouter", "anthropic/claude-haiku-4.5"),
        ("openrouter", "google/gemini-2.5-flash"),
    ]
    # Fail loudly if any extractor model is dead (avoids silently dropping every case).
    for prov, mid in extractor_specs:
        try:
            CloudLLMClient(provider=prov, model=mid).generate("reply OK", max_tokens=8, temperature=0)
        except Exception as e:
            raise SystemExit(f"Extractor health check FAILED for {prov}/{mid}: {e}\n"
                             f"Fix the model id before running.")
    print("Extractor health check passed.\n", flush=True)
    extractors = tuple(CloudLLMClient(provider=p, model=m) for p, m in extractor_specs)

    # model-outer / arm-inner: each model completes all arms before the next, so the
    # first model yields a full-200 three-arm result for the decision gate quickly.
    for model_name, (provider, model_id) in models.items():
        for arm in arms:
            run_model_arm(model_name, provider, model_id, arm, cohort, extractors, args.workers)

    print("\nGeneration done. Next: python scripts/price_arms.py --arms "
          + ",".join(arms) + "  then  python scripts/judge_dx.py per arm dir.")


if __name__ == "__main__":
    main()
