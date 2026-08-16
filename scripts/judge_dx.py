#!/usr/bin/env python3
"""
Diagnostic-concordance judge for the .

A clean, parametrized re-implementation of the diagnostic-agreement classifier used
in the main study. Serves two needs:

  (1) Phase 1 — classify the prompt-variant arms (results/models_<arm>/) which have no
      v1 dx_match field, so the original scripts/rejudge_dx.py (which only re-judges
      records that already carry a v1 label) cannot process them.

  (2) re-run the classification with a NON-OpenAI
      judge (Claude or Gemini) and compare within-family vs cross-family leniency to
      test whether a GPT judge rates GPT plans more favorably.

The classification prompt is byte-identical to scripts/rejudge_dx.py::REJUDGE_PROMPT.
Unlike the original (which copied v1 'correct'/'wrong' and only LLM-judged partials),
this judges EVERY record with the LLM, so each output field is a pure single-judge
labeling — the correct unit for the cross-judge comparison.

Usage
-----
  # judge a prompt arm with the default (OpenAI) judge -> writes dx_match_v2
  python scripts/judge_dx.py --dir results/models_parsimonious --judge gpt-4.1-mini

  # cross-judge the canonical results with a non-OpenAI judge -> writes a separate field
  python scripts/judge_dx.py --dir results/models --judge claude --field dx_match_claude
  python scripts/judge_dx.py --dir results/models --judge gemini --field dx_match_gemini
"""

import json
import os
import sys
import time
import tempfile
import threading
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulations"))
from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)
from pipeline.cloud_llm_client import CloudLLMClient

# Byte-identical to scripts/rejudge_dx.py::REJUDGE_PROMPT
REJUDGE_PROMPT = (
    "Compare the human physician's primary diagnosis to the LLM's primary diagnosis.\n\n"
    "Human diagnosis: {human_dx}\n"
    "LLM diagnosis: {llm_dx}\n\n"
    "Rate using these categories:\n"
    '- "correct": Same diagnosis, even if worded differently or different specificity\n'
    '- "correct_plus": Same primary condition AND added clinically relevant secondary diagnoses\n'
    '- "related": Same organ system but meaningfully different specific diagnosis\n'
    '- "wrong": Fundamentally different primary diagnosis\n\n'
    'Return ONLY: {{"match": "correct" or "correct_plus" or "related" or "wrong"}}'
)

# Judge model registry. Keep gpt-4.1-mini as the default to match the main study.
JUDGES = {
    "gpt-4.1-mini": ("openrouter", "openai/gpt-4.1-mini"),
    "claude":       ("openrouter", "anthropic/claude-sonnet-4.5"),
    "gemini":       ("openrouter", "google/gemini-2.5-flash"),  # flash: lighter thinking than -pro
    "gemini-pro":   ("openrouter", "google/gemini-2.5-pro"),
}

_write_lock = threading.Lock()


def judge_one(llm, human_dx, llm_dx):
    prompt = REJUDGE_PROMPT.format(human_dx=human_dx, llm_dx=llm_dx)
    for attempt in range(4):
        try:
            # 1024 (not 100): reasoning/"thinking" judge models (gemini-2.5, o-series,
            # gpt-5.x) consume completion tokens on internal reasoning before emitting JSON.
            resp = llm.generate(prompt, max_tokens=1024, temperature=0)
            text = resp.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
            return json.loads(text).get("match", "") or "error"
        except Exception as e:
            if "429" in str(e) and attempt < 3:
                time.sleep(2 ** attempt * 5)
            else:
                return "error"
    return "error"


def judge_file(fpath, provider, model_id, field, workers, force):
    data = json.load(open(fpath))
    todo = [
        i for i, r in enumerate(data)
        if r.get("llm_diagnoses") and r.get("human_diagnoses")
        and (force or not r.get(field) or r.get(field) == "error")
    ]
    if not todo:
        print(f"  {fpath.name}: all done ({len(data)})")
        return
    print(f"  {fpath.name}: judging {len(todo)}/{len(data)} -> {field}", flush=True)

    def task(idx):
        r = data[idx]
        human_dx = ", ".join(r["human_diagnoses"][:3])
        llm_dx = ", ".join(r["llm_diagnoses"][:3])
        llm = CloudLLMClient(provider=provider, model=model_id)
        return idx, judge_one(llm, human_dx, llm_dx)

    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(task, i) for i in todo]):
            idx, val = fut.result()
            data[idx][field] = val
            done += 1
            if done % 50 == 0:
                _atomic_write(fpath, data)
    _atomic_write(fpath, data)
    print(f"    {fpath.name}: {done} judged")


def _atomic_write(fpath, data):
    with _write_lock:
        fd, tmp = tempfile.mkstemp(dir=str(fpath.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as out:
                json.dump(data, out, indent=2, default=str)
            os.replace(tmp, str(fpath))
        except BaseException:
            os.unlink(tmp)
            raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="results dir with m_*.json (e.g. results/models_parsimonious)")
    ap.add_argument("--judge", default="gpt-4.1-mini", choices=list(JUDGES))
    ap.add_argument("--field", default="dx_match_v2", help="output field name")
    ap.add_argument("--models", help="comma-separated model keys (default: all m_*.json)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    provider, model_id = JUDGES[args.judge]
    d = ROOT / args.dir if not os.path.isabs(args.dir) else Path(args.dir)
    if args.models:
        files = [d / f"m_{m.strip()}.json" for m in args.models.split(",")]
    else:
        files = sorted(d.glob("m_*.json"))
    files = [f for f in files if f.exists() and f.name != "m_human.json"]

    print(f"Judge: {args.judge} ({model_id}) -> field '{args.field}' on {len(files)} files in {d}")
    for f in files:
        judge_file(f, provider, model_id, args.field, args.workers, args.force)
    print("\nDone.")


if __name__ == "__main__":
    main()
