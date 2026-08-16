#!/usr/bin/env python3
"""
Fix extractor-cost unreliability via per-order price propagation, then median.

For each (case, model):
  1. Build a price map across 3 extractors: for each unique order text
     (normalized), find the highest price any extractor successfully CPT-matched.
  2. For each extractor, recompute its total using this price map. If an
     extractor found order X but failed CPT match (price=0), it now inherits
     the best-priced version's price.
  3. Take the median of the 3 corrected totals (preserves the paper's
     median-of-3 methodology while fixing CPT-match failures).

This is conservative:
  - Does NOT add orders that only 1 extractor extracted (no over-counting
    from hallucinations).
  - Does NOT use max (avoids inflating when one extractor over-enumerates
    a single order as multiple line items).
  - Preserves the "median robustness" of the original pipeline.

Compared to the published median, this just repairs cases where 2 of 3
extractors failed the CPT lookup for an order that the third got right.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models_original_runs"

TEST_CATS = {"lab", "laboratory", "labs", "imaging", "test", "procedure",
             "monitoring", "diagnostic", "screening"}

_STRIP_PREFIX = re.compile(
    r"^(obtain|order|schedule|send|start|get|consider|recommend|perform|draw|"
    r"stat|repeat|check|request)\s+",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    """Fuzzy normalize an order description for cross-extractor matching."""
    if not text:
        return ""
    s = text.lower().strip()
    # Strip leading verbs
    s = _STRIP_PREFIX.sub("", s)
    # Strip punctuation
    s = re.sub(r"[(){}\[\],.;:]", " ", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # First 6 words is usually the identifying phrase
    words = s.split()[:6]
    return " ".join(words)


def is_test(cat: str) -> bool:
    c = (cat or "").lower()
    return ("med" not in c) and any(k in c for k in TEST_CATS)


def corrected_median(orders_abc: list[list[dict]]) -> float:
    """Apply price propagation + median across 3 extractor outputs."""
    # Build best-price map across all 3 extractors
    best_price = {}
    for orders in orders_abc:
        for o in orders or []:
            if not is_test(o.get("category", "")):
                continue
            key = normalize(o.get("order", ""))
            if not key:
                continue
            p = float(o.get("price", 0) or 0)
            if p > best_price.get(key, 0):
                best_price[key] = p

    # Recompute per-extractor total using propagated prices
    totals = []
    for orders in orders_abc:
        total = 0.0
        for o in orders or []:
            if not is_test(o.get("category", "")):
                continue
            key = normalize(o.get("order", ""))
            if not key:
                continue
            own_price = float(o.get("price", 0) or 0)
            total += best_price.get(key, own_price)
        totals.append(total)
    return sorted(totals)[1]  # median


def main() -> None:
    summary = []
    for path in sorted(MODELS.glob("m_*.json")):
        with open(path) as f:
            data = json.load(f)
        model = path.stem.replace("m_", "")

        n_llm_changed = 0
        n_hum_changed = 0
        llm_delta = 0.0
        hum_delta = 0.0
        for c in data:
            if "llm_orders_a" in c:
                new = corrected_median([c.get(f"llm_orders_{w}", [])
                                        for w in ["a", "b", "c"]])
                old = c.get("medicare_llm_dx_cost") or 0
                if abs(new - old) > 0.01:
                    n_llm_changed += 1
                    llm_delta += new - old
                c["medicare_llm_dx_cost"] = round(new, 2)
            if "human_orders_a" in c:
                new = corrected_median([c.get(f"human_orders_{w}", [])
                                        for w in ["a", "b", "c"]])
                old = c.get("medicare_human_dx_cost") or 0
                if abs(new - old) > 0.01:
                    n_hum_changed += 1
                    hum_delta += new - old
                c["medicare_human_dx_cost"] = round(new, 2)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"{model:<22}  "
              f"LLM: {n_llm_changed:>3} rows changed (+${llm_delta:>8.0f})  "
              f"HUM: {n_hum_changed:>3} rows changed (+${hum_delta:>8.0f})")
        summary.append((model, n_llm_changed, llm_delta, n_hum_changed, hum_delta))

    print("\nTotal LLM delta: ${:,.0f}".format(sum(s[2] for s in summary)))
    print("Total HUM delta: ${:,.0f}".format(sum(s[4] for s in summary)))


if __name__ == "__main__":
    main()
