#!/usr/bin/env python3
"""
Within each extractor's output for a given case, if the same CPT code appears
multiple times with the same price, keep only ONE instance. This fixes the
over-enumeration bug where extractors split one procedure into multiple line
items (e.g., "lumbar puncture: autoimmune panel" + "lumbar puncture: prion
markers" both priced as $165 for the LP procedure).

Only collapses test-category orders with identical CPT + price; leaves other
orders alone (meds, referrals, non-matched orders).
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models_original_runs"

TEST_CATS = {"lab", "laboratory", "labs", "imaging", "test", "procedure",
             "monitoring", "diagnostic", "screening"}


def is_test(cat: str) -> bool:
    c = (cat or "").lower()
    return ("med" not in c) and any(k in c for k in TEST_CATS)


def dedup_orders(orders: list[dict]) -> tuple[list[dict], int, float]:
    """Remove within-list duplicates (same CPT, test-cat, priced > 0).
    Keep the first occurrence. Returns (new_list, n_removed, dollars_removed)."""
    seen_cpts = set()
    out = []
    removed = 0
    dollars = 0.0
    for o in orders or []:
        cat = o.get("category", "") or ""
        cpt = o.get("cpt_code")
        price = float(o.get("price", 0) or 0)
        if is_test(cat) and cpt and price > 0 and cpt in seen_cpts:
            removed += 1
            dollars += price
            continue
        if is_test(cat) and cpt and price > 0:
            seen_cpts.add(cpt)
        out.append(o)
    return out, removed, dollars


def recompute_dx_cost(case: dict, key_prefix: str) -> float:
    totals = []
    for which in ["a", "b", "c"]:
        key = f"{key_prefix}_orders_{which}"
        total = sum(float(o.get("price", 0) or 0)
                    for o in (case.get(key) or [])
                    if is_test(o.get("category", "")))
        totals.append(total)
    return round(sorted(totals)[1], 2)


def main() -> None:
    for path in sorted(MODELS.glob("m_*.json")):
        model = path.stem.replace("m_", "")
        if model == "human":
            continue
        with open(path) as f:
            data = json.load(f)
        total_removed = 0
        total_dollars = 0.0
        n_llm_changed = 0
        n_hum_changed = 0
        llm_delta = 0.0
        hum_delta = 0.0
        for c in data:
            # AI orders
            for w in ["a", "b", "c"]:
                key = f"llm_orders_{w}"
                if key in c:
                    new, n, d = dedup_orders(c[key])
                    c[key] = new
                    total_removed += n
                    total_dollars += d
            old_llm = c.get("medicare_llm_dx_cost") or 0
            new_llm = recompute_dx_cost(c, "llm")
            if abs(new_llm - old_llm) > 0.01:
                n_llm_changed += 1
                llm_delta += new_llm - old_llm
            c["medicare_llm_dx_cost"] = new_llm

            # Human orders
            for w in ["a", "b", "c"]:
                key = f"human_orders_{w}"
                if key in c:
                    new, n, d = dedup_orders(c[key])
                    c[key] = new
                    total_removed += n
                    total_dollars += d
            old_hum = c.get("medicare_human_dx_cost") or 0
            new_hum = recompute_dx_cost(c, "human")
            if abs(new_hum - old_hum) > 0.01:
                n_hum_changed += 1
                hum_delta += new_hum - old_hum
            c["medicare_human_dx_cost"] = new_hum

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"{model:<22}  removed={total_removed:>4} duplicates  "
              f"LLM cases changed={n_llm_changed:>3} delta=${llm_delta:>+8.0f}  "
              f"HUM changed={n_hum_changed:>2} delta=${hum_delta:>+6.0f}")


if __name__ == "__main__":
    main()
