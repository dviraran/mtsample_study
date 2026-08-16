# Reliability of imputed medication cost

Supporting analysis for Supplementary Methods S1.3.1: why new medications are reported as counts and excluded from the primary outcome.

## 1. Agreement between the three extractors on the same plan

| Endpoint | Pair | Lin's CCC | Pearson r | Mean A | Mean B |
|---|---|---:|---:|---:|---:|
| medication | a vs b | 0.51 | 0.67 | $189 | $68 |
| medication | a vs c | 0.61 | 0.64 | $189 | $130 |
| medication | b vs c | 0.71 | 0.79 | $68 | $130 |
| diagnostic | a vs b | 0.76 | 0.77 | $166 | $198 |
| diagnostic | a vs c | 0.72 | 0.73 | $166 | $199 |
| diagnostic | b vs c | 0.83 | 0.83 | $198 | $199 |

Mean imputed medication cost per plan by extractor: A $189, B $68, C $130 — a threefold spread on identical plans.

## 2. Concentration

12 of 3131 distinct medication strings account for 53% of all imputed AI medication cost.

| Drug string | Orders | Total $ | Share | Imputed $/month (min–median–max) |
|---|---:|---:|---:|---|
| ruxolitinib | 4 | 44,000 | 13.5% | 8,000–12,000–12,000 |
| rasburicase | 3 | 21,000 | 6.4% | 5,000–8,000–8,000 |
| pegfilgrastim | 3 | 16,000 | 4.9% | 5,000–5,000–6,000 |
| ruxolitinib 10 mg twice daily | 1 | 12,000 | 3.7% | 12,000–12,000–12,000 |
| ruxolitinib 15 mg po bid | 1 | 12,000 | 3.7% | 12,000–12,000–12,000 |
| ruxolitinib 20 mg po twice daily | 1 | 12,000 | 3.7% | 12,000–12,000–12,000 |
| ruxolitinib 10 mg bid | 1 | 12,000 | 3.7% | 12,000–12,000–12,000 |
| pegfilgrastim or filgrastim | 2 | 10,000 | 3.1% | 5,000–5,000–5,000 |
| ruxolitinib 20 mg bid | 1 | 8,000 | 2.5% | 8,000–8,000–8,000 |
| ruxolitinib 10mg bid | 1 | 8,000 | 2.5% | 8,000–8,000–8,000 |
| lokelma | 1 | 8,000 | 2.5% | 8,000–8,000–8,000 |
| ruxolitinib 10 mg po bid | 1 | 8,000 | 2.5% | 8,000–8,000–8,000 |

## 3. Influence of individual cases

| Cases included | Mean difference $/visit | 95% CI |
|---|---:|---:|
| all 200 | 42 | -32 to 131 |
| dropping the 1 most influential | 13 | -47 to 85 |
| dropping the 3 most influential | -26 | -63 to 0 |
| dropping the 5 most influential | -5 | -17 to 8 |

The single most influential case (MTS_0041) accounts for 21% of the total absolute medication difference, and the sign of the estimate reverses once three of 200 cases are removed.

