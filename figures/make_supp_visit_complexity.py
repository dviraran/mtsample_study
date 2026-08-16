#!/usr/bin/env python3
"""Supplementary figure: AI cost behavior stratified by physician ordering complexity (visit type)."""

import json
import glob
import os
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent

# ── ggplot2-inspired theme (match generate_paper_figures_v2.py) ───────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.facecolor': 'white',
    'axes.edgecolor': '#CCCCCC',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.color': '#EEEEEE',
    'grid.linewidth': 0.8,
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'xtick.major.size': 0,
    'ytick.major.size': 0,
    'legend.frameon': True,
    'legend.facecolor': 'white',
    'legend.edgecolor': '#CCCCCC',
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.dpi': 300,
})

OUT_DIR = str(ROOT / 'paper' / 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

# ── Model config (from generate_paper_figures_v2.py) ──────────────────
MODEL_INFO = {
    'claude-sonnet-3.5': {'label': 'Claude 3.5', 'family': 'Claude', 'gen': 0},
    'claude-sonnet-4.5': {'label': 'Claude 4.5', 'family': 'Claude', 'gen': 1},
    'gpt-4.1': {'label': 'GPT-4.1', 'family': 'GPT', 'gen': 0},
    'gpt-5.2': {'label': 'GPT-5.2', 'family': 'GPT', 'gen': 1},
    'gemini-2.5-pro': {'label': 'Gemini 2.5', 'family': 'Gemini', 'gen': 0},
    'gemini-3-pro': {'label': 'Gemini 3', 'family': 'Gemini', 'gen': 1},
    'grok-3': {'label': 'Grok 3', 'family': 'Grok', 'gen': 0},
    'grok-4.1': {'label': 'Grok 4.1', 'family': 'Grok', 'gen': 1},
    'llama-3.3-70b': {'label': 'Llama 3.3', 'family': 'Llama', 'gen': 0},
    'llama4': {'label': 'Llama 4', 'family': 'Llama', 'gen': 1},
    'qwen-2.5-72b': {'label': 'Qwen 2.5', 'family': 'Qwen', 'gen': 0},
    'qwen3': {'label': 'Qwen 3', 'family': 'Qwen', 'gen': 1},
    'deepseek-r1': {'label': 'DeepSeek R1', 'family': 'DeepSeek', 'gen': 1},
    'deepseek-v3.2': {'label': 'DeepSeek V3', 'family': 'DeepSeek', 'gen': 0},
    'openevidence': {'label': 'OpenEvidence', 'family': 'OpenEvidence', 'gen': 0},
    'medgemma-4b': {'label': 'MedGemma', 'family': 'MedGemma', 'gen': 0},
    'meditron': {'label': 'Meditron', 'family': 'Meditron', 'gen': 0},
}

FAMILY_COLORS = {
    'Claude': '#E8834A',
    'GPT': '#66A61E',
    'Gemini': '#3B8FD2',
    'Grok': '#7ECAE3',
    'Llama': '#9467BD',
    'Qwen': '#E15759',
    'DeepSeek': '#2D9E8E',
    'OpenEvidence': '#E377C2',
    'MedGemma': '#8C564B',
    'Meditron': '#BCBD22',
}

SPECIALIZED_MODELS = {'openevidence', 'medgemma-4b', 'meditron'}

TIER_LABELS = [
    'Follow-up\n($0)',
    'Low\n($1-100)',
    'Moderate\n($101-500)',
    'High\n(>$500)',
]

TIER_COLORS = ['#A8D5BA', '#7BB3D1', '#E8A87C', '#D16B6B']


# Cases excluded after guideline currency assessment (score 4-5)
# Includes duplicate siblings (same presentation) to ensure consistent filtering
EXCLUDED_CASES = {
    'MTS_0003', 'MTS_0013', 'MTS_0070', 'MTS_0076', 'MTS_0079', 'MTS_0089',
    'MTS_0096', 'MTS_0136', 'MTS_0151', 'MTS_0244', 'MTS_0286', 'MTS_0292',
    'MTS_0380', 'MTS_0419', 'MTS_0452', 'MTS_0655', 'MTS_0733',
    'MTS_0971', 'MTS_0976', 'MTS_0977',
    # Duplicate siblings of excluded cases (same presentation text)
    'MTS_0177', 'MTS_0246', 'MTS_0260', 'MTS_0269', 'MTS_0273',
    'MTS_0730', 'MTS_0765', 'MTS_0767', 'MTS_0883', 'MTS_1001',
}


def load_all_models():
    """Load all model result files, deduplicating by presentation (same as paper)."""
    all_data = {}
    for fpath in sorted(glob.glob(str(ROOT / 'results' / 'models_original_runs' / 'm_*.json'))):
        name = os.path.basename(fpath).replace('m_', '').replace('.json', '')
        if name not in MODEL_INFO:
            continue
        with open(fpath) as f:
            data = json.load(f)
        if 'presentation' in data[0]:
            seen = set()
            unique = []
            for c in data:
                if c.get('case_id') in EXCLUDED_CASES:
                    continue
                if c['presentation'] not in seen:
                    seen.add(c['presentation'])
                    unique.append(c)
        else:
            seen = set()
            unique = []
            for c in data:
                cid = c.get('case_id', '')
                if cid in EXCLUDED_CASES:
                    continue
                if cid not in seen:
                    seen.add(cid)
                    unique.append(c)
        all_data[name] = unique
    return all_data


def classify_tier(cost):
    """Classify a physician diagnostic cost into a tier index (0-3)."""
    if cost == 0:
        return 0
    elif cost <= 100:
        return 1
    elif cost <= 500:
        return 2
    else:
        return 3


def build_tier_data(all_data):
    """Build a DataFrame with per-case, per-model tier classification and costs.

    Uses consensus (median) physician cost across models for tier classification
    so that each case is assigned to exactly one tier.
    """
    # First pass: collect physician costs per case across all models
    from collections import defaultdict
    case_h_dx_vals = defaultdict(list)
    for model, cases in all_data.items():
        for c in cases:
            cid = c.get('case_id', '')
            h_dx = c.get('medicare_human_dx_cost') or 0
            case_h_dx_vals[cid].append(h_dx)

    # Consensus physician cost = median across models
    case_h_dx_consensus = {cid: float(np.median(vals))
                           for cid, vals in case_h_dx_vals.items()}
    case_tier = {cid: classify_tier(cost)
                 for cid, cost in case_h_dx_consensus.items()}

    # Second pass: build rows using consensus tier
    rows = []
    for model, cases in all_data.items():
        info = MODEL_INFO[model]
        for c in cases:
            cid = c.get('case_id', '')
            h_dx = case_h_dx_consensus[cid]
            l_dx = c.get('medicare_llm_dx_cost') or 0
            tier = case_tier[cid]
            excess = l_dx - h_dx
            added = 1 if l_dx > h_dx else 0
            rows.append({
                'model': model,
                'label': info['label'],
                'family': info['family'],
                'gen': info['gen'],
                'case_id': cid,
                'h_dx': h_dx,
                'l_dx': l_dx,
                'tier': tier,
                'excess': excess,
                'added': added,
            })
    return pd.DataFrame(rows)


def make_figure(df):
    """Create the 3-panel supplementary figure."""
    fig = plt.figure(figsize=(18, 7))
    gs = gridspec.GridSpec(1, 3, wspace=0.32)

    # ── Compute per-model, per-tier summaries ─────────────────────────
    model_tier = df.groupby(['model', 'tier']).agg(
        mean_excess=('excess', 'mean'),
        pct_added=('added', lambda x: 100 * x.mean()),
        mean_l_dx=('l_dx', 'mean'),
        n_cases=('case_id', 'count'),
        family=('family', 'first'),
        label=('label', 'first'),
    ).reset_index()

    # ══════════════════════════════════════════════════════════════════
    # Panel A: Mean AI excess diagnostic cost ($) by tier
    # Bar = average across models; strip overlay = individual models
    # ══════════════════════════════════════════════════════════════════
    ax_a = fig.add_subplot(gs[0])

    tier_means = model_tier.groupby('tier')['mean_excess'].mean()
    tier_sems = model_tier.groupby('tier')['mean_excess'].sem()
    x = np.arange(4)
    bars = ax_a.bar(x, [tier_means.get(t, 0) for t in range(4)],
                    color=TIER_COLORS, edgecolor='white', linewidth=0.8,
                    width=0.6, zorder=2)
    ax_a.errorbar(x, [tier_means.get(t, 0) for t in range(4)],
                  yerr=[tier_sems.get(t, 0) for t in range(4)],
                  fmt='none', ecolor='#555', capsize=4, capthick=1.2, zorder=3)

    # Strip overlay: individual model means, jittered
    rng = np.random.default_rng(42)
    for _, row in model_tier.iterrows():
        jitter = rng.uniform(-0.2, 0.2)
        color = FAMILY_COLORS.get(row['family'], '#888')
        ax_a.scatter(row['tier'] + jitter, row['mean_excess'],
                     color=color, s=22, alpha=0.55, edgecolors='white',
                     linewidth=0.4, zorder=4)

    # Tier case counts as annotations (place just below x-axis)
    tier_n = df.drop_duplicates(subset=['case_id']).groupby('tier').size()
    ymin = min(tier_means.get(t, 0) for t in range(4))
    annot_y = ymin - 0.08 * (max(tier_means.get(t, 0) for t in range(4)) - ymin)
    for t in range(4):
        n = tier_n.get(t, 0)
        ax_a.text(t, annot_y, f'n={n}', ha='center', va='top', fontsize=9, color='#666')

    ax_a.set_xticks(x)
    ax_a.set_xticklabels(TIER_LABELS, fontsize=10)
    ax_a.set_ylabel('Mean AI Excess Diagnostic Cost ($)', fontsize=11)
    ax_a.set_title('A    AI Excess Cost by Visit Complexity',
                    fontsize=13, fontweight='bold', loc='left', pad=10)
    ax_a.axhline(0, color='#333', linestyle='--', lw=1, alpha=0.5, zorder=1)
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)

    # ══════════════════════════════════════════════════════════════════
    # Panel B: % of cases where AI added tests, grouped by model family
    # ══════════════════════════════════════════════════════════════════
    ax_b = fig.add_subplot(gs[1])

    # Group by family for cleaner display
    family_tier = df.groupby(['family', 'tier']).agg(
        pct_added=('added', lambda x: 100 * x.mean()),
    ).reset_index()

    families = sorted(family_tier['family'].unique())
    n_fam = len(families)
    bar_w = 0.7 / n_fam
    offsets = np.linspace(-0.35 + bar_w/2, 0.35 - bar_w/2, n_fam)

    for j, fam in enumerate(families):
        sub = family_tier[family_tier['family'] == fam]
        vals = [sub[sub['tier'] == t]['pct_added'].values[0]
                if len(sub[sub['tier'] == t]) > 0 else 0 for t in range(4)]
        color = FAMILY_COLORS.get(fam, '#888')
        ax_b.bar(x + offsets[j], vals, width=bar_w, color=color,
                 edgecolor='white', linewidth=0.3, alpha=0.85, label=fam, zorder=2)

    ax_b.set_xticks(x)
    ax_b.set_xticklabels(TIER_LABELS, fontsize=10)
    ax_b.set_ylabel('Cases Where AI Added Tests (%)', fontsize=11)
    ax_b.set_title('B    AI Over-Ordering Rate by Family',
                    fontsize=13, fontweight='bold', loc='left', pad=10)
    ax_b.legend(fontsize=7.5, ncol=2, loc='upper right',
                framealpha=0.9, handlelength=1.2, handletextpad=0.4,
                columnspacing=0.8)
    ax_b.set_ylim(0, 105)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)

    # ══════════════════════════════════════════════════════════════════
    # Panel C: Box plots of per-case AI diagnostic cost, faceted by tier
    # ══════════════════════════════════════════════════════════════════
    ax_c = fig.add_subplot(gs[2])

    # For each tier, collect all per-case AI costs (across models, take median per case first)
    case_medians = df.groupby(['case_id', 'tier'])['l_dx'].median().reset_index()

    bp_data = [case_medians[case_medians['tier'] == t]['l_dx'].values for t in range(4)]
    bp = ax_c.boxplot(bp_data, positions=x, widths=0.5, patch_artist=True,
                      showfliers=True, flierprops=dict(marker='o', markersize=3,
                      markerfacecolor='#999', markeredgecolor='none', alpha=0.5))

    for patch, color in zip(bp['boxes'], TIER_COLORS):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor('#555')
    for element in ['whiskers', 'caps']:
        for line in bp[element]:
            line.set_color('#555')
            line.set_linewidth(1)
    for line in bp['medians']:
        line.set_color('#333')
        line.set_linewidth(1.5)

    # Use symlog scale to show both low and high values clearly
    ax_c.set_yscale('symlog', linthresh=50, linscale=0.5)
    ax_c.set_ylabel('AI Diagnostic Cost per Case ($, symlog)', fontsize=11)

    # Overlay physician average per tier as diamonds
    phys_means = df.drop_duplicates(subset=['case_id']).groupby('tier')['h_dx'].mean()
    for t in range(4):
        if t in phys_means.index:
            ax_c.scatter(t, phys_means[t], marker='D', s=60, color='#333',
                         zorder=5, edgecolors='white', linewidth=1)

    ax_c.scatter([], [], marker='D', s=60, color='#333', edgecolors='white',
                 linewidth=1, label='Physician mean')
    ax_c.legend(fontsize=9, loc='upper left', framealpha=0.9)

    ax_c.set_xticks(x)
    ax_c.set_xticklabels(TIER_LABELS, fontsize=10)
    # ylabel already set above with symlog note
    ax_c.set_title('C    AI Cost Distribution by Tier',
                    fontsize=13, fontweight='bold', loc='left', pad=10)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)

    # ── Save ──────────────────────────────────────────────────────────
    fig.tight_layout()
    for ext in ['png', 'pdf']:
        fpath = os.path.join(OUT_DIR, f'supp_visit_complexity.{ext}')
        fig.savefig(fpath, bbox_inches='tight', dpi=300)
        print(f'Saved: {fpath}')
    plt.close(fig)


def print_summary(df):
    """Print summary statistics for verification."""
    print('\n── Summary by Tier ──')
    tier_n = df.drop_duplicates(subset=['case_id', 'tier']).groupby('tier').size()
    for t in range(4):
        sub = df[df['tier'] == t]
        n_cases = tier_n.get(t, 0)
        mean_excess = sub.groupby('model')['excess'].mean().mean()
        pct_added = 100 * sub.groupby('model')['added'].mean().mean()
        mean_ai = sub['l_dx'].mean()
        mean_phys = sub['h_dx'].mean()
        print(f'  Tier {t} ({TIER_LABELS[t].replace(chr(10), " ")}): '
              f'{n_cases} cases, '
              f'Phys avg=${mean_phys:.0f}, '
              f'AI avg=${mean_ai:.0f}, '
              f'Excess=${mean_excess:.0f}, '
              f'Over-ordered={pct_added:.0f}%')


if __name__ == '__main__':
    print('Loading model data...')
    all_data = load_all_models()
    print(f'Loaded {len(all_data)} models')

    df = build_tier_data(all_data)
    print(f'Built DataFrame: {len(df)} rows, {df["model"].nunique()} models, '
          f'{df["case_id"].nunique()} unique cases')

    print_summary(df)
    make_figure(df)
    print('\nDone.')
