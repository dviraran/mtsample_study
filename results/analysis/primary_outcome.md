# Primary outcome — total cost of recommended care

This is the **only** hypothesis test reported in the manuscript and supplement; every other quantity is a point estimate with a 95% confidence interval.

**Definition.** per-visit total cost of recommended care = diagnostic tests + specialist consultations; AI value is the mean across the 20 general-purpose systems; comparator is the treating physician's plan on the same case. Medications are excluded from the outcome and reported as counts.

**Result.** Physician $97/visit (95% CI $66–$135; median $0, IQR $0–$72) vs AI $314/visit (95% CI $266–$367; median $205, IQR $78–$421).

Mean difference **$216/visit** (95% CI $177–$257), ratio of means **3.22×**; AI higher in 180/200 cases, lower in 16. Paired Wilcoxon signed-rank **P < 0.001** (exact p = 1.08e-26).

## Components (point estimates only — no tests)

| Component | Physician mean (95% CI) | AI mean (95% CI) | Difference (95% CI) | Ratio |
|---|---:|---:|---:|---:|
| Diagnostic tests | $71 ($46–$103) | $176 ($140–$217) | $105 ($77–$134) | 2.47× |
| Specialist consultations | $26 ($14–$42) | $137 ($118–$158) | $111 ($92–$131) | 5.26× |
| New medications (imputed; excluded from the outcome) | $59 ($33–$98) | $101 ($35–$187) | $42 ($-32–$131) | 1.72× |

## Sensitivity: medications added back

Physician $156 vs AI $415; difference $259 (95% CI $168-$357), ratio 2.66x.

## Primary outcome by encounter type

| Stratum | n | Physician | AI | Difference (95% CI) | Ratio |
|---|---:|---:|---:|---:|---:|
| first_encounter | 73 | $134 | $399 | $265 ($191–$348) | 2.98× |
| established_repeat | 101 | $82 | $255 | $173 ($125–$220) | 3.12× |

## Per-system total cost of recommended care

| System | Physician $/visit | AI $/visit | Ratio | Excess (95% CI) |
|---|---:|---:|---:|---:|
| Qwen 3 | $96 | $599 | 6.26× | $503 ($433–$578) |
| DeepSeek R1 | $97 | $431 | 4.47× | $335 ($278–$393) |
| Grok 3 | $97 | $398 | 4.09× | $301 ($254–$348) |
| Qwen 2.5 | $97 | $374 | 3.83× | $276 ($222–$331) |
| Gemini 2.5 Pro | $97 | $340 | 3.51× | $243 ($194–$298) |
| MedGemma 27B * | $98 | $342 | 3.47× | $243 ($194–$291) |
| Claude Opus 4.8 | $98 | $329 | 3.36× | $231 ($175–$296) |
| GPT-5.2 | $97 | $324 | 3.32× | $226 ($172–$284) |
| DeepSeek V3 | $99 | $325 | 3.28× | $226 ($174–$276) |
| GPT-5.5 | $97 | $314 | 3.25× | $218 ($164–$281) |
| Claude 3.5 | $97 | $302 | 3.09× | $204 ($149–$265) |
| OpenEvidence * | $97 | $297 | 3.06× | $199 ($138–$264) |
| Gemini 3.5 Flash | $97 | $290 | 3.01× | $194 ($146–$243) |
| Meditron * | $98 | $295 | 3.00× | $197 ($148–$248) |
| Claude 4.5 | $98 | $293 | 3.00× | $195 ($134–$273) |
| Grok 4.1 | $98 | $292 | 2.98× | $194 ($149–$239) |
| Qwen 3.7 | $97 | $270 | 2.80× | $174 ($122–$228) |
| MedGemma 4B * | $97 | $260 | 2.69× | $163 ($117–$212) |
| Grok 4.3 | $97 | $251 | 2.57× | $153 ($106–$207) |
| Llama 3.3 | $98 | $248 | 2.54× | $150 ($109–$190) |
| Llama 4 | $97 | $238 | 2.47× | $142 ($80–$237) |
| GPT-4.1 | $100 | $245 | 2.45× | $145 ($101–$192) |
| Gemini 3 Pro | $97 | $210 | 2.15× | $112 ($74–$153) |
| Gemini 3.1 Pro | $98 | $209 | 2.12× | $111 ($64–$163) |

\* specialized medical AI system
