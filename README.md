# Comparative Cost of Care Recommended by Clinicians vs. Large Language Models

Data and analysis code for:

> Aran D, Goldhaber-Fiebert JD, Many I, Nguyen A, Yang D, Shelly S.
> *Comparative Cost of Care Recommended by Clinicians vs. Large Language Models.*
> **NEJM AI**, 2026.

Twenty-four AI systems (20 general-purpose LLMs and 4 specialized medical systems) were
each given the clinical presentation from 200 de-identified outpatient and emergency
department notes and asked to write an assessment and plan. Orders in every AI plan and in
the treating physician's documented plan were extracted by three independent LLMs and priced
against the CY 2026 Medicare Physician Fee Schedule. All reported quantities are derived from
the files in this repository.

---

## Contents

| Path | Contents |
|---|---|
| `results/models/` | Canonical 24-system standard-prompt panel, 200 cases per file. Each record holds the verbatim AI plan, three independent LLM order extractions with matched CPT codes and CY 2026 Medicare prices, the diagnostic-agreement classification, and the corresponding physician plan. |
| `results/models_parsimonious/`, `results/models_costaware/` | The two mitigation prompt arms, same schema. |
| `results/models_original_runs/` | Pre-deduplication runs (~315 cases per file), retained as the source for the test–retest reliability analysis and the appropriateness sub-study. |
| `results/analysis/paper_numbers.json` | Every quantity reported in the paper, in structured form. `paper_numbers.md` is the human-readable rendering. |
| `results/analysis/appropriateness_ratings.csv` | The 1,000 physician appropriateness ratings (one row per case × system). |
| `results/analysis/visit_type.json` | Encounter-type classification for all 200 cases. |
| `data/guideline_currency_review.xlsx` | Guideline-currency scores for all 220 candidate cases (two LLM reviewers plus physician adjudication). |
| `data/appropriateness_review.xlsx` | Physician appropriateness scoring workbook (the input read by `paper_numbers.py`). |
| `data/mtsamples.csv` | Snapshot of the public MTSamples corpus (4,999 notes). See https://mtsamples.com. |
| `paper/Supplementary_Table_S2.xlsx`, `paper/Supplementary_Table_S5.xlsx` | The two supplementary spreadsheets referenced by the paper. |
| `paper/figures/` | Generated figure files. |
| `figures/` | Number and figure generation. |
| `scripts/` | The pipeline that produced the canonical files: model querying, order extraction, CPT matching, Medicare pricing, the cost-cleanup passes, and the per-analysis scripts. |
| `simulations/pipeline/` | Shared LLM client and CPT lookup utilities used by the pipeline. |

The CMS NADAC drug pricing file (`data/nadac.csv`, 164 MB) is not redistributed; it is public
and available from https://data.medicaid.gov if you wish to re-run medication pricing.

---

## Reproducing the reported numbers and figures

```bash
git clone https://github.com/dviraran/mtsample_study.git
cd mtsample_study
pip install -r requirements.txt
```

```bash
python3 figures/paper_numbers.py
```

Recomputes every reported quantity from `results/models/` and writes
`results/analysis/paper_numbers.{json,md}`.

```bash
python3 figures/generate_paper_figures.py
python3 figures/make_supp_consort.py
python3 figures/make_supp_extractor_agreement.py
python3 figures/make_supp_referral_analysis.py
```

Regenerates the main and supplementary figures into `paper/figures/`. Figure 1 is a
hand-drawn study-design schematic and is not generated programmatically.

The individual scripts under `scripts/` regenerate the supporting analyses (primary outcome,
encounter-type stratification, inter-rater reliability, test–retest agreement, medication
reliability, appropriateness review, utilization patterns).

The study itself — the API queries to the 24 systems and the three-extractor order extraction —
is not re-run by these commands. Model versions and API availability change, and re-querying
would be non-deterministic; the JSON files preserve the outputs observed in March and May 2026.
`scripts/run_study.py`, `scripts/reextract*.py`, `scripts/price_arms.py` and the cleanup passes
document how those files were produced.

---

## Archival version

Zenodo: https://doi.org/10.5281/zenodo.XXXXXXX

---

## License

Code is MIT; data is CC-BY-4.0. The MTSamples and CMS files carry their own upstream terms.
See [`LICENSE`](LICENSE).

## Contact

Dvir Aran — dviraran@technion.ac.il, Technion – Israel Institute of Technology.
