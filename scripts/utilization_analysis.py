#!/usr/bin/env python3
"""
Comprehensive Utilization Analysis: Diagnostic Test Ordering Patterns
AI Models vs. Physicians
"""

import json
import glob
import os
from pathlib import Path
from collections import Counter, defaultdict
import statistics

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = str(ROOT / "results" / "models_original_runs")
DIAGNOSTIC_CATEGORIES = {"labs", "imaging", "procedure", "monitoring"}  # exclude exam, referral, medication

def load_all_models():
    """Load all model files, excluding m_human.json"""
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "m_*.json")))
    models = {}
    for f in files:
        name = os.path.basename(f).replace("m_", "").replace(".json", "")
        if name == "human":
            continue
        with open(f) as fh:
            models[name] = json.load(fh)
    return models


def get_diagnostic_orders(orders):
    """Filter to diagnostic orders only (labs, imaging, procedures, monitoring)."""
    if not orders:
        return []
    return [o for o in orders if o.get("category") in DIAGNOSTIC_CATEGORIES]


def normalize_test_name(name):
    """Light normalization of test names for grouping."""
    if not name:
        return ""
    return name.strip().lower()


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def analysis_a(models):
    """Most commonly ordered tests by AI when physician ordered nothing."""
    print_header("A) MOST COMMON AI-ORDERED TESTS WHEN PHYSICIAN ORDERED $0 IN DIAGNOSTICS")

    # Collect across all models
    test_counter = Counter()
    category_counter = Counter()
    total_cases = 0
    cases_per_model = {}

    for model_name, cases in models.items():
        model_count = 0
        for case in cases:
            if case.get("medicare_human_dx_cost", 0) == 0:
                llm_dx = get_diagnostic_orders(case.get("medicare_llm_orders", []))
                if llm_dx:
                    model_count += 1
                    for o in llm_dx:
                        test_name = normalize_test_name(o.get("order", ""))
                        if test_name:
                            test_counter[test_name] += 1
                            category_counter[o.get("category", "unknown")] += 1
        cases_per_model[model_name] = model_count
        total_cases += model_count

    n_models = len(models)
    print(f"\nTotal model-case pairs where human=$0 and AI ordered diagnostics: {total_cases}")
    print(f"Number of AI models: {n_models}")
    print()

    # Also count by CPT description for cleaner grouping
    cpt_counter = Counter()
    for model_name, cases in models.items():
        for case in cases:
            if case.get("medicare_human_dx_cost", 0) == 0:
                llm_dx = get_diagnostic_orders(case.get("medicare_llm_orders", []))
                for o in llm_dx:
                    desc = o.get("cpt_description") or o.get("order", "")
                    if desc:
                        cpt_counter[desc.strip().lower()] += 1

    print("Top 25 tests ordered by AI (by CPT description) when physician ordered nothing:")
    print(f"{'Rank':<5} {'Test':<65} {'Count':<8} {'% of cases'}")
    print("-" * 95)
    for i, (test, count) in enumerate(cpt_counter.most_common(25), 1):
        pct = count / total_cases * 100 if total_cases > 0 else 0
        print(f"{i:<5} {test[:64]:<65} {count:<8} {pct:.1f}%")

    print("\n\nTop 25 tests by raw order text:")
    print(f"{'Rank':<5} {'Test Order':<75} {'Count':<8}")
    print("-" * 95)
    for i, (test, count) in enumerate(test_counter.most_common(25), 1):
        print(f"{i:<5} {test[:74]:<75} {count:<8}")

    print(f"\nCategory breakdown of AI orders when physician ordered $0:")
    for cat, cnt in category_counter.most_common():
        print(f"  {cat:<15} {cnt:>6} orders ({cnt/sum(category_counter.values())*100:.1f}%)")


def analysis_b(models):
    """Most common 'extra' tests AI adds when both ordered something."""
    print_header("B) MOST COMMON 'EXTRA' TESTS AI ADDS (WHEN BOTH ORDERED DIAGNOSTICS)")

    extra_counter = Counter()
    extra_cat_counter = Counter()
    total_cases_both = 0
    extra_cost_total = 0

    for model_name, cases in models.items():
        for case in cases:
            human_cost = case.get("medicare_human_dx_cost", 0) or 0
            llm_cost = case.get("medicare_llm_dx_cost", 0) or 0
            if human_cost > 0 and llm_cost > 0:
                total_cases_both += 1
                human_dx = get_diagnostic_orders(case.get("medicare_human_orders", []))
                llm_dx = get_diagnostic_orders(case.get("medicare_llm_orders", []))

                # Get human test names (normalized) for comparison
                human_tests = set()
                for o in human_dx:
                    human_tests.add(normalize_test_name(o.get("order", "")))
                    # Also add CPT description
                    if o.get("cpt_description"):
                        human_tests.add(o["cpt_description"].strip().lower())
                    if o.get("cpt_code"):
                        human_tests.add(o["cpt_code"])

                # Find extra AI tests
                for o in llm_dx:
                    test_name = normalize_test_name(o.get("order", ""))
                    cpt_desc = (o.get("cpt_description") or "").strip().lower()
                    cpt_code = o.get("cpt_code") or ""

                    # Check if this test is NOT in the human set
                    if (test_name not in human_tests and
                        cpt_desc not in human_tests and
                        cpt_code not in human_tests):
                        display = cpt_desc if cpt_desc else test_name
                        extra_counter[display] += 1
                        extra_cat_counter[o.get("category", "unknown")] += 1
                        extra_cost_total += o.get("medicare_price", 0) or 0

    print(f"\nCases where both physician and AI ordered diagnostics: {total_cases_both}")
    print(f"Total extra tests AI added: {sum(extra_counter.values())}")
    print(f"Total extra cost from AI additions: ${extra_cost_total:,.2f}")
    print(f"Average extra cost per case: ${extra_cost_total/total_cases_both:.2f}" if total_cases_both else "")

    print(f"\nTop 30 'extra' tests AI adds that physicians didn't:")
    print(f"{'Rank':<5} {'Test':<65} {'Count':<8} {'% of extra'}")
    print("-" * 95)
    total_extra = sum(extra_counter.values())
    for i, (test, count) in enumerate(extra_counter.most_common(30), 1):
        pct = count / total_extra * 100 if total_extra > 0 else 0
        print(f"{i:<5} {test[:64]:<65} {count:<8} {pct:.1f}%")

    print(f"\nCategory breakdown of extra AI tests:")
    for cat, cnt in extra_cat_counter.most_common():
        print(f"  {cat:<15} {cnt:>6} ({cnt/sum(extra_cat_counter.values())*100:.1f}%)")


def analysis_c(models):
    """Vivid case examples: physician $0, AI substantial workup."""
    print_header("C) CASE EXAMPLES: PHYSICIAN $0, AI ORDERED SUBSTANTIAL WORKUP")

    # Collect all such cases with details
    examples = []
    for model_name, cases in models.items():
        for case in cases:
            human_cost = case.get("medicare_human_dx_cost", 0) or 0
            llm_cost = case.get("medicare_llm_dx_cost", 0) or 0
            if human_cost == 0 and llm_cost > 50:  # AI spent > $50
                llm_dx = get_diagnostic_orders(case.get("medicare_llm_orders", []))
                if len(llm_dx) >= 2:
                    examples.append({
                        "case_id": case["case_id"],
                        "model": model_name,
                        "specialty": case.get("specialty", ""),
                        "presentation": case.get("presentation", "")[:300],
                        "llm_dx_cost": llm_cost,
                        "human_dx_cost": human_cost,
                        "n_tests": len(llm_dx),
                        "orders": llm_dx,
                        "human_orders": get_diagnostic_orders(case.get("medicare_human_orders", [])),
                    })

    # Sort by cost descending, pick diverse specialties
    examples.sort(key=lambda x: x["llm_dx_cost"], reverse=True)

    # Pick diverse examples
    seen_specialties = set()
    selected = []
    for ex in examples:
        spec = ex["specialty"]
        if spec not in seen_specialties and len(selected) < 8:
            selected.append(ex)
            seen_specialties.add(spec)

    # If we don't have enough, add more
    if len(selected) < 5:
        for ex in examples:
            if ex not in selected and len(selected) < 8:
                selected.append(ex)

    for i, ex in enumerate(selected[:8], 1):
        print(f"\n--- Example {i}: Case {ex['case_id']} ({ex['model']}) ---")
        print(f"  Specialty: {ex['specialty']}")
        print(f"  Presentation: {ex['presentation'][:200]}...")
        print(f"  Physician diagnostic orders: $0.00 (no tests ordered)")
        print(f"  AI diagnostic orders: ${ex['llm_dx_cost']:.2f} ({ex['n_tests']} tests)")
        print(f"  Tests ordered by AI:")
        for o in ex["orders"]:
            price = o.get("medicare_price", 0) or 0
            desc = o.get("cpt_description") or "no CPT match"
            print(f"    - {o['order'][:80]}")
            print(f"      [{o.get('category','?')}] CPT: {o.get('cpt_code','N/A')} ({desc}) = ${price:.2f}")

    # Summary statistics
    print(f"\n\n--- Summary: Physician $0, AI > $0 ---")
    costs_by_model = defaultdict(list)
    for ex_full in examples:
        costs_by_model[ex_full["model"]].append(ex_full["llm_dx_cost"])

    # Count how often this happens per model
    print(f"\nTotal cases (across all models) where physician=$0 but AI ordered >$50 diagnostics: {len(examples)}")

    # Now count ALL cases where physician=$0 and AI>$0
    all_zero_human = []
    for model_name, cases in models.items():
        for case in cases:
            human_cost = case.get("medicare_human_dx_cost", 0) or 0
            llm_cost = case.get("medicare_llm_dx_cost", 0) or 0
            if human_cost == 0 and llm_cost > 0:
                all_zero_human.append({
                    "model": model_name,
                    "cost": llm_cost,
                    "case_id": case["case_id"],
                    "n_tests": len(get_diagnostic_orders(case.get("medicare_llm_orders", [])))
                })

    print(f"Total model-case pairs where physician=$0 but AI ordered ANY diagnostics: {len(all_zero_human)}")
    if all_zero_human:
        costs = [x["cost"] for x in all_zero_human]
        print(f"  Mean AI cost in these cases: ${statistics.mean(costs):.2f}")
        print(f"  Median AI cost: ${statistics.median(costs):.2f}")
        print(f"  Max AI cost: ${max(costs):.2f}")
        tests = [x["n_tests"] for x in all_zero_human]
        print(f"  Mean number of diagnostic tests: {statistics.mean(tests):.1f}")
        print(f"  Median number of diagnostic tests: {statistics.median(tests):.1f}")


def analysis_d(models):
    """Test category breakdown — which categories drive excess AI ordering."""
    print_header("D) TEST CATEGORY BREAKDOWN: WHAT DRIVES AI EXCESS ORDERING")

    # Per-category costs
    ai_cat_cost = Counter()
    human_cat_cost = Counter()
    ai_cat_count = Counter()
    human_cat_count = Counter()

    total_cases = 0
    for model_name, cases in models.items():
        for case in cases:
            total_cases += 1
            for o in get_diagnostic_orders(case.get("medicare_llm_orders", [])):
                cat = o.get("category", "unknown")
                price = o.get("medicare_price", 0) or 0
                ai_cat_cost[cat] += price
                ai_cat_count[cat] += 1
            for o in get_diagnostic_orders(case.get("medicare_human_orders", [])):
                cat = o.get("category", "unknown")
                price = o.get("medicare_price", 0) or 0
                human_cat_cost[cat] += price
                human_cat_count[cat] += 1

    all_cats = sorted(set(list(ai_cat_cost.keys()) + list(human_cat_cost.keys())))

    print(f"\nAcross {total_cases} model-case pairs:")
    print(f"\n{'Category':<15} {'AI Orders':>10} {'Human Orders':>13} {'Ratio':>8} {'AI Cost':>14} {'Human Cost':>14} {'Cost Ratio':>11} {'Excess Cost':>14}")
    print("-" * 105)

    total_ai_cost = sum(ai_cat_cost.values())
    total_human_cost = sum(human_cat_cost.values())

    for cat in all_cats:
        ac = ai_cat_count.get(cat, 0)
        hc = human_cat_count.get(cat, 0)
        acost = ai_cat_cost.get(cat, 0)
        hcost = human_cat_cost.get(cat, 0)
        ratio = ac / hc if hc > 0 else float('inf')
        cratio = acost / hcost if hcost > 0 else float('inf')
        excess = acost - hcost
        ratio_str = f"{ratio:.1f}x" if ratio != float('inf') else "inf"
        cratio_str = f"{cratio:.1f}x" if cratio != float('inf') else "inf"
        print(f"{cat:<15} {ac:>10,} {hc:>13,} {ratio_str:>8} ${acost:>12,.2f} ${hcost:>12,.2f} {cratio_str:>11} ${excess:>12,.2f}")

    print(f"{'TOTAL':<15} {sum(ai_cat_count.values()):>10,} {sum(human_cat_count.values()):>13,} {'':>8} ${total_ai_cost:>12,.2f} ${total_human_cost:>12,.2f} {'':>11} ${total_ai_cost - total_human_cost:>12,.2f}")

    # Per-category share of excess
    total_excess = total_ai_cost - total_human_cost
    print(f"\nShare of excess cost by category:")
    for cat in all_cats:
        excess = ai_cat_cost.get(cat, 0) - human_cat_cost.get(cat, 0)
        share = excess / total_excess * 100 if total_excess > 0 else 0
        print(f"  {cat:<15} ${excess:>12,.2f} ({share:.1f}% of total excess)")

    # Per-model breakdown
    print(f"\n\nPer-model average diagnostic cost (AI vs Human):")
    print(f"{'Model':<25} {'AI Mean Cost':>14} {'Human Mean Cost':>16} {'Ratio':>8} {'AI Mean Tests':>14} {'Human Mean Tests':>16}")
    print("-" * 100)

    for model_name in sorted(models.keys()):
        cases = models[model_name]
        ai_costs = []
        human_costs = []
        ai_tests = []
        human_tests = []
        for case in cases:
            ai_costs.append(case.get("medicare_llm_dx_cost", 0) or 0)
            human_costs.append(case.get("medicare_human_dx_cost", 0) or 0)
            ai_tests.append(len(get_diagnostic_orders(case.get("medicare_llm_orders", []))))
            human_tests.append(len(get_diagnostic_orders(case.get("medicare_human_orders", []))))

        ai_mean = statistics.mean(ai_costs)
        h_mean = statistics.mean(human_costs)
        ratio = ai_mean / h_mean if h_mean > 0 else float('inf')
        ratio_str = f"{ratio:.1f}x" if ratio != float('inf') else "inf"
        print(f"{model_name:<25} ${ai_mean:>12,.2f} ${h_mean:>14,.2f} {ratio_str:>8} {statistics.mean(ai_tests):>13.1f} {statistics.mean(human_tests):>15.1f}")


def analysis_e(models):
    """Kitchen sink pattern — cases with unusually large numbers of AI tests."""
    print_header("E) 'KITCHEN SINK' PATTERN: CASES WITH >8 DIAGNOSTIC TESTS")

    kitchen_sink = []

    for model_name, cases in models.items():
        for case in cases:
            llm_dx = get_diagnostic_orders(case.get("medicare_llm_orders", []))
            if len(llm_dx) >= 8:
                human_dx = get_diagnostic_orders(case.get("medicare_human_orders", []))
                kitchen_sink.append({
                    "case_id": case["case_id"],
                    "model": model_name,
                    "specialty": case.get("specialty", ""),
                    "presentation": case.get("presentation", "")[:200],
                    "n_ai_tests": len(llm_dx),
                    "n_human_tests": len(human_dx),
                    "ai_cost": case.get("medicare_llm_dx_cost", 0) or 0,
                    "human_cost": case.get("medicare_human_dx_cost", 0) or 0,
                    "orders": llm_dx,
                    "human_orders": human_dx,
                })

    kitchen_sink.sort(key=lambda x: x["n_ai_tests"], reverse=True)

    print(f"\nTotal cases with >=8 diagnostic tests ordered by AI: {len(kitchen_sink)}")

    # Distribution
    test_counts = [x["n_ai_tests"] for x in kitchen_sink]
    if test_counts:
        print(f"  Range: {min(test_counts)} - {max(test_counts)} tests")
        print(f"  Mean: {statistics.mean(test_counts):.1f} tests")
        print(f"  Median: {statistics.median(test_counts):.1f} tests")

    # Model distribution
    model_counts = Counter(x["model"] for x in kitchen_sink)
    print(f"\n  By model:")
    for m, c in model_counts.most_common():
        print(f"    {m:<25} {c:>5} cases")

    # Show top examples
    print(f"\n  Top 8 most extreme 'kitchen sink' cases:")
    seen = set()
    shown = 0
    for ex in kitchen_sink:
        key = (ex["case_id"], ex["model"])
        if key in seen:
            continue
        seen.add(key)
        shown += 1
        if shown > 8:
            break

        print(f"\n  --- {ex['case_id']} ({ex['model']}) ---")
        print(f"    Specialty: {ex['specialty']}")
        print(f"    AI: {ex['n_ai_tests']} diagnostic tests (${ex['ai_cost']:.2f})")
        print(f"    Physician: {ex['n_human_tests']} diagnostic tests (${ex['human_cost']:.2f})")
        print(f"    AI-ordered tests:")
        for o in ex["orders"]:
            price = o.get("medicare_price", 0) or 0
            cpt = o.get("cpt_code") or "N/A"
            desc = o.get("cpt_description") or ""
            print(f"      [{o.get('category','?'):<10}] ${price:>8.2f}  {o['order'][:70]}")

    # Distribution of test counts across ALL cases
    print(f"\n\n  Distribution of AI diagnostic test counts (all cases, all models):")
    all_counts = []
    for model_name, cases in models.items():
        for case in cases:
            n = len(get_diagnostic_orders(case.get("medicare_llm_orders", [])))
            all_counts.append(n)

    count_dist = Counter(all_counts)
    print(f"    {'# Tests':<10} {'# Cases':<10} {'%':<8} {'Cumulative %'}")
    print(f"    {'-'*40}")
    cum = 0
    for n_tests in sorted(count_dist.keys()):
        cnt = count_dist[n_tests]
        pct = cnt / len(all_counts) * 100
        cum += pct
        if n_tests <= 15 or cnt >= 10:
            print(f"    {n_tests:<10} {cnt:<10} {pct:.1f}%    {cum:.1f}%")

    # Same for human
    print(f"\n  Distribution of PHYSICIAN diagnostic test counts (all cases, all models):")
    all_h_counts = []
    for model_name, cases in models.items():
        for case in cases:
            n = len(get_diagnostic_orders(case.get("medicare_human_orders", [])))
            all_h_counts.append(n)

    count_dist_h = Counter(all_h_counts)
    cum = 0
    print(f"    {'# Tests':<10} {'# Cases':<10} {'%':<8} {'Cumulative %'}")
    print(f"    {'-'*40}")
    for n_tests in sorted(count_dist_h.keys()):
        cnt = count_dist_h[n_tests]
        pct = cnt / len(all_h_counts) * 100
        cum += pct
        if n_tests <= 15 or cnt >= 10:
            print(f"    {n_tests:<10} {cnt:<10} {pct:.1f}%    {cum:.1f}%")


def analysis_f(models):
    """Bonus: Most common specific tests ordered by AI overall (top CPT codes)."""
    print_header("F) BONUS: TOP CPT CODES ORDERED BY AI (ALL CASES)")

    cpt_counter = Counter()
    cpt_cost = defaultdict(float)
    cpt_desc_map = {}
    cpt_cat_map = {}

    for model_name, cases in models.items():
        for case in cases:
            for o in get_diagnostic_orders(case.get("medicare_llm_orders", [])):
                cpt = o.get("cpt_code")
                if cpt:
                    cpt_counter[cpt] += 1
                    cpt_cost[cpt] += o.get("medicare_price", 0) or 0
                    if cpt not in cpt_desc_map and o.get("cpt_description"):
                        cpt_desc_map[cpt] = o["cpt_description"]
                    cpt_cat_map[cpt] = o.get("category", "unknown")

    print(f"\nTop 30 CPT codes ordered by AI across all models and cases:")
    print(f"{'Rank':<5} {'CPT':<10} {'Category':<12} {'Count':>8} {'Total Cost':>14} {'Avg Price':>12} {'Description'}")
    print("-" * 120)
    for i, (cpt, count) in enumerate(cpt_counter.most_common(30), 1):
        avg = cpt_cost[cpt] / count if count > 0 else 0
        desc = cpt_desc_map.get(cpt, "")
        cat = cpt_cat_map.get(cpt, "")
        print(f"{i:<5} {cpt:<10} {cat:<12} {count:>8} ${cpt_cost[cpt]:>12,.2f} ${avg:>10,.2f} {desc[:50]}")

    # Same for human
    h_cpt_counter = Counter()
    h_cpt_cost = defaultdict(float)
    h_cpt_desc_map = {}

    for model_name, cases in models.items():
        for case in cases:
            for o in get_diagnostic_orders(case.get("medicare_human_orders", [])):
                cpt = o.get("cpt_code")
                if cpt:
                    h_cpt_counter[cpt] += 1
                    h_cpt_cost[cpt] += o.get("medicare_price", 0) or 0
                    if cpt not in h_cpt_desc_map and o.get("cpt_description"):
                        h_cpt_desc_map[cpt] = o["cpt_description"]

    print(f"\nTop 20 CPT codes ordered by PHYSICIANS:")
    print(f"{'Rank':<5} {'CPT':<10} {'Count':>8} {'Total Cost':>14} {'Avg Price':>12} {'Description'}")
    print("-" * 100)
    for i, (cpt, count) in enumerate(h_cpt_counter.most_common(20), 1):
        avg = h_cpt_cost[cpt] / count if count > 0 else 0
        desc = h_cpt_desc_map.get(cpt, "")
        print(f"{i:<5} {cpt:<10} {count:>8} ${h_cpt_cost[cpt]:>12,.2f} ${avg:>10,.2f} {desc[:50]}")

    # Tests AI orders that physicians NEVER order
    ai_only_cpts = set(cpt_counter.keys()) - set(h_cpt_counter.keys())
    print(f"\n\nCPT codes ordered by AI but NEVER by physicians: {len(ai_only_cpts)}")
    ai_only_sorted = sorted(ai_only_cpts, key=lambda c: cpt_counter[c], reverse=True)
    print(f"{'Rank':<5} {'CPT':<10} {'Category':<12} {'AI Count':>10} {'Total Cost':>14} {'Description'}")
    print("-" * 100)
    for i, cpt in enumerate(ai_only_sorted[:20], 1):
        desc = cpt_desc_map.get(cpt, "")
        cat = cpt_cat_map.get(cpt, "")
        print(f"{i:<5} {cpt:<10} {cat:<12} {cpt_counter[cpt]:>10} ${cpt_cost[cpt]:>12,.2f} {desc[:50]}")


def analysis_g(models):
    """Per-case comparison: how many cases does AI order more vs fewer vs same tests."""
    print_header("G) PER-CASE: AI ORDERS MORE vs FEWER vs SAME NUMBER OF TESTS")

    more = 0
    fewer = 0
    same = 0
    ai_only = 0  # AI ordered, human didn't
    human_only = 0  # Human ordered, AI didn't
    both_zero = 0

    excess_tests_list = []

    for model_name, cases in models.items():
        for case in cases:
            ai_n = len(get_diagnostic_orders(case.get("medicare_llm_orders", [])))
            h_n = len(get_diagnostic_orders(case.get("medicare_human_orders", [])))

            if ai_n > h_n:
                more += 1
            elif ai_n < h_n:
                fewer += 1
            else:
                same += 1

            if ai_n > 0 and h_n == 0:
                ai_only += 1
            if h_n > 0 and ai_n == 0:
                human_only += 1
            if ai_n == 0 and h_n == 0:
                both_zero += 1

            excess_tests_list.append(ai_n - h_n)

    total = more + fewer + same
    print(f"\nAcross all model-case pairs ({total} total):")
    print(f"  AI ordered MORE tests:    {more:>6} ({more/total*100:.1f}%)")
    print(f"  AI ordered FEWER tests:   {fewer:>6} ({fewer/total*100:.1f}%)")
    print(f"  AI ordered SAME # tests:  {same:>6} ({same/total*100:.1f}%)")
    print()
    print(f"  AI ordered tests, human didn't: {ai_only:>6} ({ai_only/total*100:.1f}%)")
    print(f"  Human ordered tests, AI didn't: {human_only:>6} ({human_only/total*100:.1f}%)")
    print(f"  Neither ordered tests:          {both_zero:>6} ({both_zero/total*100:.1f}%)")
    print()
    print(f"  Mean excess tests (AI - Human): {statistics.mean(excess_tests_list):.2f}")
    print(f"  Median excess tests: {statistics.median(excess_tests_list):.1f}")


if __name__ == "__main__":
    print("Loading data from all model files...")
    models = load_all_models()
    print(f"Loaded {len(models)} AI models")
    for m, cases in sorted(models.items()):
        print(f"  {m}: {len(cases)} cases")

    analysis_a(models)
    analysis_b(models)
    analysis_c(models)
    analysis_d(models)
    analysis_e(models)
    analysis_f(models)
    analysis_g(models)

    print("\n\n" + "=" * 80)
    print("  ANALYSIS COMPLETE")
    print("=" * 80)
