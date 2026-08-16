"""Re-price all diagnostic orders in slots A/B/C using updated price_order with supplementary dict."""
import sys, os, json, statistics, tempfile, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "malpractice"))
sys.path.insert(0, str(ROOT / "scripts"))

from cost.analyzer import CostAnalyzer
from reprice_medicare import price_order, DIAGNOSTIC_CATEGORIES

print("Loading pricing system...")
analyzer = CostAnalyzer()
print("Ready.\n")

RESULTS_DIR = ROOT / "results" / "models_original_runs"

MODEL_FILES = sorted(RESULTS_DIR.glob("m_*.json"))

for fpath in MODEL_FILES:
    if fpath.name == 'm_human.json':
        continue
    with open(fpath) as f:
        data = json.load(f)
    
    changes = 0
    for r in data:
        slot_costs = {}
        for slot in ['a', 'b', 'c']:
            for side in ['human', 'llm']:
                orders = r.get(f'{side}_orders_{slot}', []) or []
                dx_total = 0
                for o in orders:
                    cat = o.get('category', '')
                    if cat not in DIAGNOSTIC_CATEGORIES:
                        continue
                    priced = price_order(o.get('order', ''), analyzer, category=cat)
                    dx_total += priced.get('medicare_price', 0) or 0
                slot_costs[(side, slot)] = dx_total
        
        for side in ['human', 'llm']:
            costs = [slot_costs.get((side, s), 0) for s in ['a', 'b', 'c']]
            old = r.get(f'medicare_{side}_dx_cost', 0) or 0
            new = statistics.median(costs)
            if abs(new - old) > 0.01:
                changes += 1
            r[f'medicare_{side}_dx_cost'] = new
    
    tmp_fd = tempfile.NamedTemporaryFile(
        mode="w", dir=fpath.parent, suffix=".tmp", delete=False
    )
    try:
        json.dump(data, tmp_fd, indent=2)
        tmp_fd.close()
        os.replace(tmp_fd.name, fpath)
    except BaseException:
        tmp_fd.close()
        os.unlink(tmp_fd.name)
        raise

    seen = set()
    u = []
    for c in data:
        key = c.get('presentation', '')
        if key and key not in seen:
            seen.add(key)
            u.append(c)
    h = np.mean([c.get('medicare_human_dx_cost', 0) for c in u])
    l = np.mean([float(c.get('medicare_llm_dx_cost') or 0) for c in u])
    print(f"{fpath.name:30s} H=${h:.0f} L=${l:.0f} ratio={l/h:.2f}x  ({changes} changed)")

print("\nDone.")
