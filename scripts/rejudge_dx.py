"""Re-judge diagnosis matches using nuanced 4-category system."""
import json, os, sys, time, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "simulations"))
from dotenv import load_dotenv
load_dotenv(Path("~/.env").expanduser(), override=True)
from pipeline.cloud_llm_client import CloudLLMClient

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

MODELS = [
    'm_claude-sonnet-3.5.json', 'm_claude-sonnet-4.5.json',
    'm_gemini-2.5-pro.json', 'm_gemini-3-pro.json',
    'm_gpt-4.1.json', 'm_gpt-5.2.json',
    'm_grok-3.json', 'm_grok-4.1.json',
    'm_llama-3.3-70b.json', 'm_llama4.json',
    'm_qwen-2.5-72b.json', 'm_qwen3.json',
    'm_deepseek-r1.json', 'm_deepseek-v3.2.json',
    'm_openevidence.json',
]


def rejudge_file(fname, llm, results_dir):
    f = results_dir / fname
    if not f.exists():
        return

    with open(f) as fh:
        data = json.load(fh)

    to_judge = [i for i, r in enumerate(data)
                if 'dx_match_v2' not in r and r.get('dx_match') and r.get('llm_diagnoses') and r.get('human_diagnoses')]

    if not to_judge:
        print(f"  {fname}: all done ({len(data)})")
        return

    print(f"  {fname}: judging {len(to_judge)}...", end=" ", flush=True)
    done = 0
    for idx in to_judge:
        r = data[idx]
        old_match = r.get('dx_match', '')

        # If already correct or wrong in v1, just copy
        if old_match == 'correct':
            r['dx_match_v2'] = 'correct'
            done += 1
            continue
        if old_match == 'wrong':
            r['dx_match_v2'] = 'wrong'
            done += 1
            continue

        # Re-judge partials
        human_dx = ", ".join(r['human_diagnoses'][:3])
        llm_dx = ", ".join(r['llm_diagnoses'][:3])

        for attempt in range(3):
            try:
                resp = llm.generate(
                    REJUDGE_PROMPT.format(human_dx=human_dx, llm_dx=llm_dx),
                    max_tokens=100, temperature=0
                )
                text = resp.strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                if text.startswith("json"):
                    text = text[4:].strip()
                result = json.loads(text)
                match_val = result.get('match', '')
                if not match_val:
                    print(f"Warning: failed to parse LLM response for case {r.get('case_id', idx)}")
                r['dx_match_v2'] = match_val or 'error'
                done += 1
                break
            except (json.JSONDecodeError, Exception) as e:
                if "429" in str(e):
                    time.sleep(2 ** attempt * 5)
                else:
                    print(f"Warning: exception for case {r.get('case_id', idx)}: {e}")
                    r['dx_match_v2'] = 'error'
                    done += 1
                    break

    # Atomic write: write to temp file, then replace
    fd, tmp_path = tempfile.mkstemp(dir=str(results_dir), suffix=".tmp")
    try:
        with os.fdopen(fd, 'w') as out:
            json.dump(data, out, indent=2, default=str)
        os.replace(tmp_path, str(f))
    except Exception:
        os.unlink(tmp_path)
        raise
    print(f"{done} done")


if __name__ == "__main__":
    import argparse

    llm = CloudLLMClient(provider="openrouter", model="openai/gpt-4.1-mini")

    _parser = argparse.ArgumentParser()
    _parser.add_argument("--file", help="Single file to process")
    _args = _parser.parse_args()

    results_dir = ROOT / "results" / "models_original_runs"
    _file_list = [_args.file] if _args.file else MODELS

    for fname in _file_list:
        rejudge_file(fname, llm, results_dir)

    print("\nDone.")
