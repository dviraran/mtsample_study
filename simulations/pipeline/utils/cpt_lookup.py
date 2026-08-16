"""CPT code lookup utility for seed case processing.

3-tier lookup: rule-based → LLM fallback → null
Data from CMS Medicare fee schedules (PFS + CLFS, CY 2026).

Design notes (from simulations/app/cpt/retriever.py):
- Rule-based for common procedures (high confidence)
- LLM fallback for unknown procedures
- Fuzzy CSV search disabled due to too many false positives
"""

import csv
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Any


# Vendored (2026-06-01): resolve the CPT data dir without the external `common`
# package. The two CSVs (clarified_descriptions.csv, medicare_pfs_2026.csv) live in
# the malpractice cost module's data dir. _load() guards on .exists(), so the
# rule-based lookup still works even if the CSVs are absent.
def _resolve_cpt_data_dir() -> Path:
    candidates = [
        Path(os.environ["CPT_DATA_DIR"]) if os.environ.get("CPT_DATA_DIR") else None,
        Path.home() / "Documents" / "malpractice" / "data" / "cpt",
    ]
    for c in candidates:
        if c is not None and (c / "clarified_descriptions.csv").exists():
            return c
    return Path.home() / "Documents" / "malpractice" / "data" / "cpt"


_DATA_DIR = _resolve_cpt_data_dir()

logger = logging.getLogger(__name__)

# LLM client cache
_llm_client = None
_llm_cache: Dict[str, Dict] = {}

# In-memory stores (populated on first access)
_cpt_lookup: Optional[Dict[str, dict]] = None
_search_index: Optional[List[tuple]] = None  # (code, searchable_text, data)

# Rule-based CPT mappings for common procedures
RULE_BASED: Dict[str, tuple] = {
    # Free actions
    "physical examination": ("00000", "Physical examination", 0.0),
    "physical exam": ("00000", "Physical examination", 0.0),
    "vital signs": ("99211", "Office visit - nurse level", 25.0),
    "vitals": ("99211", "Office visit - nurse level", 25.0),

    # Common labs
    "cbc": ("85025", "Complete blood count with differential", 15.0),
    "complete blood count": ("85025", "Complete blood count with differential", 15.0),
    "bmp": ("80048", "Basic metabolic panel", 20.0),
    "basic metabolic panel": ("80048", "Basic metabolic panel", 20.0),
    "cmp": ("80053", "Comprehensive metabolic panel", 25.0),
    "comprehensive metabolic panel": ("80053", "Comprehensive metabolic panel", 25.0),
    "troponin": ("84484", "Troponin quantitative", 30.0),
    "bnp": ("83880", "Natriuretic peptide (BNP)", 45.0),
    "nt-probnp": ("83880", "Natriuretic peptide (BNP)", 45.0),
    "d-dimer": ("85379", "D-dimer quantitative", 35.0),
    "lipase": ("83690", "Lipase", 20.0),
    "urinalysis": ("81003", "Urinalysis automated", 10.0),
    "blood cultures": ("87040", "Blood culture", 50.0),
    "blood culture": ("87040", "Blood culture", 50.0),
    "abg": ("82803", "Blood gases with O2 saturation", 40.0),
    "arterial blood gas": ("82803", "Blood gases with O2 saturation", 40.0),
    "lactate": ("83605", "Lactic acid", 25.0),
    "procalcitonin": ("84145", "Procalcitonin", 60.0),
    "esr": ("85652", "Erythrocyte sedimentation rate", 15.0),
    "crp": ("86140", "C-reactive protein", 20.0),
    "c-reactive protein": ("86140", "C-reactive protein", 20.0),
    "hba1c": ("83036", "Hemoglobin A1c", 30.0),
    "tsh": ("84443", "Thyroid stimulating hormone", 35.0),
    "liver function tests": ("80076", "Hepatic function panel", 25.0),
    "lfts": ("80076", "Hepatic function panel", 25.0),
    "hepatic function panel": ("80076", "Hepatic function panel", 25.0),
    "coagulation": ("85610", "Prothrombin time", 15.0),
    "pt/inr": ("85610", "Prothrombin time", 15.0),
    "ptt": ("85730", "Partial thromboplastin time", 15.0),
    "lipid panel": ("80061", "Lipid panel", 30.0),

    # Specialty labs
    "serum protein electrophoresis": ("84165", "Protein electrophoresis", 45.0),
    "spep": ("84165", "Protein electrophoresis", 45.0),
    "urine protein electrophoresis": ("84166", "Protein electrophoresis urine", 45.0),
    "upep": ("84166", "Protein electrophoresis urine", 45.0),
    "immunofixation": ("86334", "Immunofixation electrophoresis", 75.0),
    "serum free light chains": ("83883", "Nephelometry free light chains", 80.0),
    "free light chain assay": ("83883", "Nephelometry free light chains", 80.0),
    "ana": ("86038", "Antinuclear antibody", 35.0),
    "antinuclear antibodies": ("86038", "Antinuclear antibody", 35.0),
    "anca": ("86039", "Antineutrophil cytoplasmic antibody", 50.0),
    "complement c3": ("86160", "Complement C3", 25.0),
    "complement c4": ("86161", "Complement C4", 25.0),
    "anti-gbm": ("86255", "Fluorescent antibody screen", 60.0),

    # Tumor markers
    "cea": ("82378", "Carcinoembryonic antigen (CEA)", 40.0),
    "ca 19-9": ("86301", "CA 19-9", 50.0),
    "ca 125": ("86304", "CA 125", 50.0),
    "afp": ("82105", "Alpha-fetoprotein (AFP)", 40.0),
    "psa": ("84153", "Prostate specific antigen (PSA)", 35.0),

    # Common imaging
    "ecg": ("93000", "Electrocardiogram 12-lead", 30.0),
    "ekg": ("93000", "Electrocardiogram 12-lead", 30.0),
    "electrocardiogram": ("93000", "Electrocardiogram 12-lead", 30.0),
    "chest x-ray": ("71046", "Chest X-ray 2 views", 50.0),
    "cxr": ("71046", "Chest X-ray 2 views", 50.0),
    "echocardiogram": ("93306", "Transthoracic echocardiogram", 350.0),
    "echo": ("93306", "Transthoracic echocardiogram", 350.0),
    "transthoracic echocardiogram": ("93306", "Transthoracic echocardiogram", 350.0),

    # Ultrasounds
    "ultrasound abdomen": ("76700", "Ultrasound abdomen complete", 200.0),
    "abdominal ultrasound": ("76700", "Ultrasound abdomen complete", 200.0),
    "renal ultrasound": ("76770", "Ultrasound retroperitoneal", 180.0),
    "kidney ultrasound": ("76770", "Ultrasound retroperitoneal", 180.0),
    "pelvic ultrasound": ("76856", "Ultrasound pelvic", 200.0),
    "thyroid ultrasound": ("76536", "Ultrasound thyroid", 150.0),
    "carotid ultrasound": ("93880", "Duplex scan carotid", 250.0),

    # CT scans
    "ct head": ("70450", "CT head without contrast", 300.0),
    "ct brain": ("70450", "CT head without contrast", 300.0),
    "ct chest": ("71250", "CT chest without contrast", 350.0),
    "ct abdomen": ("74150", "CT abdomen without contrast", 400.0),
    "ct abdomen pelvis": ("74176", "CT abdomen and pelvis without contrast", 500.0),
    "ct abdomen and pelvis": ("74176", "CT abdomen and pelvis without contrast", 500.0),

    # MRI
    "mri brain": ("70551", "MRI brain without contrast", 600.0),
    "mri head": ("70551", "MRI brain without contrast", 600.0),
    "mri spine": ("72141", "MRI spine cervical without contrast", 550.0),
    "mri lumbar": ("72148", "MRI spine lumbar without contrast", 550.0),
    "cardiac mri": ("75557", "Cardiac MRI without contrast", 800.0),

    # Procedures
    "bone marrow biopsy": ("38221", "Bone marrow biopsy", 400.0),
    "bone marrow aspiration": ("38220", "Bone marrow aspiration", 350.0),
    "renal biopsy": ("50200", "Renal biopsy percutaneous", 800.0),
    "liver biopsy": ("47000", "Liver biopsy percutaneous", 700.0),
    "lumbar puncture": ("62270", "Spinal puncture lumbar", 300.0),
    "paracentesis": ("49083", "Abdominal paracentesis", 350.0),
    "thoracentesis": ("32555", "Thoracentesis aspiration", 400.0),

    # Cardiac procedures
    "cardiac catheterization": ("93458", "Cardiac catheterization left", 2500.0),
    "coronary angiography": ("93458", "Cardiac catheterization left", 2500.0),
    "pci": ("92928", "Percutaneous coronary intervention", 5000.0),

    # Type and screen
    "type and screen": ("86900", "Blood typing ABO", 25.0),
    "blood type": ("86900", "Blood typing ABO", 25.0),
    "crossmatch": ("86920", "Compatibility test", 50.0),

    # Neurological
    "eeg": ("95816", "EEG awake and asleep", 250.0),
    "electroencephalogram": ("95816", "EEG awake and asleep", 250.0),
    "gcs": ("00000", "Glasgow Coma Scale (no charge)", 0.0),
    "glasgow coma scale": ("00000", "Glasgow Coma Scale (no charge)", 0.0),
    # Neurological exam is part of physical exam (E/M code, not separate)
    "neurological examination": ("00000", "Neurological examination (part of E/M)", 0.0),
    "neuro exam": ("00000", "Neurological examination (part of E/M)", 0.0),
    "focused neurological exam": ("00000", "Focused neurological examination (part of E/M)", 0.0),
    "neurobehavioral status exam": ("96116", "Neurobehavioral status exam", 150.0),
    "cognitive testing": ("96116", "Neurobehavioral status exam", 150.0),
    "mental status exam": ("96116", "Neurobehavioral status exam", 150.0),
    "lumbar puncture": ("62270", "Spinal puncture lumbar", 300.0),
    "lp": ("62270", "Spinal puncture lumbar", 300.0),
    "spinal tap": ("62270", "Spinal puncture lumbar", 300.0),
    "csf analysis": ("89050", "Cell count synovial fluid", 30.0),

    # MRI with contrast
    "mri brain with contrast": ("70553", "MRI brain with and without contrast", 800.0),
    "mri brain with and without contrast": ("70553", "MRI brain with and without contrast", 800.0),
    "mr venography": ("70543", "MR angiography head with contrast", 600.0),
    "mrv": ("70543", "MR angiography head with contrast", 600.0),

    # Blood pressure monitoring
    "blood pressure": ("93784", "Ambulatory blood pressure monitoring", 50.0),
    "blood pressure measurement": ("93784", "Ambulatory blood pressure monitoring", 50.0),
    "bp monitoring": ("93784", "Ambulatory blood pressure monitoring", 50.0),

    # Drug levels
    "drug level": ("80299", "Drug screen quantitative", 50.0),
    "drug levels": ("80299", "Drug screen quantitative", 50.0),
    "tacrolimus level": ("80197", "Tacrolimus level", 60.0),
    "cyclosporine level": ("80158", "Cyclosporine level", 60.0),
    "phenytoin level": ("80185", "Phenytoin level", 40.0),
    "levetiracetam level": ("80177", "Levetiracetam level", 50.0),
    "valproic acid level": ("80164", "Valproic acid level", 45.0),

    # Common panels
    "electrolyte panel": ("80051", "Electrolyte panel", 20.0),
    "electrolytes": ("80051", "Electrolyte panel", 20.0),
    "renal function tests": ("80069", "Renal function panel", 25.0),
    "renal panel": ("80069", "Renal function panel", 25.0),
    "kidney function": ("80069", "Renal function panel", 25.0),

    # IV medications (no CPT for administration route)
    "lorazepam": ("J2060", "Lorazepam injection", 10.0),
    "lorazepam iv": ("J2060", "Lorazepam injection", 10.0),
    "fosphenytoin": ("J1165", "Fosphenytoin injection", 80.0),
    "fosphenytoin injection": ("J1165", "Fosphenytoin injection", 80.0),
    "furosemide": ("J1940", "Furosemide injection", 5.0),
    "furosemide injection": ("J1940", "Furosemide injection", 5.0),

    # Other common procedures
    "supportive care": ("00000", "Supportive care (no specific code)", 0.0),
    "iv fluids": ("90760", "IV infusion therapy", 100.0),
    "oxygen therapy": ("94760", "Oxygen saturation by pulse oximetry", 20.0),

    # Management/therapeutic actions (map to appropriate monitoring/treatment codes)
    "blood pressure management": ("99217", "Observation care discharge", 150.0),
    "aggressive blood pressure management": ("99217", "Observation care discharge", 150.0),
    "bp management": ("99217", "Observation care discharge", 150.0),
    "hypertension management": ("99217", "Observation care discharge", 150.0),
    "blood pressure control": ("99217", "Observation care discharge", 150.0),

    # Repeat/follow-up imaging
    "repeat imaging": ("76380", "CT limited follow-up study", 200.0),
    "repeat imaging studies": ("76380", "CT limited follow-up study", 200.0),
    "follow-up imaging": ("76380", "CT limited follow-up study", 200.0),
    "repeat mri": ("70553", "MRI brain with and without contrast", 800.0),
    "repeat ct": ("70460", "CT head with contrast", 400.0),
    "repeat ct head": ("70460", "CT head with contrast", 400.0),

    # Seizure management
    "seizure management": ("99223", "Hospital admission comprehensive", 300.0),
    "seizure control": ("99223", "Hospital admission comprehensive", 300.0),
    "status epilepticus management": ("99291", "Critical care first hour", 500.0),
    "anticonvulsant therapy": ("99217", "Observation care discharge", 150.0),

    # Monitoring
    "continuous monitoring": ("99356", "Prolonged physician service", 100.0),
    "neuro monitoring": ("95812", "EEG extended monitoring", 400.0),
    "cardiac monitoring": ("93224", "ECG monitoring 24h", 150.0),
    "telemetry": ("93224", "ECG monitoring 24h", 150.0),

    # Additional IV medications
    "labetalol": ("J1945", "Leuprolide acetate injection", 50.0),  # No specific code, using placeholder
    "labetalol iv": ("J1945", "Leuprolide acetate injection", 50.0),
    "nicardipine": ("90760", "IV infusion therapy", 100.0),
    "nicardipine drip": ("90760", "IV infusion therapy", 100.0),
    "magnesium sulfate": ("J3475", "Magnesium sulfate injection", 20.0),
    "magnesium": ("J3475", "Magnesium sulfate injection", 20.0),
    "phenytoin": ("J1165", "Fosphenytoin injection", 80.0),
    "phenytoin iv": ("J1165", "Fosphenytoin injection", 80.0),
    "valproic acid": ("J3490", "Valproic acid injection", 50.0),
    "valproic acid iv": ("J3490", "Valproic acid injection", 50.0),

    # Eye procedures
    "subconjunctival injection": ("67500", "Subconjunctival injection", 150.0),
    "intravitreal injection": ("67028", "Intravitreal injection", 400.0),
    "intravitreal anti-vegf": ("67028", "Intravitreal injection", 400.0),
    "fluorescein angiography": ("92235", "Fluorescein angiography", 200.0),
    "fundoscopy": ("92250", "Fundus photography", 100.0),
    "fundus photography": ("92250", "Fundus photography", 100.0),
    "slit lamp examination": ("92012", "Eye exam with dilation", 75.0),
    "slit lamp exam": ("92012", "Eye exam with dilation", 75.0),
    "oct": ("92134", "OCT scanning posterior segment", 150.0),
    "optical coherence tomography": ("92134", "OCT scanning posterior segment", 150.0),
    "visual acuity": ("99173", "Visual acuity screening", 20.0),
    "visual acuity testing": ("99173", "Visual acuity screening", 20.0),
    "retrobulbar injection": ("67500", "Retrobulbar injection", 250.0),
    "peribulbar injection": ("67500", "Peribulbar injection", 200.0),
}


def _load() -> None:
    """Load CPT descriptions and prices from CSV files."""
    global _cpt_lookup, _search_index

    # Load descriptions
    desc_path = _DATA_DIR / "clarified_descriptions.csv"
    descriptions: Dict[str, dict] = {}

    if desc_path.exists():
        with open(desc_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                code = row.get("code", "").strip()
                if code:
                    descriptions[code] = {
                        "description": row.get("description", ""),
                        "clear": row.get("clear", ""),
                    }

    # Load prices
    price_path = _DATA_DIR / "medicare_pfs_2026.csv"
    prices: Dict[str, dict] = {}

    if price_path.exists():
        with open(price_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                code = row.get("primary_code", "").strip()
                if not code:
                    continue
                try:
                    neg = float(row.get("negotiated_dollar", "") or 0)
                except (ValueError, TypeError):
                    neg = 0.0
                if code not in prices:
                    prices[code] = {"price": neg}

    # Merge
    _cpt_lookup = {}
    _search_index = []

    for code, desc_data in descriptions.items():
        price_data = prices.get(code, {})
        entry = {
            "cpt_code": code,
            "description": desc_data["description"],
            "clear": desc_data["clear"],
            "price": price_data.get("price", 0.0),
        }
        _cpt_lookup[code] = entry
        searchable = f"{code} {desc_data['description']} {desc_data['clear']}".lower()
        _search_index.append((code, searchable, entry))


def _ensure_loaded() -> None:
    if _cpt_lookup is None:
        _load()


def get_cpt(code: str) -> Optional[dict]:
    """Look up a CPT code by its code string."""
    _ensure_loaded()
    return _cpt_lookup.get(code) if _cpt_lookup else None


def lookup_cpt(procedure: str, use_llm: bool = False, llm_client: Any = None) -> Optional[Dict]:
    """
    Look up CPT code for a procedure name.

    3-tier lookup:
    1. Rule-based (high confidence)
    2. LLM fallback (if enabled and client provided)
    3. Return None (rather than returning wrong codes from fuzzy search)

    Args:
        procedure: Procedure name to look up
        use_llm: Whether to use LLM fallback for unknown procedures
        llm_client: LLM client instance for LLM lookup

    Returns:
        dict with cpt_code, description, price, source or None
    """
    proc_lower = procedure.lower().strip()

    # Tier 1: Exact match in rule-based
    if proc_lower in RULE_BASED:
        code, desc, price = RULE_BASED[proc_lower]
        return {"cpt_code": code, "description": desc, "price": price, "source": "rule_based"}

    # Tier 2: Substring match in rule-based (partial match)
    best_match = None
    for key, (code, desc, price) in RULE_BASED.items():
        # Only match if key is substantially in procedure name
        if key in proc_lower and len(key) >= 3:
            if best_match is None or len(key) > len(best_match[0]):
                best_match = (key, code, desc, price)
        # Reverse check - but only for short procedures
        elif proc_lower in key and len(proc_lower) >= 5:
            if best_match is None:
                best_match = (key, code, desc, price)

    if best_match:
        _, code, desc, price = best_match
        return {"cpt_code": code, "description": desc, "price": price, "source": "rule_based"}

    # Tier 3: LLM fallback (if enabled)
    if use_llm and llm_client:
        llm_result = _llm_lookup_sync(procedure, llm_client)
        if llm_result:
            return llm_result

    # NOTE: Fuzzy CSV search disabled due to too many false positives
    # The previous implementation would return completely wrong CPT codes
    # (e.g., "Dix-Hallpike maneuver" → 62270 which is lumbar puncture)
    # Better to return None and let the caller handle missing CPT codes

    logger.debug(f"No CPT code found for: {procedure}")
    return None


def _llm_lookup_sync(procedure: str, llm_client: Any) -> Optional[Dict]:
    """
    LLM fallback for CPT code lookup (synchronous wrapper).

    Uses the LLM to identify appropriate CPT codes for procedures
    not in our rule-based mapping.
    """
    global _llm_cache

    cache_key = procedure.lower().strip()
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]

    prompt = f"""Find the most appropriate CPT code for this medical procedure/test:
"{procedure}"

Return ONLY a JSON object with:
{{"cpt_code": "XXXXX", "description": "brief description"}}

If no appropriate CPT code exists or you're unsure, return: {{"cpt_code": null}}

Be precise - only return a CPT code if you're confident it's correct.
Do NOT guess or approximate."""

    try:
        response = llm_client.generate(prompt, max_tokens=200, temperature=0.0)
        text = response.strip()

        # Clean markdown
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        # Find JSON
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start:end + 1])
            cpt_code = data.get("cpt_code")

            if cpt_code and cpt_code != "null":
                # Look up price from CSV
                price = _price_from_csv(cpt_code)
                result = {
                    "cpt_code": cpt_code,
                    "description": data.get("description", ""),
                    "price": price,
                    "source": "llm"
                }
                _llm_cache[cache_key] = result
                logger.debug(f"LLM found CPT {cpt_code} for: {procedure}")
                return result

    except Exception as e:
        logger.warning(f"LLM CPT lookup failed for '{procedure}': {e}")

    _llm_cache[cache_key] = None
    return None


def _price_from_csv(cpt_code: str) -> float:
    """Look up price from CSV data for a CPT code."""
    entry = get_cpt(cpt_code)
    if entry:
        return entry.get("price", 0.0)
    return 0.0


def search_cpt(query: str, top_k: int = 5) -> List[dict]:
    """
    Fuzzy text search across CPT descriptions.

    Tokenizes the query, scores each CPT entry by how many
    query tokens appear in its searchable text.
    """
    _ensure_loaded()
    if not _search_index:
        return []

    # Tokenize query
    tokens = [t.strip().lower() for t in re.split(r"[\s,]+", query) if len(t.strip()) > 2]
    if not tokens:
        return []

    scored: List[tuple] = []
    for code, searchable, entry in _search_index:
        matches = sum(1 for t in tokens if t in searchable)
        if matches == 0:
            continue
        score = matches / len(tokens)
        if query.lower() in searchable:
            score += 0.5
        scored.append((score, entry))

    scored.sort(key=lambda x: -x[0])
    return [entry for _, entry in scored[:top_k]]


def get_cpt_for_workup(action: str, use_llm: bool = False, llm_client: Any = None) -> tuple:
    """
    Get CPT code and price for an expected workup action.

    Returns (cpt_code, price) tuple. Returns (None, 0.0) if not found.
    """
    result = lookup_cpt(action, use_llm=use_llm, llm_client=llm_client)
    if result:
        return (result.get("cpt_code"), result.get("price", 0.0))
    return (None, 0.0)


def set_llm_client(client: Any) -> None:
    """Set the default LLM client for CPT lookups."""
    global _llm_client
    _llm_client = client


def get_llm_client() -> Any:
    """Get the current LLM client."""
    return _llm_client
