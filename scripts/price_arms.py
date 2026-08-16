#!/usr/bin/env python3
"""
Price the prompt-variant arms — PRICING step.

Applies the EXACT canonical pricing sequence that produced results/models/m_*.json to
the freshly generated arm files (results/models_<arm>/m_*.json):

  1. price_order()            from scripts/reprice_medicare.py
     (supplementary dict -> substring dict -> analyzer direct match -> RAG search),
     writing per-order cpt_code / price / source on each diagnostic order.
  2. apply_canonical()        from scripts/canonical_cpt_override.py
     (forces ~50 common tests to their canonical CPT/price, e.g. anti-dsDNA -> 86225,
     correcting RAG false positives).
  3. recompute_dx_cost()      from scripts/canonical_cpt_override.py
     (median of the three extraction-slot totals over is_test orders) -> medicare_llm_dx_cost.

Only the AI side is (re)priced. The physician side was copied verbatim from the canonical
reference file and already carries final canonical prices; medicare_human_dx_cost is left
as published.

Usage
-----
  python scripts/price_arms.py --arms default,parsimonious,costaware
  python scripts/price_arms.py --arms parsimonious --models gpt-4.1
"""

import sys
import os
import json
import statistics
import tempfile
import argparse
from pathlib import Path

# Cached HF assets; skip slow huggingface.co HEAD checks during RAG init.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "simulations"))
sys.path.insert(0, str(ROOT.parent / "malpractice"))

from cost.rag import CPTVectorStore
from cost.pricing import CPTPricingDatabase
from cost.analyzer import CostAnalyzer
from reprice_medicare import price_order, DIAGNOSTIC_CATEGORIES
from canonical_cpt_override import apply_canonical, recompute_dx_cost


def make_analyzer():
    cpt = ROOT.parent / "malpractice" / "data" / "cpt"
    rag = CPTVectorStore(
        descriptions_path=cpt / "clarified_descriptions.csv",
        embeddings_path=cpt / "embeddings" / "cpt_embeddings.npz",
    )
    pricing = CPTPricingDatabase(prices_path=cpt / "medicare_pfs_2026.csv")
    return CostAnalyzer(rag=rag, pricing=pricing, use_mock_extractor=True)


def price_slot_orders(orders, analyzer):
    """In-place: attach cpt_code/price/source to diagnostic orders via price_order."""
    for o in orders or []:
        if o.get("category") not in DIAGNOSTIC_CATEGORIES:
            continue
        p = price_order(o.get("order", ""), analyzer, category=o.get("category", ""))
        o["cpt_code"] = p.get("cpt_code")
        o["price"] = p.get("medicare_price", 0) or 0
        o["source"] = p.get("match_method", "unknown")


def price_record(rec, analyzer):
    # 1) price each AI extraction slot
    for slot in ("a", "b", "c"):
        price_slot_orders(rec.get(f"llm_orders_{slot}"), analyzer)
    # 2) canonical override (fixes RAG false positives on common tests)
    for slot in ("a", "b", "c"):
        apply_canonical(rec.get(f"llm_orders_{slot}", []))
    # 3) median of three slot totals over is_test orders
    rec["medicare_llm_dx_cost"] = recompute_dx_cost(rec, "llm")


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as out:
            json.dump(data, out, indent=2, default=str)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="default,parsimonious,costaware")
    ap.add_argument("--models", help="comma-separated model keys (default: all m_*.json per arm)")
    args = ap.parse_args()

    print("Loading Medicare pricing system...", flush=True)
    analyzer = make_analyzer()
    print("Ready.\n", flush=True)

    arms = [a.strip() for a in args.arms.split(",")]
    for arm in arms:
        d = ROOT / "results" / ("models" if arm == "default" else f"models_{arm}")
        if not d.exists():
            print(f"[{arm}] no dir {d}, skipping")
            continue
        if args.models:
            files = [d / f"m_{m.strip()}.json" for m in args.models.split(",")]
        else:
            files = sorted(d.glob("m_*.json"))
        for f in files:
            if not f.exists():
                print(f"  {f.name}: not found"); continue
            data = json.load(open(f))
            for rec in data:
                price_record(rec, analyzer)
            atomic_write(f, data)
            uniq, seen = [], set()
            for c in data:
                if c.get("presentation") and c["presentation"] not in seen:
                    seen.add(c["presentation"]); uniq.append(c)
            ai = statistics.mean([c.get("medicare_llm_dx_cost", 0) or 0 for c in uniq])
            ph = statistics.mean([c.get("medicare_human_dx_cost", 0) or 0 for c in uniq])
            print(f"  [{arm}] {f.name:28s} n={len(uniq):3d}  AI=${ai:6.1f}  phys=${ph:5.1f}  "
                  f"ratio={ai/ph:.2f}x" if ph else
                  f"  [{arm}] {f.name:28s} n={len(uniq):3d}  AI=${ai:6.1f}", flush=True)
    print("\nDone. Next: scripts/judge_dx.py per arm dir, then analysis.")


if __name__ == "__main__":
    main()
