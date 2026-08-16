"""
Re-price existing cost study results using the Medicare RAG-based pricing system
from the malpractice module.

Usage:
    python reprice_medicare.py                    # Re-price all result files
    python reprice_medicare.py --file m_gpt-4.1.json  # Single file
"""

import sys
import json
import os
import statistics
import tempfile
from pathlib import Path
from argparse import ArgumentParser

ROOT = Path(__file__).resolve().parent.parent
# Add malpractice module to path
sys.path.insert(0, str(ROOT.parent / "malpractice"))

from cost.rag import CPTVectorStore
from cost.pricing import CPTPricingDatabase
from cost.analyzer import CostAnalyzer


RAG_SIM_THRESHOLD = 0.50

# Supplementary direct-match dictionary for common orders that fail RAG matching
# ALL PRICES VERIFIED against CY2026 Medicare Physician Fee Schedule database
SUPPLEMENTARY_MATCHES = {
    "cbc": ("85025", 7.77), "complete blood count": ("85025", 7.77),
    "complete blood count (cbc)": ("85025", 7.77), "cbc with differential": ("85025", 7.77),
    "cbc with diff": ("85025", 7.77), "cbc drawn weekly": ("85025", 7.77),
    "repeat cbc": ("85025", 7.77), "repeat cbc in am": ("85025", 7.77),
    "repeat cbc in the morning": ("85025", 7.77),
    "cmp": ("80053", 10.56), "comprehensive metabolic panel": ("80053", 10.56),
    "comprehensive metabolic panel (cmp)": ("80053", 10.56),
    "cmp (including lfts)": ("80053", 10.56), "cmp (including liver enzymes)": ("80053", 10.56),
    "cmp (including creatinine, lfts)": ("80053", 10.56), "cmp/lfts": ("80053", 10.56),
    "cmp lab test": ("80053", 10.56), "cmp stat": ("80053", 10.56),
    "order cmp": ("80053", 10.56), "baseline cmp": ("80053", 10.56),
    "stat cmp": ("80053", 10.56), "repeat cmp": ("80053", 10.56),
    "bmp/cmp": ("80053", 10.56), "chem profile": ("80053", 10.56),
    "chemistry profile": ("80053", 10.56), "chemistry panel": ("80053", 10.56),
    "chem-12": ("80053", 10.56),
    "bmp": ("80048", 8.46), "basic metabolic panel": ("80048", 8.46),
    "basic metabolic panel (bmp)": ("80048", 8.46),
    "repeat bmp": ("80048", 8.46), "repeat bmp in am": ("80048", 8.46),
    "daily bmp": ("80048", 8.46), "stat bmp": ("80048", 8.46),
    "tsh": ("84443", 16.80), "thyroid stimulating hormone": ("84443", 16.80),
    "thyroid stimulating hormone (tsh)": ("84443", 16.80),
    "tsh level": ("84443", 16.80), "recheck tsh": ("84443", 16.80),
    "tsh and free t4": ("84443", 16.80), "tsh/free t4": ("84443", 16.80),
    "tsh with reflex free t4": ("84443", 16.80),
    "check tsh": ("84443", 16.80), "obtain tsh": ("84443", 16.80),
    "hba1c": ("83036", 9.71), "hemoglobin a1c": ("83036", 9.71),
    "a1c": ("83036", 9.71), "hgba1c": ("83036", 9.71),
    "fasting glucose or hba1c": ("83036", 9.71), "blood test for diabetes": ("83036", 9.71),
    "lipid panel": ("80061", 13.39), "lipid profile": ("80061", 13.39),
    "fasting lipid panel": ("80061", 13.39), "fasting lipid profile": ("80061", 13.39),
    "urinalysis": ("81003", 2.25), "ua": ("81003", 2.25),
    "ua with microscopy": ("81001", 3.17), "urine culture": ("87088", 8.09),
    "cpk": ("82550", 6.51), "creatine kinase": ("82550", 6.51), "ck": ("82550", 6.51),
    "esr": ("85652", 2.70), "sed rate": ("85652", 2.70),
    "esr/crp": ("85652", 2.70), "esr and crp": ("85652", 2.70),
    "crp": ("86140", 5.18), "c-reactive protein": ("86140", 5.18), "hs-crp": ("86141", 12.95),
    "inflammatory markers (esr, crp)": ("85652", 2.70),
    "ppd test": ("86580", 11.02), "ppd": ("86580", 11.02), "ppd skin test": ("86580", 11.02),
    "tuberculin skin test": ("86580", 11.02),
    "quantiferon-tb gold": ("86480", 61.98), "quantiferon gold": ("86480", 61.98),
    "hiv serology": ("86703", 13.71), "hiv test": ("86703", 13.71),
    "hiv ag/ab test": ("87389", 24.08),
    "rpr test": ("86592", 4.27), "rpr": ("86592", 4.27), "vdrl": ("86592", 4.27),
    "rpr/fta-abs": ("86592", 4.27), "rpr (syphilis) test": ("86592", 4.27),
    "pertussis pcr": ("87798", 35.09), "rsv pcr": ("87798", 35.09),
    "fasting blood sugar": ("82947", 3.93), "fasting glucose": ("82947", 3.93),
    "pro-time": ("85610", 4.29), "protime": ("85610", 4.29), "pt/inr": ("85610", 4.29),
    "inr": ("85610", 4.29), "repeat inr": ("85610", 4.29), "monitor inr": ("85610", 4.29),
    "stat pt/inr": ("85610", 4.29), "pt/inr/ptt": ("85610", 4.29),
    "alt": ("84460", 5.30), "recheck alt": ("84460", 5.30),
    "ast": ("84450", 5.18), "ldh": ("83615", 6.04),
    "pth": ("83970", 41.28), "parathyroid hormone": ("83970", 41.28),
    "intact pth": ("83970", 41.28),
    "lfts": ("80076", 8.17), "liver function tests": ("80076", 8.17),
    "repeat lfts": ("80076", 8.17), "hepatic function panel": ("80076", 8.17),
    "renal function panel": ("80069", 8.68),
    "stool studies": ("87046", 9.44), "stool culture": ("87046", 9.44),
    "hemoccult": ("82270", 4.38), "fobt": ("82270", 4.38), "stool guaiac": ("82270", 4.38),
    "csf cultures": ("87070", 8.62), "csf culture": ("87070", 8.62),
    "cd4 count": ("86361", 26.78),
    "type & screen": ("86900", 2.99), "type and screen": ("86900", 2.99),
    "hcv genotype": ("87902", 257.45),
    "hpv dna": ("87624", 35.09), "hpv testing": ("87624", 35.09),
    "rvvt": ("85613", 9.58),
    "microalbumin": ("82043", 5.78), "urine microalbumin": ("82043", 5.78),
    "follow-up labs": ("80053", 10.56),
    "magnesium": ("83735", 6.70), "phosphorus": ("84100", 4.74),
    "iron studies": ("83550", 8.74), "ferritin": ("82728", 13.63),
    "b12": ("82607", 15.08), "vitamin b12": ("82607", 15.08),
    "folate": ("82746", 14.70), "vitamin d": ("82306", 29.60),
    "uric acid": ("84550", 4.52),
    "psa": ("84153", 18.39), "repeat psa": ("84153", 18.39),
    "bnp": ("83880", 39.26), "nt-probnp": ("83880", 39.26), "stat bnp": ("83880", 39.26),
    "troponin": ("84484", 12.47), "d-dimer": ("85379", 10.18),
    "fibrinogen": ("85384", 9.72),
    "blood cultures": ("87040", 10.32), "blood culture": ("87040", 10.32),
    "hepatitis b panel": ("80055", 47.81),
    "hepatitis c antibody": ("86803", 14.27), "hep c antibody": ("86803", 14.27),
    "ana": ("86235", 17.93), "ana titer": ("86235", 17.93), "ana with reflex": ("86235", 17.93),
    "asma": ("86235", 17.93), "ama": ("86255", 12.05),
    "rf and anti-ccp": ("86431", 5.67),
    "free t4": ("84439", 9.02), "cortisol": ("82533", 16.30),
    "prolactin": ("84146", 19.38), "albumin": ("82040", 4.95),
    "spep": ("86334", 22.34), "methylmalonic acid": ("83921", 21.21),
    "dilantin level": ("80185", 13.25), "keppra level": ("80177", 13.25),
    "lead level": ("83655", 12.11), "drug screen": ("80305", 12.60),
    "urine toxicology": ("80305", 12.60),
    "hav igg": ("86709", 11.26), "anti-hbs": ("86706", 10.74),
    "ggt": ("82977", 7.20), "tibc": ("83550", 8.74),
    "ace level": ("82164", 14.60), "igf-1": ("84305", 21.26),
    "cea": ("82378", 18.96), "ca-125": ("86304", 20.81),
    "lysozyme": ("85549", 18.75), "c3/c4": ("86160", 12.00),
    "c3": ("86160", 12.00), "c4": ("86160", 12.00),
    "igg": ("82784", 9.30), "a1at level": ("82104", 14.46),
    "afp": ("82105", 16.77),
    "formal neuropsychological testing": ("96132", 122.25),
    "chest x-ray": ("71046", 33.07), "cxr": ("71046", 33.07),
    "mri": ("70553", 316.97), "mri brain": ("70553", 316.97), "brain mri": ("70553", 316.97),
    "brain mri with and without contrast": ("70553", 316.97),
    "dexa scan": ("77080", 39.41), "dexa": ("77080", 39.41), "bone density scan": ("77080", 39.41),
    "mammogram": ("77067", 126.26), "screening mammogram": ("77067", 126.26),
    "upper gi series": ("74240", 121.91),
    "barium swallow": ("74220", 94.19), "barium enema": ("74270", 148.63),
    "kub": ("74018", 29.73), "abdominal x-ray": ("74018", 29.73),
    "venous doppler": ("93970", 184.04), "lower extremity doppler": ("93970", 184.04),
    "carotid doppler": ("93880", 189.05), "carotid ultrasound": ("93880", 189.05),
    "carotid doppler study": ("93880", 189.05),
    "renal ultrasound": ("76770", 106.21), "abdominal ultrasound": ("76700", 114.23),
    "ct head": ("70450", 106.55), "ct chest": ("71250", 132.60),
    "ct abdomen and pelvis": ("74177", 300.27),
    "psma pet/ct": ("78816", 250.00), "pet scan": ("78816", 250.00),
    "electroencephalogram (eeg)": ("95816", 413.50),
    "pap smear": ("88175", 26.61), "pap test": ("88175", 26.61),
    "12-lead ekg": ("93000", 15.36), "ekg": ("93000", 15.36),
    "ecg": ("93000", 15.36), "obtain ecg": ("93000", 15.36),
    "holter monitor": ("93224", 70.48), "outpatient holter monitor": ("93224", 70.48),
    "echocardiogram": ("93306", 196.73), "echo": ("93306", 196.73),
    "spirometry": ("94010", 29.73), "pfts": ("94010", 29.73),
    "humphrey visual field": ("92083", 63.80), "visual field test": ("92083", 63.80),
    "audiogram": ("92557", 35.74), "hearing screen": ("92551", 10.00),
    "phq-9": ("96127", 5.01), "gad-7": ("96127", 5.01),
    "post-void residual": ("51798", 12.69), "pvr": ("51798", 12.69),
    "colonoscopy": ("45378", 378.10), "egd": ("43235", 322.65),
    "stress test": ("93015", 73.48), "cardiac stress test": ("93015", 73.48),
    "fiberoptic ent exam": ("31575", 127.26), "nasal endoscopy": ("31231", 193.39),
    "6-minute walk test": ("94618", 37.07),
    "liquid nitrogen treatment for wart": ("17110", 111.22),
    "large volume lumbar puncture": ("62270", 165.00),
    "epley maneuver": ("95992", 40.75), "dix-hallpike maneuver": ("95992", 40.75),
    "diet evaluation": ("97802", 36.74),
    "orthostatic vital signs": ("99000", 0), "orthostatic vitals": ("99000", 0),
    "surgical clearance": ("99000", 0), "preoperative assessment with anesthesiology": ("99000", 0),
}

SUBSTRING_MATCHES = {
    "complete blood count": ("85025", 7.77), "cbc": ("85025", 7.77),
    "comprehensive metabolic": ("80053", 10.56), "basic metabolic": ("80048", 8.46),
    "hemoglobin a1c": ("83036", 9.71), "lipid panel": ("80061", 13.39),
    "lipid profile": ("80061", 13.39), "urinalysis": ("81003", 2.25),
    "chest x-ray": ("71046", 33.07), "dexa": ("77080", 39.41),
    "mammogra": ("77067", 126.26), "echocardiogram": ("93306", 196.73),
    "thyroid stimulating": ("84443", 16.80), "hepatitis b": ("80055", 47.81),
    "mri brain": ("70553", 316.97), "brain mri": ("70553", 316.97),
    "ekg": ("93000", 15.36), "holter": ("93224", 70.48),
    "colonoscopy": ("45378", 378.10), "stress test": ("93015", 73.48),
    "bone density": ("77080", 39.41), "pulmonary function": ("94010", 29.73),
    "visual field": ("92083", 63.80), "carotid": ("93880", 189.05),
    "tsh": ("84443", 16.80), "free t4": ("84439", 9.02),
    "inr": ("85610", 4.29), "pt/inr": ("85610", 4.29),
    "bnp": ("83880", 39.26), "d-dimer": ("85379", 10.18),
    "psa": ("84153", 18.39), "esr": ("85652", 2.70),
    "crp": ("86140", 5.18), "hba1c": ("83036", 9.71),
    "a1c": ("83036", 9.71), "ana": ("86235", 17.93),
    "pth": ("83970", 41.28), "quantiferon": ("86480", 61.98),
    "lumbar puncture": ("62270", 165.00), "neuropsychological": ("96132", 122.25),
    "eeg": ("95816", 413.50), "pet/ct": ("78816", 250.00),
    "doppler": ("93970", 184.04), "barium": ("74220", 94.19),
    "hearing screen": ("92551", 10.00), "lead level": ("83655", 12.11),
    "drug screen": ("80305", 12.60), "toxicology": ("80305", 12.60),
    "pertussis": ("87798", 35.09), "fiberoptic": ("31575", 127.26),
    "inflammatory markers": ("85652", 2.70),
    "repeat inr": ("85610", 4.29), "repeat bmp": ("80048", 8.46),
    "repeat cmp": ("80053", 10.56), "repeat cbc": ("85025", 7.77),
    "stat cmp": ("80053", 10.56), "stat bmp": ("80048", 8.46),
}

# CPT code ranges that are diagnostic (not surgical)
# 70000-79999: Radiology
# 80000-89999: Pathology/Laboratory
# 90000-99999: Medicine/E&M (includes ECG, echo, etc.)
# 00000-09999: Anesthesia (rare but not surgical)
# 10000-69999: SURGERY — should NOT match diagnostic orders
SURGICAL_CPT_RANGE = (10000, 69999)
def _is_surgical_cpt(cpt_code: str) -> bool:
    """Check if a CPT code is in the surgical range."""
    try:
        code_num = int(cpt_code)
        return SURGICAL_CPT_RANGE[0] <= code_num <= SURGICAL_CPT_RANGE[1]
    except (ValueError, TypeError):
        return False


def price_order(order_text: str, analyzer: CostAnalyzer, category: str = "") -> dict:
    """Price a single order using Medicare RAG system."""
    # Try supplementary dictionary first (exact match)
    order_lower = order_text.strip().lower()
    if order_lower in SUPPLEMENTARY_MATCHES:
        cpt_code, price = SUPPLEMENTARY_MATCHES[order_lower]
        return {
            "order": order_text,
            "cpt_code": cpt_code,
            "cpt_description": f"Supplementary match: {order_text}",
            "medicare_price": price,
            "match_method": "supplementary",
            "similarity": 1.0,
        }

    # Try substring matching (catches "Complete Blood Count (CBC) with differential" etc.)
    for substr, (cpt_code, price) in SUBSTRING_MATCHES.items():
        if substr in order_lower:
            return {
                "order": order_text,
                "cpt_code": cpt_code,
                "cpt_description": f"Substring match on '{substr}'",
                "medicare_price": price,
                "match_method": "substring",
                "similarity": 0.9,
            }

    # Try direct match from analyzer
    direct = analyzer._try_direct_match(order_text)
    if direct:
        price_info = analyzer.pricing.get_price(direct.cpt_code)
        return {
            "order": order_text,
            "cpt_code": direct.cpt_code,
            "cpt_description": direct.description,
            "medicare_price": price_info.negotiated_dollar if price_info else 0,
            "match_method": "direct",
            "similarity": 1.0,
        }

    # RAG search with higher threshold
    matches = analyzer.rag.search(order_text, top_k=3, threshold=RAG_SIM_THRESHOLD)
    for m in matches:
        # Reject surgical CPT codes for non-procedure diagnostic orders
        if _is_surgical_cpt(m.cpt_code) and category in ("labs", "imaging", "monitoring", "exam", ""):
            continue  # try next match

        price_info = analyzer.pricing.get_price(m.cpt_code)
        return {
            "order": order_text,
            "cpt_code": m.cpt_code,
            "cpt_description": m.description,
            "medicare_price": price_info.negotiated_dollar if price_info else 0,
            "match_method": "rag",
            "similarity": m.similarity_score,
        }

    return {
        "order": order_text,
        "cpt_code": None,
        "cpt_description": None,
        "medicare_price": 0,
        "match_method": "unmatched",
        "similarity": 0,
    }


DIAGNOSTIC_CATEGORIES = {"labs", "imaging", "procedure", "exam", "monitoring"}


def reprice_result(result: dict, analyzer: CostAnalyzer) -> dict:
    """Re-price a single result entry using Medicare prices."""
    # Re-price human orders (use extractor A as representative)
    human_orders = result.get("human_orders_a", [])
    human_dx_total = 0
    human_med_total = 0
    human_repriced = []
    for order in human_orders:
        if order.get("category") in DIAGNOSTIC_CATEGORIES:
            cat = order.get("category", "")
            priced = price_order(order.get("order", ""), analyzer, category=cat)
            priced["category"] = cat
            human_repriced.append(priced)
            human_dx_total += priced["medicare_price"]
        elif order.get("category") == "medication":
            human_med_total += order.get("monthly_cost_usd", 0)

    # Re-price LLM orders (use extractor A as representative)
    llm_orders = result.get("llm_orders_a", [])
    llm_dx_total = 0
    llm_med_total = 0
    llm_repriced = []
    for order in llm_orders:
        if order.get("category") in DIAGNOSTIC_CATEGORIES:
            cat = order.get("category", "")
            priced = price_order(order.get("order", ""), analyzer, category=cat)
            priced["category"] = cat
            llm_repriced.append(priced)
            llm_dx_total += priced["medicare_price"]
        elif order.get("category") == "medication":
            llm_med_total += order.get("monthly_cost_usd", 0)

    # Compute ratio
    ratio = llm_dx_total / human_dx_total if human_dx_total > 0 else (
        float("inf") if llm_dx_total > 0 else 1.0
    )

    # Add Medicare fields to result
    result["medicare_human_orders"] = human_repriced
    result["medicare_llm_orders"] = llm_repriced
    result["medicare_human_dx_cost"] = human_dx_total
    result["medicare_llm_dx_cost"] = llm_dx_total
    result["medicare_human_med_cost"] = human_med_total
    result["medicare_llm_med_cost"] = llm_med_total
    result["medicare_cost_ratio"] = ratio

    return result


def main():
    parser = ArgumentParser(description="Re-price results with Medicare RAG system")
    parser.add_argument("--file", help="Single result file to re-price")
    parser.add_argument("--force", action="store_true", help="Force re-price even if already done")
    args = parser.parse_args()

    results_dir = ROOT / "results" / "models_original_runs"

    # Initialize analyzer (loads embeddings + pricing once)
    print("Loading Medicare pricing system...")
    analyzer = CostAnalyzer(use_mock_extractor=True)
    print("Ready.\n")

    if args.file:
        files = [results_dir / args.file]
    else:
        files = sorted(results_dir.glob("m_*.json"))

    for f in files:
        if not f.exists():
            print(f"  {f.name}: not found, skipping")
            continue

        try:
            results = json.load(open(f))
        except Exception as e:
            print(f"Warning: {f.name}: corrupt JSON, skipping ({e})")
            continue

        n = len(results)
        print(f"  {f.name}: {n} results...", end=" ", flush=True)

        repriced = 0
        for r in results:
            if args.force or "medicare_human_dx_cost" not in r:
                # Clear old medicare fields if force re-pricing
                for k in list(r.keys()):
                    if k.startswith("medicare_"):
                        del r[k]
                reprice_result(r, analyzer)
                repriced += 1

        # Save back (atomic write)
        tmp_fd = tempfile.NamedTemporaryFile(
            mode="w", dir=f.parent, suffix=".tmp", delete=False
        )
        try:
            json.dump(results, tmp_fd, indent=2, default=str)
            tmp_fd.close()
            os.replace(tmp_fd.name, f)
        except BaseException:
            tmp_fd.close()
            os.unlink(tmp_fd.name)
            raise

        print(f"repriced {repriced}/{n}")

    # Print summary across all files
    print(f"\n{'='*70}")
    print("MEDICARE PRICING SUMMARY")
    print(f"{'='*70}")

    all_results = []
    for f in files:
        if f.exists():
            try:
                all_results.extend(json.load(open(f)))
            except Exception as e:
                print(f"Warning: could not load {f.name}: {e}")

    if not all_results or "medicare_human_dx_cost" not in all_results[0]:
        print("No repriced results found.")
        return

    by_model = {}
    for r in all_results:
        by_model.setdefault(r["model"], []).append(r)

    print(f"\n{'Model':<22} {'Avg LLM$':>9} {'Avg Human$':>11} {'Median Ratio':>13} {'N':>4}")
    print("─" * 62)
    for model in sorted(by_model, key=lambda m: sum(c["medicare_llm_dx_cost"] for c in by_model[m]) / len(by_model[m])):
        comps = by_model[model]
        avg_llm = sum(c["medicare_llm_dx_cost"] for c in comps) / len(comps)
        avg_human = sum(c["medicare_human_dx_cost"] for c in comps) / len(comps)
        finite_ratios = sorted([c["medicare_cost_ratio"] for c in comps
                                if c["medicare_cost_ratio"] != float("inf") and c["medicare_human_dx_cost"] > 0])
        median = statistics.median(finite_ratios) if finite_ratios else 0
        print(f"{model:<22} ${avg_llm:>7.0f} ${avg_human:>9.0f} {median:>12.2f}x {len(comps):>4}")


if __name__ == "__main__":
    main()
