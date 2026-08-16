#!/usr/bin/env python3
"""
Classify each of the 200 primary-analysis cases as a FIRST encounter or an
ESTABLISHED/REPEAT visit, using the same three-judge majority-vote design the
study already uses for diagnostic concordance (judge_dx.py).

Rationale: in a repeat visit to
a practitioner with whom the patient has an established relationship, prior
testing may exist that is not written in the note, so the physician's plan can
look cheaper than it "really" is. If >10% of visits are repeat visits, the
primary analysis must be repeated on first encounters only.

Output: results/analysis/visit_type.json
  {"cases": [{case_id, specialty, sample_name, votes:{judge: {...}},
              encounter_type, setting, prior_results_in_note, evidence,
              unanimous, needs_adjudication}], "summary": {...}}

Usage:
  python3 scripts/classify_visit_type.py                 # all 3 judges, 200 cases
  python3 scripts/classify_visit_type.py --judges gpt-4.1-mini --limit 10
"""

import os
import re
import sys
import json
import time
import argparse
import tempfile
import threading
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulations"))
from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)
from pipeline.cloud_llm_client import CloudLLMClient

# Same three developers as the diagnostic-concordance judge panel.
JUDGES = {
    "gpt-4.1-mini": ("openrouter", "openai/gpt-4.1-mini"),
    "claude":       ("openrouter", "anthropic/claude-sonnet-4.5"),
    "gemini":       ("openrouter", "google/gemini-2.5-flash"),
}

REFERENCE_FILE = ROOT / "results" / "models" / "m_gpt-4.1.json"
OUT_FILE = ROOT / "results" / "analysis" / "visit_type.json"

ENCOUNTER_LEVELS = ["first_encounter", "established_repeat", "indeterminate"]
SETTING_LEVELS = [
    "emergency_department", "urgent_care", "office_new_or_consult",
    "office_established", "other_or_unclear",
]

PROMPT = """You are classifying a real, de-identified clinical note from the MTSamples corpus.

Below is the clinical presentation only (everything the treating clinician wrote BEFORE the assessment and plan). Decide whether this encounter is the documenting clinician's FIRST encounter with this patient, or a REPEAT visit with a clinician/practice that already has an established relationship with the patient.

Definitions:
- "first_encounter": emergency department or urgent care presentation; a new-patient office visit; an initial specialty consultation requested by another provider; any note in which the writer is clearly seeing this patient for the first time (e.g. "presents to the emergency room", "asked to see", "referred for evaluation of", "this is a new patient").
- "established_repeat": the note documents a return or follow-up visit with the same clinician or practice (e.g. "returns to clinic", "here for follow-up", "since her last visit", "I last saw him in", a post-operative check by the operating surgeon, routine chronic-disease follow-up, a scheduled recheck).
- "indeterminate": the text gives no reliable signal either way.

Judge ONLY from the text. Do not infer from the note type or specialty label. If the note describes a consultation that is itself the first time this consultant meets the patient, that is "first_encounter" even if the patient has a long history with other providers.

Also report:
- "setting": one of emergency_department, urgent_care, office_new_or_consult, office_established, other_or_unclear.
- "prior_results_in_note": true if the presentation reports results of testing done BEFORE this visit (prior labs with values, prior imaging findings, prior biopsy/pathology), otherwise false.
- "evidence": the single most decisive verbatim phrase from the note (25 words max) supporting your encounter_type, or "" if none.

CLINICAL PRESENTATION:
---
{presentation}
---

Return ONLY JSON:
{{"encounter_type": "first_encounter" | "established_repeat" | "indeterminate", "setting": "...", "prior_results_in_note": true | false, "evidence": "..."}}"""

_write_lock = threading.Lock()


def _atomic_write(fpath, data):
    with _write_lock:
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(fpath.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as out:
                json.dump(data, out, indent=2, default=str)
            os.replace(tmp, str(fpath))
        except BaseException:
            os.unlink(tmp)
            raise


def _parse(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if text.startswith("json"):
        text = text[4:].strip()
    # tolerate leading prose before the JSON object
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        text = m.group(0)
    obj = json.loads(text)
    et = str(obj.get("encounter_type", "")).strip().lower()
    st = str(obj.get("setting", "")).strip().lower()
    return {
        "encounter_type": et if et in ENCOUNTER_LEVELS else "error",
        "setting": st if st in SETTING_LEVELS else "other_or_unclear",
        "prior_results_in_note": bool(obj.get("prior_results_in_note", False)),
        "evidence": str(obj.get("evidence", ""))[:300],
    }


def classify_one(provider, model_id, presentation):
    llm = CloudLLMClient(provider=provider, model=model_id)
    prompt = PROMPT.format(presentation=presentation)
    for attempt in range(4):
        try:
            resp = llm.generate(prompt, max_tokens=1024, temperature=0)
            return _parse(resp)
        except Exception as e:                                   # noqa: BLE001
            if "429" in str(e) and attempt < 3:
                time.sleep(2 ** attempt * 5)
            elif attempt == 3:
                return {"encounter_type": "error", "setting": "other_or_unclear",
                        "prior_results_in_note": False, "evidence": f"ERROR: {e}"[:200]}
            else:
                time.sleep(2)
    return {"encounter_type": "error", "setting": "other_or_unclear",
            "prior_results_in_note": False, "evidence": "ERROR"}


def majority(votes):
    """Majority label across judges; no majority -> indeterminate + adjudication flag."""
    labels = [v["encounter_type"] for v in votes.values() if v["encounter_type"] != "error"]
    if not labels:
        return "error", False, True
    counts = Counter(labels)
    top, n = counts.most_common(1)[0]
    unanimous = n == len(labels) and len(labels) == len(votes)
    if n * 2 > len(labels):                      # strict majority
        return top, unanimous, False
    return "indeterminate", False, True          # tie -> physician adjudication


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judges", default=",".join(JUDGES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--force", action="store_true", help="re-query judges already stored")
    args = ap.parse_args()

    judges = [j.strip() for j in args.judges.split(",") if j.strip()]
    for j in judges:
        if j not in JUDGES:
            sys.exit(f"unknown judge {j}; choose from {list(JUDGES)}")

    cases = json.load(open(REFERENCE_FILE))
    if args.limit:
        cases = cases[:args.limit]

    prior = {}
    if OUT_FILE.exists() and not args.force:
        prior = {c["case_id"]: c for c in json.load(open(OUT_FILE)).get("cases", [])}

    out = []
    for c in cases:
        rec = prior.get(c["case_id"], {})
        out.append({
            "case_id": c["case_id"],
            "specialty": c.get("specialty", ""),
            "sample_name": c.get("sample_name", ""),
            "presentation_chars": len(c.get("presentation", "")),
            "votes": rec.get("votes", {}),
        })
    by_id = {r["case_id"]: r for r in out}
    pres = {c["case_id"]: c.get("presentation", "") for c in cases}

    todo = [(r["case_id"], j) for r in out for j in judges
            if j not in r["votes"] or r["votes"][j].get("encounter_type") == "error"]
    print(f"{len(out)} cases x {len(judges)} judges -> {len(todo)} calls", flush=True)

    def task(cid, judge):
        provider, model_id = JUDGES[judge]
        return cid, judge, classify_one(provider, model_id, pres[cid])

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(task, cid, j) for cid, j in todo]
        for fut in as_completed(futs):
            cid, judge, val = fut.result()
            by_id[cid]["votes"][judge] = val
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(todo)}", flush=True)
                _atomic_write(OUT_FILE, {"cases": out, "summary": {}})

    # ---- consensus + summary -------------------------------------------------
    for r in out:
        lab, unan, adj = majority(r["votes"])
        r["encounter_type"] = lab
        r["unanimous"] = unan
        r["needs_adjudication"] = adj
        settings = [v["setting"] for v in r["votes"].values() if v["setting"]]
        r["setting"] = Counter(settings).most_common(1)[0][0] if settings else "other_or_unclear"
        pr = [v["prior_results_in_note"] for v in r["votes"].values()]
        r["prior_results_in_note"] = sum(pr) * 2 > len(pr) if pr else False
        ev = [v["evidence"] for v in r["votes"].values() if v.get("evidence")]
        r["evidence"] = ev[0] if ev else ""

    n = len(out)
    enc = Counter(r["encounter_type"] for r in out)
    summary = {
        "n_cases": n,
        "judges": judges,
        "encounter_type": {k: enc.get(k, 0) for k in ENCOUNTER_LEVELS + ["error"]},
        "encounter_type_pct": {k: round(100 * enc.get(k, 0) / n, 1)
                               for k in ENCOUNTER_LEVELS + ["error"]},
        "setting": dict(Counter(r["setting"] for r in out)),
        "prior_results_in_note": sum(r["prior_results_in_note"] for r in out),
        "unanimous": sum(r["unanimous"] for r in out),
        "needs_adjudication": sum(r["needs_adjudication"] for r in out),
        "by_specialty": {
            sp: dict(Counter(r["encounter_type"] for r in out if r["specialty"] == sp))
            for sp in sorted({r["specialty"] for r in out})
        },
    }
    # pairwise judge agreement (raw), for the supplement
    pair = {}
    for i, a in enumerate(judges):
        for b in judges[i + 1:]:
            both = [(r["votes"][a]["encounter_type"], r["votes"][b]["encounter_type"])
                    for r in out if a in r["votes"] and b in r["votes"]]
            both = [(x, y) for x, y in both if "error" not in (x, y)]
            if both:
                pair[f"{a} vs {b}"] = round(sum(x == y for x, y in both) / len(both), 3)
    summary["pairwise_agreement"] = pair

    _atomic_write(OUT_FILE, {"cases": out, "summary": summary})
    print(json.dumps(summary, indent=2))
    print(f"\nwrote {OUT_FILE}")


if __name__ == "__main__":
    main()
