#!/usr/bin/env python3
"""
Fix intra-run CPT disagreements by forcing common lab/imaging orders to their
canonical CPT code. Extractor agreement is high for unusual orders; the
disagreement concentrates on common tests where one or more extractors
assigns a completely wrong CPT (e.g., HbA1c → molecular genetics code).

We only override when the order text clearly matches a common test. Other
orders are left alone (their CPT ambiguity may be legitimate).
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "results" / "models_original_runs"

# Canonical CPT codes for common tests.
# ONLY include tests where:
#   (1) the order text is unambiguous
#   (2) the CPT code is well-established and stable
#   (3) the wrong alternatives are clearly incorrect procedures
# Everything else (iron studies, Vitamin D variants, HLA-B27, etc.) is left
# alone because legitimate CPT variation exists.
CANONICAL = [
    # Basic labs — very clear canonical codes
    (r"\bcomplete blood count\b(?!\s+with)|\bcbc\b(?!.*platelet kinetics)", "85025", 7.77, "CBC with differential"),
    (r"\bcomprehensive metabolic panel\b|\bcmp\b|\bchem[- ]?12\b", "80053", 10.56, "CMP"),
    (r"\bbasic metabolic panel\b|\bbmp\b|\bchem[- ]?7\b", "80048", 8.46, "BMP"),
    (r"\bhemoglobin a1c\b|\bhba1c\b|\b(?<!v)a1c\b", "83036", 9.71, "HbA1c"),
    (r"\bfasting lipid panel\b|\blipid panel\b|\blipid profile\b", "80061", 13.44, "Lipid panel"),
    (r"\bthyroid[- ]?stimulating hormone\b|\btsh\b(?!.*free t4)(?!.*with.*t4)", "84443", 16.80, "TSH"),
    (r"\burinalysis with microscopy\b|\burinalysis.*micro\b|\bua with micro\b", "81001", 2.25, "UA with microscopy"),
    (r"\burinalysis\b(?!.*micro)(?!.*culture)|\bua\b(?!.*micro)(?!.*culture)", "81003", 2.25, "Urinalysis automated"),
    (r"\burine culture\b|\burine cx\b", "87086", 7.87, "Urine culture"),
    (r"\bvitamin b12\b|\bb12 level\b|\bb[- ]?12\s*$", "82607", 15.08, "Vitamin B12"),
    (r"\besr\b|\berythrocyte sedimentation\b|\bsed rate\b", "85652", 2.70, "ESR"),
    (r"\bc[- ]?reactive protein\b(?!.*cardiac)(?!.*high)|\bcrp\b(?!.*cardiac)(?!.*high)", "86140", 5.18, "CRP"),
    (r"\bekg\b|\becg\b(?!.*stress)|\b12[- ]?lead (ekg|ecg)\b", "93000", 15.36, "ECG"),
    # Chest X-ray — 75756 (CTA) is a common wrong extraction
    (r"\bchest x[- ]?ray\b|\bcxr\b(?!\s+lateral)|\bportable chest.*x[- ]?ray\b", "71046", 33.07, "Chest X-ray"),
    (r"\btroponin\b(?!.*high)", "84484", 11.71, "Troponin I"),
    (r"\bbnp\b|\bnt[- ]?probnp\b|\bb[- ]?type natriuretic peptide\b", "83880", 39.26, "BNP"),
    (r"\bldh\b|\blactate dehydrogenase\b", "83615", 6.04, "LDH"),
    (r"\bca[- ]?125\b", "86304", 20.81, "CA-125"),
    (r"\bpsa\b|\bprostate[- ]?specific antigen\b", "84153", 18.22, "PSA"),
    (r"\bpt/inr\b|\bprothrombin time\b", "85610", 4.29, "PT/INR"),
    (r"\bptt\b|\bpartial thromboplastin\b", "85730", 6.01, "PTT"),
    (r"\bblood culture\b", "87040", 10.32, "Blood culture"),
    (r"\bmammogram\b|\bmammography\b|\bscreening mammo\b", "77067", 126.26, "Mammogram"),
    (r"\bdexa\b|\bbone density\b|\bbone densitometry\b", "77080", 39.41, "DEXA"),
    (r"\bcolonoscopy\b(?!.*referral)(?!.*schedule)", "45378", 378.10, "Colonoscopy"),
    (r"\btransthoracic echocardiogram\b|\btte\b(?!xt)|^echocardiogram$|\bechocardiogram\b(?!.*transesophageal)(?!.*stress)(?!.*exercise)(?!.*dobutamine)", "93306", 196.73, "TTE"),
    (r"\bcarotid (?:doppler|ultrasound|duplex)\b(?!.*tsh)|\bcarotid.*us\b", "93880", 189.05, "Carotid duplex"),
    (r"\babg\b|\barterial blood gas\b", "82803", 26.07, "ABG"),
    (r"\bpulse ox\b|\bpulse oximetry\b", "94760", 4.01, "Pulse oximetry"),
    (r"\bhome.*bp.*monitor\b|\bhome blood pressure monitor\b|\bhome bp log\b", "93784", 47.76, "Home BP monitor"),
    # Round 2 additions
    (r"\bliver function tests?\b(?!\s+panel)|\blfts?\b(?!\s+panel)|\bhepatic function panel\b", "80076", 10.23, "LFTs"),
    (r"\brenal ultrasound\b(?!.*doppler)|\bkidney ultrasound\b(?!.*doppler)", "76770", 106.21, "Renal US"),
    (r"\bhiv\b(?=.*test|.*screen|.*ag.?ab|.*antibody)", "87389", 13.71, "HIV Ag/Ab"),
    (r"\bvenous doppler\b|\blower extremity.*doppler\b|\bduplex.*lower\b|\blower.*venous.*duplex\b", "93970", 184.04, "LE venous duplex"),
    (r"\bhepatitis panel\b|\bhepatitis b.*surface antigen.*and.*surface antibody\b|\bacute hepatitis panel\b", "80055", 47.63, "Hepatitis panel"),
    (r"\bhepatitis b surface antibody\b|\bhbsab\b|\banti-?hbs\b", "86706", 11.86, "HBsAb"),
    (r"\bpet\b[- ]?ct\b|\bpsma pet\b|\bpet\s+ct\s+scan\b", "78816", 250.00, "PET/CT"),
    (r"\bexercise stress test\b|\btreadmill stress\b|\bstress test\b(?!.*echo)(?!.*nuclear)", "93015", 73.00, "Stress test"),
    (r"\babdominal ultrasound\b(?!.*doppler)|\babdomen ultrasound\b", "76700", 106.21, "Abdominal US"),
    (r"\bpth\b|\bparathyroid hormone\b", "83970", 41.28, "PTH"),
    (r"\bferritin\b", "82728", 13.54, "Ferritin"),
    (r"\banti[- ]?dsdna\b|\bdsdna antibody\b", "86225", 17.93, "Anti-dsDNA"),
    (r"\bc3\b|\bcomplement c3\b", "86160", 12.09, "C3"),
    (r"\bc4\b|\bcomplement c4\b", "86160", 12.09, "C4"),
    (r"\bcreatine kinase\b|\bcpk\b|\bck\b(?!.*mb)(?!.*brain)", "82550", 7.21, "CK"),
    (r"\brheumatoid factor\b|\brf\b(?=\s)", "86431", 6.31, "RF"),
    (r"\bammonia\b|\bserum ammonia\b", "82140", 14.57, "Ammonia"),
    (r"\bquantiferon\b|\btb gold\b|\bigra\b", "86480", 62.03, "Quantiferon"),
    (r"\bsputum culture\b|\brespiratory culture\b|\bendotracheal.*culture\b", "87070", 11.25, "Sputum culture"),
    (r"\bhaptoglobin\b", "83010", 26.89, "Haptoglobin"),
    (r"\breticulocyte count\b", "85045", 4.31, "Reticulocyte count"),
    (r"\bceruloplasmin\b", "82390", 10.74, "Ceruloplasmin"),
    (r"\bbordetella pertussis\b|\bpertussis pcr\b|\bpertussis.*nasopharyngeal\b", "87798", 35.00, "Pertussis PCR"),
    (r"\brespiratory viral panel\b|\brvp\b|\bnasopharyngeal.*viral\b", "87633", 257.00, "Resp viral panel"),
]

# Precompile
CANONICAL_COMPILED = [(re.compile(p, re.IGNORECASE), cpt, price, label)
                     for p, cpt, price, label in CANONICAL]


def canonical_match(order_text: str) -> tuple[str, float, str] | None:
    """If order matches a canonical pattern, return (cpt, price, label)."""
    for pat, cpt, price, label in CANONICAL_COMPILED:
        if pat.search(order_text):
            return (cpt, price, label)
    return None


def is_test(cat: str) -> bool:
    c = (cat or "").lower()
    return ("med" not in c) and any(k in c for k in
        {"lab", "laboratory", "labs", "imaging", "test", "procedure",
         "monitoring", "diagnostic", "screening"})


def apply_canonical(orders: list[dict]) -> tuple[int, float]:
    """In-place update orders; return (n_changed, net_delta)."""
    n = 0
    delta = 0.0
    for o in orders or []:
        if not is_test(o.get("category", "")):
            continue
        text = o.get("order", "") or ""
        canon = canonical_match(text)
        if canon is None:
            continue
        canon_cpt, canon_price, canon_label = canon
        old_cpt = o.get("cpt_code")
        old_price = float(o.get("price", 0) or 0)
        # Only override if disagreement AND current CPT differs
        if old_cpt != canon_cpt:
            o["cpt_code"] = canon_cpt
            o["price"] = canon_price
            if o.get("source") != "canonical":
                o["source"] = "canonical_override"
            delta += canon_price - old_price
            n += 1
    return n, delta


def recompute_dx_cost(case: dict, key_prefix: str) -> float:
    """Sum test prices per extractor, then take median."""
    totals = []
    for which in ["a", "b", "c"]:
        key = f"{key_prefix}_orders_{which}"
        total = sum(float(o.get("price", 0) or 0)
                    for o in (case.get(key) or [])
                    if is_test(o.get("category", "")))
        totals.append(total)
    return round(sorted(totals)[1], 2)


def main() -> None:
    for path in sorted(MODELS.glob("m_*.json")):
        model = path.stem.replace("m_", "")
        # m_human.json is a special aggregate file with empty orders and
        # pre-computed statistics; don't recompute it from empty extractions.
        if model == "human":
            continue
        with open(path) as f:
            data = json.load(f)
        total_orders_changed = 0
        total_delta = 0.0
        n_llm_changed = 0
        n_hum_changed = 0
        llm_cost_delta = 0.0
        hum_cost_delta = 0.0
        for c in data:
            # AI orders
            for w in ["a", "b", "c"]:
                n, d = apply_canonical(c.get(f"llm_orders_{w}", []))
                total_orders_changed += n
                total_delta += d
            old_llm = c.get("medicare_llm_dx_cost") or 0
            new_llm = recompute_dx_cost(c, "llm")
            if abs(new_llm - old_llm) > 0.01:
                n_llm_changed += 1
                llm_cost_delta += new_llm - old_llm
            c["medicare_llm_dx_cost"] = new_llm

            # Human orders (same override)
            for w in ["a", "b", "c"]:
                n, d = apply_canonical(c.get(f"human_orders_{w}", []))
                total_orders_changed += n
                total_delta += d
            old_hum = c.get("medicare_human_dx_cost") or 0
            new_hum = recompute_dx_cost(c, "human")
            if abs(new_hum - old_hum) > 0.01:
                n_hum_changed += 1
                hum_cost_delta += new_hum - old_hum
            c["medicare_human_dx_cost"] = new_hum

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"{model:<22}  orders_overridden={total_orders_changed:>5}  "
              f"LLM cases changed={n_llm_changed:>3} delta=${llm_cost_delta:>+8.0f}  "
              f"HUM cases changed={n_hum_changed:>3} delta=${hum_cost_delta:>+7.0f}")


if __name__ == "__main__":
    main()
