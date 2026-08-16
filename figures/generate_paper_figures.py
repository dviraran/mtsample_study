#!/usr/bin/env python3
"""Generate publication-quality figures for NEJM AI paper — ggplot2 style."""

import json
import glob
import os
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent

# ── ggplot2-inspired theme ─────────────────────────────────────────────
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

# ── Model config ───────────────────────────────────────────────────────
# gen = within-family version-recency index (0 = oldest evaluated version). Families now
# span 2-4 versions; "newest per family" is computed as the max gen within each family
# rather than a fixed gen==1, since the unified panel adds the newest frontier releases.
MODEL_INFO = {
    'claude-sonnet-3.5': {'label': 'Claude 3.5', 'family': 'Claude', 'gen': 0},
    'claude-sonnet-4.5': {'label': 'Claude 4.5', 'family': 'Claude', 'gen': 1},
    'claude-opus-4.8': {'label': 'Claude Opus 4.8', 'family': 'Claude', 'gen': 2},
    'gpt-4.1': {'label': 'GPT-4.1', 'family': 'GPT', 'gen': 0},
    'gpt-5.2': {'label': 'GPT-5.2', 'family': 'GPT', 'gen': 1},
    'gpt-5.5': {'label': 'GPT-5.5', 'family': 'GPT', 'gen': 2},
    'gemini-2.5-pro': {'label': 'Gemini 2.5 Pro', 'family': 'Gemini', 'gen': 0},
    'gemini-3-pro': {'label': 'Gemini 3 Pro', 'family': 'Gemini', 'gen': 1},
    'gemini-3.1-pro': {'label': 'Gemini 3.1 Pro', 'family': 'Gemini', 'gen': 2},
    'gemini-3.5-flash': {'label': 'Gemini 3.5 Flash', 'family': 'Gemini', 'gen': 3},
    'grok-3': {'label': 'Grok 3', 'family': 'Grok', 'gen': 0},
    'grok-4.1': {'label': 'Grok 4.1', 'family': 'Grok', 'gen': 1},
    'grok-4.3': {'label': 'Grok 4.3', 'family': 'Grok', 'gen': 2},
    'llama-3.3-70b': {'label': 'Llama 3.3', 'family': 'Llama', 'gen': 0},
    'llama4': {'label': 'Llama 4', 'family': 'Llama', 'gen': 1},
    'qwen-2.5-72b': {'label': 'Qwen 2.5', 'family': 'Qwen', 'gen': 0},
    'qwen3': {'label': 'Qwen 3', 'family': 'Qwen', 'gen': 1},
    'qwen-3.7': {'label': 'Qwen 3.7', 'family': 'Qwen', 'gen': 2},
    'deepseek-r1': {'label': 'DeepSeek R1', 'family': 'DeepSeek', 'gen': 1},
    'deepseek-v3.2': {'label': 'DeepSeek V3', 'family': 'DeepSeek', 'gen': 0},
    'openevidence': {'label': 'OpenEvidence', 'family': 'OpenEvidence', 'gen': 0},
    'medgemma-4b': {'label': 'MedGemma 4B', 'family': 'MedGemma', 'gen': 0},
    'medgemma-27b': {'label': 'MedGemma 27B', 'family': 'MedGemma', 'gen': 1},
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

# Softer component colors for stacked bars
COMP_COLORS = {
    'Diagnostic': '#4393C3',
    'Medication': '#F4A582',
    'Referral': '#8073AC',
}

# Specialized medical AI systems — styled differently (hatched, outlined)
SPECIALIZED_MODELS = {'openevidence', 'medgemma-4b', 'medgemma-27b', 'meditron'}


# ── Data loading ───────────────────────────────────────────────────────
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


# ── 3-judge majority concordance (no single judge favors its own family) ──
# Each judge labels correct/correct_plus/related/wrong -> ordinal tier (concordant=2,
# adjacent=1, discordant=0). Concordance = majority tier; 3-way tie -> ordinal middle.
_TIER = {'correct': 2, 'correct_plus': 2, 'related': 1, 'wrong': 0}
_JUDGE_FIELDS = ('dx_match_v2', 'dx_claude', 'dx_gemini')


def majority_tier(case):
    """Return 2/1/0 (concordant/adjacent/discordant) by 3-judge majority, or None."""
    ts = [_TIER[case[f]] for f in _JUDGE_FIELDS if case.get(f) in _TIER]
    if not ts:
        return None
    c = Counter(ts)
    top, n = c.most_common(1)[0]
    if n == 1 and len(c) == len(ts):      # all distinct -> ordinal middle
        return sorted(ts)[len(ts) // 2]
    return top


def majority_label(case):
    """Majority tier as a v1-style label ('correct'/'related'/'wrong'), or 'unknown'."""
    t = majority_tier(case)
    return {2: 'correct', 1: 'related', 0: 'wrong'}.get(t, 'unknown')


def load_unified_panel():
    """The unified standard-prompt panel: the 24-system standard
    panel in results/models/ (re-run models + re-extracted Group O systems),
    deduped by presentation. This is the MAIN-result source (replaces load_all_models,
    which now serves the appropriateness sub-study anchored to the original plans in
    results/models_original_runs/)."""
    all_data = {}
    for fpath in sorted(glob.glob(str(ROOT / 'results' / 'models' / 'm_*.json'))):
        name = os.path.basename(fpath).replace('m_', '').replace('.json', '')
        if name not in MODEL_INFO:
            continue
        with open(fpath) as f:
            data = json.load(f)
        seen, unique = set(), []
        for c in data:
            if c.get('case_id') in EXCLUDED_CASES:
                continue
            p = c.get('presentation')
            if p in seen:
                continue
            seen.add(p)
            unique.append(c)
        all_data[name] = unique
    return all_data


def _namcs_weighted_excess(h_dx, l_dx):
    """Compute NAMCS-reweighted per-visit excess using post-stratification."""
    # Strata: routine ($0), simple ($1-100), significant (>$100)
    namcs_weights = {'routine': 0.584, 'simple': 0.165, 'significant': 0.251}
    excess = l_dx - h_dx
    strata = np.where(h_dx == 0, 'routine', np.where(h_dx <= 100, 'simple', 'significant'))
    weighted = 0
    for stratum, w in namcs_weights.items():
        mask = strata == stratum
        if mask.sum() > 0:
            weighted += w * excess[mask].mean()
    return weighted


def build_stats_df(all_data):
    """Build a pandas DataFrame with per-model statistics."""
    rows = []
    for model, cases in all_data.items():
        n = len(cases)
        h_dx = np.array([c.get('medicare_human_dx_cost') or 0 for c in cases])
        l_dx = np.array([c.get('medicare_llm_dx_cost') or 0 for c in cases])
        # Always use medicare fields for consistency (matches REPORT.md)
        h_med = np.array([float(c.get('medicare_human_med_cost') or 0) for c in cases])
        l_med = np.array([float(c.get('medicare_llm_med_cost') or 0) for c in cases])
        h_ref = np.array([c.get('human_referral_cost') or 0 for c in cases])
        l_ref = np.array([c.get('llm_referral_cost') or 0 for c in cases])

        h_total = h_dx + h_med + h_ref
        l_total = l_dx + l_med + l_ref

        # Diagnostic agreement — 3-judge majority (concordant/adjacent/discordant)
        tiers = [majority_tier(c) for c in cases]
        tiers = [t for t in tiers if t is not None]
        n_dx = len(tiers)
        correct = sum(1 for t in tiers if t == 2)
        correct_exact = correct          # majority collapses correct/correct_plus
        correct_plus = 0
        related = sum(1 for t in tiers if t == 1)
        wrong = sum(1 for t in tiers if t == 0)
        accuracy = 100 * correct / n_dx if n_dx > 0 else 0

        # Over/Match/Under
        over = int(np.sum(l_dx > h_dx))
        match = int(np.sum(l_dx == h_dx))
        under = int(np.sum(l_dx < h_dx))

        # Medication counts (median across 3 extractions)
        llm_med_counts = []
        human_med_counts = []
        for c in cases:
            slot_counts_l = []
            slot_counts_h = []
            for slot in ['a', 'b', 'c']:
                l_orders = c.get(f'llm_orders_{slot}', [])
                h_orders = c.get(f'human_orders_{slot}', [])
                slot_counts_l.append(sum(1 for o in l_orders if o.get('category') == 'medication'))
                slot_counts_h.append(sum(1 for o in h_orders if o.get('category') == 'medication'))
            llm_med_counts.append(np.median(slot_counts_l) if slot_counts_l else 0)
            human_med_counts.append(np.median(slot_counts_h) if slot_counts_h else 0)
        llm_med_counts = np.array(llm_med_counts)
        human_med_counts = np.array(human_med_counts)

        # Defensive ordering
        zero_mask = h_dx == 0
        n_zero = int(np.sum(zero_mask))
        n_added = int(np.sum(l_dx[zero_mask] > 0))
        pct_added = 100 * n_added / n_zero if n_zero > 0 else 0

        rows.append({
            'model': model,
            'label': MODEL_INFO[model]['label'],
            'family': MODEL_INFO[model]['family'],
            'gen': MODEL_INFO[model]['gen'],
            'n': n,
            'h_dx': h_dx.mean(), 'l_dx': l_dx.mean(),
            'h_med': h_med.mean(), 'l_med': l_med.mean(),
            'h_ref': h_ref.mean(), 'l_ref': l_ref.mean(),
            'h_total': h_total.mean(), 'l_total': l_total.mean(),
            'dx_ratio': l_dx.mean() / h_dx.mean() if h_dx.mean() > 0 else 1,
            'total_ratio': l_total.mean() / h_total.mean() if h_total.mean() > 0 else 1,
            'excess_dx': l_dx.mean() - h_dx.mean(),
            'excess_dx_weighted': _namcs_weighted_excess(h_dx, l_dx),
            'excess_total': l_total.mean() - h_total.mean(),
            'accuracy': accuracy,
            'correct': correct, 'correct_exact': correct_exact,
            'correct_plus': correct_plus, 'related': related, 'wrong': wrong, 'n_dx': n_dx,
            'over': over, 'match': match, 'under': under,
            'n_zero': n_zero, 'n_added': n_added, 'pct_added': pct_added,
            'llm_med_count': llm_med_counts.mean(), 'human_med_count': human_med_counts.mean(),
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════
# FIGURE 2: Cost Comparison (5 panels)
# A = total fold-change, B = diagnostic fold-change, C = referrals/case,
# D = medication fold-change, E = over/match/under stacked bar
# ══════════════════════════════════════════════════════════════════════
def newest_per_family(df):
    """One row per family: the newest evaluated version (max gen). Families now span
    2-4 versions, so 'current generation' is the per-family max gen, not a fixed gen==1."""
    idx = df.groupby('family')['gen'].idxmax()
    return df.loc[idx].copy()


def make_fig3_cost(df, all_data):
    fig = plt.figure(figsize=(18, 11))
    gs = gridspec.GridSpec(2, 2, wspace=0.28, hspace=0.22)

    # Newest version per family + specialized systems (older versions in Fig 3F / supp)
    current_gen = newest_per_family(df)
    df_sorted = current_gen.sort_values('dx_ratio').reset_index(drop=True)
    bar_h = 0.65

    def ratio_panel(ax, df_in, col, human_avg, title, panel_label, xlabel='Cost Ratio (AI / Physician)'):
        """Draw a horizontal bar chart sorted by col values."""
        df_local = df_in.sort_values(col).reset_index(drop=True)
        y_local = np.arange(len(df_local))
        for i, (_, row) in enumerate(df_local.iterrows()):
            color = FAMILY_COLORS.get(row['family'], '#888')
            val = row[col]
            is_special = row['model'] in SPECIALIZED_MODELS
            ax.barh(i, val, height=bar_h, color=color,
                    alpha=0.5 if is_special else 0.85,
                    edgecolor=color if is_special else 'white',
                    linewidth=1.5 if is_special else 0.5,
                    )
            ax.text(val + 0.04, i, f'{val:.1f}×', fontsize=8.5, va='center',
                    fontweight='normal' if is_special else 'bold', color='#333')

        ax.axvline(x=1.0, color='#333', linestyle='--', lw=1.2, alpha=0.7, zorder=0)
        ax.text(1.0, -1.2, f'Physician avg: ${human_avg:.0f}', ha='center', fontsize=9,
                fontweight='bold', color='#555',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFDE7',
                         edgecolor='#E0C97F', alpha=0.95))

        ax.set_yticks(y_local)
        ax.set_yticklabels(df_local['label'], fontsize=10)
        ax.set_xlabel(xlabel, fontsize=10.5)
        ax.set_title(f'{panel_label}    {title}', fontsize=13,
                     fontweight='bold', loc='left', pad=10)
        ax.set_ylim(-1.8, len(df_local) - 0.3)
        ax.set_xlim(0, df_local[col].max() * 1.18)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def count_panel(ax, df_in, col, human_avg, title, panel_label, xlabel, fmt='{:.1f}'):
        """Draw a horizontal bar chart for count data (no fold-change)."""
        df_local = df_in.sort_values(col).reset_index(drop=True)
        y_local = np.arange(len(df_local))
        for i, (_, row) in enumerate(df_local.iterrows()):
            color = FAMILY_COLORS.get(row['family'], '#888')
            val = row[col]
            is_special = row['model'] in SPECIALIZED_MODELS
            ax.barh(i, val, height=bar_h, color=color,
                    alpha=0.5 if is_special else 0.85,
                    edgecolor=color if is_special else 'white',
                    linewidth=1.5 if is_special else 0.5,
                    )
            ax.text(val + 0.03, i, fmt.format(val), fontsize=8.5, va='center',
                    fontweight='normal' if is_special else 'bold', color='#333')

        ax.axvline(x=human_avg, color='#333', linestyle='--', lw=1.2, alpha=0.7, zorder=0)
        ax.text(human_avg, -1.2, f'Physician avg: {fmt.format(human_avg)}', ha='center',
                fontsize=9, fontweight='bold', color='#555',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFDE7',
                         edgecolor='#E0C97F', alpha=0.95))

        ax.set_yticks(y_local)
        ax.set_yticklabels(df_local['label'], fontsize=10)
        ax.set_xlabel(xlabel, fontsize=10.5)
        ax.set_title(f'{panel_label}    {title}', fontsize=13,
                     fontweight='bold', loc='left', pad=10)
        ax.set_ylim(-1.8, len(df_local) - 0.3)
        ax.set_xlim(0, df_local[col].max() * 1.25)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # ═══ TOP ROW: A (diagnostic fold-change) + B (over/match/under) ═══

    # ── Panel A: Diagnostic fold-change ──
    ax_a = fig.add_subplot(gs[0, 0])
    ratio_panel(ax_a, df_sorted, 'dx_ratio', df_sorted['h_dx'].mean(),
                'Diagnostic Test Cost', 'A')

    # ── Panel B: Over / Match / Under stacked bar ──
    ax_b = fig.add_subplot(gs[0, 1])
    df_b = df_sorted.sort_values('over').reset_index(drop=True)

    for i, (_, row) in enumerate(df_b.iterrows()):
        is_special = row['model'] in SPECIALIZED_MODELS
        a = 0.55 if is_special else 0.85
        elw = 1.8 if is_special else 0.5
        edc = '#333' if is_special else 'white'
        ax_b.barh(i, row['over'], height=bar_h, color='#E15759', alpha=a,
                  edgecolor=edc, linewidth=elw)
        ax_b.barh(i, row['match'], height=bar_h, left=row['over'],
                  color='#D5D5D5', alpha=a, edgecolor=edc, linewidth=elw)
        ax_b.barh(i, row['under'], height=bar_h,
                  left=row['over'] + row['match'],
                  color='#59A14F', alpha=a, edgecolor=edc, linewidth=elw)
        fw = 'normal' if is_special else 'bold'
        if row['over'] > 18:
            ax_b.text(row['over']/2, i, f"{int(row['over'])}", fontsize=7.5,
                     ha='center', va='center', color='white', fontweight=fw)
        if row['match'] > 18:
            ax_b.text(row['over'] + row['match']/2, i, f"{int(row['match'])}",
                     fontsize=7.5, ha='center', va='center', color='#555', fontweight=fw)
        if row['under'] > 18:
            ax_b.text(row['over'] + row['match'] + row['under']/2, i,
                     f"{int(row['under'])}", fontsize=7.5,
                     ha='center', va='center', color='white', fontweight=fw)

    ax_b.set_yticks(np.arange(len(df_b)))
    ax_b.set_yticklabels(df_b['label'], fontsize=10)
    ax_b.set_xlabel('Number of Cases (N=200)', fontsize=10.5)
    ax_b.set_title('B    Per-Case Ordering Pattern', fontsize=13,
                   fontweight='bold', loc='left', pad=10)
    ax_b.set_ylim(-1.8, len(df_b) - 0.3)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)

    legend_elements = [
        mpatches.Patch(facecolor='#E15759', alpha=0.85, label='Over-ordered'),
        mpatches.Patch(facecolor='#D5D5D5', alpha=0.85, label='Matched'),
        mpatches.Patch(facecolor='#59A14F', alpha=0.85, label='Under-ordered'),
    ]
    ax_b.legend(handles=legend_elements, fontsize=9, loc='lower right',
               framealpha=0.95, ncol=3, columnspacing=1.0)

    # ═══ BOTTOM ROW: C (referrals count), D (medications count) ═══

    # ── Panel C: Referrals per case ──
    ax_c = fig.add_subplot(gs[1, 0])

    ref_counts = {}
    for model, cases in all_data.items():
        if model not in MODEL_INFO:
            continue
        l_refs = [c.get('llm_referral_count') or 0 for c in cases]
        h_refs = [c.get('human_referral_count') or 0 for c in cases]
        ref_counts[model] = {
            'llm_ref_count': np.mean(l_refs),
            'human_ref_count': np.mean(h_refs),
        }
    df_sorted['llm_ref_count'] = df_sorted['model'].map(
        lambda m: ref_counts.get(m, {}).get('llm_ref_count', 0))
    df_sorted['human_ref_count'] = df_sorted['model'].map(
        lambda m: ref_counts.get(m, {}).get('human_ref_count', 0))

    human_ref_avg = df_sorted['human_ref_count'].mean()
    count_panel(ax_c, df_sorted, 'llm_ref_count', human_ref_avg,
                'Specialist Referrals', 'C', 'Avg Referrals per Case')

    # ── Panel D: Medications per case ──
    ax_d = fig.add_subplot(gs[1, 1])
    human_med_avg = df_sorted['human_med_count'].mean()
    count_panel(ax_d, df_sorted, 'llm_med_count', human_med_avg,
                'New Medications', 'D', 'Avg New Medications per Case')

    fig.savefig(f'{OUT_DIR}/fig3_cost.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/fig3_cost.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Figure 3: Cost (panels A-D)')


# ══════════════════════════════════════════════════════════════════════
# FIGURE 2B (NEW): Diagnostic Accuracy
# ══════════════════════════════════════════════════════════════════════
def make_fig2(df, include_panel_c=True, stem='fig2_diagnostic_accuracy'):
    """Panel A: 3-tier explanation. Panel B: 3-color stacked bars. Panel C: easy vs hard scatter.

    include_panel_c=False drops the Case Consensus Index scatter, which the published
    editorial review removed from both manuscript and supplement, and emits the
    A+B figure under `stem`."""
    if include_panel_c:
        fig = plt.figure(figsize=(28, 8))
        gs = gridspec.GridSpec(1, 3, width_ratios=[0.45, 0.75, 0.65], wspace=0.25)
    else:
        fig = plt.figure(figsize=(19, 8))
        gs = gridspec.GridSpec(1, 2, width_ratios=[0.45, 0.75], wspace=0.25)

    # ── Panel A: 3-tier card-style explanation ──
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_xlim(0, 100)
    ax_a.set_ylim(0, 100)
    ax_a.axis('off')
    ax_a.set_facecolor('white')
    ax_a.text(2, 97, 'A', fontsize=20, fontweight='bold', va='top')
    ax_a.text(8, 97, 'Diagnostic Agreement Categories', fontsize=16,
              fontweight='bold', va='top')

    examples = [
        {
            'level': 'Concordant',
            'color': '#2E7D32',
            'bg': '#F1F8E9',
            'desc': 'Same diagnosis (exact or with additions)',
            'human': 'Thrombocytopenia',
            'ai': 'Immune\nthrombocytopenia (ITP)',
        },
        {
            'level': 'Adjacent',
            'color': '#EF6C00',
            'bg': '#FFF8E1',
            'desc': 'Same clinical domain, different framing',
            'human': 'Upper respiratory\ninfection',
            'ai': 'Viral pharyngitis\nwith allergic\ncomponent',
        },
        {
            'level': 'Discordant',
            'color': '#C62828',
            'bg': '#FFF3F0',
            'desc': 'Fundamentally different diagnosis',
            'human': 'Normal growth and\ndevelopment\n(sports physical)',
            'ai': 'Asthma, Allergic\nrhinitis, Irregular\nmenstrual cycles',
        },
    ]

    card_h = 26
    y_start = 88
    card_left = 2
    card_w = 96
    card_gap = 3

    for i, ex in enumerate(examples):
        y_top = y_start - i * (card_h + card_gap)

        card = FancyBboxPatch((card_left, y_top - card_h), card_w, card_h,
                               boxstyle="round,pad=1.2",
                               facecolor='white', edgecolor=ex['color'],
                               linewidth=1.8, alpha=0.95)
        ax_a.add_patch(card)
        card_fill = FancyBboxPatch((card_left, y_top - card_h), card_w, card_h,
                               boxstyle="round,pad=1.2",
                               facecolor=ex['bg'], edgecolor='none',
                               alpha=0.35)
        ax_a.add_patch(card_fill)

        badge_w = 24 if ex['level'] == 'Concordant' else 22 if ex['level'] == 'Discordant' else 20
        badge = FancyBboxPatch((5, y_top - 6), badge_w, 5,
                                boxstyle="round,pad=1.0",
                                facecolor=ex['color'], edgecolor='none', zorder=4)
        ax_a.add_patch(badge)
        ax_a.text(5 + badge_w / 2, y_top - 3.5, ex['level'],
                 fontsize=13, fontweight='bold', color='white',
                 ha='center', va='center', zorder=5)

        ax_a.text(5 + badge_w + 2, y_top - 3.5, ex['desc'],
                 fontsize=11, color='#666', va='center', style='italic')

        col1_x = 6
        content_top = y_top - 9
        ax_a.text(col1_x, content_top, 'Physician:', fontsize=11,
                 fontweight='bold', color='#888', va='top')
        ax_a.text(col1_x, content_top - 3.5, ex['human'], fontsize=11,
                 color='#333', va='top', linespacing=1.3)

        arrow_x = 42
        arrow_y = content_top - 5
        ax_a.annotate('', xy=(arrow_x + 5, arrow_y),
                      xytext=(arrow_x, arrow_y),
                      arrowprops=dict(arrowstyle='->', color=ex['color'],
                                      lw=2.0, mutation_scale=15))

        col2_x = 52
        ax_a.text(col2_x, content_top, 'AI:', fontsize=11,
                 fontweight='bold', color='#888', va='top')
        ax_a.text(col2_x, content_top - 3.5, ex['ai'], fontsize=11,
                 color='#333', va='top', linespacing=1.3)

    # ── Panel B: 3-color stacked horizontal bars ──
    ax_b = fig.add_subplot(gs[1])

    tier_colors = {
        'concordant': '#4CAF50',
        'adjacent': '#FFB74D',
        'discordant': '#E57373',
    }

    # Build family pairs + specialized triplet
    family_order = ['Claude', 'DeepSeek', 'GPT', 'Gemini', 'Grok', 'Llama', 'Qwen']
    specialized_families = ['OpenEvidence', 'MedGemma', 'Meditron']

    # Compute 3-tier percentages for each model
    def get_pcts(row):
        total = row['n_dx'] if row['n_dx'] > 0 else 220
        conc = ((row.get('correct_exact') or 0) + (row.get('correct_plus') or 0)) / total * 100 if total > 0 else 0
        adj = (row.get('related') or 0) / total * 100 if total > 0 else 0
        disc = (row.get('wrong') or 0) / total * 100 if total > 0 else 0
        return conc, adj, disc

    # Build y positions with gaps between families
    bar_h = 0.38
    pair_gap = 0.06       # gap between bars within a pair
    family_gap = 0.55     # gap between families
    section_gap = 0.85    # gap between general and specialized

    y_positions = []  # (y, row_data, is_old_gen)
    labels = []
    y = 0

    for fi, fam in enumerate(family_order):
        fam_models = df[df['family'] == fam].sort_values('gen')
        for gi, (_, row) in enumerate(fam_models.iterrows()):
            y_positions.append((y, row, row['gen'] == 0))
            labels.append(row['label'])
            if gi == 0 and len(fam_models) > 1:
                y += bar_h + pair_gap
            else:
                y += bar_h
        y += family_gap

    # Add separator position
    separator_y = y - family_gap + section_gap / 2

    y = y - family_gap + section_gap  # reset gap and add section gap

    # Specialized models
    for si, sfam in enumerate(specialized_families):
        sfam_models = df[df['family'] == sfam]
        for _, row in sfam_models.iterrows():
            y_positions.append((y, row, False))
            labels.append(row['label'])
            y += bar_h + pair_gap
        if si < len(specialized_families) - 1:
            pass  # keep them close as a triplet

    n_bars = len(y_positions)
    y_coords = [yp[0] for yp in y_positions]

    # Draw bars
    for y_val, row, is_old in y_positions:
        conc, adj, disc = get_pcts(row)
        alpha = 0.50 if is_old else 0.90

        ax_b.barh(y_val, conc, height=bar_h, color=tier_colors['concordant'],
                  alpha=alpha, edgecolor='white', linewidth=0.5)
        ax_b.barh(y_val, adj, height=bar_h, left=conc, color=tier_colors['adjacent'],
                  alpha=alpha, edgecolor='white', linewidth=0.5)
        ax_b.barh(y_val, disc, height=bar_h, left=conc + adj, color=tier_colors['discordant'],
                  alpha=alpha, edgecolor='white', linewidth=0.5)

        # Percentage labels inside bars (only if segment is wide enough)
        segments = [
            (0, conc, 'white'),
            (conc, adj, '#5D4037'),
            (conc + adj, disc, '#5D4037'),
        ]
        for left, width_val, text_color in segments:
            if width_val >= 8:
                ax_b.text(left + width_val / 2, y_val, f'{width_val:.0f}%',
                         fontsize=8, fontweight='bold', color=text_color,
                         ha='center', va='center',
                         alpha=0.85 if not is_old else 0.6)

        # Overall concordance label on the right
        ax_b.text(101, y_val, f'{conc:.0f}%', fontsize=10, va='center',
                  fontweight='bold', color='#333',
                  alpha=0.6 if is_old else 1.0)

    # Y-axis labels
    ax_b.set_yticks(y_coords)
    ax_b.set_yticklabels(labels, fontsize=12)

    # Style old-gen labels lighter
    for tick_label, (_, row, is_old) in zip(ax_b.get_yticklabels(), y_positions):
        if is_old:
            tick_label.set_alpha(0.55)

    # Add family brackets/labels on the left
    # (Use subtle background shading for alternating families)
    idx = 0
    for fi, fam in enumerate(family_order):
        fam_n = len(df[df['family'] == fam])
        fam_y_vals = [y_positions[idx + j][0] for j in range(fam_n)]
        idx += fam_n

    # Separator line before specialized
    ax_b.axhline(y=separator_y, color='#999', linewidth=1.0, linestyle='--')
    # Place "Medical AI" label centered in the separator gap
    ax_b.text(50, separator_y, '  Medical AI  ', fontsize=10, color='#888',
             ha='center', va='center', style='italic',
             bbox=dict(facecolor='white', edgecolor='none', pad=2))

    ax_b.set_xlabel('Percentage of Cases', fontsize=14)
    ax_b.tick_params(axis='x', labelsize=12)
    ax_b.set_xlim(0, 108)
    ax_b.set_ylim(-0.5, y_coords[-1] + 0.5)
    ax_b.invert_yaxis()
    ax_b.text(0.0, 1.02, 'B', fontsize=20, fontweight='bold',
              transform=ax_b.transAxes, va='bottom')
    ax_b.text(0.03, 1.02, 'Diagnostic Agreement by Model', fontsize=16,
              fontweight='bold', transform=ax_b.transAxes, va='bottom')
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=tier_colors['concordant'], alpha=0.9, label='Concordant'),
        mpatches.Patch(facecolor=tier_colors['adjacent'], alpha=0.9, label='Adjacent'),
        mpatches.Patch(facecolor=tier_colors['discordant'], alpha=0.9, label='Discordant'),
        mpatches.Patch(facecolor='#999', alpha=0.9, label='Current gen'),
        mpatches.Patch(facecolor='#999', alpha=0.45, label='Previous gen'),
    ]
    ax_b.legend(handles=legend_elements, fontsize=11, loc='upper center',
                bbox_to_anchor=(0.5, -0.10), framealpha=0.95, ncol=5,
                columnspacing=1.2, borderaxespad=0, handletextpad=0.5)

    # ── Panel C: Easy vs Hard scatter ──
    if not include_panel_c:
        plt.tight_layout()
        fig.savefig(f'{OUT_DIR}/{stem}.png', dpi=300, bbox_inches='tight')
        fig.savefig(f'{OUT_DIR}/{stem}.pdf', bbox_inches='tight')
        plt.close(fig)
        print(f'✓ {stem}: Diagnostic Agreement (panels A+B only)')
        return
    ax_c = fig.add_subplot(gs[2])

    import json as _json
    consensus_path = str(ROOT / 'results' / 'analysis' / 'model_agreement_summary.json')
    if os.path.exists(consensus_path):
        with open(consensus_path) as _f:
            model_agreement = _json.load(_f)

        from adjustText import adjust_text

        texts_c = []
        for _, row in df.iterrows():
            m = row['model']
            if m not in model_agreement:
                continue
            ma = model_agreement[m]
            x_val = ma['concordance_high']
            y_val = ma['concordance_low']
            color = FAMILY_COLORS.get(row['family'], '#888')
            is_special = m in SPECIALIZED_MODELS
            marker = 'D' if is_special else 'o'
            size = 160 if is_special else 130
            # Only show current gen + specialized
            if row['gen'] == 0 and m not in SPECIALIZED_MODELS:
                continue
            ax_c.scatter(x_val, y_val, c=color, s=size, marker=marker,
                        edgecolors='white', linewidth=1.5, zorder=5)

            texts_c.append(ax_c.text(x_val, y_val, row['label'],
                          fontsize=12, color='#333',
                          fontstyle='italic' if is_special else 'normal'))

        adjust_text(texts_c, ax=ax_c,
                    arrowprops=dict(arrowstyle='-', color='#AAAAAA', lw=0.8),
                    expand=(1.8, 2.0), force_text=(1.5, 2.0),
                    force_points=(1.0, 1.0))

        ax_c.set_xlabel('Concordance on Easy Cases (%)', fontsize=13)
        ax_c.set_ylabel('Concordance on Hard Cases (%)', fontsize=13)
        ax_c.tick_params(axis='both', labelsize=11)
        ax_c.spines['top'].set_visible(False)
        ax_c.spines['right'].set_visible(False)
        ax_c.text(-0.05, 1.05, 'C', fontsize=18, fontweight='bold',
                  transform=ax_c.transAxes, va='bottom')
        ax_c.text(0.02, 1.05, 'Easy vs. Hard Cases', fontsize=15,
                  fontweight='bold', transform=ax_c.transAxes, va='bottom')

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/{stem}.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/{stem}.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Figure 2: Diagnostic Agreement (3-tier + CCI stratification)')


# ══════════════════════════════════════════════════════════════════════
# FIGURE 3: Accuracy vs Cost + Generational Evolution
# ══════════════════════════════════════════════════════════════════════
def make_fig3_scatter(df, only_generational=False, stem='fig3_scatter_generational'):
    """only_generational=True emits the generational-evolution panel alone.

    The concordance-versus-cost panel is omitted from both the manuscript and
    the supplement; the generational panel appears in the supplement and so has
    to stand by itself."""
    if only_generational:
        fig, ax2 = plt.subplots(figsize=(9, 6.5))
        ax1 = None
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))

    # ── Panel A: Accuracy vs Cost Scatter ──
    if ax1 is not None:
        from adjustText import adjust_text

        texts = []
        for _, row in df.iterrows():
            color = FAMILY_COLORS.get(row['family'], '#888')
            is_special = row['model'] in SPECIALIZED_MODELS
            marker = 'D' if is_special else 'o'
            size = 130 if is_special else 100
            alpha = 0.6 if is_special else 1.0
            ax1.scatter(row['dx_ratio'], row['accuracy'], c=color, s=size,
                       marker=marker, edgecolors='white', linewidth=1.5,
                       zorder=5, alpha=alpha)
            texts.append(ax1.text(row['dx_ratio'], row['accuracy'],
                                 row['label'], fontsize=10.5,
                                 color='#888' if is_special else '#444',
                                 style='italic' if is_special else 'normal'))

        # Use adjustText to repel labels
        adjust_text(texts, ax=ax1, arrowprops=dict(arrowstyle='-', color='#AAAAAA', lw=0.5),
                    expand=(1.5, 1.5), force_text=(0.8, 0.8), force_points=(0.5, 0.5))

        # Correlation (all AI systems in the unified panel)
        r_val, p_val = pearsonr(df['dx_ratio'], df['accuracy'])

        # Stats box — top left
        ax1.text(0.35, 0.96,
                f'r = {r_val:.2f}, p = {p_val:.2f}\n({len(df)} AI systems)',
                transform=ax1.transAxes, fontsize=9, ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFDE7',
                         edgecolor='#E0C97F', alpha=0.95))

        ax1.axvline(x=1.0, color='#CCC', linestyle='--', lw=1, zorder=0)
        ax1.set_xlabel('Mean Diagnostic Cost Ratio (AI / Physician)', fontsize=11)
        ax1.set_ylabel('Diagnostic Concordance (%)', fontsize=11)
        ax1.set_title('E    Diagnostic Concordance vs. Cost',
                      fontsize=12.5, fontweight='bold', loc='left', pad=10)

        # Extend y-axis to make room for legend above GPT-5.2 (84.3%)
        ax1.set_ylim(ax1.get_ylim()[0], 92)
        # Family legend — upper right, above all data points
        handles = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
        ax1.legend(handles=handles, fontsize=8, loc='upper right', ncol=2,
                  framealpha=0.95)

    # ── Panel F: Generational Evolution (full per-family version trajectory) ──
    # Families now span 2-4 evaluated versions. Show each version as a bar shaded by
    # recency (oldest lightest -> newest darkest) and annotate the net oldest->newest
    # change. Gemini uses its pro line only (3.5-flash is a separate, cheaper tier).
    PANEL_F_EXCLUDE = SPECIALIZED_MODELS | {'gemini-3.5-flash'}
    families = {}
    for _, row in df.iterrows():
        if row['model'] in PANEL_F_EXCLUDE:
            continue
        families.setdefault(row['family'], []).append((row['gen'], row['dx_ratio'], row['label']))
    for fam in families:
        families[fam].sort()                       # ascending gen (oldest -> newest)

    # Sort families by net oldest->newest change (largest rise first)
    def net_change(fam):
        v = families[fam]
        return (v[-1][1] - v[0][1]) / v[0][1] if len(v) > 1 and v[0][1] else 0
    fam_names = sorted(families, key=net_change, reverse=True)

    group_w = 0.8
    for i, fam in enumerate(fam_names):
        versions = families[fam]
        k = len(versions)
        bw = group_w / k
        color = FAMILY_COLORS[fam]
        for j, (g, ratio, lbl) in enumerate(versions):
            alpha = 0.45 + 0.5 * (j / (k - 1)) if k > 1 else 0.85
            xpos = i - group_w / 2 + (j + 0.5) * bw
            ax2.bar(xpos, ratio, bw * 0.92, color=color, alpha=alpha,
                    edgecolor=color, linewidth=1.0)
            # short version tag under each bar (e.g. '4.1', '5.5')
            tag = lbl.split()[-1] if lbl.split()[-1][0].isdigit() else lbl.split()[-1]
            ax2.text(xpos, -0.13, tag, ha='center', va='top', fontsize=6.5,
                     color='#666', rotation=0)
        if k > 1:
            change = 100 * net_change(fam)
            arrow_color = '#C62828' if change > 0 else '#2E7D32'
            prefix = '+' if change > 0 else '−'
            y_top = max(v[1] for v in versions) + 0.12
            ax2.annotate(f'{prefix}{abs(change):.0f}%', xy=(i, y_top), ha='center',
                         fontsize=10, fontweight='bold', color=arrow_color)

    ax2.axhline(y=1.0, color='#555', linestyle='--', lw=1.2, alpha=0.7, zorder=0)
    ax2.text(-0.7, 1.0, 'Physician\nbaseline', fontsize=8, color='#777',
            va='center', ha='right', linespacing=1.3)
    ax2.set_xticks(np.arange(len(fam_names)))
    ax2.set_xticklabels(fam_names, fontsize=10.5)
    ax2.set_ylim(0, max(v[1] for fam in families for v in families[fam]) * 1.15)
    ax2.set_ylabel('Mean Diagnostic Cost Ratio', fontsize=11)
    # Standing alone in the supplement it carries no panel letter, and the
    # arrow glyph is missing from the Helvetica/Times fallback used here.
    ax2.set_title(('Generational cost evolution (oldest to newest version)'
                   if only_generational else
                   'F    Generational Cost Evolution (oldest to newest version)'),
                  fontsize=12.5, fontweight='bold', loc='left', pad=10)
    ax2.annotate('lighter = older, darker = newer', xy=(0.98, 0.97),
                 xycoords='axes fraction', ha='right', va='top', fontsize=8, color='#777')

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/{stem}.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/{stem}.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Figure 3: Scatter + Generational')


# ══════════════════════════════════════════════════════════════════════
# FIGURE 4: Population Cost Projections (selected models only)
# ══════════════════════════════════════════════════════════════════════
def make_fig4(df):
    fig, ax = plt.subplots(figsize=(10, 6.5))

    visits = 883e6  # CDC NAMCS
    adoption_rates = [0.05, 0.10, 0.25]

    # Newest representative flagships (this is the standalone Figure 5)
    selected = ['gpt-5.5', 'claude-opus-4.8', 'qwen-3.7', 'gemini-3.1-pro', 'grok-4.3', 'deepseek-r1']
    sel_df = df[df['model'].isin(selected)].sort_values('excess_dx_weighted')

    n_models = len(sel_df)
    bar_width = 0.15
    x = np.arange(len(adoption_rates))

    for j, (_, row) in enumerate(sel_df.iterrows()):
        excess = row['excess_dx_weighted']
        costs_commercial = [visits * rate * excess * 2.0 / 1e9 for rate in adoption_rates]
        color = FAMILY_COLORS.get(row['family'], '#888')
        offset = (j - n_models/2 + 0.5) * bar_width

        bars = ax.bar(x + offset, costs_commercial, bar_width, color=color,
                     alpha=0.85, edgecolor='white', linewidth=0.8,
                     label=row['label'])

        # Value labels
        for k, v in enumerate(costs_commercial):
            ax.text(x[k] + offset, v + 0.8, f'${v:.0f}B', ha='center',
                   fontsize=8.5, fontweight='bold', color='#333')

    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(r*100)}%\n({int(visits*r/1e6)}M visits)' for r in adoption_rates],
                       fontsize=11)
    ax.set_xlabel('AI Adoption Rate', fontsize=12)
    ax.set_ylabel('Additional Upfront Diagnostic Spending ($ Billions/year)', fontsize=12)
    ax.set_title('Illustrative Population-Scale Additional Upfront Diagnostic Spending',
                fontsize=13, fontweight='bold', pad=12)

    ax.legend(fontsize=10, loc='upper left', framealpha=0.95)

    # Annotation — below the x-axis label
    fig.text(0.98, 0.01, '883M U.S. ambulatory visits/year (CDC NAMCS). Commercial pricing (2× Medicare rates).',
            fontsize=8.5, ha='right', va='bottom',
            color='#999', style='italic')

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/fig4_projections.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/fig4_projections.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Figure 4: Population Projections')


# ══════════════════════════════════════════════════════════════════════
# FIGURE 3 (COMBINED): ordering behavior + cost consequences (merges old 3+4)
# Row 1: A cost ratio | B referrals | C medications
# Row 2: D ordering pattern | E concordance vs cost
# Row 3: F generational cost rise | G illustrative population projection
# (the incorrect-diagnosis analysis lives with the mitigation figure, not here)
# ══════════════════════════════════════════════════════════════════════
def make_fig3_combined(df, all_data):
    from adjustText import adjust_text
    fig = plt.figure(figsize=(20, 12.5))
    gs_top = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.12], hspace=0.30)
    gs_r1 = gs_top[0].subgridspec(1, 3, wspace=0.26)                       # A B C equal
    gs_r2 = gs_top[1].subgridspec(1, 3, width_ratios=[3.2, 4.4, 4.4], wspace=0.24)  # smaller gaps -> bigger panels

    newest = newest_per_family(df).copy()
    # referral counts (computed from all_data, like the old panel C)
    ref_counts = {}
    for model, cases in all_data.items():
        if model not in MODEL_INFO:
            continue
        ref_counts[model] = np.mean([c.get('llm_referral_count') or 0 for c in cases])
    newest['llm_ref_count'] = newest['model'].map(lambda m: ref_counts.get(m, 0))
    human_ref_avg = np.mean([np.mean([c.get('human_referral_count') or 0 for c in cases])
                             for m, cases in all_data.items() if m in MODEL_INFO])
    bar_h = 0.66

    def ratio_panel(ax, dfin, col, human_avg, title, plabel, xlabel='Cost Ratio (AI / Physician)'):
        dl = dfin.sort_values(col).reset_index(drop=True)
        for i, (_, row) in enumerate(dl.iterrows()):
            color = FAMILY_COLORS.get(row['family'], '#888')
            sp = row['model'] in SPECIALIZED_MODELS
            ax.barh(i, row[col], height=bar_h, color=color, alpha=0.5 if sp else 0.85,
                    edgecolor=color if sp else 'white', linewidth=1.5 if sp else 0.5)
            ax.text(row[col] + dl[col].max() * 0.02, i, f'{row[col]:.1f}×', fontsize=9,
                    va='center', fontweight='normal' if sp else 'bold', color='#333')
        ax.axvline(1.0, color='#333', ls='--', lw=1.2, alpha=0.7, zorder=0)
        ax.text(1.0, -1.3, f'Physician avg: ${human_avg:.0f}', ha='center', fontsize=9,
                fontweight='bold', color='#555',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFDE7', edgecolor='#E0C97F'))
        ax.set_yticks(range(len(dl))); ax.set_yticklabels(dl['label'], fontsize=10)
        ax.set_xlabel(xlabel, fontsize=10.5)
        ax.set_title(f'{plabel}    {title}', fontsize=13.5, fontweight='bold', loc='left', pad=10)
        ax.set_ylim(-1.9, len(dl) - 0.3); ax.set_xlim(0, dl[col].max() * 1.18)
        ax.spines[['top', 'right']].set_visible(False)

    def count_panel(ax, dfin, col, human_avg, title, plabel, xlabel, fmt='{:.1f}'):
        dl = dfin.sort_values(col).reset_index(drop=True)
        for i, (_, row) in enumerate(dl.iterrows()):
            color = FAMILY_COLORS.get(row['family'], '#888')
            sp = row['model'] in SPECIALIZED_MODELS
            ax.barh(i, row[col], height=bar_h, color=color, alpha=0.5 if sp else 0.85,
                    edgecolor=color if sp else 'white', linewidth=1.5 if sp else 0.5)
            ax.text(row[col] + dl[col].max() * 0.02, i, fmt.format(row[col]), fontsize=9,
                    va='center', fontweight='normal' if sp else 'bold', color='#333')
        ax.axvline(human_avg, color='#333', ls='--', lw=1.2, alpha=0.7, zorder=0)
        ax.text(human_avg, -1.3, f'Physician avg: {fmt.format(human_avg)}', ha='center',
                fontsize=9, fontweight='bold', color='#555',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFDE7', edgecolor='#E0C97F'))
        ax.set_yticks(range(len(dl))); ax.set_yticklabels(dl['label'], fontsize=10)
        ax.set_xlabel(xlabel, fontsize=10.5)
        ax.set_title(f'{plabel}    {title}', fontsize=13.5, fontweight='bold', loc='left', pad=10)
        ax.set_ylim(-1.9, len(dl) - 0.3); ax.set_xlim(0, dl[col].max() * 1.25)
        ax.spines[['top', 'right']].set_visible(False)

    # ── Row 1: A cost, B referrals, C meds ──
    ratio_panel(fig.add_subplot(gs_r1[0]), newest, 'dx_ratio', newest['h_dx'].mean(),
                'Diagnostic Test Cost', 'A')
    count_panel(fig.add_subplot(gs_r1[1]), newest, 'llm_ref_count', human_ref_avg,
                'Specialist Referrals', 'B', 'Avg Referrals per Case')
    count_panel(fig.add_subplot(gs_r1[2]), newest, 'llm_med_count', newest['human_med_count'].mean(),
                'New Medications', 'C', 'Avg New Medications per Case')

    # ── Row 2, D: per-case ordering pattern (over/match/under) ──
    ax_d = fig.add_subplot(gs_r2[0])
    df_b = newest.sort_values('over').reset_index(drop=True)
    for i, (_, row) in enumerate(df_b.iterrows()):
        ax_d.barh(i, row['over'], height=bar_h, color='#E15759', alpha=0.85, edgecolor='white', linewidth=0.5)
        ax_d.barh(i, row['match'], height=bar_h, left=row['over'], color='#D5D5D5', alpha=0.85, edgecolor='white', linewidth=0.5)
        ax_d.barh(i, row['under'], height=bar_h, left=row['over'] + row['match'], color='#59A14F', alpha=0.85, edgecolor='white', linewidth=0.5)
    ax_d.set_yticks(range(len(df_b))); ax_d.set_yticklabels(df_b['label'], fontsize=10)
    ax_d.set_xlabel('Number of Cases', fontsize=10.5)
    ax_d.set_xlim(0, 200)
    ax_d.set_title('D    Per-Case Ordering Pattern', fontsize=13.5, fontweight='bold', loc='left', pad=10)
    ax_d.set_ylim(-0.7, len(df_b) - 0.3); ax_d.spines[['top', 'right']].set_visible(False)
    ax_d.legend(handles=[mpatches.Patch(facecolor='#E15759', alpha=0.85, label='AI ordered more'),
                         mpatches.Patch(facecolor='#D5D5D5', alpha=0.85, label='Matched'),
                         mpatches.Patch(facecolor='#59A14F', alpha=0.85, label='AI ordered less')],
                fontsize=9, loc='upper center', bbox_to_anchor=(0.5, -0.11), framealpha=0.95, ncol=3)

    # ── Row 2, E: diagnostic concordance vs cost (does cost buy agreement?) ──
    ax_e = fig.add_subplot(gs_r2[1])
    texts = []
    for _, row in df.iterrows():
        color = FAMILY_COLORS.get(row['family'], '#888')
        sp = row['model'] in SPECIALIZED_MODELS
        ax_e.scatter(row['dx_ratio'], row['accuracy'], c=color, s=130 if sp else 95,
                     marker='D' if sp else 'o', edgecolors='white', linewidth=1.3, zorder=5,
                     alpha=0.65 if sp else 1.0)
        texts.append(ax_e.text(row['dx_ratio'], row['accuracy'], row['label'], fontsize=8.5,
                               color='#888' if sp else '#444'))
    adjust_text(texts, ax=ax_e, arrowprops=dict(arrowstyle='-', color='#BBB', lw=0.5),
                expand=(1.4, 1.6))
    r_val, p_val = pearsonr(df['dx_ratio'], df['accuracy'])
    ax_e.text(0.03, 0.05, f'r = {r_val:.2f}, p = {p_val:.2f}  ({len(df)} AI systems)',
              transform=ax_e.transAxes, fontsize=9, ha='left', va='bottom',
              bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFDE7', edgecolor='#E0C97F'))
    ax_e.axvline(1.0, color='#CCC', ls='--', lw=1, zorder=0)
    ax_e.set_xlabel('Mean Diagnostic Cost Ratio (AI / Physician)', fontsize=10.5)
    ax_e.set_ylabel('Diagnostic Concordance (%)', fontsize=10.5)
    ax_e.set_title('E    Diagnostic Concordance vs. Cost', fontsize=13.5, fontweight='bold', loc='left', pad=10)
    handles = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
    ax_e.legend(handles=handles, fontsize=8, loc='upper left', ncol=2, framealpha=0.95)
    ax_e.spines[['top', 'right']].set_visible(False)

    # ── Row 2, F: generational cost rise (per-family trajectory) ──
    ax_f = fig.add_subplot(gs_r2[2])
    SHORT_VER = {'gpt-4.1': '4.1', 'gpt-5.2': '5.2', 'gpt-5.5': '5.5',
                 'claude-sonnet-3.5': '3.5', 'claude-sonnet-4.5': '4.5', 'claude-opus-4.8': '4.8',
                 'gemini-2.5-pro': '2.5', 'gemini-3-pro': '3', 'gemini-3.1-pro': '3.1',
                 'grok-3': '3', 'grok-4.1': '4.1', 'grok-4.3': '4.3',
                 'llama-3.3-70b': '3.3', 'llama4': '4', 'qwen-2.5-72b': '2.5', 'qwen3': '3',
                 'qwen-3.7': '3.7', 'deepseek-v3.2': 'V3', 'deepseek-r1': 'R1'}
    # Exclude specialized + Llama (per design); fixed family order.
    PANEL_F_EXCLUDE = SPECIALIZED_MODELS | {'gemini-3.5-flash', 'llama-3.3-70b', 'llama4'}
    F_ORDER = ['GPT', 'Claude', 'Gemini', 'Grok', 'DeepSeek', 'Qwen']
    fams = {}
    for _, row in df.iterrows():
        if row['model'] in PANEL_F_EXCLUDE:
            continue
        fams.setdefault(row['family'], []).append((row['gen'], row['dx_ratio'], row['model']))
    for f in fams:
        fams[f].sort()
    net = lambda f: (fams[f][-1][1] - fams[f][0][1]) / fams[f][0][1] if len(fams[f]) > 1 and fams[f][0][1] else 0
    fam_names = [f for f in F_ORDER if f in fams]
    ymax = max(v[1] for f in fams for v in fams[f])
    group_w = 0.80
    for i, fam in enumerate(fam_names):
        vs = fams[fam]; k = len(vs); bw = group_w / k; color = FAMILY_COLORS[fam]
        for j, (g, ratio, mk) in enumerate(vs):
            alpha = 0.40 + 0.55 * (j / (k - 1)) if k > 1 else 0.80
            xp = i - group_w / 2 + (j + 0.5) * bw
            ax_f.bar(xp, ratio, bw * 0.9, color=color, alpha=alpha, edgecolor=color, linewidth=0.8)
            ax_f.text(xp, ratio + ymax * 0.015, SHORT_VER.get(mk, ''), ha='center', va='bottom',
                      fontsize=7.5, color='#555')
        if k > 1:
            ch = 100 * net(fam)
            ax_f.annotate(f"{'+' if ch > 0 else '−'}{abs(ch):.0f}%",
                          xy=(i, max(v[1] for v in vs) + ymax * 0.11), ha='center', fontsize=10,
                          fontweight='bold', color='#C62828' if ch > 0 else '#2E7D32')
    ax_f.axhline(1.0, color='#555', ls='--', lw=1.2, alpha=0.7, zorder=0)
    ax_f.set_xticks(range(len(fam_names))); ax_f.set_xticklabels(fam_names, fontsize=10)
    ax_f.set_ylim(0, ymax * 1.28)
    ax_f.set_ylabel('Mean Diagnostic Cost Ratio', fontsize=10.5)
    ax_f.set_title('F    Generational Cost Trend', fontsize=13.5, fontweight='bold', loc='left', pad=10)
    ax_f.annotate('version above each bar;\nlighter = older, darker = newer',
                  xy=(0.97, 0.97), xycoords='axes fraction', ha='right', va='top', fontsize=7.5, color='#777')
    ax_f.spines[['top', 'right']].set_visible(False)

    fig.savefig(f'{OUT_DIR}/fig3_combined.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/fig3_combined.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Figure 3 (combined): A-F ordering behavior + cost (projection moved to standalone Fig 5)')


# ══════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Defensive Ordering
# ══════════════════════════════════════════════════════════════════════
def make_supp_defensive(df):
    fig, ax = plt.subplots(figsize=(9, 7))
    df_sorted = df.sort_values('pct_added')
    y = np.arange(len(df_sorted))

    for i, (_, row) in enumerate(df_sorted.iterrows()):
        color = FAMILY_COLORS.get(row['family'], '#888')
        is_special = row['model'] in SPECIALIZED_MODELS
        ax.barh(i, row['pct_added'], height=0.65, color=color,
                alpha=0.5 if is_special else 0.85,
                edgecolor=color if is_special else 'white',
                linewidth=1.5 if is_special else 0.5,
                hatch='///' if is_special else '')
        ax.text(row['pct_added'] + 1, i, f"{row['pct_added']:.0f}%",
                fontsize=9, va='center', color='#333',
                fontweight='normal' if is_special else 'bold')

    ax.set_yticks(y)
    ax.set_yticklabels(df_sorted['label'], fontsize=10)
    ax.set_xlabel('% of Follow-Up Visits Where AI Added Diagnostic Tests', fontsize=11)
    ax.set_title('Defensive Ordering on Follow-Up Visits\n(Cases where physician ordered $0 in diagnostics)',
                fontsize=12.5, fontweight='bold', pad=10)
    ax.set_xlim(0, 100)

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/supp_defensive_ordering.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/supp_defensive_ordering.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Supp: Defensive Ordering')


# ══════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Test-Retest
# ══════════════════════════════════════════════════════════════════════
def make_supp_test_retest():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    correlations = {}
    best_model = None
    best_r = -1

    for fpath in sorted(glob.glob(str(ROOT / 'results' / 'models_original_runs' / 'm_*.json'))):
        model = os.path.basename(fpath).replace('m_', '').replace('.json', '')
        if model not in MODEL_INFO or model == 'openevidence':
            continue
        with open(fpath) as f:
            raw_cases = json.load(f)
        if 'presentation' not in raw_cases[0]:
            continue

        pres_map = {}
        for c in raw_cases:
            p = c['presentation']
            if p not in pres_map:
                pres_map[p] = []
            pres_map[p].append(c.get('medicare_llm_dx_cost') or 0)

        pairs = [(v[0], v[1]) for v in pres_map.values() if len(v) >= 2]
        if len(pairs) < 10:
            continue

        x_vals = [p[0] for p in pairs]
        y_vals = [p[1] for p in pairs]
        r, _ = pearsonr(x_vals, y_vals)
        correlations[model] = {'r': r, 'n': len(pairs)}

        if r > best_r:
            best_r = r
            best_model = model
            best_x, best_y = x_vals, y_vals

    sorted_models = sorted(correlations.keys(), key=lambda m: correlations[m]['r'])
    y_pos = np.arange(len(sorted_models))

    for i, m in enumerate(sorted_models):
        color = FAMILY_COLORS.get(MODEL_INFO[m]['family'], '#888')
        ax1.barh(i, correlations[m]['r'], color=color, alpha=0.85, height=0.65,
                edgecolor='white', linewidth=0.5)
        ax1.text(correlations[m]['r'] + 0.01, i, f"{correlations[m]['r']:.2f}",
                fontsize=9, va='center', fontweight='bold', color='#333')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([MODEL_INFO[m]['label'] for m in sorted_models], fontsize=10)
    ax1.set_xlabel('Pearson r', fontsize=11)
    ax1.set_title('A    Test-Retest Correlation\n(92 duplicate case pairs)',
                  fontsize=12, fontweight='bold', loc='left')

    if best_model:
        color = FAMILY_COLORS.get(MODEL_INFO[best_model]['family'], '#888')
        ax2.scatter(best_x, best_y, alpha=0.5, s=40, c=color, edgecolors='white', linewidth=0.8)
        max_val = max(max(best_x), max(best_y))
        ax2.plot([0, max_val*1.05], [0, max_val*1.05], '--', color='#E15759',
                alpha=0.6, lw=1.5, label='Perfect agreement')
        ax2.set_xlabel('Cost — 1st Occurrence ($)', fontsize=11)
        ax2.set_ylabel('Cost — 2nd Occurrence ($)', fontsize=11)
        ax2.set_title(f'B    {MODEL_INFO[best_model]["label"]} (r = {best_r:.2f})',
                     fontsize=12, fontweight='bold', loc='left')
        ax2.legend(fontsize=9)

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/supp_test_retest.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/supp_test_retest.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Supp: Test-Retest')


# ══════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Case Characteristics
# ══════════════════════════════════════════════════════════════════════
def make_supp_case_characteristics(all_data):
    """4-panel: specialty, diagnosis categories, human cost distribution, visit type."""
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2, wspace=0.3, hspace=0.35)

    # Use gpt-4.1 as reference (all models share same cases)
    cases = all_data['gpt-4.1']

    from collections import Counter, defaultdict

    # ── Panel A: Specialty distribution (pie) ──
    ax_a = fig.add_subplot(gs[0, 0])
    specs = Counter(c['specialty'] for c in cases)
    spec_labels = {
        'SOAP / Chart / Progress Notes': 'SOAP/Progress\nNotes',
        'Consult - History and Phy.': 'Consult\nH&P',
        'General Medicine': 'General\nMedicine',
        'Emergency Room Reports': 'Emergency\nRoom',
    }
    labels = [spec_labels.get(s, s) for s in specs.keys()]
    sizes = list(specs.values())
    colors = ['#4393C3', '#F4A582', '#8073AC', '#D6604D']
    wedges, texts, autotexts = ax_a.pie(
        sizes, labels=labels, colors=colors, autopct=lambda p: f'{p:.0f}%\n(n={int(p*sum(sizes)/100)})',
        startangle=90, textprops={'fontsize': 10}, pctdistance=0.65)
    for t in autotexts:
        t.set_fontsize(8.5)
        t.set_color('#333')
    ax_a.set_title('A    Clinical Specialties', fontsize=13,
                    fontweight='bold', pad=15)

    # ── Panel B: Diagnosis categories (horizontal bar) ──
    ax_b = fig.add_subplot(gs[0, 1])

    # Categorize primary diagnoses — expanded keyword lists to reduce 'Other' residual
    dx_categories = {
        'Cardiovascular': ['hypertension', 'htn', 'chf', 'heart failure', 'cardiac', 'afib',
                          'atrial fib', 'coronary', 'cad', 'angina', 'chest pain', 'dvt',
                          'murmur', 'aortic', 'mitral', 'pericard', 'hyperlipid', 'hypercholest',
                          'arrhythmia', 'palpitation', 'syncope', 'hypotension', 'bradycardia',
                          'tachycardia', 'peripheral vascular', 'edema', 'valvular'],
        'Endocrine/Metabolic': ['diabetes', 'diabet', 'dm ', 'dm2', 't2dm', 'thyroid', 'hypothyroid',
                               'hyperthyroid', 'obesity', 'weight loss', 'weight gain',
                               'metabolic', 'lipid', 'cholesterol', 'adrenal', 'cushing',
                               'hyperparathyroid', 'hyponatremia', 'hyperkalemia', 'dehydration',
                               'vitamin d', 'osteoporosis', 'osteopenia'],
        'Respiratory': ['copd', 'asthma', 'pneumonia', 'bronchitis', 'cough', 'dyspnea',
                       'respiratory', 'lung', 'apnea', 'uri', 'upper respiratory', 'sinusitis',
                       'pharyngitis', 'rhinitis', 'allerg', 'wheez', 'hemoptysis', 'pleur'],
        'GI/Hepatic': ['gerd', 'reflux', 'abdominal pain', 'abdomen', 'nausea', 'vomit',
                      'gastro', 'liver', 'hepat', 'colitis', 'diarrhea', 'constipat',
                      'ulcer', 'dysphagia', 'pancreat', 'cholecyst', 'biliary', 'hemorrhoid',
                      'ibs', 'crohn', 'c. difficile', 'c.diff', 'c diff'],
        'Musculoskeletal/Pain': ['pain', 'arthritis', 'arthralg', 'back', 'neck', 'knee',
                                'shoulder', 'hip', 'joint', 'fracture', 'osteo',
                                'epicondyl', 'carpal', 'tendon', 'muscle', 'bursitis',
                                'sprain', 'strain', 'radiculopathy', 'cervicalgia', 'lumbago',
                                'spinal stenos', 'disc', 'fibromyalg'],
        'Neurological': ['headache', 'migraine', 'seizure', 'neuro', 'neuropathy', 'dizziness',
                        'vertigo', 'stroke', 'tia', 'tethered', 'dementia', 'alzheimer',
                        'parkinson', 'ms ', 'multiple sclerosis', 'tremor', 'ataxia', 'weakness',
                        'numbness', 'tingling', 'paresthesia', 'memory loss', 'cognitive'],
        'Psychiatric/Behavioral': ['depression', 'depressive', 'anxiety', 'anxious', 'bipolar',
                                  'adhd', 'insomnia', 'psych', 'mental', 'substance',
                                  'alcohol', 'panic', 'ptsd', 'ocd', 'schizo'],
        'Infectious': ['infection', 'uti', 'urinary tract', 'cellulitis', 'abscess', 'sepsis',
                      'fever', 'viral', 'cystitis', 'pyelonephritis', 'gastroenteritis'],
        'Oncology': ['cancer', 'carcinoma', 'tumor', 'malignant', 'oncol', 'lymphoma',
                    'leukemia', 'melanoma', 'glioma', 'metasta', 'neoplas', 'chemother',
                    'radiation therapy'],
        'Dermatologic': ['rash', 'eczema', 'dermat', 'skin lesion', 'acne', 'psoriasis',
                        'wound', 'laceration', 'ulcer (skin)', 'nevi', 'mole'],
        'Well Visit/Preventive': ['well child', 'well-child', 'well baby', 'newborn', 'routine',
                                 'checkup', 'follow-up', 'followup', 'follow up', 'screening',
                                 'postpartum', 'prenatal', 'preoperative', 'pre-op',
                                 'annual', 'preventive'],
        'Genitourinary / Renal': ['renal', 'kidney', 'ckd', 'chronic kidney', 'bph',
                                 'prostat', 'hematuria', 'proteinuria', 'nephro', 'dialys',
                                 'transplant', 'incontinence', 'urinary retention'],
        'Trauma / Injury': ['mvc', 'motor vehicle', 'contusion', 'trauma', 'injury', 'fall',
                           'laceration', 'burn', 'assault'],
    }

    cat_counts = Counter()
    for c in cases:
        dx_list = c.get('human_diagnoses', [])
        if not dx_list:
            cat_counts['Unclassified'] += 1
            continue
        dx = dx_list[0].lower()
        found = False
        for cat, keywords in dx_categories.items():
            if any(kw in dx for kw in keywords):
                cat_counts[cat] += 1
                found = True
                break
        if not found:
            cat_counts['Other'] += 1

    # Approximate NAMCS 2019 ambulatory visit share by diagnosis category
    # (CDC National Ambulatory Medical Care Survey 2019 Summary Tables, office-based
    # visits, primary diagnosis by major category — approximate values for context only)
    NAMCS_SHARE = {
        'Cardiovascular': 16.0,
        'Endocrine/Metabolic': 12.0,
        'Musculoskeletal/Pain': 12.0,
        'Well Visit/Preventive': 13.0,
        'Psychiatric/Behavioral': 7.0,
        'Respiratory': 8.0,
        'GI/Hepatic': 5.0,
        'Infectious': 5.0,
        'Oncology': 3.0,
        'Dermatologic': 4.0,
        'Neurological': 3.0,
        'Genitourinary / Renal': 4.0,
        'Trauma / Injury': 3.0,
        'Other': 3.0,
        'Unclassified': 2.0,
    }

    # Compute MTSamples share as %
    n_total = sum(cat_counts.values())
    cats_all = list(set(cat_counts.keys()) | set(NAMCS_SHARE.keys()))
    mts_share = {c: 100 * cat_counts.get(c, 0) / n_total for c in cats_all}
    namcs_share = {c: NAMCS_SHARE.get(c, 0) for c in cats_all}

    # Sort by MTSamples share desc
    sorted_cats = sorted(cats_all, key=lambda c: -mts_share[c])
    y_pos = np.arange(len(sorted_cats))
    bar_h = 0.38
    mts_vals = [mts_share[c] for c in sorted_cats]
    namcs_vals = [namcs_share[c] for c in sorted_cats]

    ax_b.barh(y_pos - bar_h/2, mts_vals, height=bar_h, color='#4393C3',
              edgecolor='white', linewidth=0.5, label='MTSamples (n=200)')
    ax_b.barh(y_pos + bar_h/2, namcs_vals, height=bar_h, color='#C0C0C0',
              edgecolor='white', linewidth=0.5, label='NAMCS 2019 (approx.)')

    for i, (m, n) in enumerate(zip(mts_vals, namcs_vals)):
        ax_b.text(max(m, n) + 0.5, i, f'{m:.0f}% / {n:.0f}%',
                  fontsize=8, va='center', color='#333')

    ax_b.set_yticks(y_pos)
    ax_b.set_yticklabels(sorted_cats, fontsize=9)
    ax_b.set_xlabel('Share of Visits (%)', fontsize=10.5)
    ax_b.set_title('B    Primary Diagnosis Categories: MTSamples vs. NAMCS 2019',
                    fontsize=12, fontweight='bold', loc='left', pad=10)
    ax_b.legend(fontsize=8.5, loc='lower right', framealpha=0.95)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.invert_yaxis()

    # ── Panel C: Human cost distribution (histogram) ──
    ax_c = fig.add_subplot(gs[1, 0])

    h_dx = [float(c.get('medicare_human_dx_cost') or 0) for c in cases]
    h_med = [float(c.get('medicare_human_med_cost') or 0) for c in cases]
    h_ref = [float(c.get('human_referral_cost') or 0) for c in cases]
    h_total = [d+m+r for d,m,r in zip(h_dx, h_med, h_ref)]

    # Stacked histogram: show how many cases fall in each cost bucket
    bins = [0, 1, 50, 100, 200, 500, 1000, 3000]
    bin_labels = ['$0', '$1-50', '$51-100', '$101-200', '$201-500', '$501-1K', '>$1K']

    dx_hist = np.histogram(h_dx, bins=bins)[0]
    med_hist = np.histogram(h_med, bins=bins)[0]
    total_hist = np.histogram(h_total, bins=bins)[0]

    x = np.arange(len(bin_labels))
    w = 0.25
    ax_c.bar(x - w, dx_hist, w, color=COMP_COLORS['Diagnostic'], alpha=0.85, label='Diagnostic')
    ax_c.bar(x, med_hist, w, color=COMP_COLORS['Medication'], alpha=0.85, label='Medication')
    ax_c.bar(x + w, total_hist, w, color='#666', alpha=0.6, label='Total')

    ax_c.set_xticks(x)
    ax_c.set_xticklabels(bin_labels, fontsize=9)
    ax_c.set_xlabel('Physician Cost per Visit', fontsize=10.5)
    ax_c.set_ylabel('Number of Cases', fontsize=10.5)
    ax_c.set_title('C    Physician Cost Distribution', fontsize=13,
                    fontweight='bold', loc='left', pad=10)
    ax_c.legend(fontsize=9, framealpha=0.95)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)

    # ── Panel D: Visit type and complexity ──
    ax_d = fig.add_subplot(gs[1, 1])

    # Categorize visits
    n_zero_dx = sum(1 for x in h_dx if x == 0)
    n_low = sum(1 for x in h_dx if 0 < x <= 100)
    n_mid = sum(1 for x in h_dx if 100 < x <= 500)
    n_high = sum(1 for x in h_dx if x > 500)

    visit_types = ['Follow-up\n(No Dx ordered)', 'Low workup\n($1-100)', 'Moderate workup\n($101-500)', 'High workup\n(>$500)']
    visit_counts = [n_zero_dx, n_low, n_mid, n_high]
    visit_colors = ['#B0B0B0', '#A1D99B', '#FDD0A2', '#FC9272']

    bars = ax_d.bar(visit_types, visit_counts, color=visit_colors, edgecolor='white',
                    linewidth=0.5, width=0.6)
    for bar, v in zip(bars, visit_counts):
        ax_d.text(bar.get_x() + bar.get_width()/2, v + 2, f'{v}\n({100*v/len(cases):.1f}%)',
                 ha='center', fontsize=10, fontweight='bold', color='#333')

    ax_d.set_ylabel('Number of Cases', fontsize=10.5)
    ax_d.set_title('D    Visit Complexity (by Physician Ordering)', fontsize=13,
                    fontweight='bold', loc='left', pad=10)
    ax_d.spines['top'].set_visible(False)
    ax_d.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(f'{OUT_DIR}/supp_case_characteristics.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/supp_case_characteristics.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Supp: Case Characteristics')


# ══════════════════════════════════════════════════════════════════════
# SUPPLEMENTARY: Diagnostic Utilization Analysis
# ══════════════════════════════════════════════════════════════════════
def make_supp_utilization(all_data):
    """3-panel: top AI-ordered tests, volume vs cost by category, test count distribution."""
    from collections import Counter, defaultdict

    fig = plt.figure(figsize=(18, 6.5))
    gs = gridspec.GridSpec(1, 3, wspace=0.35, width_ratios=[1.2, 0.8, 1.0])

    # Collect data across all models and cases
    top_tests = Counter()       # canonical CPT code -> # of $0-physician visits ordering it
    top_test_desc = defaultdict(Counter)  # key -> {raw description: n} (for fallback labels)
    n_zero_pairs = 0            # model-case pairs where physician=$0

    cat_ai_orders = Counter()   # category -> total AI order count
    cat_human_orders = Counter()
    cat_ai_cost = Counter()     # category -> total AI cost
    cat_human_cost = Counter()

    ai_test_counts = []         # number of dx tests per encounter (AI)
    human_test_counts = []      # number of dx tests per encounter (human)

    for model, cases in all_data.items():
        if model not in MODEL_INFO:
            continue
        seen = set()
        for c in cases:
            pid = c.get('presentation', c.get('case_id', ''))
            if pid in seen:
                continue
            seen.add(pid)

            h_dx = c.get('medicare_human_dx_cost') or 0
            l_dx = c.get('medicare_llm_dx_cost') or 0

            # Get orders (use slot B which has CPT codes and prices)
            l_orders = c.get('llm_orders_b', []) or []
            h_orders = c.get('human_orders_b', []) or []

            # Filter to diagnostic orders (exclude medications, referrals)
            dx_cats = {'labs', 'imaging', 'procedure', 'monitoring', 'exam'}
            l_dx_orders = [o for o in l_orders if o.get('category', '') in dx_cats]
            h_dx_orders = [o for o in h_orders if o.get('category', '') in dx_cats]

            ai_test_counts.append(len(l_dx_orders))
            human_test_counts.append(len(h_dx_orders))

            # Category breakdown
            for o in l_dx_orders:
                cat = o.get('category', 'other')
                cat_ai_orders[cat] += 1
                cat_ai_cost[cat] += o.get('price', 0) or 0
            for o in h_dx_orders:
                cat = o.get('category', 'other')
                cat_human_orders[cat] += 1
                cat_human_cost[cat] += o.get('price', 0) or 0

            # Top tests when physician ordered $0 — group by canonical CPT code so
            # name variants of the same test (e.g. "CBC", "complete blood count",
            # "CBC with differential" -> 85025) collapse into one bar. Count each
            # canonical test at most once per visit ("% of visits ordering it").
            if h_dx == 0 and len(l_dx_orders) > 0:
                n_zero_pairs += 1
                seen_keys = set()
                for o in l_dx_orders:
                    desc = (o.get('order') or '').strip()
                    if not desc or desc.lower() == 'none':
                        continue
                    code = o.get('cpt_code')
                    key = f"cpt:{code}" if code else desc.lower()
                    top_test_desc[key][desc.lower()] += 1
                    if key not in seen_keys:
                        seen_keys.add(key)
                        top_tests[key] += 1

    # ── Panel A: Top 10 AI-ordered tests when physician=$0 ──
    ax_a = fig.add_subplot(gs[0])
    top10 = top_tests.most_common(10)
    # Canonical display labels for the common CPT codes (collapses name variants)
    CPT_CANON = {
        '85025': 'CBC', '80053': 'Comprehensive metabolic panel',
        '83036': 'Hemoglobin A1c', '84443': 'TSH', '80048': 'Basic metabolic panel',
        '80061': 'Lipid panel', '85652': 'ESR', '82607': 'Vitamin B12',
        '86140': 'C-reactive protein (CRP)', '82947': 'Fasting glucose',
        '71046': 'Chest X-ray', '71020': 'Chest X-ray', '81003': 'Urinalysis',
        '81001': 'Urinalysis', '93000': 'EKG', '80076': 'Hepatic function panel (LFTs)',
        '82746': 'Folate', '84439': 'Free T4', '82728': 'Ferritin',
    }
    # Clean up names for display
    def fmt_test_name(name):
        name = name.title()
        replacements = {
            'Complete Blood Count With Differential': 'CBC with differential',
            'Comprehensive Metabolic Panel': 'Comprehensive metabolic panel',
            'Comprehen Metabolic Panel': 'Comprehensive metabolic panel',
            'Hemoglobin A1C': 'Hemoglobin A1c',
            'Hemoglobin A1c': 'Hemoglobin A1c',
            'Lipid Panel': 'Lipid panel',
            'Thyroid Stimulating Hormone': 'TSH',
            'Basic Metabolic Panel': 'Basic metabolic panel',
            'Glucose Blood': 'Glucose',
            'Hepatic Function Panel': 'Hepatic function panel',
            'Urinalysis Automated': 'Urinalysis',
            'X-Ray Chest 2 Views': 'Chest X-ray (2 views)',
            'Vitamin B12': 'Vitamin B12',
            'C-Reactive Protein': 'C-reactive protein (CRP)',
            'Complete Cbc Automated': 'CBC (automated)',
        }
        for old, new in replacements.items():
            if name == old:
                return new
        return name

    def label_for(key):
        if key.startswith('cpt:'):
            code = key[4:]
            if code in CPT_CANON:
                return CPT_CANON[code]
            # unknown code: use its most common raw description, cleaned
            return fmt_test_name(top_test_desc[key].most_common(1)[0][0])
        return fmt_test_name(key)

    test_names = [label_for(t[0]) for t in top10]
    test_pcts = [100 * t[1] / n_zero_pairs for t in top10]

    y_pos = np.arange(len(test_names))
    colors_a = ['#4393C3'] * len(test_names)

    bars = ax_a.barh(y_pos, test_pcts, height=0.65, color=colors_a, alpha=0.85,
                     edgecolor='white', linewidth=0.5)
    for i, (bar, pct) in enumerate(zip(bars, test_pcts)):
        ax_a.text(pct + 0.8, i, f'{pct:.0f}%', fontsize=9, va='center',
                 fontweight='bold', color='#333')

    ax_a.set_yticks(y_pos)
    ax_a.set_yticklabels(test_names, fontsize=10)
    ax_a.set_xlabel('% of follow-up visits with test ordered', fontsize=10.5)
    ax_a.set_title('A    Most Common AI-Ordered Tests\n(when physician ordered none)',
                   fontsize=12, fontweight='bold', loc='left', pad=10)
    ax_a.invert_yaxis()
    ax_a.spines['top'].set_visible(False)
    ax_a.spines['right'].set_visible(False)
    ax_a.set_xlim(0, max(test_pcts) * 1.2)

    # ── Panel B: Volume vs Cost share by category ──
    ax_b = fig.add_subplot(gs[1])

    # Focus on main categories
    main_cats = ['labs', 'imaging', 'procedure', 'monitoring']
    cat_labels = ['Labs', 'Imaging', 'Procedures', 'Monitoring']
    cat_colors = ['#4393C3', '#F4A582', '#E15759', '#B0B0B0']

    # Compute excess shares
    total_excess_orders = sum(cat_ai_orders[c] - cat_human_orders.get(c, 0) for c in main_cats)
    total_excess_cost = sum(cat_ai_cost[c] - cat_human_cost.get(c, 0) for c in main_cats)

    volume_shares = []
    cost_shares = []
    for c in main_cats:
        excess_orders = cat_ai_orders[c] - cat_human_orders.get(c, 0)
        excess_cost = cat_ai_cost[c] - cat_human_cost.get(c, 0)
        volume_shares.append(100 * excess_orders / total_excess_orders if total_excess_orders > 0 else 0)
        cost_shares.append(100 * excess_cost / total_excess_cost if total_excess_cost > 0 else 0)

    x_pos = np.arange(len(main_cats))
    width = 0.35

    bars1 = ax_b.bar(x_pos - width/2, volume_shares, width, color=[c + '99' for c in cat_colors],
                     edgecolor='white', linewidth=0.5, label='Share of excess orders')
    bars2 = ax_b.bar(x_pos + width/2, cost_shares, width, color=cat_colors,
                     alpha=0.85, edgecolor='white', linewidth=0.5, label='Share of excess cost')

    for bar, val in zip(bars1, volume_shares):
        if val > 3:
            ax_b.text(bar.get_x() + bar.get_width()/2, val + 1.5, f'{val:.0f}%',
                     ha='center', fontsize=8.5, fontweight='bold', color='#555')
    for bar, val in zip(bars2, cost_shares):
        if val > 3:
            ax_b.text(bar.get_x() + bar.get_width()/2, val + 1.5, f'{val:.0f}%',
                     ha='center', fontsize=8.5, fontweight='bold', color='#333')

    ax_b.set_xticks(x_pos)
    ax_b.set_xticklabels(cat_labels, fontsize=10)
    ax_b.set_ylabel('% of total excess', fontsize=10.5)
    ax_b.set_title('B    Excess Orders vs. Excess Cost\n(by category)',
                   fontsize=12, fontweight='bold', loc='left', pad=10)
    ax_b.legend(fontsize=8.5, loc='upper right', framealpha=0.95)
    ax_b.spines['top'].set_visible(False)
    ax_b.spines['right'].set_visible(False)
    ax_b.set_ylim(0, max(max(volume_shares), max(cost_shares)) * 1.25)

    # ── Panel C: Distribution of test counts per encounter ──
    ax_c = fig.add_subplot(gs[2])

    bins = np.arange(0, 20, 1)
    ai_counts = np.array(ai_test_counts)
    human_counts = np.array(human_test_counts)

    ax_c.hist(human_counts, bins=bins, alpha=0.6, color='#66A61E', edgecolor='white',
              linewidth=0.5, label=f'Physician (mean {human_counts.mean():.1f})', density=True)
    ax_c.hist(ai_counts, bins=bins, alpha=0.5, color='#E15759', edgecolor='white',
              linewidth=0.5, label=f'AI (mean {ai_counts.mean():.1f})', density=True)

    # Mark kitchen sink threshold
    ax_c.axvline(x=8, color='#333', linestyle='--', lw=1.2, alpha=0.7)
    pct_kitchen = 100 * np.sum(ai_counts >= 8) / len(ai_counts)
    ax_c.text(8.3, ax_c.get_ylim()[1] * 0.85, f'≥8 tests\n({pct_kitchen:.0f}% of AI)',
             fontsize=9, color='#333', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFDE7',
                      edgecolor='#E0C97F', alpha=0.95))

    ax_c.set_xlabel('Diagnostic tests per encounter', fontsize=10.5)
    ax_c.set_ylabel('Density', fontsize=10.5)
    ax_c.set_title('C    Distribution of Test Counts\n(AI vs. Physician)',
                   fontsize=12, fontweight='bold', loc='left', pad=10)
    ax_c.legend(fontsize=9, loc='upper right', framealpha=0.95)
    ax_c.spines['top'].set_visible(False)
    ax_c.spines['right'].set_visible(False)
    ax_c.set_xlim(-0.5, 18)

    fig.savefig(f'{OUT_DIR}/supp_utilization.png', dpi=300, bbox_inches='tight')
    fig.savefig(f'{OUT_DIR}/supp_utilization.pdf', bbox_inches='tight')
    plt.close(fig)
    print('✓ Supp: Diagnostic Utilization')


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('Loading data...')
    all_data = load_unified_panel()   # 23-system unified standard-prompt panel
    print(f'Loaded {len(all_data)} models')

    print('\nBuilding statistics...')
    df = build_stats_df(all_data)

    # Verification
    print('\n── Verification ──')
    for _, row in df.sort_values('dx_ratio').iterrows():
        print(f"{row['label']:20s} N={row['n']:3.0f}  "
              f"Dx={row['dx_ratio']:.2f}×  Total={row['total_ratio']:.2f}×  "
              f"Excess=${row['excess_total']:.0f}  "
              f"Acc={row['accuracy']:.0f}%  Def={row['pct_added']:.0f}%")

    print('\n── Generating Figures ──')
    # Figure 1 is a hand-drawn study-design schematic (paper/figures/fig1_study_design.png,
    # bronchiolitis exemplar MTS_0481); it is not generated programmatically.
    make_fig2(df)
    make_fig3_combined(df, all_data)   # merged Fig 3 (old 3 + 4), 7 panels A-G
    make_fig3_cost(df, all_data)       # retained: subpanels for supplement / reference
    make_fig3_scatter(df)
    make_fig4(df)
    make_supp_defensive(df)
    make_supp_test_retest()
    make_supp_case_characteristics(all_data)
    make_supp_utilization(all_data)

    print(f'\n✓ All figures saved to {OUT_DIR}/')
