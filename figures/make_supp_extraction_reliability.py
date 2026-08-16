#!/usr/bin/env python3
"""Supplementary Figure: Reliability of the 3-extraction order extraction process.

Each physician and AI plan was independently extracted 3 times (slots a, b, c)
and the median cost was used. This figure shows consistency across extractions.

Panels:
  A – Distribution of per-case coefficient of variation (CV), AI vs Physician
  B – Pairwise scatter plots (slot A vs B, A vs C, B vs C) for diagnostic costs
  C – Mean pairwise Pearson correlation by model
"""

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
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent

# ── ggplot2-inspired theme (matching paper style) ──────────────────────
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

# ── Model config (matching paper) ─────────────────────────────────────
MODEL_INFO = {
    'claude-sonnet-3.5': {'label': 'Claude 3.5', 'family': 'Claude'},
    'claude-sonnet-4.5': {'label': 'Claude 4.5', 'family': 'Claude'},
    'gpt-4.1': {'label': 'GPT-4.1', 'family': 'GPT'},
    'gpt-5.2': {'label': 'GPT-5.2', 'family': 'GPT'},
    'gemini-2.5-pro': {'label': 'Gemini 2.5', 'family': 'Gemini'},
    'gemini-3-pro': {'label': 'Gemini 3', 'family': 'Gemini'},
    'grok-3': {'label': 'Grok 3', 'family': 'Grok'},
    'grok-4.1': {'label': 'Grok 4.1', 'family': 'Grok'},
    'llama-3.3-70b': {'label': 'Llama 3.3', 'family': 'Llama'},
    'llama4': {'label': 'Llama 4', 'family': 'Llama'},
    'qwen-2.5-72b': {'label': 'Qwen 2.5', 'family': 'Qwen'},
    'qwen3': {'label': 'Qwen 3', 'family': 'Qwen'},
    'deepseek-r1': {'label': 'DeepSeek R1', 'family': 'DeepSeek'},
    'deepseek-v3.2': {'label': 'DeepSeek V3', 'family': 'DeepSeek'},
    'openevidence': {'label': 'OpenEvidence', 'family': 'OpenEvidence'},
    'medgemma-4b': {'label': 'MedGemma', 'family': 'MedGemma'},
    'meditron': {'label': 'Meditron', 'family': 'Meditron'},
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

AI_COLOR = '#4393C3'
PHYS_COLOR = '#E8834A'


# ── Data loading ──────────────────────────────────────────────────────
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
    all_data = {}
    for fpath in sorted(glob.glob(str(ROOT / 'results' / 'models_original_runs' / 'm_*.json'))):
        name = os.path.basename(fpath).replace('m_', '').replace('.json', '')
        if name not in MODEL_INFO:
            continue
        with open(fpath) as f:
            data = json.load(f)
        # De-duplicate by presentation, excluding guideline-outdated cases
        seen = set()
        unique = []
        for c in data:
            if c.get('case_id') in EXCLUDED_CASES:
                continue
            p = c.get('presentation', '')
            if p not in seen:
                seen.add(p)
                unique.append(c)
        all_data[name] = unique
    return all_data


def compute_slot_costs_from_orders(case, side, slot):
    """Compute diagnostic cost for a given slot from the per-slot orders.

    Uses the 'price' field if available (non-medicare pricing), falling back
    to summing individual order prices.
    """
    orders = case.get(f'{side}_orders_{slot}', []) or []
    total = 0
    for o in orders:
        cat = o.get('category', '')
        if cat == 'medication':
            continue  # Only diagnostic costs
        price = o.get('price', 0) or 0
        total += price
    return total


def extract_slot_data(all_data):
    """Build a DataFrame with per-slot costs for every case x model."""
    rows = []
    for model, cases in all_data.items():
        label = MODEL_INFO[model]['label']
        family = MODEL_INFO[model]['family']
        for case in cases:
            case_id = case.get('case_id', case.get('presentation', '')[:40])
            for side, side_label in [('llm', 'AI'), ('human', 'Physician')]:
                a = case.get(f'{side}_dx_cost_a', 0) or 0
                b = case.get(f'{side}_dx_cost_b', 0) or 0
                c = case.get(f'{side}_dx_cost_c', 0) or 0
                costs = [a, b, c]
                mean_val = np.mean(costs)
                std_val = np.std(costs, ddof=0)
                cv = (std_val / mean_val * 100) if mean_val > 0 else 0.0
                rows.append({
                    'model': model,
                    'label': label,
                    'family': family,
                    'case_id': case_id,
                    'side': side_label,
                    'cost_a': a,
                    'cost_b': b,
                    'cost_c': c,
                    'mean_cost': mean_val,
                    'std_cost': std_val,
                    'cv': cv,
                })
    return pd.DataFrame(rows)


def compute_pairwise_correlations(df_slots):
    """Compute pairwise Pearson correlations between slots for each model x side."""
    results = []
    for (model, side), grp in df_slots.groupby(['model', 'side']):
        # Only use cases where at least one slot is nonzero
        mask = (grp['cost_a'] > 0) | (grp['cost_b'] > 0) | (grp['cost_c'] > 0)
        g = grp[mask]
        if len(g) < 5:
            continue
        pairs = [('cost_a', 'cost_b'), ('cost_a', 'cost_c'), ('cost_b', 'cost_c')]
        pair_rs = []
        for x_col, y_col in pairs:
            x, y = g[x_col].values, g[y_col].values
            if np.std(x) > 0 and np.std(y) > 0:
                r, _ = pearsonr(x, y)
                pair_rs.append(r)
        if pair_rs:
            results.append({
                'model': model,
                'label': MODEL_INFO[model]['label'],
                'family': MODEL_INFO[model]['family'],
                'side': side,
                'mean_r': np.mean(pair_rs),
                'min_r': np.min(pair_rs),
                'max_r': np.max(pair_rs),
                'n_cases': len(g),
            })
    return pd.DataFrame(results)


# ── Figure creation ───────────────────────────────────────────────────
def make_figure(df_slots, df_corr):
    fig = plt.figure(figsize=(18, 14))
    gs = gridspec.GridSpec(2, 3, wspace=0.32, hspace=0.30,
                           left=0.06, right=0.97, top=0.94, bottom=0.06)

    # ═══ Panel A: CV distribution (violin + box), AI vs Physician ═══
    ax_a = fig.add_subplot(gs[0, 0])

    # Filter to cases with at least one nonzero slot
    df_nonzero = df_slots[(df_slots['cost_a'] > 0) | (df_slots['cost_b'] > 0) | (df_slots['cost_c'] > 0)].copy()

    # Separate AI and Physician
    ai_cv = df_nonzero[df_nonzero['side'] == 'AI']['cv'].values
    phys_cv = df_nonzero[df_nonzero['side'] == 'Physician']['cv'].values

    # Cap extreme CVs for visualization (some edge cases have CV > 150)
    ai_cv_capped = np.clip(ai_cv, 0, 150)
    phys_cv_capped = np.clip(phys_cv, 0, 150)

    parts_ai = ax_a.violinplot([ai_cv_capped], positions=[1], showextrema=False, widths=0.7)
    parts_phys = ax_a.violinplot([phys_cv_capped], positions=[2], showextrema=False, widths=0.7)

    for pc in parts_ai['bodies']:
        pc.set_facecolor(AI_COLOR)
        pc.set_alpha(0.4)
        pc.set_edgecolor(AI_COLOR)
    for pc in parts_phys['bodies']:
        pc.set_facecolor(PHYS_COLOR)
        pc.set_alpha(0.4)
        pc.set_edgecolor(PHYS_COLOR)

    # Overlay box plots
    bp = ax_a.boxplot([ai_cv_capped, phys_cv_capped], positions=[1, 2],
                      widths=0.25, patch_artist=True, showfliers=False,
                      medianprops=dict(color='white', linewidth=2),
                      whiskerprops=dict(color='#555', linewidth=1),
                      capprops=dict(color='#555', linewidth=1))
    bp['boxes'][0].set_facecolor(AI_COLOR)
    bp['boxes'][0].set_alpha(0.8)
    bp['boxes'][1].set_facecolor(PHYS_COLOR)
    bp['boxes'][1].set_alpha(0.8)

    ax_a.set_xticks([1, 2])
    ax_a.set_xticklabels(['AI Plans', 'Physician Plans'], fontsize=11)
    ax_a.set_ylabel('Coefficient of Variation (%)', fontsize=11)
    ax_a.set_title('A    Extraction Variability (CV)', fontsize=13,
                    fontweight='bold', loc='left', pad=10)

    # Add summary stats
    ai_median = np.median(ai_cv)
    phys_median = np.median(phys_cv)
    ax_a.text(1, max(ai_cv_capped) * 0.95,
              f'Median: {ai_median:.1f}%\nn = {len(ai_cv):,}',
              ha='center', fontsize=9, color=AI_COLOR, fontweight='bold',
              bbox=dict(facecolor='white', edgecolor=AI_COLOR, alpha=0.8, pad=3))
    ax_a.text(2, max(phys_cv_capped) * 0.95,
              f'Median: {phys_median:.1f}%\nn = {len(phys_cv):,}',
              ha='center', fontsize=9, color=PHYS_COLOR, fontweight='bold',
              bbox=dict(facecolor='white', edgecolor=PHYS_COLOR, alpha=0.8, pad=3))

    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)

    # ═══ Panel B: Pairwise scatter plots ═══
    # B1: Slot A vs Slot B
    pairs = [('cost_a', 'cost_b', 'B1', 'Slot A vs Slot B'),
             ('cost_a', 'cost_c', 'B2', 'Slot A vs Slot C'),
             ('cost_b', 'cost_c', 'B3', 'Slot B vs Slot C')]

    for idx, (xcol, ycol, panel_lbl, title) in enumerate(pairs):
        ax = fig.add_subplot(gs[0, 1]) if idx == 0 else fig.add_subplot(gs[0, 2]) if idx == 1 else fig.add_subplot(gs[1, 0])

        # Pool all models together, separate by side
        for side, color, marker, alpha in [('AI', AI_COLOR, 'o', 0.25),
                                            ('Physician', PHYS_COLOR, 's', 0.25)]:
            sub = df_nonzero[df_nonzero['side'] == side]
            x_vals = sub[xcol].values
            y_vals = sub[ycol].values

            ax.scatter(x_vals, y_vals, c=color, alpha=alpha, s=12,
                       edgecolors='none', marker=marker, label=side, rasterized=True)

        # Identity line
        max_val = max(df_nonzero[xcol].max(), df_nonzero[ycol].max())
        ax.plot([0, max_val], [0, max_val], '--', color='#333', lw=1.2, alpha=0.7, zorder=5)

        # Correlation text
        for side, color, yoff in [('AI', AI_COLOR, 0.92), ('Physician', PHYS_COLOR, 0.84)]:
            sub = df_nonzero[df_nonzero['side'] == side]
            x_vals = sub[xcol].values
            y_vals = sub[ycol].values
            mask = (x_vals > 0) | (y_vals > 0)
            if np.sum(mask) > 5 and np.std(x_vals[mask]) > 0 and np.std(y_vals[mask]) > 0:
                r, p = pearsonr(x_vals[mask], y_vals[mask])
                ax.text(0.03, yoff, f'{side}: r = {r:.3f}',
                        transform=ax.transAxes, fontsize=9, color=color,
                        fontweight='bold',
                        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

        slot_name_x = xcol.replace('cost_', 'Slot ').replace('a', 'A').replace('b', 'B').replace('c', 'C')
        slot_name_y = ycol.replace('cost_', 'Slot ').replace('a', 'A').replace('b', 'B').replace('c', 'C')
        ax.set_xlabel(f'{slot_name_x} Diagnostic Cost ($)', fontsize=10)
        ax.set_ylabel(f'{slot_name_y} Diagnostic Cost ($)', fontsize=10)
        ax.set_title(f'{panel_lbl}    {title}', fontsize=13,
                     fontweight='bold', loc='left', pad=10)
        ax.set_xlim(left=-10)
        ax.set_ylim(bottom=-10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if idx == 0:
            ax.legend(loc='lower right', fontsize=9, markerscale=2,
                      framealpha=0.9)

    # ═══ Panel C: Mean pairwise correlation by model (AI plans only) ═══
    ax_c = fig.add_subplot(gs[1, 1])

    df_ai_corr = df_corr[df_corr['side'] == 'AI'].sort_values('mean_r').reset_index(drop=True)
    y_pos = np.arange(len(df_ai_corr))
    bar_h = 0.65

    for i, (_, row) in enumerate(df_ai_corr.iterrows()):
        color = FAMILY_COLORS.get(row['family'], '#888')
        ax_c.barh(i, row['mean_r'], height=bar_h, color=color, alpha=0.85,
                  edgecolor='white', linewidth=0.5)
        # Error bar showing range
        ax_c.plot([row['min_r'], row['max_r']], [i, i], color='#333',
                  linewidth=1.5, solid_capstyle='round')
        ax_c.text(max(row['max_r'] + 0.01, row['mean_r'] + 0.01), i,
                  f'{row["mean_r"]:.3f}', fontsize=8.5, va='center',
                  fontweight='bold', color='#333')

    ax_c.set_yticks(y_pos)
    ax_c.set_yticklabels(df_ai_corr['label'], fontsize=10)
    ax_c.set_xlabel('Mean Pairwise Pearson r', fontsize=10.5)
    ax_c.set_title('C    Extraction Correlation by Model (AI Plans)', fontsize=13,
                    fontweight='bold', loc='left', pad=10)
    ax_c.axvline(x=1.0, color='#333', linestyle='--', lw=1, alpha=0.3)
    # Set reasonable x limit
    min_r = df_ai_corr['min_r'].min()
    ax_c.set_xlim(max(0, min_r - 0.05), 1.02)
    ax_c.set_ylim(-0.8, len(df_ai_corr) - 0.2)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)

    # ═══ Panel D: Fraction of cases with perfect agreement (CV=0) ═══
    ax_d = fig.add_subplot(gs[1, 2])

    perfect_rows = []
    for model in MODEL_INFO:
        sub = df_slots[df_slots['model'] == model]
        for side in ['AI', 'Physician']:
            s = sub[sub['side'] == side]
            # Cases where at least one slot is nonzero
            nonzero = s[(s['cost_a'] > 0) | (s['cost_b'] > 0) | (s['cost_c'] > 0)]
            if len(nonzero) == 0:
                continue
            # Perfect agreement: all 3 slots identical
            perfect = nonzero[nonzero['cv'] == 0]
            # Near-perfect: CV < 10%
            near = nonzero[nonzero['cv'] < 10]
            perfect_rows.append({
                'model': model,
                'label': MODEL_INFO[model]['label'],
                'family': MODEL_INFO[model]['family'],
                'side': side,
                'pct_perfect': 100 * len(perfect) / len(nonzero),
                'pct_near': 100 * len(near) / len(nonzero),
                'n_nonzero': len(nonzero),
            })
    df_perf = pd.DataFrame(perfect_rows)

    # Show AI vs Physician as grouped bars
    ai_perf = df_perf[df_perf['side'] == 'AI'].sort_values('pct_perfect').reset_index(drop=True)
    phys_perf = df_perf[df_perf['side'] == 'Physician']

    y_pos2 = np.arange(len(ai_perf))
    bar_w = 0.35

    for i, (_, row) in enumerate(ai_perf.iterrows()):
        color = FAMILY_COLORS.get(row['family'], '#888')
        ax_d.barh(i + bar_w/2, row['pct_perfect'], height=bar_w,
                  color=color, alpha=0.85, edgecolor='white', linewidth=0.5)

        # Find matching physician data
        phys_row = phys_perf[phys_perf['model'] == row['model']]
        if len(phys_row) > 0:
            pval = phys_row.iloc[0]['pct_perfect']
            ax_d.barh(i - bar_w/2, pval, height=bar_w,
                      color=color, alpha=0.35, edgecolor=color, linewidth=1,
                      hatch='///')

    ax_d.set_yticks(y_pos2)
    ax_d.set_yticklabels(ai_perf['label'], fontsize=10)
    ax_d.set_xlabel('Cases With Perfect Agreement (%)', fontsize=10.5)
    ax_d.set_title('D    Perfect Agreement Across Extractions', fontsize=13,
                    fontweight='bold', loc='left', pad=10)
    ax_d.set_ylim(-0.8, len(ai_perf) - 0.2)
    ax_d.spines['top'].set_visible(False)
    ax_d.spines['right'].set_visible(False)

    # Legend for D
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#999', alpha=0.85, label='AI Plans'),
        Patch(facecolor='#999', alpha=0.35, edgecolor='#999', hatch='///', label='Physician Plans'),
    ]
    ax_d.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)

    # ── Global title ──
    fig.suptitle('Supplementary Figure: Reliability of Structured Order Extraction',
                 fontsize=15, fontweight='bold', y=0.98)

    # Save
    for fmt in ['png', 'pdf']:
        out = os.path.join(OUT_DIR, f'supp_extraction_reliability.{fmt}')
        fig.savefig(out, bbox_inches='tight', dpi=300)
        print(f'Saved {out}')
    plt.close(fig)


# ── Summary statistics ────────────────────────────────────────────────
def print_summary(df_slots, df_corr):
    df_nz = df_slots[(df_slots['cost_a'] > 0) | (df_slots['cost_b'] > 0) | (df_slots['cost_c'] > 0)]

    print('\n=== EXTRACTION RELIABILITY SUMMARY ===\n')

    for side in ['AI', 'Physician']:
        sub = df_nz[df_nz['side'] == side]
        # Also filter to cases where ALL 3 slots are nonzero
        all3 = sub[(sub['cost_a'] > 0) & (sub['cost_b'] > 0) & (sub['cost_c'] > 0)]
        print(f'{side} Plans (any slot > 0):')
        print(f'  N observations (case x model): {len(sub):,}')
        print(f'  Median CV: {sub["cv"].median():.1f}%')
        print(f'  Mean CV: {sub["cv"].mean():.1f}%')
        print(f'  % perfect agreement (CV=0): {100 * (sub["cv"] == 0).mean():.1f}%')
        print(f'  % near-perfect (CV<10%): {100 * (sub["cv"] < 10).mean():.1f}%')
        print(f'{side} Plans (all 3 slots > 0):')
        print(f'  N observations: {len(all3):,}')
        if len(all3) > 0:
            print(f'  Median CV: {all3["cv"].median():.1f}%')
            print(f'  Mean CV: {all3["cv"].mean():.1f}%')
            print(f'  % perfect agreement (CV=0): {100 * (all3["cv"] == 0).mean():.1f}%')
            print(f'  % near-perfect (CV<10%): {100 * (all3["cv"] < 10).mean():.1f}%')
        print()

    print('Pairwise correlations (AI Plans):')
    ai_corr = df_corr[df_corr['side'] == 'AI']
    print(f'  Overall mean r: {ai_corr["mean_r"].mean():.3f}')
    print(f'  Range: {ai_corr["mean_r"].min():.3f} - {ai_corr["mean_r"].max():.3f}')
    print()

    print('Pairwise correlations (Physician Plans):')
    ph_corr = df_corr[df_corr['side'] == 'Physician']
    print(f'  Overall mean r: {ph_corr["mean_r"].mean():.3f}')
    print(f'  Range: {ph_corr["mean_r"].min():.3f} - {ph_corr["mean_r"].max():.3f}')
    print()


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('Loading model data...')
    all_data = load_all_models()
    print(f'Loaded {len(all_data)} models')

    print('Extracting per-slot costs...')
    df_slots = extract_slot_data(all_data)
    print(f'Total observations: {len(df_slots):,}')

    print('Computing pairwise correlations...')
    df_corr = compute_pairwise_correlations(df_slots)

    print_summary(df_slots, df_corr)

    print('Generating figure...')
    make_figure(df_slots, df_corr)
    print('Done.')
