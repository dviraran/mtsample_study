#!/usr/bin/env python3
"""Supplementary Figure: Inter-Extractor Agreement for diagnostic costs.

Shows pairwise scatter plots between the 3 independent LLM extractors
(GPT-4.1-mini, Claude Haiku 4.5, Gemini 2.5 Flash) for both AI and physician plans.

Reads the 24-system unified standard-prompt panel (results/models/) via
generate_paper_figures.load_unified_panel().
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'figures'))
from generate_paper_figures import load_unified_panel

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
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.dpi': 300,
})

OUT_DIR = str(ROOT / 'paper' / 'figures')

AI_COLOR = '#4393C3'
PHYS_COLOR = '#E8834A'

EXTRACTOR_NAMES = {
    'a': 'GPT-4.1-mini',
    'b': 'Claude Haiku',
    'c': 'Gemini Flash',
}


def compute_dx_cost_from_orders(orders):
    """Sum diagnostic costs from a list of extracted orders."""
    if not orders:
        return 0
    total = 0
    for o in orders:
        cat = o.get('category', '')
        if cat == 'medication':
            continue
        price = o.get('price', 0) or 0
        total += price
    return total


def get_slot_costs(all_data):
    """Extract per-slot diagnostic costs for all cases across all models."""
    rows = []
    for model, cases in all_data.items():
        for case in cases:
            for side in ['llm', 'human']:
                a = compute_dx_cost_from_orders(case.get(f'{side}_orders_a', []))
                b = compute_dx_cost_from_orders(case.get(f'{side}_orders_b', []))
                c = compute_dx_cost_from_orders(case.get(f'{side}_orders_c', []))
                rows.append({
                    'side': 'AI' if side == 'llm' else 'Physician',
                    'cost_a': a, 'cost_b': b, 'cost_c': c,
                })
    return pd.DataFrame(rows)


def make_figure(df):
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, wspace=0.30, hspace=0.35,
                           left=0.07, right=0.97, top=0.91, bottom=0.06)

    pairs = [
        ('cost_a', 'cost_b', EXTRACTOR_NAMES['a'], EXTRACTOR_NAMES['b']),
        ('cost_a', 'cost_c', EXTRACTOR_NAMES['a'], EXTRACTOR_NAMES['c']),
        ('cost_b', 'cost_c', EXTRACTOR_NAMES['b'], EXTRACTOR_NAMES['c']),
    ]

    for row_idx, (side, color) in enumerate([('AI', AI_COLOR), ('Physician', PHYS_COLOR)]):
        sub = df[df['side'] == side]
        # Filter to cases with at least one nonzero cost
        sub = sub[(sub['cost_a'] > 0) | (sub['cost_b'] > 0) | (sub['cost_c'] > 0)]

        for col_idx, (xcol, ycol, xname, yname) in enumerate(pairs):
            ax = fig.add_subplot(gs[row_idx, col_idx])

            x_vals = sub[xcol].values
            y_vals = sub[ycol].values

            ax.scatter(x_vals, y_vals, c=color, alpha=0.35, s=18,
                       edgecolors='none', rasterized=True)

            # Identity line
            max_val = max(x_vals.max(), y_vals.max()) if len(x_vals) > 0 else 2000
            ax.plot([0, max_val], [0, max_val], '--', color='#333', lw=1.2, alpha=0.5)

            # Correlation
            mask = (x_vals > 0) | (y_vals > 0)
            if np.sum(mask) > 5:
                r, _ = pearsonr(x_vals[mask], y_vals[mask])
                ax.set_title(f'{side} Plans: r = {r:.2f}', fontsize=12,
                             fontweight='bold', pad=8)

            slot_x = xcol[-1].upper()
            slot_y = ycol[-1].upper()
            ax.set_xlabel(f'Extractor {slot_x} ({xname}) ($)', fontsize=10)
            ax.set_ylabel(f'Extractor {slot_y} ({yname}) ($)', fontsize=10)
            ax.set_xlim(-10, 2050)
            ax.set_ylim(-10, 2050)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

    # Row labels on the left side
    fig.text(0.02, 0.72, 'AI Plans', fontsize=16, fontweight='bold', color=AI_COLOR,
             rotation=90, va='center', ha='center')
    fig.text(0.02, 0.28, 'Physician Plans', fontsize=16, fontweight='bold', color=PHYS_COLOR,
             rotation=90, va='center', ha='center')

    fig.suptitle('Inter-Extractor Agreement: Diagnostic Costs ($)',
                 fontsize=15, fontweight='bold', y=0.97)

    for fmt in ['png', 'pdf']:
        out = os.path.join(OUT_DIR, f'supp_extractor_agreement.{fmt}')
        fig.savefig(out, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Done: supp_extractor_agreement')


if __name__ == '__main__':
    all_data = load_unified_panel()
    df = get_slot_costs(all_data)
    make_figure(df)
