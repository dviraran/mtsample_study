# Paper Numbers (source of truth)

All numbers computed from `results/models/m_*.json` with n=200 filter.

## Aggregates (used in Abstract / Results body)

- N cases (primary): **200**
- Total AI–physician comparisons: **4800** (24 models × 200 cases)
- Physician avg dx cost: **$71.35**
- Physician med count: **0.60** / visit
- Physician ref count: **0.15** / visit
- Zero-phys cases: **133/200** (**66%**)
- Nonzero-phys cases: **67**
- dx_ratio range: **1.37× – 4.02×** (Llama 3.3 → Qwen 3)
- dx cost range: **$97 – $289** / visit
- GP mean excess (unweighted): **$105.21** / visit
- Med count range: **0.29 – 2.02** (phys 0.60), up to **3.4×** physician
- Ref count range: **0.4 – 1.94** (**2.6× – 12.6×**)
- pct-added (zero-phys subset): **45% – 79%**
- NAMCS strata: routine 66%, simple 16%, significant 17%
- Subset (zero phys) AI mean: **$117**
- Subset (nonzero phys) physician mean: **$213**
- Subset (nonzero phys) mean ratio: **1.38×**, 1/20 GP models under physician

## Per-model (Table 1 source)

| Model | Concordant | Adjacent | Discordant | Dx cost | Dx fold | Med count | Med fold | Ref count | Ref fold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 4.8 | 83% | 13% | 4% | $216 | 3.02× | 1.10 | 1.8× | 0.69 | 4.6× |
| Claude 3.5 | 76% | 19% | 5% | $167 | 2.34× | 1.05 | 1.8× | 0.84 | 5.6× |
| Claude 4.5 | 78% | 16% | 6% | $181 | 2.54× | 1.16 | 1.9× | 0.70 | 4.7× |
| DeepSeek R1 | 77% | 16% | 7% | $218 | 3.06× | 1.84 | 3.1× | 1.36 | 9.1× |
| DeepSeek V3 | 75% | 18% | 7% | $171 | 2.40× | 1.07 | 1.8× | 1.02 | 6.8× |
| Gemini 2.5 Pro | 75% | 18% | 7% | $199 | 2.78× | 1.49 | 2.5× | 0.84 | 5.6× |
| Gemini 3 Pro | 80% | 14% | 6% | $145 | 2.04× | 1.12 | 1.9× | 0.41 | 2.7× |
| Gemini 3.1 Pro | 82% | 14% | 4% | $146 | 2.05× | 0.85 | 1.4× | 0.40 | 2.6× |
| Gemini 3.5 Flash | 80% | 15% | 6% | $167 | 2.34× | 1.33 | 2.2× | 0.77 | 5.1× |
| GPT-4.1 | 82% | 12% | 6% | $137 | 1.92× | 0.57 | 1.0× | 0.68 | 4.5× |
| GPT-5.2 | 84% | 11% | 5% | $217 | 3.04× | 1.52 | 2.5× | 0.69 | 4.6× |
| GPT-5.5 | 88% | 7% | 5% | $230 | 3.22× | 1.30 | 2.2× | 0.54 | 3.6× |
| Grok 3 | 78% | 15% | 7% | $189 | 2.65× | 1.19 | 2.0× | 1.33 | 8.9× |
| Grok 4.1 | 75% | 19% | 6% | $159 | 2.22× | 2.02 | 3.4× | 0.89 | 5.9× |
| Grok 4.3 | 80% | 14% | 6% | $148 | 2.07× | 1.08 | 1.8× | 0.67 | 4.4× |
| Llama 3.3 | 72% | 20% | 8% | $97 | 1.37× | 0.37 | 0.6× | 0.88 | 5.9× |
| Llama 4 | 74% | 18% | 9% | $130 | 1.82× | 0.29 | 0.5× | 0.65 | 4.3× |
| MedGemma 27B | 80% | 15% | 5% | $185 | 2.60× | 0.97 | 1.6× | 0.97 | 6.5× |
| MedGemma 4B | 73% | 18% | 9% | $142 | 1.99× | 0.69 | 1.1× | 0.70 | 4.7× |
| Meditron | 68% | 21% | 10% | $171 | 2.40× | 0.83 | 1.4× | 0.76 | 5.0× |
| OpenEvidence | 74% | 19% | 7% | $181 | 2.54× | 1.03 | 1.7× | 0.74 | 5.0× |
| Qwen 2.5 | 68% | 24% | 8% | $171 | 2.40× | 0.82 | 1.4× | 1.28 | 8.6× |
| Qwen 3.7 | 81% | 13% | 6% | $155 | 2.18× | 1.13 | 1.9× | 0.74 | 4.9× |
| Qwen 3 | 78% | 15% | 7% | $289 | 4.02× | 1.43 | 2.4× | 1.94 | 12.9× |

## Version changes (paired Wilcoxon, n=200 per family)

| Family | Old | New | fold_old | fold_new | % change | p |
|---|---|---|---:|---:|---:|---:|
| GPT | gpt-4.1 | gpt-5.5 | 1.92× | 3.22× | +68.1% | 0.0 |
| Qwen | qwen-2.5-72b | qwen-3.7 | 2.40× | 2.18× | -9.3% | 0.0019 |
| Gemini | gemini-2.5-pro | gemini-3.1-pro | 2.78× | 2.05× | -26.3% | 0.0 |
| Grok | grok-3 | grok-4.3 | 2.65× | 2.07× | -21.9% | 0.0 |
| Llama | llama-3.3-70b | llama4 | 1.37× | 1.82× | +33.1% | 0.2737 |
| Claude | claude-sonnet-3.5 | claude-opus-4.8 | 2.34× | 3.02× | +29.0% | 0.0007 |
| DeepSeek | deepseek-v3.2 | deepseek-r1 | 2.40× | 3.06× | +27.6% | 0.0002 |

## Population projections (commercial 2× Medicare, 883M visits)

| Adoption | Min | Max |
|---|---|---|
| 5% | $5.6B (Grok 4.3) | $14.5B (GPT-5.5) |
| 10% | $11.3B (Grok 4.3) | $29.1B (GPT-5.5) |
| 25% | $28.2B (Grok 4.3) | $72.7B (GPT-5.5) |

## Subset analysis (Table S5 source)

| Model | Zero-phys: AI/visit | Nonzero: Phys | Nonzero: AI | Ratio |
|---|---:|---:|---:|---:|
| Claude Opus 4.8 | $137 | $213 | $371 | 1.74× |
| Claude 3.5 | $102 | $213 | $297 | 1.39× |
| Claude 4.5 | $89 | $213 | $364 | 1.71× |
| DeepSeek R1 | $168 | $213 | $318 | 1.49× |
| DeepSeek V3 | $111 | $213 | $289 | 1.36× |
| Gemini 2.5 Pro | $140 | $213 | $316 | 1.48× |
| Gemini 3 Pro | $83 | $213 | $269 | 1.26× |
| Gemini 3.1 Pro | $91 | $213 | $255 | 1.20× |
| Gemini 3.5 Flash | $118 | $213 | $265 | 1.24× |
| GPT-4.1 | $97 | $213 | $215 | 1.01× |
| GPT-5.2 | $139 | $213 | $370 | 1.74× |
| GPT-5.5 | $149 | $213 | $391 | 1.84× |
| Grok 3 | $148 | $213 | $270 | 1.27× |
| Grok 4.1 | $101 | $213 | $273 | 1.28× |
| Grok 4.3 | $111 | $213 | $221 | 1.04× |
| Llama 3.3 | $61 | $213 | $169 | 0.79× |
| Llama 4 | $57 | $213 | $274 | 1.29× |
| MedGemma 27B | $129 | $213 | $297 | 1.40× |
| MedGemma 4B | $99 | $213 | $226 | 1.06× |
| Meditron | $132 | $213 | $249 | 1.17× |
| OpenEvidence | $135 | $213 | $274 | 1.29× |
| Qwen 2.5 | $130 | $213 | $252 | 1.19× |
| Qwen 3.7 | $97 | $213 | $271 | 1.27× |
| Qwen 3 | $212 | $213 | $440 | 2.07× |

## Clinical Appropriateness Review (Table S4 source)

- N cases × N models: **200 × 5 = 1000 ratings**
- Mean score distribution: **1=5.2% / 2=17.2% / 3=59.2% / 4=18.4%**
- Mean inappropriate (1+2): **22.4%** (range 15.0–30.5%)
- Mean guideline-concordant (4): **18.4%** (range 12.5–23.0%)
- Mean unadjusted $/visit excess: **$72.92** (5-model mean; paper overall $71)
- Mean strict-adjusted (score 1+2): **$17.94** (**24.6%** retained)
- Mean lenient-adjusted (score 1+2+3): **$56.83** (**77.9%** retained)

| Model | 1 | 2 | 3 | 4 | Unadj | Strict | Lenient |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.2 | 4.5% | 18.0% | 55.0% | 22.5% | $114 | $27 (23.7%) | $79 (69.2%) |
| Claude 4.5 | 4.5% | 11.0% | 61.5% | 23.0% | $72 | $12 (16.4%) | $49 (67.6%) |
| Gemini 3 Pro | 3.0% | 12.0% | 68.5% | 16.5% | $62 | $4 (5.9%) | $53 (85.9%) |
| Grok 4.1 | 4.5% | 24.0% | 59.0% | 12.5% | $57 | $26 (45.9%) | $43 (76.4%) |
| OpenEvidence | 9.5% | 21.0% | 52.0% | 17.5% | $60 | $21 (35.1%) | $60 (100.2%) |

## MTS_0100 exemplar (Figure 1 source)

- GPT-5.2 stored total: **$816.8**
- GPT-5.2 median-slot breakdown: stress/echo **$270.21**, X-ray **$309.97**, DEXA **$39.41**, labs **$197.21** (n=11)
- Physician CRP cost: **$5.18** (CPT 86140)
- Physician total dx cost (inc. colonoscopy): **$383.28**