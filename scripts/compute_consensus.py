#!/usr/bin/env python3
"""Compute consensus-based diagnostic agreement metrics.

Three-tier agreement: concordant / adjacent / discordant
Case Consensus Index (CCI): fraction of models concordant or adjacent per case
Stratified concordance by CCI difficulty tier
"""

import json
import glob
import os
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
import sys

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = str(ROOT / 'results')
MODELS_DIR = str(ROOT / 'results' / 'models_original_runs')
ANALYSIS_DIR = str(ROOT / 'results' / 'analysis')

# Unified 24-system panel + 3-judge majority labels: reuse the single source of
# truth in the figure module rather than re-deriving them here.
sys.path.insert(0, str(ROOT / 'figures'))
from generate_paper_figures import load_unified_panel, majority_label, MODEL_INFO as _GP_INFO

MODEL_INFO = {m: info['label'] for m, info in _GP_INFO.items()}


def classify_3tier(dx_match_v2):
    """Collapse 4-category to 3-tier."""
    if dx_match_v2 in ('correct', 'correct_plus'):
        return 'concordant'
    elif dx_match_v2 == 'related':
        return 'adjacent'
    elif dx_match_v2 == 'wrong':
        return 'discordant'
    return None


def main():
    # Step 1: Load all ratings
    # Key by presentation text to deduplicate cases that share the same
    # clinical vignette but have different case_ids (315 -> 220 unique).
    case_ratings = defaultdict(dict)  # presentation -> {model: dx_match_v2}
    case_meta = {}  # presentation -> {case_id, sample_name, specialty, ...}

    # The unified panel is already deduped by presentation and excludes the 20
    # guideline-outdated cases. Each (case, model) rating is the 3-judge majority
    # ('correct'/'related'/'wrong'), mapped to the 3-tier scheme by classify_3tier.
    all_data = load_unified_panel()
    for name, cases in all_data.items():
        for c in cases:
            key = c.get('presentation', '') or c.get('case_id', '')
            if not key:
                continue
            rating = majority_label(c)  # correct / related / wrong / unknown
            if rating and rating != 'unknown':
                case_ratings[key][name] = rating
            if key not in case_meta:
                case_meta[key] = {
                    'case_id': c.get('case_id', ''),
                    'sample_name': c.get('sample_name', ''),
                    'specialty': c.get('specialty', ''),
                }

    print(f'Loaded {len(case_ratings)} cases across {len(all_data)} models\n')

    # Step 2: Compute CCI per case (all 17 models)
    case_consensus = {}
    for cid, ratings in case_ratings.items():
        n_models = len(ratings)
        if n_models < 10:  # require sufficient coverage
            continue

        tiers = {m: classify_3tier(r) for m, r in ratings.items()}
        n_concordant = sum(1 for t in tiers.values() if t == 'concordant')
        n_adjacent = sum(1 for t in tiers.values() if t == 'adjacent')
        n_discordant = sum(1 for t in tiers.values() if t == 'discordant')

        cci = (n_concordant + n_adjacent) / n_models  # fraction not-wrong
        cci_strict = n_concordant / n_models  # fraction concordant only

        # Use strict CCI (concordant only) for tiers — better discrimination
        if cci_strict >= 0.85:
            tier = 'high'
        elif cci_strict >= 0.50:
            tier = 'moderate'
        else:
            tier = 'low'

        case_consensus[cid] = {
            'cci': round(cci, 3),
            'cci_strict': round(cci_strict, 3),
            'tier': tier,
            'n_concordant': n_concordant,
            'n_adjacent': n_adjacent,
            'n_discordant': n_discordant,
            'n_models': n_models,
            **case_meta.get(cid, {}),
        }

    # Step 3: Tier distribution
    tier_counts = Counter(c['tier'] for c in case_consensus.values())
    print(f'=== Case Difficulty Tiers (N={len(case_consensus)}) ===')
    for tier in ['high', 'moderate', 'low']:
        n = tier_counts[tier]
        print(f'  {tier:>10}: {n} ({100 * n / len(case_consensus):.0f}%)')

    print(f'\n=== CCI Distribution ===')
    ccis = [c['cci'] for c in case_consensus.values()]
    print(f'  Mean: {np.mean(ccis):.2f}, Median: {np.median(ccis):.2f}')
    print(f'  Min: {min(ccis):.2f}, Max: {max(ccis):.2f}')

    # Step 4: Per-model stratified concordance
    print(f'\n=== Per-Model Concordance (3-tier) ===\n')
    print(f'{"Model":<17} {"Overall":>8} {"High":>8} {"Moderate":>8} {"Low":>8}  '
          f'{"Conc":>5} {"Adj":>5} {"Disc":>5}')
    print('-' * 80)

    model_summary = {}
    for name in sorted(MODEL_INFO.keys(), key=lambda x: MODEL_INFO[x]):
        label = MODEL_INFO[name]
        by_tier = {'high': [0, 0], 'moderate': [0, 0], 'low': [0, 0]}
        n_conc = n_adj = n_disc = 0

        for cid, consensus in case_consensus.items():
            if name not in case_ratings[cid]:
                continue
            rating = case_ratings[cid][name]
            tier3 = classify_3tier(rating)
            tier = consensus['tier']

            by_tier[tier][1] += 1  # total in tier
            if tier3 == 'concordant':
                by_tier[tier][0] += 1  # concordant in tier
                n_conc += 1
            elif tier3 == 'adjacent':
                n_adj += 1
            elif tier3 == 'discordant':
                n_disc += 1

        total = n_conc + n_adj + n_disc
        overall = n_conc / total * 100 if total else 0

        tier_pcts = {}
        for t in ['high', 'moderate', 'low']:
            if by_tier[t][1] > 0:
                tier_pcts[t] = by_tier[t][0] / by_tier[t][1] * 100
            else:
                tier_pcts[t] = 0

        model_summary[name] = {
            'label': label,
            'concordance_overall': round(overall, 1),
            'concordance_high': round(tier_pcts['high'], 1),
            'concordance_moderate': round(tier_pcts['moderate'], 1),
            'concordance_low': round(tier_pcts['low'], 1),
            'n_concordant': n_conc,
            'n_adjacent': n_adj,
            'n_discordant': n_disc,
            'n_total': total,
            'pct_concordant': round(n_conc / total * 100, 1) if total else 0,
            'pct_adjacent': round(n_adj / total * 100, 1) if total else 0,
            'pct_discordant': round(n_disc / total * 100, 1) if total else 0,
            'n_per_tier': {t: by_tier[t][1] for t in ['high', 'moderate', 'low']},
        }

        print(f'{label:<17} {overall:>7.0f}% {tier_pcts["high"]:>7.0f}% '
              f'{tier_pcts["moderate"]:>7.0f}% {tier_pcts["low"]:>7.0f}%  '
              f'{n_conc:>5} {n_adj:>5} {n_disc:>5}')

    # Step 5: Show low-consensus cases
    print(f'\n=== Low Consensus Cases (CCI < 0.50) ===\n')
    low_cases = [(key, c) for key, c in case_consensus.items() if c['tier'] == 'low']
    low_cases.sort(key=lambda x: x[1]['cci'])
    for key, c in low_cases[:15]:
        cid_label = c.get('case_id', key)
        print(f'{cid_label} ({c.get("sample_name", "")[:40]:40s}) '
              f'CCI={c["cci"]:.2f} ({c["n_concordant"]}C/{c["n_adjacent"]}A/{c["n_discordant"]}D)')

    # Step 6: Save outputs — re-key case_consensus by case_id for readability
    case_consensus_out = {}
    for key, c in case_consensus.items():
        cid_out = c.get('case_id', key)
        case_consensus_out[cid_out] = c

    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    with open(f'{ANALYSIS_DIR}/case_consensus.json', 'w') as f:
        json.dump(case_consensus_out, f, indent=2)
    with open(f'{ANALYSIS_DIR}/model_agreement_summary.json', 'w') as f:
        json.dump(model_summary, f, indent=2)

    print(f'\nSaved: {ANALYSIS_DIR}/case_consensus.json ({len(case_consensus_out)} cases)')
    print(f'Saved: {ANALYSIS_DIR}/model_agreement_summary.json ({len(model_summary)} models)')


if __name__ == '__main__':
    main()
