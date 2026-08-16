#!/usr/bin/env python3
"""
Backfill `medicare_human_med_cost` into the canonical model files.

The AI side has carried `medicare_llm_med_cost` since the original runs, but the
physician side of that pair was never written into results/models/ (only
scripts/reprice_medicare.py, which targets results/models_original_runs/, ever
computed it). Consequently `build_stats_df` computes the physician's total cost
of care with medications valued at $0, which was harmless while the paper
reported diagnostic cost only — but the primary outcome is the aggregate of
tests + consultations + medications, so the field has to exist.

The value is derived from data already in each record, using exactly the rule
applied to the AI side: sum `monthly_cost_usd` over medication-category orders
within each extraction slot, then take the median of the three slots
(scripts/run_prompt_variants.py::med_total, the study's aggregation rule).

Purely additive: no existing key is modified. Idempotent; re-running recomputes
identical values. Use --check to report without writing.

Usage:
  /usr/bin/python3 scripts/backfill_human_med_cost.py --check
  /usr/bin/python3 scripts/backfill_human_med_cost.py
"""

import ast
import json
import argparse
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRS = ["results/models", "results/models_parsimonious", "results/models_costaware"]
FIELD = "medicare_human_med_cost"


def as_orders(v):
    if isinstance(v, list):
        return v
    if not v:
        return []
    try:
        out = ast.literal_eval(v)
        return out if isinstance(out, list) else []
    except (ValueError, SyntaxError):
        return []


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def med_total(orders):
    return sum(fnum(o.get("monthly_cost_usd", 0)) for o in orders
               if isinstance(o, dict) and o.get("category") == "medication")


def human_med_cost(case):
    slots = [med_total(as_orders(case.get(f"human_orders_{s}"))) for s in "abc"]
    return float(sorted(slots)[1])


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2, default=str)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, do not write")
    ap.add_argument("--force", action="store_true", help="overwrite an existing field")
    args = ap.parse_args()

    grand_added = grand_files = 0
    for d in DIRS:
        dpath = ROOT / d
        if not dpath.exists():
            continue
        for fpath in sorted(dpath.glob("m_*.json")):
            if fpath.name == "m_human.json":
                continue
            cases = json.load(open(fpath))
            added = changed = 0
            total = 0.0
            for c in cases:
                if FIELD in c and not args.force:
                    total += fnum(c[FIELD])
                    continue
                v = human_med_cost(c)
                if FIELD in c and fnum(c[FIELD]) != v:
                    changed += 1
                if FIELD not in c:
                    added += 1
                c[FIELD] = v
                total += v
            mean = total / len(cases) if cases else 0
            flag = "" if args.check else " (written)"
            if added or changed:
                print(f"  {fpath.parent.name}/{fpath.name}: +{added} added, "
                      f"{changed} changed, mean ${mean:.2f}/visit{flag}")
                if not args.check:
                    atomic_write(fpath, cases)
                grand_added += added
                grand_files += 1
            else:
                print(f"  {fpath.parent.name}/{fpath.name}: up to date, mean ${mean:.2f}/visit")

    verb = "would add" if args.check else "added"
    print(f"\n{verb} {FIELD} to {grand_added} records across {grand_files} files")


if __name__ == "__main__":
    main()
