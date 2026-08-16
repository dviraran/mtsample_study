#!/usr/bin/env python3
"""
Merge the physician adjudication of encounter type back into visit_type.json.

The three LLM judges agreed unanimously on 151 of 200 cases; the 49 they split on
were referred to a physician reviewer (I.M.) via data/visit_type_adjudication.csv.
This script applies those labels, which override the LLM majority, and records
provenance on every case so the source of each label stays auditable.

Input:  a CSV or Numbers-exported CSV with columns `case_id` and a
        `PHYSICIAN_LABEL...` column (extra columns are ignored).
Output: results/analysis/visit_type.json updated in place, with
          label_source = "llm_unanimous" | "llm_majority" | "physician_adjudicated"
        and the pre-adjudication label preserved as `llm_label`.

Usage:
  /usr/bin/python3 scripts/merge_visit_type_adjudication.py path/to/adjudicated.csv
  /usr/bin/python3 scripts/merge_visit_type_adjudication.py path/to.csv --dry-run
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VISIT_FILE = ROOT / "results" / "analysis" / "visit_type.json"
VALID = {"first_encounter", "established_repeat", "indeterminate"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv_path)))
    if not rows:
        sys.exit("empty adjudication file")
    label_col = next((c for c in rows[0] if c.startswith("PHYSICIAN_LABEL")), None)
    note_col = next((c for c in rows[0] if c.startswith("PHYSICIAN_NOTE")), None)
    if not label_col:
        sys.exit("no PHYSICIAN_LABEL column found")

    adj, bad, blank = {}, [], 0
    for r in rows:
        lab = (r.get(label_col) or "").strip().lower()
        if not lab:
            blank += 1
            continue
        if lab not in VALID:
            bad.append((r["case_id"], lab))
            continue
        adj[r["case_id"]] = {"label": lab,
                             "note": (r.get(note_col) or "").strip() if note_col else ""}
    if bad:
        print("unrecognised labels (skipped):")
        for cid, lab in bad:
            print(f"   {cid}: {lab!r}")
    print(f"{len(adj)} adjudicated, {blank} left blank")

    data = json.load(open(VISIT_FILE))
    changed = Counter()
    applied = 0
    for c in data["cases"]:
        if "llm_label" not in c:
            c["llm_label"] = c["encounter_type"]
        if "label_source" not in c:
            c["label_source"] = "llm_unanimous" if c.get("unanimous") else "llm_majority"
        a = adj.get(c["case_id"])
        if not a:
            continue
        # Compare against the pre-adjudication LLM label, not the current value,
        # so the script is idempotent and the reported agreement stays correct
        # when it is re-run after an override.
        if a["label"] != c["llm_label"]:
            changed[(c["llm_label"], a["label"])] += 1
        c["encounter_type"] = a["label"]
        c["label_source"] = "physician_adjudicated"
        if a["note"]:
            c["physician_note"] = a["note"]
        applied += 1

    missing = set(adj) - {c["case_id"] for c in data["cases"]}
    if missing:
        print(f"WARNING: {len(missing)} adjudicated case ids not in visit_type.json: "
              f"{sorted(missing)[:5]}")

    counts = Counter(c["encounter_type"] for c in data["cases"])
    n = len(data["cases"])
    data["summary"]["encounter_type"] = {k: counts.get(k, 0)
                                         for k in list(VALID) + ["error"]}
    data["summary"]["encounter_type_pct"] = {k: round(100 * counts.get(k, 0) / n, 1)
                                             for k in list(VALID) + ["error"]}
    data["summary"]["physician_adjudicated"] = applied
    data["summary"]["adjudication_changed"] = {f"{a} -> {b}": v
                                               for (a, b), v in changed.items()}
    data["summary"]["adjudication_agreement"] = (
        round((applied - sum(changed.values())) / applied, 3) if applied else None)

    print(f"\napplied to {applied} cases; {sum(changed.values())} labels changed")
    for (a, b), v in changed.most_common():
        print(f"   {a:20s} -> {b:20s} {v}")
    print("\nfinal cohort:")
    for k in ("first_encounter", "established_repeat", "indeterminate"):
        print(f"   {k:20s} {counts.get(k,0):>3}  ({100*counts.get(k,0)/n:.1f}%)")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return
    VISIT_FILE.write_text(json.dumps(data, indent=2))
    print(f"\nwrote {VISIT_FILE}")


if __name__ == "__main__":
    main()
