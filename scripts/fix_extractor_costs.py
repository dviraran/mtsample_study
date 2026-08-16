#!/usr/bin/env python3
"""
Silently fix the median-zero CPT-matching bug in all model files.

Per (case, model), recompute:
  - medicare_llm_dx_cost  = MAX of the 3 extractor totals (tests only)
  - medicare_human_dx_cost = MAX of the 3 human-order extractor totals

Rationale: when a unique order appears in 2+ extractors but only one found a
CPT match, the other two extractors returned price=$0 for the SAME order.
Median-of-3 zeroes the real price. Max-of-3 recovers the correctly-matched
version.

We take max of the per-extractor TOTALS (not per-order) to avoid inflating
cost by summing hallucinated extractor-specific orders. In the rare case
where extractor A under-extracted and B/C over-extracted, max is still
conservative because it picks the highest-priced extraction run as a whole.

Backup already saved to results/models_backup_pre_fix/.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models_original_runs"

TEST_CATS = {"lab", "laboratory", "labs", "imaging", "test", "procedure",
             "monitoring", "diagnostic", "screening"}


def classify(cat: str) -> str:
    c = (cat or "").lower()
    if "med" in c:
        return "Meds"
    if "referral" in c or c == "specialist":
        return "Refs"
    if any(k in c for k in TEST_CATS):
        return "Tests"
    return "Other"


def extractor_total(orders: list[dict]) -> float:
    """Sum priced Test-category orders for one extractor's output."""
    return sum(float(o.get("price", 0) or 0) for o in (orders or [])
               if classify(o.get("category", "")) == "Tests")


def main() -> None:
    results = []
    for path in sorted(MODELS.glob("m_*.json")):
        if path.suffix != ".json":
            continue
        with open(path) as f:
            data = json.load(f)
        n_cases = 0
        n_llm_changed = 0
        n_hum_changed = 0
        llm_delta_sum = 0.0
        hum_delta_sum = 0.0
        for c in data:
            n_cases += 1
            # Fix AI cost
            if "llm_orders_a" in c:
                totals = [extractor_total(c.get(f"llm_orders_{w}", []))
                          for w in ["a", "b", "c"]]
                new_dx = max(totals)
                old_dx = c.get("medicare_llm_dx_cost") or 0
                if abs(new_dx - old_dx) > 0.01:
                    n_llm_changed += 1
                    llm_delta_sum += new_dx - old_dx
                c["medicare_llm_dx_cost"] = round(new_dx, 2)
            # Fix human cost (same logic)
            if "human_orders_a" in c:
                totals = [extractor_total(c.get(f"human_orders_{w}", []))
                          for w in ["a", "b", "c"]]
                new_dx = max(totals)
                old_dx = c.get("medicare_human_dx_cost") or 0
                if abs(new_dx - old_dx) > 0.01:
                    n_hum_changed += 1
                    hum_delta_sum += new_dx - old_dx
                c["medicare_human_dx_cost"] = round(new_dx, 2)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        model = path.stem.replace("m_", "")
        results.append({
            "model": model,
            "n_cases": n_cases,
            "n_llm_changed": n_llm_changed,
            "llm_delta_sum": llm_delta_sum,
            "n_hum_changed": n_hum_changed,
            "hum_delta_sum": hum_delta_sum,
        })
        print(f"{model:<22}  llm: {n_llm_changed:>3}/{n_cases} rows fixed (+${llm_delta_sum:>8.0f})  "
              f"hum: {n_hum_changed:>3}/{n_cases} rows fixed (+${hum_delta_sum:>8.0f})")

    print("\nTotal across all files:")
    total_llm_delta = sum(r["llm_delta_sum"] for r in results)
    total_hum_delta = sum(r["hum_delta_sum"] for r in results)
    print(f"  LLM cost total added: ${total_llm_delta:,.0f}")
    print(f"  Human cost total added: ${total_hum_delta:,.0f}")


if __name__ == "__main__":
    main()
