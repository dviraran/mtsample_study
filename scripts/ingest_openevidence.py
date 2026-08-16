#!/usr/bin/env python3
"""
Ingest manually-collected OpenEvidence responses from data/openevidence_manual_prompts.md
into the prompt-variant arm files, then they can be priced/judged like any other model.

Parses each <!-- RESPONSE_START case=.. arm=.. --> ... <!-- RESPONSE_END --> block; for
each FILLED block, treats the pasted text as the OpenEvidence plan, extracts diagnoses +
orders (same 3 extractors as the study), and writes/merges a record (model="openevidence")
into results/models_<arm>/m_openevidence.json. Pricing and judging are done afterward by
price_arms.py and judge_dx.py (--models openevidence).
"""
import re
import sys
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "simulations"))

from run_prompt_variants import load_cohort, med_total, _retry, REFERENCE_BASELINE
from run_study import extract_orders, extract_diagnoses
from pipeline.cloud_llm_client import CloudLLMClient

MD = ROOT / "data" / "openevidence_manual_prompts.md"
PLACEHOLDER = "(paste response here)"
START = re.compile(r"<!--\s*RESPONSE_START\s+case=(\S+)\s+arm=(\S+)\s*-->")
END = re.compile(r"<!--\s*RESPONSE_END\s*-->")


def parse_responses():
    """Bound each response by the next END *or* the next START (whichever comes first),
    so a missing/extra marker can't swallow an adjacent block."""
    text = MD.read_text()
    starts = list(START.finditer(text))
    out = []
    for i, m in enumerate(starts):
        case, arm = m.group(1), m.group(2)
        seg_start = m.end()
        nxt_start = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        end_m = END.search(text, seg_start, nxt_start)
        seg_end = end_m.start() if end_m else nxt_start
        resp = text[seg_start:seg_end].strip()
        cleaned = resp.replace("_" + PLACEHOLDER + "_", "").replace(PLACEHOLDER, "").strip()
        if len(cleaned) > 40:  # treat as filled
            out.append((case, arm, cleaned))
    return out


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp); raise


def main():
    responses = parse_responses()
    print(f"Filled responses found: {len(responses)}")
    by_arm = {}
    for c, a, _ in responses:
        by_arm.setdefault(a, []).append(c)
    for a, cs in by_arm.items():
        print(f"  {a}: {len(cs)} -> {sorted(cs)}")
    if not responses:
        print("Nothing to ingest."); return

    cohort = {c["case_id"]: c for c in load_cohort(REFERENCE_BASELINE)}
    ex_a = CloudLLMClient(provider="openai", model="gpt-4.1-mini")
    ex_b = CloudLLMClient(provider="openrouter", model="anthropic/claude-haiku-4.5")
    ex_c = CloudLLMClient(provider="openrouter", model="google/gemini-2.5-flash")

    for case, arm, plan in responses:
        if case not in cohort:
            print(f"  WARN {case} not in cohort, skipping"); continue
        ca = cohort[case]
        dx = _retry(lambda: extract_diagnoses(plan, ex_a))
        oa = _retry(lambda: extract_orders(plan, ex_a))
        ob = _retry(lambda: extract_orders(plan, ex_b))
        oc = _retry(lambda: extract_orders(plan, ex_c))
        rec = {
            "case_id": case, "sample_name": ca["sample_name"], "specialty": ca["specialty"],
            "presentation": ca["presentation"], "model": "openevidence", "prompt_arm": arm,
            "human_ap": ca["human_ap"], "human_diagnoses": ca["human_diagnoses"],
            "human_dx_summary": ca["human_dx_summary"],
            "human_orders_a": ca["human_orders_a"], "human_orders_b": ca["human_orders_b"],
            "human_orders_c": ca["human_orders_c"], "human_referrals": ca["human_referrals"],
            "human_referral_count": ca["human_referral_count"],
            "human_referral_cost": ca["human_referral_cost"],
            "medicare_human_dx_cost": ca["medicare_human_dx_cost"],
            "llm_plan": plan, "llm_diagnoses": dx["diagnoses"], "llm_dx_summary": dx["summary"],
            "llm_orders_a": oa, "llm_orders_b": ob, "llm_orders_c": oc,
            "medicare_llm_med_cost": sorted([med_total(oa), med_total(ob), med_total(oc)])[1],
            "source": "manual_openevidence",
        }
        out_dir = ROOT / "results" / f"models_{arm}"
        out_dir.mkdir(parents=True, exist_ok=True)
        f = out_dir / "m_openevidence.json"
        data = json.load(open(f)) if f.exists() else []
        data = [r for r in data if r.get("case_id") != case]  # replace if re-ingesting
        data.append(rec)
        atomic_write(f, data)
        n_dx = sum(1 for o in oa if o.get("category") in {"labs","imaging","procedure","exam","monitoring"})
        print(f"  ingested {arm}/{case}: {n_dx} dx orders (slot a), dx='{', '.join(dx['diagnoses'][:2])}'")

    print("\nNext: price + judge openevidence arms.")


if __name__ == "__main__":
    main()
