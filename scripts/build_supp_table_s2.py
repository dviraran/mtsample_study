#!/usr/bin/env python3
"""
Regenerate Supplementary Table S2 (complete case-level data) from the canonical
24-system panel in results/models/.

Schema (matches the original S2): 10 human/global columns + 6 columns per model
(Diagnoses, Agreement, Dx Cost ($), Tests, Medications, Referral Count).

Conventions (documented for the submission):
  - Dx Cost ($)     : canonical median-of-three-extractions diagnostic cost
                      (medicare_*_dx_cost), CY 2026 Medicare, post-cleanup.
  - Agreement       : 3-judge majority concordance tier (concordant/adjacent/
                      discordant) using the SAME logic as the manuscript figures
                      (dx_match_v2, dx_claude, dx_gemini; 3-way tie -> ordinal middle).
  - Tests / Meds    : orders from the median-by-count extraction of the three
                      independent extractions (Tests = labs+imaging; Meds = medication),
                      so the listed orders track the median cost/counts the paper reports.
  - Referral Count  : canonical *_referral_count.
Cases follow the 200-case primary cohort (gpt-4.1 reference); cells are blank for the
few models missing a case (gemini-2.5-pro, qwen3).

Usage: python3 scripts/build_supp_table_s2.py [out.xlsx]
"""
import glob, json, re, sys
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models"
FIG = ROOT / "figures" / "generate_paper_figures.py"

# --- pull the canonical model -> display-label map straight from the figure script ---
src = FIG.read_text()
LABEL = dict(re.findall(r"'([a-z0-9.\-]+)':\s*\{'label':\s*'([^']+)'", src))

# --- 3-judge majority concordance (identical to generate_paper_figures.py) ---
_TIER = {'correct': 2, 'correct_plus': 2, 'related': 1, 'wrong': 0}
_JUDGE = ('dx_match_v2', 'dx_claude', 'dx_gemini')
_TIERNAME = {2: 'concordant', 1: 'adjacent', 0: 'discordant'}

def agreement(case):
    ts = [_TIER[case[f]] for f in _JUDGE if case.get(f) in _TIER]
    if not ts:
        return None
    c = Counter(ts)
    top, n = c.most_common(1)[0]
    if n == 1 and len(c) == len(ts):
        top = sorted(ts)[len(ts) // 2]
    return _TIERNAME[top]

TEST_CATS = {"labs", "imaging"}
MED_CATS = {"medication"}

def median_list(rec, prefix, cats):
    """Orders (joined) from the median-by-count of the three extractions for `cats`."""
    lists = []
    for ext in ("a", "b", "c"):
        orders = rec.get(f"{prefix}_orders_{ext}") or []
        names, seen = [], set()
        for o in orders:
            if o.get("category") in cats:
                nm = str(o.get("order", "")).strip()
                if nm and nm.lower() not in seen:
                    seen.add(nm.lower()); names.append(nm)
        lists.append(names)
    mid = sorted(lists, key=len)[1]           # median by count
    return "; ".join(mid) if mid else ""

def diag(lst):
    return "; ".join(lst) if isinstance(lst, list) else ("" if lst is None else str(lst))

def side_tables():
    """Case-level fields the caption promises that do not live in results/models/.

    Each source is the same file the corresponding analysis reads, so the
    spreadsheet cannot drift from the published numbers:
      encounter type          results/analysis/visit_type.json  (post-adjudication)
      consensus / CCI         results/analysis/case_consensus.json
      guideline currency      data/guideline_currency_review.xlsx
      appropriateness         data/appropriateness_review.xlsx  (S.S., 5 systems)
    """
    vt = {c["case_id"]: c for c in json.load(open(ROOT / "results/analysis/visit_type.json"))["cases"]}
    cc = json.load(open(ROOT / "results/analysis/case_consensus.json"))

    gc = pd.read_excel(ROOT / "data/guideline_currency_review.xlsx")
    gc = {r["Case ID"]: r for _, r in gc.iterrows()}

    ap = pd.read_excel(ROOT / "data/appropriateness_review.xlsx")
    # the reviewer's own score sits in an unnamed column after each model block,
    # which pandas de-duplicates as Score, Score.1, ... in model order
    ap_models = ["GPT-5.2", "Claude 4.5", "Gemini 3", "Grok 4.1", "OpenEvidence"]
    ap_cols = ["Score"] + [f"Score.{i}" for i in range(1, len(ap_models))]
    ap = {r["case_id"]: {m: r[c] for m, c in zip(ap_models, ap_cols)}
          for _, r in ap.iterrows()}
    return vt, cc, gc, ap, ap_models


def look(table, cid, field):
    """table[cid][field], or None. Rows may be pandas Series, whose truthiness
    is ambiguous, so the missing-key test has to be explicit."""
    rec = table.get(cid)
    if rec is None:
        return None
    v = rec.get(field)
    return None if v is None or (isinstance(v, float) and v != v) else v


ENC_LABEL = {"first_encounter": "first encounter",
             "established_repeat": "established or repeat visit",
             "indeterminate": "indeterminate"}


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper" / "Supplementary_Table_S5.xlsx"
    files = sorted(glob.glob(str(MODELS / "m_*.json")))
    data = {}
    for f in files:
        recs = json.load(open(f))
        mid = recs[0]["model"]
        data[mid] = {r["case_id"]: r for r in recs}

    # 200-case cohort + ordering from the gpt-4.1 reference
    ref = json.load(open(MODELS / "m_gpt-4.1.json"))
    case_order = [r["case_id"] for r in ref]
    ref_by_id = {r["case_id"]: r for r in ref}

    # models ordered alphabetically by display label (matches the original S2)
    model_ids = sorted(data, key=lambda m: LABEL.get(m, m).lower())

    vt, cc, gc, ap, ap_models = side_tables()

    rows = []
    for cid in case_order:
        h = ref_by_id[cid]      # human fields are identical across model files
        row = {
            "Case ID": cid,
            "Sample Name": h.get("sample_name"),
            "Specialty": h.get("specialty"),
            "Presentation": h.get("presentation"),
            "Human A&P": h.get("human_ap"),
            "Human Diagnoses": diag(h.get("human_diagnoses")),
            "Human Dx Cost ($)": h.get("medicare_human_dx_cost"),
            "Human Tests": median_list(h, "human", TEST_CATS),
            "Human Medications": median_list(h, "human", MED_CATS),
            "Human Referral Count": h.get("human_referral_count"),
            "Encounter Type": ENC_LABEL.get(look(vt, cid, "encounter_type")),
            "Guideline Currency (Claude)": look(gc, cid, "Claude Score"),
            "Guideline Currency (Grok)": look(gc, cid, "Grok Score"),
            "AI Consensus Tier": look(cc, cid, "tier"),
            "Case Consensus Index": look(cc, cid, "cci"),
        }
        for m in ap_models:
            row[f"{m} | Appropriateness"] = look(ap, cid, m)
        for mid in model_ids:
            lab = LABEL.get(mid, mid)
            r = data[mid].get(cid)
            if r is None:
                vals = (None, None, None, None, None, None)
            else:
                vals = (diag(r.get("llm_diagnoses")), agreement(r),
                        r.get("medicare_llm_dx_cost"),
                        median_list(r, "llm", TEST_CATS),
                        median_list(r, "llm", MED_CATS),
                        r.get("llm_referral_count"))
            for sub, v in zip(("Diagnoses", "Agreement", "Dx Cost ($)",
                               "Tests", "Medications", "Referral Count"), vals):
                row[f"{lab} | {sub}"] = v
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel(out, index=False)
    # quick concordance sanity vs manuscript
    print(f"wrote {out}: {df.shape[0]} cases x {df.shape[1]} cols, {len(model_ids)} models")
    conc = {}
    for mid in model_ids:
        col = f"{LABEL.get(mid, mid)} | Agreement"
        s = df[col].dropna()
        conc[LABEL.get(mid, mid)] = round(100 * (s == "concordant").mean(), 0)
    overall = pd.concat([df[f"{LABEL.get(m, m)} | Agreement"] for m in model_ids]).dropna()
    print("overall concordance: %.0f%% (manuscript: 78%%)" % (100 * (overall == "concordant").mean()))
    for k in ("GPT-5.5", "OpenEvidence", "Qwen 2.5", "Meditron"):
        if k in conc:
            print(f"  {k}: {conc[k]:.0f}%")

if __name__ == "__main__":
    main()
