#!/usr/bin/env python3
"""
Run Grok 4.20 on the same guideline currency assessment task.
Sends cases in batches to stay within rate limits.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'medbar'))

import pandas as pd
import json
import time
import os
from pipeline.cloud_llm_client import CloudLLMClient

SCORING_PROMPT = """You are a physician reviewer assessing whether clinical assessment and plans from the mid-2000s are still current under 2026 clinical guidelines.

For each case below, score the physician's plan on a 1-5 scale:

1 = Fully current — plan would be essentially the same today
2 = Mostly current — minor updates possible, core approach unchanged
3 = Partially outdated — some elements have changed but core approach may still be valid
4 = Significantly outdated — major treatment elements have changed
5 = Substantially outdated — current standard of care is fundamentally different

Key areas where guidelines have changed substantially since the mid-2000s include (but are not limited to):
- Opioid prescribing (CDC 2016/2022 guidelines — non-opioid first-line for most pain)
- Opioid use disorder treatment (buprenorphine/MAT is now standard of care)
- Heart failure (four-pillar therapy: ARNI, beta-blocker, MRA, SGLT2i)
- Anticoagulation (DOACs replacing warfarin for AF and VTE)
- Diabetes (SGLT2 inhibitors, GLP-1 RAs for cardiorenal protection)
- Obesity (GLP-1 receptor agonists)
- Cancer (immunotherapy, molecular profiling for NSCLC)
- HIV (integrase inhibitor-based ART)
- Hepatitis C (curative DAA therapy)
- C. difficile (oral vancomycin/fidaxomicin over metronidazole)
- Antibiotic stewardship (no antibiotics for viral URI, avoid fluoroquinolones when possible)
- Screening (colonoscopy at 45, Pap every 3-5yr not annually, shared decision-making for PSA)
- Benzodiazepines (SSRIs/SNRIs first-line for anxiety, not benzos)
- Asthma (ICS-formoterol as maintenance and reliever per GINA)
- Bariatric surgery (sleeve > Lap-Band; GLP-1 RAs as pharmacological option)

Return a JSON array with one object per case. Each object must have:
- "case_id": the Case ID exactly as given
- "score": integer 1-5
- "comment": brief explanation (1-3 sentences)

Return ONLY the JSON array, no other text.

CASES:
{cases_text}
"""

def format_case(row):
    ap = str(row['Human A&P'])
    if len(ap) > 1000:
        ap = ap[:1000] + '...'
    meds = str(row['Human Medications']) if pd.notna(row['Human Medications']) else 'None'
    tests = str(row['Human Tests']) if pd.notna(row['Human Tests']) else 'None'
    diag = str(row['Human Diagnoses']) if pd.notna(row['Human Diagnoses']) else 'None'
    return f"""Case ID: {row['Case ID']}
Sample: {row['Sample Name']}
Diagnoses: {diag}
A&P: {ap}
Medications: {meds}
Tests: {tests}
---"""


def run_batch(llm, cases_text, attempt=0):
    """Run a batch through Grok and parse results."""
    prompt = SCORING_PROMPT.format(cases_text=cases_text)

    for retry in range(3):
        try:
            response = llm.generate(prompt, max_tokens=8192, temperature=0.2)
            # Try to extract JSON from response
            text = response.strip()
            # Find JSON array
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > start:
                json_text = text[start:end]
                results = json.loads(json_text)
                return results
            else:
                print(f"  No JSON array found in response (attempt {retry+1})")
                print(f"  Response preview: {text[:200]}")
        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {retry+1}): {e}")
            print(f"  Text preview: {json_text[:200] if 'json_text' in locals() else 'N/A'}")
        except Exception as e:
            print(f"  API error (attempt {retry+1}): {e}")
            if "429" in str(e):
                wait = 2 ** retry * 10
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                time.sleep(5)

    return None


def main():
    df = pd.read_excel('paper/Supplementary_Table_1.xlsx')

    llm = CloudLLMClient(provider="openrouter", model="x-ai/grok-4.20")
    print(f"Using model: {llm.model}")

    # Process in batches of 20 cases
    batch_size = 20
    all_results = []

    for batch_start in range(0, len(df), batch_size):
        batch_end = min(batch_start + batch_size, len(df))
        batch = df.iloc[batch_start:batch_end]

        cases_text = "\n".join(format_case(row) for _, row in batch.iterrows())

        print(f"Processing cases {batch_start}-{batch_end-1} ({len(batch)} cases)...")
        results = run_batch(llm, cases_text)

        if results:
            all_results.extend(results)
            print(f"  Got {len(results)} results")
        else:
            print(f"  FAILED for batch {batch_start}-{batch_end-1}")
            # Add placeholder results
            for _, row in batch.iterrows():
                all_results.append({
                    "case_id": row['Case ID'],
                    "score": -1,
                    "comment": "FAILED TO PROCESS"
                })

        # Small delay between batches
        if batch_end < len(df):
            time.sleep(2)

    # Build output dataframe
    # Map results by case_id
    result_map = {}
    for r in all_results:
        cid = r.get('case_id', '')
        result_map[cid] = r

    rows = []
    for i in range(len(df)):
        row = df.iloc[i]
        cid = row['Case ID']
        r = result_map.get(cid, {"score": -1, "comment": "NOT FOUND"})
        rows.append({
            'Case ID': cid,
            'Grok Score': r.get('score', -1),
            'Grok Comment': r.get('comment', ''),
        })

    out_df = pd.DataFrame(rows)
    out_df.to_csv('data/grok_guideline_scores.csv', index=False)

    # Print summary
    print("\n" + "="*60)
    print("GROK 4.20 SCORING SUMMARY")
    print("="*60)
    scores = out_df['Grok Score']
    valid = scores[scores > 0]
    for s in range(1, 6):
        n = (valid == s).sum()
        pct = n / len(valid) * 100
        print(f"  Score {s}: {n} ({pct:.1f}%)")
    print(f"  Failed: {(scores <= 0).sum()}")
    print(f"  Mean: {valid.mean():.2f}")

    # Load Claude scores for comparison
    claude_df = pd.read_excel('data/guideline_currency_review.xlsx')
    comparison = pd.DataFrame({
        'Case ID': out_df['Case ID'],
        'Claude Score': claude_df['Guideline Currency Score (1-5)'],
        'Grok Score': out_df['Grok Score'],
    })
    comparison['Diff'] = comparison['Grok Score'] - comparison['Claude Score']

    print(f"\nCOMPARISON WITH CLAUDE:")
    print(f"  Exact agreement: {(comparison['Diff'] == 0).sum()} ({(comparison['Diff'] == 0).mean()*100:.1f}%)")
    print(f"  Within ±1: {(comparison['Diff'].abs() <= 1).sum()} ({(comparison['Diff'].abs() <= 1).mean()*100:.1f}%)")
    print(f"  Grok higher (more outdated): {(comparison['Diff'] > 0).sum()}")
    print(f"  Grok lower (less outdated): {(comparison['Diff'] < 0).sum()}")

    # KEY: Cases where they disagree by ≥2 points
    big_disagree = comparison[comparison['Diff'].abs() >= 2]
    if len(big_disagree) > 0:
        print(f"\n  DISAGREEMENTS (≥2 points, N={len(big_disagree)}):")
        for _, r in big_disagree.iterrows():
            grok_comment = out_df[out_df['Case ID'] == r['Case ID']]['Grok Comment'].values[0]
            print(f"    {r['Case ID']}: Claude={r['Claude Score']}, Grok={r['Grok Score']}  ({grok_comment[:100]})")

    # Cases Grok flags as 4-5 that Claude scored 1-2
    missed = comparison[(comparison['Grok Score'] >= 4) & (comparison['Claude Score'] <= 2)]
    if len(missed) > 0:
        print(f"\n  POTENTIAL MISSES (Grok 4-5, Claude 1-2, N={len(missed)}):")
        for _, r in missed.iterrows():
            grok_comment = out_df[out_df['Case ID'] == r['Case ID']]['Grok Comment'].values[0]
            sample = df[df['Case ID'] == r['Case ID']]['Sample Name'].values[0]
            print(f"    {r['Case ID']} ({sample}): Claude={r['Claude Score']}, Grok={r['Grok Score']}")
            print(f"      Grok says: {grok_comment[:200]}")

    comparison.to_csv('data/claude_vs_grok_scores.csv', index=False)
    print(f"\nSaved to data/grok_guideline_scores.csv and data/claude_vs_grok_scores.csv")


if __name__ == "__main__":
    main()
