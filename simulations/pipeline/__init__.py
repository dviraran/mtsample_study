"""Vendored pipeline package for the mtsample_study analysis.
Shared LLM client and CPT lookup utilities (cloud_llm_client.py, utils/cpt_lookup.py),
vendored 2026-06-01 so the LLM generation/extraction/judge pipeline is reproducible
independently of the transient medbar worktrees. Cost pricing still uses the malpractice
cost module via scripts/reprice_medicare.py (self-bootstrapped sys.path)."""
