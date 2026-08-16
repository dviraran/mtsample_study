# OpenEvidence — manual prompt worksheet (two additional prompts)

For each case below, **copy the prompt block** into OpenEvidence, then **paste the verbatim response** between the `RESPONSE_START`/`RESPONSE_END` markers. Do both prompts (A = parsimonious+safe, B = cost-aware) for each case. The default-prompt OpenEvidence plans already exist, so only these two are needed.

Tips: submit each prompt in a **fresh OpenEvidence conversation** (no carried context); paste the response exactly as returned (no edits).

---

## Case 1/10 — MTS_0449  ·  Emergency Room Reports

**Why this case:** Extreme over-ordering: ER pathologic-fracture workup, OpenEvidence ~$2.5k vs physician ~$309.

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** A 53-year-old female with a probable pathological fracture of the left proximal femur likely due to metastatic bone lesion from a history of malignant melanoma, requiring further imaging and oncology consultation.

- **Physician's diagnostic orders:** bone scan, repeat x-rays including AP pelvis, femur, hip including knee, left hip hemiarthroplasty versus calcar hemiarthroplasty, cemented type

- **OpenEvidence (default prompt) ordered:** Repeat radiographs: AP pelvis, full-length left femur, and left knee, CT chest/abdomen/pelvis with contrast for metastatic staging, MRI of the left femur and lumbar spine, Bone scan (whole body) for comprehensive skeletal survey, CBC, CMP, Coagulation studies, Type and screen, LDH, Alkaline phosphatase, Calcium, Phosphorus, Preoperative urinalysis, Preoperative ECG, Proximal femoral replacement surgery (tumor prosthesis/endoprosthetic reconstruction), Intraoperative tissue biopsy of lytic lesion for frozen section and permanent pathology (~$2513; physician ~$309)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
REASON FOR CONSULTATION: , Left hip fracture.,HISTORY OF PRESENT ILLNESS: , The patient is a pleasant 53-year-old female with a known history of sciatica, apparently presented to the emergency room due to severe pain in the left lower extremity and unable to bear weight.  History was obtained from the patient.  As per the history, she reported that she has been having back pain with left leg pain since past 4 weeks.  She has been using a walker for ambulation due to disabling pain in her left thigh and lower back.  She was seen by her primary care physician and was scheduled to go for MRI yesterday.  However, she was walking and her right foot got caught on some type of rug leading to place excessive weight on her left lower extremity to prevent her fall.  Since then, she was unable to ambulate.  The patient called paramedics and was brought to the emergency room.  She denied any history of fall.  She reported that she stepped the wrong way causing the pain to become worse.  She is complaining of severe pain in her lower extremity and back pain.  Denies any tingling or numbness.  Denies any neurological symptoms.  Denies any bowel or bladder incontinence.,X-rays were obtained which were remarkable for left hip fracture.  Orthopedic consultation was called for further evaluation and management.  On further interview with the patient, it is noted that she has a history of malignant melanoma, which was diagnosed approximately 4 to 5 years ago.  She underwent surgery at that time and subsequently, she was noted to have a spread to the lymphatic system and lymph nodes for which she underwent surgery in 3/2008.,PAST MEDICAL HISTORY: , Sciatica and melanoma.,PAST SURGICAL HISTORY:  ,As discussed above, surgery for melanoma and hysterectomy.,ALLERGIES: , NONE.,SOCIAL HISTORY: , Denies any tobacco or alcohol use.  She is divorced with 2 children.  She lives with her son.,PHYSICAL EXAMINATION:,GENERAL:  The patient is well developed, well nourished in mild distress secondary to left lower extremity and back pain.,MUSCULOSKELETAL:  Examination of the left lower extremity, there is presence of apparent shortening and external rotation deformity.  Tenderness to palpation is present.  Leg rolling is positive for severe pain in the left proximal hip.  Further examination of the spine is incomplete secondary to severe leg pain.  She is unable to perform a straight leg raising.  EHL/EDL 5/5.  2+ pulses are present distally.  Calf is soft and nontender.  Homans sign is negative.  Sensation to light touch is intact.,IMAGING:,  AP view of the hip is reviewed.  Only 1 limited view is obtained.  This is a poor quality x-ray with a lot of soft tissue shadow.  This x-ray is significant for basicervical-type femoral neck fracture.  Lesser trochanter is intact.  This is a high intertrochanteric fracture/basicervical.  There is presence of lytic lesion around the femoral neck, which is not well delineated on this particular x-ray.  We need to order repeat x-rays including AP pelvis, femur, and knee.,LABS:,  Have been reviewed.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0449 arm=parsimonious -->
### Assessment and Plan – Left Hip Fracture

**ASSESSMENT:**

53-year-old female with history of malignant melanoma (diagnosed 4–5 years ago with lymph node metastasis, surgery 3/2008) presenting with a basicervical/high intertrochanteric left femoral neck fracture with an associated lytic lesion on radiograph, in the setting of 4 weeks of progressive back pain with left leg pain (sciatica). No history of significant trauma — mechanism was simply shifting weight to the left leg.

**Three Most Likely Diagnoses:**

1. **Pathologic fracture of the left proximal femur through a metastatic melanoma deposit.** The combination of a lytic lesion at the femoral neck, a low-energy mechanism (no fall), and a known history of melanoma with prior lymph node metastasis makes metastatic disease the most likely etiology. Melanoma bone metastases are predominantly osteolytic (77% of cases) and the proximal femur is a common site.
2. **Spinal metastatic disease causing the 4-week history of progressive back pain and left-sided radiculopathy (sciatica).** The progressive, disabling back and leg pain preceding the fracture, in a patient with known metastatic melanoma, raises strong concern for concurrent vertebral/epidural metastatic disease. Radicular symptoms can result from nerve root compression by vertebral metastases or epidural tumor extension.
3. **Widely disseminated metastatic melanoma.** Given confirmed lymph node spread and now likely osseous metastasis at two sites (femur and possibly spine), systemic dissemination is probable. Staging is essential to guide both orthopedic and oncologic management.

**Can't-Miss Diagnoses:**

- **Metastatic spinal cord compression (MSCC) or cauda equina syndrome.** The 4-week history of progressive back pain with radiculopathy in a melanoma patient demands urgent evaluation. Although she currently denies bowel/bladder incontinence and has intact EHL/EDL strength, MSCC can progress rapidly to irreversible paraplegia if not identified and treated promptly.
- **Impending pathologic fracture of the contralateral femur or other weight-bearing bones.** Additional lytic lesions elsewhere could lead to further fractures perioperatively or during rehabilitation.

---

**PLAN:**

**1. Pathologic fracture of the left proximal femur (most likely metastatic melanoma):**

- Obtain AP pelvis, full-length left femur, and left knee radiographs (already ordered per note) to better characterize the lytic lesion, assess extent of bony involvement, and evaluate for additional femoral lesions.
- Surgical fixation is indicated — this is a completed pathologic femoral neck fracture. Given the femoral neck location and lytic destruction, **arthroplasty** (long-stem cemented hemiarthroplasty or proximal femoral replacement) is preferred over internal fixation, as pathologic femoral neck fractures do not heal reliably and arthroplasty provides immediate weight-bearing stability. Choice of implant (hemiarthroplasty vs. endoprosthetic reconstruction) should be guided by estimated survival and extent of bone loss; consult orthopedic oncology if available.
- Send intraoperative tissue for pathologic confirmation of metastatic melanoma at the time of surgery.
- Postoperative radiation therapy to the surgical site is recommended for local tumor control.
- Pain management: IV opioid analgesia for acute fracture pain; DVT prophylaxis per institutional protocol given immobility.

**2. Possible spinal metastatic disease / rule out MSCC:**

- **Urgent MRI of the entire spine** (with and without contrast) to evaluate for vertebral metastases, epidural disease, and spinal cord or cauda equina compression. This is the single most important diagnostic study to obtain and should be performed prior to or concurrent with surgical planning for the hip, as findings may alter the sequence of interventions.
- If MRI confirms spinal cord compression: initiate dexamethasone (10 mg IV bolus, then 4 mg IV q6h) and obtain urgent neurosurgical/radiation oncology consultation.
- If MRI shows vertebral metastases without cord compression: proceed with hip surgery first; spine can be addressed with radiation therapy postoperatively.

**3. Staging of metastatic melanoma:**

- CT chest/abdomen/pelvis with contrast and MRI brain to assess extent of systemic disease. These studies directly inform prognosis, survival estimation, and surgical decision-making (e.g., implant durability needs).
- LDH level.
- BRAF mutation testing on metastatic tissue (from femoral biopsy specimen) if not previously performed — this determines eligibility for targeted therapy (BRAF/MEK inhibitors) in addition to immunotherapy.
- Oncology consultation for systemic therapy planning (checkpoint inhibitor immunotherapy ± targeted therapy depending on BRAF status).

**4. Excluding can't-miss diagnoses:**

- MSCC: addressed by urgent spine MRI as above.
- Additional impending fractures: the AP pelvis and full femur films will screen the contralateral hip and bilateral femora. A bone scan or PET/CT (obtained as part of staging) will identify additional skeletal lesions at risk.

**5. Additional orders:**

- Type and screen (anticipate significant intraoperative blood loss given melanoma vascularity; consider preoperative embolization if large soft-tissue component identified on advanced imaging).
- Standard preoperative labs: CBC, BMP, coagulation studies.
- Strict non-weight-bearing on left lower extremity; bed rest with log-roll precautions pending spine MRI results.
- Social work consultation for discharge planning given limited home support.

**6. Follow-up:**

- Multidisciplinary tumor board discussion once staging is complete to coordinate orthopedic, radiation oncology, and medical oncology care.
- Postoperative rehabilitation planning contingent on spine MRI findings and overall disease burden.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
REASON FOR CONSULTATION: , Left hip fracture.,HISTORY OF PRESENT ILLNESS: , The patient is a pleasant 53-year-old female with a known history of sciatica, apparently presented to the emergency room due to severe pain in the left lower extremity and unable to bear weight.  History was obtained from the patient.  As per the history, she reported that she has been having back pain with left leg pain since past 4 weeks.  She has been using a walker for ambulation due to disabling pain in her left thigh and lower back.  She was seen by her primary care physician and was scheduled to go for MRI yesterday.  However, she was walking and her right foot got caught on some type of rug leading to place excessive weight on her left lower extremity to prevent her fall.  Since then, she was unable to ambulate.  The patient called paramedics and was brought to the emergency room.  She denied any history of fall.  She reported that she stepped the wrong way causing the pain to become worse.  She is complaining of severe pain in her lower extremity and back pain.  Denies any tingling or numbness.  Denies any neurological symptoms.  Denies any bowel or bladder incontinence.,X-rays were obtained which were remarkable for left hip fracture.  Orthopedic consultation was called for further evaluation and management.  On further interview with the patient, it is noted that she has a history of malignant melanoma, which was diagnosed approximately 4 to 5 years ago.  She underwent surgery at that time and subsequently, she was noted to have a spread to the lymphatic system and lymph nodes for which she underwent surgery in 3/2008.,PAST MEDICAL HISTORY: , Sciatica and melanoma.,PAST SURGICAL HISTORY:  ,As discussed above, surgery for melanoma and hysterectomy.,ALLERGIES: , NONE.,SOCIAL HISTORY: , Denies any tobacco or alcohol use.  She is divorced with 2 children.  She lives with her son.,PHYSICAL EXAMINATION:,GENERAL:  The patient is well developed, well nourished in mild distress secondary to left lower extremity and back pain.,MUSCULOSKELETAL:  Examination of the left lower extremity, there is presence of apparent shortening and external rotation deformity.  Tenderness to palpation is present.  Leg rolling is positive for severe pain in the left proximal hip.  Further examination of the spine is incomplete secondary to severe leg pain.  She is unable to perform a straight leg raising.  EHL/EDL 5/5.  2+ pulses are present distally.  Calf is soft and nontender.  Homans sign is negative.  Sensation to light touch is intact.,IMAGING:,  AP view of the hip is reviewed.  Only 1 limited view is obtained.  This is a poor quality x-ray with a lot of soft tissue shadow.  This x-ray is significant for basicervical-type femoral neck fracture.  Lesser trochanter is intact.  This is a high intertrochanteric fracture/basicervical.  There is presence of lytic lesion around the femoral neck, which is not well delineated on this particular x-ray.  We need to order repeat x-rays including AP pelvis, femur, and knee.,LABS:,  Have been reviewed.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0449 arm=costaware -->
### Assessment and Plan

ASSESSMENT:

1. Left basicervical/high intertrochanteric femoral neck fracture, likely pathologic — 53-year-old female presenting with acute inability to bear weight on the left lower extremity after a low-energy mechanism (stepping awkwardly to avoid a fall). Radiograph demonstrates a basicervical-type femoral neck fracture with an associated lytic lesion around the femoral neck. The clinical shortening and external rotation deformity are consistent with a displaced proximal femur fracture. Given her history of malignant melanoma with lymph node metastases (status post surgical resection in 2008), the lytic lesion is highly suspicious for metastatic melanoma to bone. The 4-week history of progressive left lower extremity and back pain preceding the fracture further supports an underlying pathologic process weakening the bone prior to fracture.
2. Concern for metastatic melanoma with osseous involvement — The combination of a known melanoma history with lymphatic spread, progressive pain in the left lower extremity and back over 4 weeks, and a lytic femoral neck lesion raises high concern for metastatic disease. Additional sites of bony or visceral metastasis must be evaluated.
3. Low back pain with left lower extremity radiculopathy — History of "sciatica" with progressive symptoms over 4 weeks. In the setting of possible metastatic melanoma, spinal metastasis with nerve root or epidural involvement must be excluded.

PLAN:

Imaging:

- Repeat radiographs: AP pelvis, full-length left femur (AP and lateral), and left knee to better characterize the fracture pattern, assess the extent of the lytic lesion, and evaluate for additional femoral lesions.
- CT chest/abdomen/pelvis with contrast for metastatic staging.
- Bone scan or PET/CT to evaluate for additional osseous metastases.
- MRI of the lumbar spine to evaluate for spinal metastases as the etiology of her progressive back and leg pain, and to rule out epidural disease.

Laboratory:

- CBC, CMP (including calcium), LDH, coagulation studies, type and screen (in preparation for surgery).
- SPEP/UPEP and serum free light chains to exclude multiple myeloma as an alternative diagnosis for the lytic lesion.

Surgical Planning:

- Given the location of the fracture (basicervical/femoral neck) with an associated lytic lesion, arthroplasty (long-stem cemented hemiarthroplasty or proximal femoral replacement) is the preferred surgical approach over internal fixation. Pathologic femoral neck fractures are best managed with arthroplasty, which provides immediate stability and durable weight-bearing capacity. The choice between hemiarthroplasty and endoprosthetic reconstruction will depend on the extent of bone destruction as further delineated on repeat imaging and estimated survival.
- Tissue from the lesion should be sent for pathologic analysis at the time of surgery to confirm the diagnosis.
- Preoperative optimization: correct any metabolic abnormalities (hypercalcemia), ensure adequate hemoglobin, type and crossmatch for anticipated blood loss.

Consultations:

- Medical oncology consultation for evaluation of metastatic melanoma, BRAF mutation testing (if not previously performed), and coordination of systemic therapy planning.
- Radiation oncology consultation for consideration of postoperative adjuvant radiation therapy to the surgical site.

Pain Management:

- Adequate analgesia with scheduled acetaminophen and opioids as needed for breakthrough pain.
- Maintain the left lower extremity in a position of comfort; strict non-weight-bearing precautions.

DVT Prophylaxis:

- Mechanical prophylaxis with sequential compression devices on the contralateral extremity.
- Pharmacologic prophylaxis per institutional protocol, balancing timing with planned surgery.

Follow-Up:

- Multidisciplinary discussion once staging workup is complete to finalize surgical approach and coordinate systemic and radiation therapy.
- Postoperative follow-up with orthopedic surgery and medical oncology.
<!-- RESPONSE_END -->


---

## Case 2/10 — MTS_0582  ·  Consult - History and Phy.

**Why this case:** Can't-miss: rapid dementia/ataxia/vision loss (CJD vs treatable autoimmune encephalitis). Physician ordered none; OE ordered 23 tests. Does parsimony still catch the dangerous workup?

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** A 32-year-old female presents with rapid and early onset dementia accompanied by ataxia, vision loss, and illusions, with no clear precipitating factors.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** Repeat lumbar puncture: autoimmune encephalitis panel (serum and CSF), CMP, CBC, TSH, Vitamin B12/folate/methylmalonic acid, Ceruloplasmin/24-hour urine copper, HIV, RPR, ANA, Anti-TPO, Lactate/pyruvate, Urine drug screen, Serum autoimmune panel, Repeat brain MRI with and without contrast, Prolonged video EEG monitoring, CT chest/abdomen/pelvis, Mammography, Pelvic ultrasound, PRNP gene sequencing (~$1668; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
REASON FOR CONSULT,:  Dementia.,HISTORY OF PRESENT ILLNESS:  ,The patient is a 33-year-old black female, referred to the hospital by a neurologist in Tyler, Texas for disorientation and illusions.  Symptoms started in June of 2006, when the patient complained of vision problems and disorientation.  The patient was seen wearing clothes inside out along with other unusual behaviors.  In August or September of 2006, the patient reported having a sudden onset of headaches, loss of vision, and talking sporadically without making any sense.  The patient sought treatment from an ophthalmologist.  We did not find any abnormality in the Behavior Center in Tyler, Texas.  The Behavior Center referred the patient to Dr. Abc, a neurologist in Tyler, who then referred the patient to this hospital.,According to the mother, the patient has had no past major medical or psychiatric illnesses.  The patient was functioning normally before June 2006, working as accounting tech after having completed 2 years of college.  She reports of worsening in symptoms, mainly unable to communicate about auditory or visual hallucinations or any symptoms of anxiety.  Currently, the patient lives with mother and requires her assistance to perform ADLs and the patient has become ataxic since November 2006.  Sleeping patterns and the amount is unknown.  Appetite is okay.,PAST PSYCHIATRIC HISTORY:,  The patient was diagnosed with severe depression in November 2006 at the Behavior Center in Tyler, Texas, where she was given Effexor.  She stopped taking it soon after, since they worsened her eye vision and balance.,PAST MEDICAL HISTORY: , In 2001 diagnosed with Meniere disease, was treated such that she could function normally in everyday activities including work.  No current medications.  Denies history of seizures, strokes, diabetes, hypertension, heart disease, or head injury.,FAMILY MEDICAL HISTORY:  ,Father's grandmother was diagnosed with Alzheimer disease in her 70s with symptoms similar to the patient described by the patient's mother.  Both, the mother's father and father's mother had "nervous breakdowns" but at unknown dates.,SOCIAL HISTORY: , The patient lives with a mother, who takes care of the patient's ADLs.  The patient completed school, up to two years in college and worked as accounting tech for eight years.  Denies use of alcohol, tobacco, or illicit drugs.,MENTAL STATUS EXAMINATION: , The patient is 33-year-old black female wearing clean clothes, a small towel on her head and over a wheel chair with her head rested on a pillow and towel.  Decreased motor activity, but did blink her eyes often, but arrhythmically.  Poor eye contact.  Speech illogic.  Concentration was not able to be assessed.  Mood is unknown.  Flat and constricted affect.  Thought content, thought process and perception could not be assessed.  Sensorial memory, information, intelligence, judgment, and insight could not be evaluated due to lack of communication by the patient.,MINI-MENTAL STATUS EXAM: , Unable to be performed.,AXIS I:  Rapidly progressing early onset of dementia, rule out dementia secondary to general medical condition, rule out dementia secondary to substance abuse.,AXIS II:  Deferred.,AXIS III:  Deferred.,AXIS IV:  Deferred.,AXIS V:  1.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0582 arm=parsimonious -->
## ASSESSMENT

**1. Autoimmune encephalitis (most likely anti-NMDA receptor encephalitis)**

This is the leading diagnosis given the patient's demographics (33-year-old woman), subacute onset of behavioral changes, progressive cognitive decline to near-mutism, visual/auditory hallucinations, and speech dysfunction — all evolving over approximately 6 months.[1] Anti-NMDAR encephalitis is the most common autoimmune encephalitis in women under 40 and classically presents with psychiatric symptoms progressing to cognitive dysfunction, speech deterioration, movement abnormalities, and decreased level of consciousness.[2][1] The development of ataxia and flat affect with loss of communication is consistent with this trajectory. Autoimmune encephalitis is the most common treatable cause of rapidly progressive dementia and must be identified early, as immunotherapy can dramatically alter outcomes.[3][4]

**2. Prion disease (Creutzfeldt-Jakob disease)**

The rapid progression from normal functioning to wheelchair-bound, nonverbal status over ~6 months, combined with visual symptoms, ataxia, and flat affect, is consistent with CJD.[5][6] Although sporadic CJD typically affects older adults (median onset ~65 years), rare cases occur in younger patients, and variant CJD specifically affects younger individuals. The combination of rapidly progressive dementia with cerebellar ataxia and visual disturbance is a classic CJD presentation.[5][7]

**3. Metabolic/genetic neurodegenerative disease**

Given the young age, family history of early-onset Alzheimer-like symptoms in a paternal great-grandmother, and prior Ménière disease (associated with increased risk of young-onset dementia), inherited conditions such as Niemann-Pick type C (dementia + ataxia + vertical gaze palsy), adult-onset leukodystrophy, or mitochondrial disease should be considered.[8][9][10] Early-onset familial Alzheimer disease (presenilin mutations) can present in the 30s with rapid decline.

**Can't-miss diagnoses:**

- **Anti-NMDAR encephalitis with occult ovarian teratoma** — treatable and potentially reversible; failure to diagnose leads to continued decline and death[1]
- **CNS infection** (HIV, neurosyphilis, progressive multifocal leukoencephalopathy) — treatable infectious causes must be excluded[11]
- **CNS lymphoma or paraneoplastic encephalitis** — occult malignancy driving a paraneoplastic syndrome can mimic this presentation[12][13]

---

## PLAN

**For autoimmune encephalitis (Diagnosis #1):**

- **MRI brain with contrast** (with DWI/FLAIR sequences) — essential first test; will also evaluate for CJD pattern (cortical ribboning, basal ganglia signal), structural lesions, and inflammatory changes[5][11]
- **EEG** — assess for extreme delta brush (suggestive of anti-NMDAR encephalitis), periodic sharp-wave complexes (CJD), or subclinical seizure activity[5][14][1]
- **Lumbar puncture** with cell count, protein, glucose, oligoclonal bands, and CSF sent for **anti-NMDAR antibodies** and autoimmune encephalitis antibody panel (CSF is more sensitive than serum for NMDAR antibodies)[1]
- **Pelvic ultrasound** to evaluate for ovarian teratoma, which is present in a substantial proportion of young women with anti-NMDAR encephalitis[1]
- If antibody results are delayed and clinical suspicion is high, consider empiric **high-dose IV methylprednisolone** as a diagnostic-therapeutic trial, given that autoimmune encephalitis is the most common treatable RPD etiology[13][15]

**For prion disease (Diagnosis #2):**

- MRI with DWI (ordered above) will evaluate for cortical ribboning and caudate/putamen restricted diffusion characteristic of CJD[5][7][16]
- EEG (ordered above) will assess for periodic sharp-wave complexes[5][6]
- CSF **14-3-3 protein** and **RT-QuIC assay** (real-time quaking-induced conversion) — RT-QuIC has very high sensitivity and specificity for prion disease and should be sent from the LP specimen[5][7][16]

**For metabolic/genetic disease (Diagnosis #3):**

- **Basic labs**: CBC, CMP, TSH, vitamin B12, folate[17][11]
- Defer genetic testing (e.g., presenilin, NPC1) pending MRI and LP results, as these are costly and the treatable diagnoses above take priority

**To exclude can't-miss diagnoses:**

- **HIV and RPR/VDRL** from serum — low cost, high yield to exclude treatable infections[11][18]
- Pelvic ultrasound (ordered above) addresses occult teratoma
- CT chest/abdomen/pelvis if paraneoplastic syndrome is suspected based on antibody results or imaging findings[13]

**Medications:**

- Hold all psychotropic medications pending workup; Effexor was previously discontinued
- Supportive care with assistance for ADLs; fall precautions given ataxia

**Follow-up:**

- Expedite MRI, EEG, and LP results; if autoimmune encephalitis antibodies return positive, initiate first-line immunotherapy (IV methylprednisolone, IVIG, or plasma exchange) without delay[3][15]
- Neurology consultation is already in place; ensure continuity for interpretation of specialized CSF biomarkers

---

Would you like to explore the specific immunotherapy protocols and expected timeline for treatment response in anti-NMDA receptor encephalitis?

Figure 2
MRI Findings in Antibody-Mediated Encephalitis.
Dalmau J, Graus F. Antibody-Mediated Encephalitis. The New England Journal of Medicine. 2018;378(9):840-851. doi:10.1056/NEJMra1708712.

Figure 1
Regional T2 Magnetic Resonance Imaging (MRI) Hyperintensities, Diffusion Restriction, and Contrast Uptake
Kelly MJ, Grant E, Murchison AG, et al. Magnetic Resonance Imaging Characteristics of LGI1-Antibody and CASPR2-Antibody Encephalitis. JAMA Neurology. 2024;81(5):525-533. doi:10.1001/jamaneurol.2024.0126.

Figure 1
Evaluation of cognitive impairment. Information from references 10–13.
Kramer ES, Johnson MN, Winslow B. Evaluation of Suspected Dementia. American Family Physician. 2025;112(6):657-667.

### References

1. An Update on Anti-Nmda Receptor Encephalitis for Neurologists and Psychiatrists: Mechanisms and Models. Dalmau J, Armangué T, Planagumà J, et al. The Lancet. Neurology. 2019;18(11):1045-1057. doi:10.1016/S1474-4422(19)30244-3.
2. Encephalitis. Binks SNM, Saylor D, Easton A, Thakur KT, Irani SR. Lancet (London, England). 2026;407(10542):1968-1983. doi:10.1016/S0140-6736(26)00363-6.
3. Autoimmune Encephalitis as Treatment-Responsive Cause of Rapidly Progressive Dementia: A Multicenter Prospective Cohort Study. van Steenhoven RW, Bastiaansen AEM, Kerstens J, et al. Neurology. 2026;106(11):e214933. doi:10.1212/WNL.0000000000214933.
4. The Evolving Etiologies of Rapidly Progressive Dementia: A Systematic Review. Lei MH, Cao LJ, Liu R, et al. Translational Psychiatry. 2025;:10.1038/s41398-025-03777-7. doi:10.1038/s41398-025-03777-7.
5. Biomarkers and Diagnostic Guidelines for Sporadic Creutzfeldt-Jakob Disease. Hermann P, Appleby B, Brandel JP, et al. The Lancet. Neurology. 2021;20(3):235-246. doi:10.1016/S1474-4422(20)30477-4.
6. Pearls & Oy-Sters: Rapidly Progressive Dementia: Prions or Immunomediated?. Cavallieri F, Mandrioli J, Tondelli M, et al. Neurology. 2014;82(17):e149-52. doi:10.1212/WNL.0000000000000354.
7. Laboratory Diagnosis of Creutzfeldt–Jakob Disease. Zerr I. The New England Journal of Medicine. 2022;386(14):1345-1350. doi:10.1056/NEJMra2119323.
8. Association of Young-Onset Dementia With Pre-Existing Peripheral Vestibular Disorders. Hung SH, Chang AH, Cheng YF, Lin HC, Chen CS. Journal of Alzheimer's Disease : JAD. 2024;101(2):603-610. doi:10.3233/JAD-240309.
9. The Diagnosis of Young-Onset Dementia. Rossor MN, Fox NC, Mummery CJ, Schott JM, Warren JD. The Lancet. Neurology. 2010;9(8):793-806. doi:10.1016/S1474-4422(10)70159-9.
10. Genetic testing in dementia‐A medical genetics perspective. Huq AJ, Sexton A, Lacaze P, et al. International Journal of Geriatric Psychiatry. 2021;36(8):1158-1170. doi:10.1002/gps.5535.
11. Clinical Reasoning: A 47-Year-Old Man With Diffuse White Matter Disease and Rapidly Progressive Dementia. Di Luca DG, Landman J, Ortega MR, Gultekin SH, Sun X. Neurology. 2019;92(24):e2832-e2837. doi:10.1212/WNL.0000000000007655.
12. Clinical Reasoning: A 54-Year-Old Woman With Dementia, Myoclonus, and Ataxia. Ali F, Murray JA, Adams AC, Flanagan EP. Neurology. 2017;89(2):e7-e12. doi:10.1212/WNL.0000000000004093.
13. Diagnostic Challenges in Rapidly Progressive Dementia. Zerr I, Hermann P. Expert Review of Neurotherapeutics. 2018;18(10):761-772. doi:10.1080/14737175.2018.1519397.
14. Acute Encephalitis in Immunocompetent Adults. Venkatesan A, Michael BD, Probasco JC, Geocadin RG, Solomon T. Lancet (London, England). 2019;393(10172):702-716. doi:10.1016/S0140-6736(18)32526-1.
15. Rapidly Progressive Dementias - Aetiologies, Diagnosis and Management. Hermann P, Zerr I. Nature Reviews. Neurology. 2022;18(6):363-376. doi:10.1038/s41582-022-00659-0.
16. Advances in Biomarkers for Diagnosis and Prognosis of Prion Diseases. Zerr I, Hermann P, Mok TH, Mead S. The Lancet. Neurology. 2026;25(2):195-205. doi:10.1016/S1474-4422(25)00406-5.
17. Evaluation of Suspected Dementia. Kramer ES, Johnson MN, Winslow B. American Family Physician. 2025;112(6):657-667.
18. Clinical Reasoning: A 59-Year-Old Man Who Became Lost in His Own Home. Mondon K, Beaufils E, Perrier D, Matysiak A, Hommet C. Neurology. 2010;74(16):e66-8. doi:10.1212/WNL.0b013e3181d9ed32.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
REASON FOR CONSULT,:  Dementia.,HISTORY OF PRESENT ILLNESS:  ,The patient is a 33-year-old black female, referred to the hospital by a neurologist in Tyler, Texas for disorientation and illusions.  Symptoms started in June of 2006, when the patient complained of vision problems and disorientation.  The patient was seen wearing clothes inside out along with other unusual behaviors.  In August or September of 2006, the patient reported having a sudden onset of headaches, loss of vision, and talking sporadically without making any sense.  The patient sought treatment from an ophthalmologist.  We did not find any abnormality in the Behavior Center in Tyler, Texas.  The Behavior Center referred the patient to Dr. Abc, a neurologist in Tyler, who then referred the patient to this hospital.,According to the mother, the patient has had no past major medical or psychiatric illnesses.  The patient was functioning normally before June 2006, working as accounting tech after having completed 2 years of college.  She reports of worsening in symptoms, mainly unable to communicate about auditory or visual hallucinations or any symptoms of anxiety.  Currently, the patient lives with mother and requires her assistance to perform ADLs and the patient has become ataxic since November 2006.  Sleeping patterns and the amount is unknown.  Appetite is okay.,PAST PSYCHIATRIC HISTORY:,  The patient was diagnosed with severe depression in November 2006 at the Behavior Center in Tyler, Texas, where she was given Effexor.  She stopped taking it soon after, since they worsened her eye vision and balance.,PAST MEDICAL HISTORY: , In 2001 diagnosed with Meniere disease, was treated such that she could function normally in everyday activities including work.  No current medications.  Denies history of seizures, strokes, diabetes, hypertension, heart disease, or head injury.,FAMILY MEDICAL HISTORY:  ,Father's grandmother was diagnosed with Alzheimer disease in her 70s with symptoms similar to the patient described by the patient's mother.  Both, the mother's father and father's mother had "nervous breakdowns" but at unknown dates.,SOCIAL HISTORY: , The patient lives with a mother, who takes care of the patient's ADLs.  The patient completed school, up to two years in college and worked as accounting tech for eight years.  Denies use of alcohol, tobacco, or illicit drugs.,MENTAL STATUS EXAMINATION: , The patient is 33-year-old black female wearing clean clothes, a small towel on her head and over a wheel chair with her head rested on a pillow and towel.  Decreased motor activity, but did blink her eyes often, but arrhythmically.  Poor eye contact.  Speech illogic.  Concentration was not able to be assessed.  Mood is unknown.  Flat and constricted affect.  Thought content, thought process and perception could not be assessed.  Sensorial memory, information, intelligence, judgment, and insight could not be evaluated due to lack of communication by the patient.,MINI-MENTAL STATUS EXAM: , Unable to be performed.,AXIS I:  Rapidly progressing early onset of dementia, rule out dementia secondary to general medical condition, rule out dementia secondary to substance abuse.,AXIS II:  Deferred.,AXIS III:  Deferred.,AXIS IV:  Deferred.,AXIS V:  1.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0582 arm=costaware -->

### Assessment and Plan – Rapidly Progressive Dementia

**ASSESSMENT:**

33-year-old woman with rapidly progressive cognitive and functional decline over approximately 6 months, progressing from visual disturbances and disorientation (June 2006) to incoherent speech, visual/auditory hallucinations, complete loss of functional independence, and ataxia (November 2006). She was previously high-functioning (employed as an accounting technician for 8 years). On examination, she is wheelchair-bound, nonverbal, with flat affect and inability to participate in cognitive testing (GAF = 1). Past medical history is notable for Meniere disease (2001, previously well-controlled) and a remote family history of Alzheimer disease in a paternal great-grandmother.

This presentation is most consistent with **rapidly progressive dementia (RPD)** in a young adult, defined as dementia developing within less than 1 year. The differential diagnosis is broad and includes several potentially treatable etiologies that must be urgently excluded:

1. **Autoimmune/antibody-mediated encephalitis** – Leading consideration given her age, sex, rapid progression, psychiatric/behavioral features, and visual symptoms. Anti-NMDA receptor encephalitis is particularly important to exclude in a young woman (associated with ovarian teratoma). Other autoimmune etiologies include LGI1, CASPR2, GFAP astrocytopathy, and Hashimoto encephalopathy.
2. **Prion disease (Creutzfeldt-Jakob disease)** – Rapidly progressive dementia with visual symptoms, ataxia, and behavioral changes is consistent, though sporadic CJD is uncommon at age 33.
3. **Wilson disease** – Must be excluded in any patient under 50 with unexplained neuropsychiatric decline. Can present with behavioral changes, dysarthria, ataxia, and psychiatric symptoms.
4. **Infectious etiologies** – HIV encephalopathy, neurosyphilis, progressive multifocal leukoencephalopathy, subacute sclerosing panencephalitis (SSPE).
5. **CNS neoplasm/paraneoplastic syndrome** – Gliomatosis cerebri, CNS lymphoma, or paraneoplastic limbic/brainstem encephalitis.
6. **Metabolic/toxic** – Vitamin B12 deficiency, thyroid disease, heavy metal toxicity, inborn errors of metabolism (e.g., mitochondrial disease, Niemann-Pick type C, metachromatic leukodystrophy).
7. **Neurodegenerative** – Early-onset Alzheimer disease or frontotemporal dementia (less likely given the rapidity of decline, but possible).

The prior diagnosis of "severe depression" with worsening on venlafaxine may have represented early misidentification of an organic encephalopathy as a primary psychiatric disorder.

---

**PLAN:**

**Neuroimaging:**

- MRI brain with and without gadolinium contrast (evaluate for cortical ribboning suggestive of CJD, mesial temporal signal changes of limbic encephalitis, white matter disease, mass lesion, hydrocephalus, or basal ganglia abnormalities suggestive of Wilson disease)

**Laboratory workup:**

- CBC, CMP, hepatic function panel, TSH, free T4
- Vitamin B12, folate, methylmalonic acid
- ESR, CRP
- HIV 1/2 antibody/antigen, RPR with reflex FTA-ABS
- Serum ceruloplasmin and 24-hour urine copper (Wilson disease screen)
- ANA, anti-TPO antibodies (Hashimoto encephalopathy)
- Serum autoimmune encephalitis panel (NMDA-R, LGI1, CASPR2, GFAP, AMPA, GABA-B antibodies)
- Serum paraneoplastic antibody panel (anti-Hu, anti-Yo, anti-Ri, anti-CV2/CRMP5, anti-amphiphysin, anti-Ma2)
- Heavy metals screen if clinically indicated
- Consider very long chain fatty acids, arylsulfatase A if metabolic leukodystrophy suspected

**Lumbar puncture:**

- CSF cell count, protein, glucose
- CSF autoimmune encephalitis antibody panel (NMDA-R IgG is most sensitive in CSF)
- CSF 14-3-3 protein and RT-QuIC (prion disease)
- CSF oligoclonal bands, IgG index
- CSF cytology
- CSF viral panel (HSV, VZV)
- CSF VDRL

**Electroencephalogram (EEG):**

- Routine EEG to evaluate for periodic sharp wave complexes (CJD), extreme delta brush (anti-NMDAR encephalitis), epileptiform activity, or subclinical seizures

**Ophthalmologic examination:**

- Slit-lamp exam for Kayser-Fleischer rings (Wilson disease)

**Additional imaging:**

- CT chest/abdomen/pelvis with contrast to evaluate for occult malignancy or ovarian teratoma (relevant if anti-NMDA receptor antibodies are positive)
- Pelvic ultrasound to screen for ovarian teratoma

**Consultations:**

- Neurology (primary service for RPD workup coordination)
- Ophthalmology (slit-lamp exam)
- Social work (caregiver support, disability resources)

**Medications:**

- No psychotropic medications at this time pending diagnostic workup; avoid medications that may confound the clinical picture
- Ensure safety precautions given wheelchair dependence and inability to communicate

**Follow-up:**

- Expedite workup given the possibility of treatable autoimmune encephalitis, where early immunotherapy is associated with improved outcomes
- If autoimmune encephalitis is confirmed or strongly suspected, initiate first-line immunotherapy (IV methylprednisolone and/or IVIG) in consultation with neurology
- Reassess after initial results return; if workup is unrevealing, consider FDG-PET, genetic testing, and possible brain biopsy
- Family meeting to discuss prognosis, goals of care, and the importance of identifying a treatable etiology
<!-- RESPONSE_END -->


---

## Case 3/10 — MTS_0239  ·  General Medicine

**Why this case:** Can't-miss oncologic: newly diagnosed high-risk acute leukemia; physician already worked up (~$676). Does parsimony preserve necessary induction workup?

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient has newly diagnosed high-risk acute lymphoblastic leukemia complicated by deep vein thrombosis requiring anticoagulation and probable chronic left epididymitis.

- **Physician's diagnostic orders:** bone marrow aspirate/biopsy, lumbar puncture using a #27-gauge pencil-tip needle, Doppler studies of the deep venous system

- **OpenEvidence (default prompt) ordered:** Bone marrow aspirate and biopsy with morphology, flow cytometry, and MRD characterization, Karyotype with G-banded metaphase chromosomes, FISH panel including BCR::ABL1, KMT2A rearrangements, Next-generation sequencing, Hepatitis B testing, Hepatitis C testing, HIV testing, Echocardiogram prior to anthracycline therapy, Scrotal ultrasound, Lumbar puncture with intrathecal chemotherapy, Central venous access device placement, Monitor antithrombin III levels during asparaginase therapy, Plan for IVC filter retrieval once DVT resolved, Transfusion support with leukoreduced/irradiated blood products (~$1204; physician ~$676)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT: , Newly diagnosed high-risk acute lymphoblastic leukemia; extensive deep vein thrombosis, right iliac vein and inferior vena cava (IVC), status post balloon angioplasty, and mechanical and pharmacologic thrombolysis following placement of a vena caval filter.,HISTORY OF PRESENT ILLNESS: , The patient was transferred here the evening of 02/23/2007 from Hospital with a new diagnosis of high-risk acute lymphoblastic leukemia based on confirmation by flow cytometry of peripheral blood lymphoblasts that afternoon.  History related to this illness probably dates back to October of 2006 when he had onset of swelling and discomfort in the left testicle with what he described as a residual "lump" posteriorly.  The left testicle has continued to be painful off and on since.  In early November, he developed pain in the posterior part of his upper right leg, which he initially thought was related to skateboarding and muscle strain.  Physical therapy was prescribed and the discomfort temporarily improved.  In December, he noted onset of increasing fatigue.  He used to work out regularly, lifting lifts, doing abdominal exercises, and playing basketball and found he did not have energy to pursue these activities.  He has lost 10 pounds since December and feels his appetite has decreased.  Night sweats and cough began in December, for which he was treated with a course of Augmentin.  However, both of these problems have continued.  He also began taking Accutane for persistent acne in December (this agent was stopped on 02/19/2007).  Despite increasing fatigue and lethargy, he continues his studies at University of Denver, has a biology major (he aspires to be an ophthalmologist).,The morning of 02/19/2007, he awakened with severe right inguinal and right lower quadrant pain.  He was seen in Emergency Room where it was noted that he had an elevated WBC of 18,000.  CT scan of the abdomen was obtained to rule out possible appendicitis and on that CT, a large clot in the inferior vena cava extending to the right iliac and femoral veins was found.  He promptly underwent appropriate treatment in interventional radiology with the above-noted angioplasty and placement of a vena caval filter followed by mechanical and pharmacologic thrombolysis.  Repeat ultrasound there on 02/20/2007 showed no evidence of deep venous thrombosis (DVT).  Continuous intravenous unfractionated heparin infusion was continued.  Because there was no obvious cause of this extensive thrombosis, occult malignancy was suspected.  Appropriate blood studies were obtained and he underwent a PET/CT scan as part of his diagnostic evaluation.  This study showed moderately increased diffuse bone marrow metabolic activity.  Because the WBC continued to rise and showed a preponderance of lymphocytes, the smear was reviewed by pathologist, Sheryl Asplund, M.D., and flow cytometry was performed on the peripheral blood.  These studies became available the afternoon of 02/23/2007, and confirmed the diagnosis of precursor-B acute lymphoblastic leukemia.  The patient was transferred here after stopping of the continuous infusion heparin and receiving a dose of Lovenox 60 mg subcutaneously for further diagnostic evaluation and management of the acute lymphoblastic leukemia (ALL).,ALLERGIES: , NO KNOWN DRUG ALLERGIES.  HE DOES SEEM TO REACT TO CERTAIN ADHESIVES.,CURRENT MEDICATIONS:  ,1.  Lovenox 60 mg subcutaneously q.12h. initiated.,2.  Coumadin 5 mg p.o., was administered on 02/19/2007 and 02/22/2007.,3.  Protonix 40 mg intravenous (IV) daily.,4.  Vicodin p.r.n.,5.  Levaquin 750 mg IV on 02/23/2007.,IMMUNIZATIONS: , Up-to-date.,PAST SURGICAL HISTORY:  ,The treatment of the thrombosis as noted above on 02/19/2007 and 02/20/2007.,FAMILY HISTORY:  ,Two half-brothers, ages 26 and 28, both in good health.  Parents are in good health.  A maternal great-grandmother had a deep venous thrombosis (DVT) of leg in her 40s.  A maternal great-uncle developed leukemia around age 50.  A maternal great-grandfather had bone cancer around age 80.  His paternal grandfather died of colon cancer at age 73, which he had had since age 68.  Adult-onset diabetes is present in distant relatives on both sides.,SOCIAL HISTORY:  ,The patient is a student at the University majoring in biology.  He lives in a dorm there.  His parents live in Breckenridge.  He admits to having smoked marijuana off and on with friends and drinking beer off and on as well.,REVIEW OF SYSTEMS: , He has had emesis off and on related to Vicodin and constipation since 02/19/2007, also related to pain medication.  He has had acne for about two years, which he describes as mild to moderate.  He denied shortness of breath, chest pain, hemoptysis, dyspnea, headaches, joint pains, rashes, except where he has had dressings applied, and extremity pain except for the right leg pain noted above.,PHYSICAL EXAMINATION:  ,GENERAL:  Alert, cooperative, moderately ill-appearing young man.,VITAL SIGNS:  At the time of admission, pulse was 94, respirations 20, blood pressure 120/62, temperature 98.7, height 171.5 cm, weight 63.04 kg, and pulse oximetry on room air 95%.,HAIR AND SKIN:  Mild facial acne.,HEENT:  Extraocular muscles (EOMs) intact.  Pupils equal, round, and reactive to light and accommodation (PERRLA), fundi normal.,CARDIOVASCULAR:  A 2/6 systolic ejection murmur (SEM), regular sinus rhythm (RSR).,LUNGS:  Clear to auscultation with an occasional productive cough.,ABDOMEN:  Soft with mild lower quadrant tenderness, right more so than left; liver and spleen each decreased 4 cm below their respective costal margins.,MUSCULOSKELETAL:  Mild swelling of the dorsal aspect of the right foot and distal right leg.  Mild tenderness over the prior catheter entrance site in the right popliteal fossa and mild tenderness over the right medial upper thigh.,GENITOURINARY:  Testicle exam disclosed no firm swelling with mild nondiscrete fullness in the posterior left testicle.,NEUROLOGIC:  Exam showed him to be oriented x4.  Normal fundi, intact cranial nerves II through XII with downgoing toes, symmetric muscle strength, and decreased patellar deep tendon reflexes (DTRs).,LABORATORY DATA:  ,White count 25,500 (26 neutrophils, 1 band, 7 lymphocytes, 1 monocyte, 1 myelocyte, 64 blasts), hemoglobin 13.3, hematocrit 38.8, and 312,000 platelets.  Electrolytes, BUN, creatinine, phosphorus, uric acid, AST, ALT, alkaline phosphatase, and magnesium were all normal.  LDH was elevated to 1925 units/L (upper normal 670), and total protein and albumin were both low at 6.2 and 3.4 g/dL respectively.  Calcium was also slightly low at 8.8 mg/dL.  Low molecular weight heparin test was low at 0.27 units/mL.  PT was 11.8, INR 1.2, and fibrinogen 374.  Urinalysis was normal.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0239 arm=parsimonious -->
**ASSESSMENT AND PLAN**

---

**ASSESSMENT:**

**Three Most Likely Diagnoses:**

1. **Precursor B-cell acute lymphoblastic leukemia (ALL), high-risk** — Confirmed by flow cytometry of peripheral blood showing 64% blasts with precursor-B immunophenotype. The patient is an AYA (adolescent/young adult) male with a several-month prodrome of fatigue, weight loss, night sweats, and hepatosplenomegaly. WBC 25,500 with 64% blasts, markedly elevated LDH (1925 U/L), and diffuse bone marrow metabolic activity on PET/CT are all consistent. The left testicular fullness raises concern for possible testicular extramedullary involvement, which occurs in a small percentage of ALL cases at diagnosis.[1][2]
2. **Cancer-associated extensive deep venous thrombosis (right iliac vein and IVC), status post mechanical/pharmacologic thrombolysis and IVC filter placement** — VTE is a well-recognized complication of ALL, occurring in 8–10% of cases, driven by the prothrombotic state of malignancy and potentially exacerbated by the Accutane (isotretinoin) use. The thrombosis has been acutely treated, but ongoing anticoagulation management will be complicated by anticipated chemotherapy-induced thrombocytopenia. The IVC filter is in situ and will need planned retrieval once sustained anticoagulation is feasible.[3][4]
3. **Tumor lysis syndrome risk (intermediate-to-high)** — LDH is markedly elevated at 1925 U/L (>2× ULN), with a WBC of 25,500 and hepatosplenomegaly indicating significant disease burden. Although current electrolytes, uric acid, and renal function are normal, the risk of TLS upon initiation of induction chemotherapy is substantial and requires prophylaxis.[5][6]

**Can't-Miss Diagnoses:**

- **Testicular germ cell tumor** — The patient is a young male with months of left testicular pain and posterior fullness. Although the clinical context strongly favors leukemic infiltration, a primary testicular germ cell tumor must be excluded, particularly given the age group. Scrotal ultrasound and serum tumor markers (AFP, beta-hCG, LDH) will clarify this.[1]
- **Philadelphia chromosome-positive ALL (Ph+ ALL)** — Ph+ status fundamentally changes treatment (addition of TKI) and must be determined urgently before initiating induction chemotherapy.[7][1]
- **CNS leukemia** — Present in 3–7% of ALL at diagnosis; missed CNS involvement leads to inadequate therapy and relapse. Lumbar puncture with intrathecal chemotherapy is required.[1]

---

**PLAN:**

**1. Precursor B-cell ALL — Diagnostic Completion and Induction Therapy**

- **Bone marrow aspirate and biopsy** (if not already performed): morphology, comprehensive flow cytometry, conventional karyotype, and FISH panel including BCR::ABL1, KMT2A rearrangements, and probes for hyperdiploidy/hypodiploidy. RT-PCR for BCR::ABL1 (with transcript size determination, p190 vs. p210) is essential to distinguish Ph+ from Ph− disease and guide regimen selection. Multigene panel testing for gene fusions and pathogenic variants is recommended per NCCN.[7][1]
- **Lumbar puncture with intrathecal chemotherapy** at time of first scheduled IT therapy per protocol to assess CNS status (CNS-1/2/3).[1]
- **Scrotal ultrasound** to evaluate the left testicular fullness and assess for leukemic infiltration vs. other pathology. Testicular disease at diagnosis that does not resolve after induction may require radiation (24 Gy).[1]
- **Serum tumor markers**: AFP, beta-hCG to exclude concurrent germ cell tumor (can't-miss diagnosis).
- **Echocardiogram** prior to anthracycline-based induction.[1]
- **Hepatitis B/C and HIV testing** per NCCN workup recommendations.[1]
- **Fertility counseling and sperm banking** — urgent, must occur before initiating chemotherapy.
- **Induction chemotherapy**: Once Ph status is confirmed, initiate appropriate regimen. For Ph-negative B-ALL in an AYA patient without substantial comorbidities, NCCN-preferred regimens include pediatric-inspired protocols such as **CALGB 10403** (daunorubicin, pegaspargase, prednisone, vincristine) or the **DFCI ALL regimen**. If Ph-positive, a TKI-based regimen is indicated. Enrollment in a clinical trial is preferred if available.[1]
- **Discontinue warfarin** — warfarin is not recommended for cancer-associated VTE; LMWH is preferred (see below).[8][4]
- **Discontinue Accutane** (already stopped 02/19) — confirm discontinuation given teratogenicity concerns with chemotherapy agents and potential thrombotic risk.

**2. Cancer-Associated DVT / IVC Filter Management**

- **Continue enoxaparin (LMWH)** at therapeutic dosing (1 mg/kg BID) as the preferred anticoagulant for cancer-associated VTE. The current dose of 60 mg q12h is appropriate for his weight of 63 kg.[8]
- **Discontinue warfarin** — LMWH is preferred over vitamin K antagonists in cancer-associated thrombosis per NCCN and ITAC guidelines.[8][4]
- **Anticoagulation adjustment during chemotherapy-induced thrombocytopenia** per NCCN guidelines:[4]
  - Platelets >50,000/μL: full-dose enoxaparin (1 mg/kg BID)
  - Platelets 25,000–50,000/μL: half-dose enoxaparin (0.5 mg/kg BID)
  - Platelets [4][9]
- **Minimum 6 months of anticoagulation**, and indefinitely while cancer is active.[4][8]

**3. Tumor Lysis Syndrome Prophylaxis**

- **Aggressive IV hydration**: 1.5–2× maintenance without potassium.[5]
- **Rasburicase** (single dose 0.2 mg/kg, max 6 mg) prior to initiating chemotherapy, given LDH >2× ULN indicating high risk. Screen for G6PD deficiency if feasible, though treatment should not be delayed if G6PD status is unknown and TLS risk is high.[5]
- **Monitor TLS labs** (potassium, phosphorus, calcium, uric acid, creatinine) every 6–8 hours from admission through the initial days of induction.[5]
- **Allopurinol** can be started after rasburicase effect for ongoing uric acid control.[5]

**4. Excluding Can't-Miss Diagnoses**

- **Ph+ ALL**: BCR::ABL1 RT-PCR and FISH (ordered above) — result needed urgently before or concurrent with induction start.[7]
- **Testicular germ cell tumor**: Scrotal ultrasound + AFP/beta-hCG (ordered above).[1]
- **CNS leukemia**: Lumbar puncture with IT chemotherapy (ordered above).[1]

**5. Supportive Care and Follow-Up**

- **Protonix** (pantoprazole) — continue for GI prophylaxis during corticosteroid therapy.
- **Discontinue Vicodin** — transition to non-hepatotoxic analgesic given upcoming chemotherapy; avoid excessive acetaminophen.
- **Psychosocial support** and counseling — young college student facing a life-altering diagnosis; social work and psychology referral.
- **AYA-specific counseling**: cessation of marijuana and alcohol use during treatment.[5]
- **Transfer/referral consideration**: NCCN recommends that ALL patients be evaluated and treated at specialized centers. If this facility lacks the resources for intensive ALL induction, transfer to a center with hematologic malignancy expertise should be arranged.[1]

---

Would you like to explore the specific cytogenetic and molecular risk stratification categories for B-ALL and how they influence the decision between consolidation with blinatumomab versus allogeneic transplant in first remission?

ALL-D-14
Acute Lymphoblastic Leukemia: Ph-Negative B-ALL Frontline Induction Components — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 43 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-D-17
Acute Lymphoblastic Leukemia: Principles of Systemic Therapy - Ph-Negative B-ALL Frontline Consolidation Regimens — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 46 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-D-13
Acute Lymphoblastic Leukemia: Principles of Systemic Therapy - Ph-Negative B-ALL Frontline Induction Regimens — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 42 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-D-6
Acute Lymphoblastic Leukemia: Ph-Positive B-ALL Frontline Induction Regimens — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 35 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-D-19
Acute Lymphoblastic Leukemia: Ph-Negative B-ALL Frontline Consolidation Components Footnotes — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 48 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-5
Ph- B-ALL: Treatment Induction, Consolidation Therapy, and Post-Remission Management — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 17 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

PEDALL-1
DIAGNOSIS — NCCN Guidelines® — Pediatric Acute Lymphoblastic Leukemia p. 11 (v1.2026)
National Comprehensive Cancer Network. Pediatric Acute Lymphoblastic Leukemia.

ALL-1
Acute Lymphoblastic Leukemia: Diagnosis — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 10 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

ALL-2
Acute Lymphoblastic Leukemia: Cytogenetic and Molecular Prognostic Risk Stratification for B-ALL — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 12 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

PEDALL-B
Pediatric Acute Lymphoblastic Leukemia: Genetic Risk Groups for B-ALL — NCCN Guidelines® — Pediatric Acute Lymphoblastic Leukemia p. 29 (v1.2026)
National Comprehensive Cancer Network. Pediatric Acute Lymphoblastic Leukemia.

BLAST-1
Lymphoblastic Lymphoma: Additional Diagnostic Testing and Workup — NCCN Guidelines® — B-Cell Lymphomas p. 106 (v3.2026)
National Comprehensive Cancer Network. B-Cell Lymphomas.

ALL-3
Acute Lymphoblastic Leukemia: Workup and ALL Subtype Classification — NCCN Guidelines® — Acute Lymphoblastic Leukemia p. 14 (v1.2026)
National Comprehensive Cancer Network. Acute Lymphoblastic Leukemia.

### References

1. Acute Lymphoblastic Leukemia. National Comprehensive Cancer Network. Updated 2026-04-08.
2. Testicular Involvement of Acute Lymphoblastic Leukemia in Children and Adolescents: Diagnosis, Biology, and Management. Nguyen HTK, Terao MA, Green DM, Pui CH, Inaba H. Cancer. 2021;127(17):3067-3081. doi:10.1002/cncr.33609.
3. Direct Oral Anticoagulants for Cancer‐Associated Venous Thromboembolism in Hematologic Malignancies: A Comprehensive Review. Zhu Y, Xu C, Chen Z, et al. European Journal of Haematology. 2026;116(5):512-521. doi:10.1111/ejh.70130.
4. Cancer-Associated Venous Thromboembolic Disease. National Comprehensive Cancer Network. Updated 2026-05-05.
5. Pediatric Acute Lymphoblastic Leukemia. National Comprehensive Cancer Network. Updated 2025-08-11.
6. Tumor Lysis Syndrome in Patients With Hematological Malignancies. Belay Y, Yirdaw K, Enawgaw B. Journal of Oncology. 2017;2017:9684909. doi:10.1155/2017/9684909.
7. Initial Diagnostic Work-Up of Acute Leukemia: ASCO Clinical Practice Guideline Endorsement of the College of American Pathologists and American Society of Hematology Guideline. de Haas V, Ismaila N, Advani A, et al. Journal of Clinical Oncology : Official Journal of the American Society of Clinical Oncology. 2019;37(3):239-253. doi:10.1200/JCO.18.01468.
8. 2022 International Clinical Practice Guidelines for the Treatment and Prophylaxis of Venous Thromboembolism in Patients With Cancer, Including Patients With COVID-19. Farge D, Frere C, Connors JM, et al. The Lancet. Oncology. 2022;23(7):e334-e347. doi:10.1016/S1470-2045(22)00160-7.
9. 2019 International Clinical Practice Guidelines for the Treatment and Prophylaxis of Venous Thromboembolism in Patients With Cancer. Farge D, Frere C, Connors JM, et al. The Lancet. Oncology. 2019;20(10):e566-e581. doi:10.1016/S1470-2045(19)30336-5.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT: , Newly diagnosed high-risk acute lymphoblastic leukemia; extensive deep vein thrombosis, right iliac vein and inferior vena cava (IVC), status post balloon angioplasty, and mechanical and pharmacologic thrombolysis following placement of a vena caval filter.,HISTORY OF PRESENT ILLNESS: , The patient was transferred here the evening of 02/23/2007 from Hospital with a new diagnosis of high-risk acute lymphoblastic leukemia based on confirmation by flow cytometry of peripheral blood lymphoblasts that afternoon.  History related to this illness probably dates back to October of 2006 when he had onset of swelling and discomfort in the left testicle with what he described as a residual "lump" posteriorly.  The left testicle has continued to be painful off and on since.  In early November, he developed pain in the posterior part of his upper right leg, which he initially thought was related to skateboarding and muscle strain.  Physical therapy was prescribed and the discomfort temporarily improved.  In December, he noted onset of increasing fatigue.  He used to work out regularly, lifting lifts, doing abdominal exercises, and playing basketball and found he did not have energy to pursue these activities.  He has lost 10 pounds since December and feels his appetite has decreased.  Night sweats and cough began in December, for which he was treated with a course of Augmentin.  However, both of these problems have continued.  He also began taking Accutane for persistent acne in December (this agent was stopped on 02/19/2007).  Despite increasing fatigue and lethargy, he continues his studies at University of Denver, has a biology major (he aspires to be an ophthalmologist).,The morning of 02/19/2007, he awakened with severe right inguinal and right lower quadrant pain.  He was seen in Emergency Room where it was noted that he had an elevated WBC of 18,000.  CT scan of the abdomen was obtained to rule out possible appendicitis and on that CT, a large clot in the inferior vena cava extending to the right iliac and femoral veins was found.  He promptly underwent appropriate treatment in interventional radiology with the above-noted angioplasty and placement of a vena caval filter followed by mechanical and pharmacologic thrombolysis.  Repeat ultrasound there on 02/20/2007 showed no evidence of deep venous thrombosis (DVT).  Continuous intravenous unfractionated heparin infusion was continued.  Because there was no obvious cause of this extensive thrombosis, occult malignancy was suspected.  Appropriate blood studies were obtained and he underwent a PET/CT scan as part of his diagnostic evaluation.  This study showed moderately increased diffuse bone marrow metabolic activity.  Because the WBC continued to rise and showed a preponderance of lymphocytes, the smear was reviewed by pathologist, Sheryl Asplund, M.D., and flow cytometry was performed on the peripheral blood.  These studies became available the afternoon of 02/23/2007, and confirmed the diagnosis of precursor-B acute lymphoblastic leukemia.  The patient was transferred here after stopping of the continuous infusion heparin and receiving a dose of Lovenox 60 mg subcutaneously for further diagnostic evaluation and management of the acute lymphoblastic leukemia (ALL).,ALLERGIES: , NO KNOWN DRUG ALLERGIES.  HE DOES SEEM TO REACT TO CERTAIN ADHESIVES.,CURRENT MEDICATIONS:  ,1.  Lovenox 60 mg subcutaneously q.12h. initiated.,2.  Coumadin 5 mg p.o., was administered on 02/19/2007 and 02/22/2007.,3.  Protonix 40 mg intravenous (IV) daily.,4.  Vicodin p.r.n.,5.  Levaquin 750 mg IV on 02/23/2007.,IMMUNIZATIONS: , Up-to-date.,PAST SURGICAL HISTORY:  ,The treatment of the thrombosis as noted above on 02/19/2007 and 02/20/2007.,FAMILY HISTORY:  ,Two half-brothers, ages 26 and 28, both in good health.  Parents are in good health.  A maternal great-grandmother had a deep venous thrombosis (DVT) of leg in her 40s.  A maternal great-uncle developed leukemia around age 50.  A maternal great-grandfather had bone cancer around age 80.  His paternal grandfather died of colon cancer at age 73, which he had had since age 68.  Adult-onset diabetes is present in distant relatives on both sides.,SOCIAL HISTORY:  ,The patient is a student at the University majoring in biology.  He lives in a dorm there.  His parents live in Breckenridge.  He admits to having smoked marijuana off and on with friends and drinking beer off and on as well.,REVIEW OF SYSTEMS: , He has had emesis off and on related to Vicodin and constipation since 02/19/2007, also related to pain medication.  He has had acne for about two years, which he describes as mild to moderate.  He denied shortness of breath, chest pain, hemoptysis, dyspnea, headaches, joint pains, rashes, except where he has had dressings applied, and extremity pain except for the right leg pain noted above.,PHYSICAL EXAMINATION:  ,GENERAL:  Alert, cooperative, moderately ill-appearing young man.,VITAL SIGNS:  At the time of admission, pulse was 94, respirations 20, blood pressure 120/62, temperature 98.7, height 171.5 cm, weight 63.04 kg, and pulse oximetry on room air 95%.,HAIR AND SKIN:  Mild facial acne.,HEENT:  Extraocular muscles (EOMs) intact.  Pupils equal, round, and reactive to light and accommodation (PERRLA), fundi normal.,CARDIOVASCULAR:  A 2/6 systolic ejection murmur (SEM), regular sinus rhythm (RSR).,LUNGS:  Clear to auscultation with an occasional productive cough.,ABDOMEN:  Soft with mild lower quadrant tenderness, right more so than left; liver and spleen each decreased 4 cm below their respective costal margins.,MUSCULOSKELETAL:  Mild swelling of the dorsal aspect of the right foot and distal right leg.  Mild tenderness over the prior catheter entrance site in the right popliteal fossa and mild tenderness over the right medial upper thigh.,GENITOURINARY:  Testicle exam disclosed no firm swelling with mild nondiscrete fullness in the posterior left testicle.,NEUROLOGIC:  Exam showed him to be oriented x4.  Normal fundi, intact cranial nerves II through XII with downgoing toes, symmetric muscle strength, and decreased patellar deep tendon reflexes (DTRs).,LABORATORY DATA:  ,White count 25,500 (26 neutrophils, 1 band, 7 lymphocytes, 1 monocyte, 1 myelocyte, 64 blasts), hemoglobin 13.3, hematocrit 38.8, and 312,000 platelets.  Electrolytes, BUN, creatinine, phosphorus, uric acid, AST, ALT, alkaline phosphatase, and magnesium were all normal.  LDH was elevated to 1925 units/L (upper normal 670), and total protein and albumin were both low at 6.2 and 3.4 g/dL respectively.  Calcium was also slightly low at 8.8 mg/dL.  Low molecular weight heparin test was low at 0.27 units/mL.  PT was 11.8, INR 1.2, and fibrinogen 374.  Urinalysis was normal.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0239 arm=costaware -->
### Assessment and Plan

ASSESSMENT:

1. Precursor B-cell acute lymphoblastic leukemia (ALL), newly diagnosed, high-risk

This young adult male presents with a several-month prodrome of fatigue, weight loss, night sweats, and decreased appetite, now with a WBC of 25,500 with 64% circulating blasts confirmed as precursor-B ALL by flow cytometry. Markedly elevated LDH (1,925 U/L, nearly 3x ULN) and hepatosplenomegaly (liver and spleen each 4 cm below costal margins) indicate significant disease burden. PET/CT showing diffuse bone marrow metabolic activity is consistent with extensive marrow involvement. The left testicular fullness raises concern for possible extramedullary (testicular) involvement. This is classified as high-risk given the age (AYA), elevated WBC, and markedly elevated LDH.

2. Extensive deep venous thrombosis, right iliac vein and IVC, status post IVC filter placement, balloon angioplasty, and mechanical/pharmacologic thrombolysis

The extensive DVT is likely multifactorial: cancer-associated hypercoagulability (ALL itself), possible contribution from asparaginase-related coagulopathy once treatment begins, and a possible underlying inherited thrombophilia (family history of DVT in maternal great-grandmother). The thrombosis has been treated with successful thrombolysis and IVC filter placement. Currently on enoxaparin 60 mg SC q12h and has received two doses of warfarin. Warfarin should be discontinued given the upcoming need for chemotherapy with anticipated thrombocytopenia; LMWH is the preferred anticoagulant in this setting.

3. Tumor lysis syndrome risk — high

LDH >2x ULN (1,925 U/L), elevated WBC with high blast percentage, and hepatosplenomegaly place this patient at high risk for TLS with initiation of chemotherapy.

PLAN:

Problem 1: Precursor B-ALL — Diagnostic Workup and Treatment Planning

Diagnostic studies (urgent):

- Bone marrow aspirate and biopsy with:
  - Morphologic assessment
  - Comprehensive flow cytometric immunophenotyping (including baseline MRD characterization)
  - Conventional cytogenetics (karyotype)
  - FISH panel (BCR::ABL1, KMT2A rearrangements, ETV6::RUNX1, iAMP21, trisomy 4/10, CDKN2A deletion, CRLF2 rearrangements)
  - RT-PCR for BCR::ABL1 (quantitative, with transcript size determination p190 vs p210)
  - Multigene panel testing for gene fusions and pathogenic variants (including Ph-like ALL evaluation)
- Lumbar puncture with intrathecal chemotherapy at time of first scheduled IT therapy (defer if platelet count inadequate; coordinate with initiation of induction)
- Scrotal ultrasound to evaluate left testicular fullness and rule out testicular involvement
- Echocardiogram (baseline cardiac function prior to anthracycline-based therapy)
- Hepatitis B and C serologies, HIV testing
- TPMT and NUDT15 pharmacogenomic testing
- G6PD testing (prior to potential rasburicase use)
- Fertility counseling and sperm banking prior to initiation of chemotherapy

Treatment planning:

- This patient falls within the AYA age group. Per NCCN guidelines, preferred induction regimens for Ph-negative B-ALL in AYA patients without substantial comorbidities include pediatric-inspired regimens such as CALGB 10403 or DFCI ALL regimen. Treatment selection will depend on cytogenetic/molecular results, particularly BCR::ABL1 status.
- Initiate a corticosteroid prephase (e.g., prednisone or dexamethasone for 3–7 days) to begin cytoreduction while awaiting final molecular characterization and to reduce TLS risk.
- Place central venous access device (implanted port preferred given concurrent anticoagulation needs).
- Discuss clinical trial enrollment.
- Counseling on cessation of marijuana and alcohol use.
- Early transplant evaluation and donor search to be considered once risk stratification is complete.

Problem 2: DVT / Anticoagulation Management

- Discontinue warfarin. LMWH (enoxaparin) is the preferred anticoagulant for cancer-associated VTE, particularly during chemotherapy when thrombocytopenia is anticipated.
- Continue enoxaparin 1 mg/kg (approximately 60 mg) SC q12h as therapeutic anticoagulation. Adjust dose based on platelet counts per NCCN guidelines:
  - Platelets >50,000: full-dose enoxaparin
  - Platelets 25,000–50,000: half-dose enoxaparin (0.5 mg/kg q12h)
  - Platelets 2x ULN and high disease burden, administer rasburicase 0.2 mg/kg IV x1 dose prior to initiation of chemotherapy (confirm G6PD status; if unavailable, benefit likely outweighs risk given high TLS risk).
- Monitor TLS labs (potassium, calcium, phosphorus, uric acid, creatinine, LDH) every 6–8 hours from admission through initial cytoreduction.
- Ensure uric acid samples are placed on ice if rasburicase has been administered.

Supportive Care:

- Continue pantoprazole 40 mg IV daily (GI prophylaxis during steroid therapy).
- Discontinue Vicodin; transition to non-hepatotoxic analgesic (e.g., oxycodone) if needed for pain control. Initiate bowel regimen in anticipation of vincristine.
- Confirm Accutane (isotretinoin) has been discontinued (teratogenic, hepatotoxic, and potential drug interactions with chemotherapy).
- Levofloxacin — assess need for continued antibiotic prophylaxis per institutional protocol.
- Leukoreduced and irradiated blood products for all transfusions.

Follow-up:

- Daily assessment during induction hospitalization.
- Molecular/cytogenetic results expected within 5–14 days; finalize risk stratification and treatment protocol at that time.
- Multidisciplinary discussion with hematology/oncology, interventional radiology (IVC filter management), and social work (AYA support, academic accommodations).
<!-- RESPONSE_END -->


---

## Case 4/10 — MTS_0481  ·  Emergency Room Reports

**Why this case:** Defensive in peds ER: 2-month-old with bronchiolitis; physician ordered none, OE ~$1.1k.

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** A 2-month-old female presents with bronchiolitis, currently managed with aggressive suctioning and supplemental oxygen as needed, without respiratory treatments, and will be closely monitored due to a family history of reactive airway disease.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** Monitor respiratory status, Monitor hydration, Monitor feeding tolerance, Gentle nasal suctioning as needed, Initiate nasogastric tube feeds, Monitor intake/output, Monitor daily weights, Daily reassessment (~$1082; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT: , Increased work of breathing.,HISTORY OF PRESENT ILLNESS: , The patient is a 2-month-old female with a 9-day history of illness.  Per mom's report, the illness started 9 days ago with a dry cough.  The patient was eating normal up until approximately three days ago.  Mom was using a vaporizer at night, which she feels to have helped.  The patient's cough gradually worsened and three days ago, the patient had a significant increasing cough.  At that time, the patient also had significant increasing congestion.  Two days ago the patient was taken to the primary care physician's office and the patient was given Xopenex 2 puffs every 4 to 6 hours for home regimen, but this per mom's report, did not help the patient's symptoms.  On Wednesday evening, the patient's congestion and work of breathing increased and the patient was gagging after feedings.  The patient was brought to Children's Hospital Emergency Room at which time the patient was evaluated.  A chest x-ray was obtained and was noted to be normal.  The patient's saturations were noted to be normal and the patient was discharged home.  Last night, the patient was having multiple episodes of emesis after feedings with coughing and today was noted to have decreasing activity.  The patient had a 101 temperature on Wednesday evening, but has had no true fevers.  The patient has had a mild decrease in urine output today and secondary to the persistent increased work of breathing, coughing, and posttussive emesis, the patient was brought to Children's Hospital for reevaluation.,REVIEW OF SYSTEMS: , The remainder of the review of system is otherwise negative, all systems being reviewed, outside of pertinent positives as stated above.,ALLERGIES:,  NO KNOWN DRUG ALLERGIES.,MEDICATIONS:  ,As above.,IMMUNIZATIONS:,  None.,PAST MEDICAL HISTORY:  ,No hospitalizations.  No surgeries.,BIRTH HISTORY: , The patient was born to a G8, P2, A6 mom via normal spontaneous vaginal delivery.  Birth weight 6 pounds 12 ounces.  Mom stated she had a uterine infection during her pregnancy and at the time of delivery, but the patient was only in the hospital for 24 hours with mom after delivery.  The patient was full term and mom was noted to have gestational diabetes controlled with diet during her pregnancy.,FAMILY HISTORY: , Brother, mother, and father all have asthma.  Mom was noted to have gestational diabetes.,SOCIAL HISTORY: , The patient lives with mother, father, and a brother.  There is one bird.  There are smokers in the household.  There are sick contacts.,PHYSICAL EXAMINATION:,VITAL SIGNS:  Temperature is 97.7 and pulse is 181, but the patient is fussy.  Respiratory rate ranged between 36 and 44.  The patient is saturating 100% on one-half liter and 89% on room air.,GENERAL APPEARANCE:  Nontoxic child, but with increased work of breathing.  No respiratory distress.,HEENT:  Head is normocephalic and atraumatic.  Anterior fontanelle flat.  Pupils are equal, round, and reactive to light bilaterally.  Tympanic membranes are clear bilaterally.  Nares are congested.  Mucous membranes are moist without erythema.,NECK:  Supple.  No lymphadenopathy.,CHEST:  Exhibits symmetric expansion and retractions.,LUNGS:  The patient has diffuse crackles bilaterally, but no wheezes, rales, or rhonchi.,CARDIOVASCULAR:  Heart has a 2/6 vibratory systolic ejection murmur, best heard over the left sternal boarder.,ABDOMEN:  Soft, nondistended, and nondistended.  Good bowel sounds noted in all 4 quadrants.,GU:  Normal female.  No discharge or erythema.,BACK:  Normal with a normal curvature.,EXTREMITIES:  A 2+ pulses in the bilateral upper lower extremities.  No evidence of clubbing, cyanosis, or edema.  Capillary refill less than 3 seconds.,LABORATORY DATA: , Labs in the emergency room include a CBC, which showed a white blood cell count of 20.8 with a hemoglobin of 10.7, hematocrit of 31.3 with platelet count of 715,000 with 40% neutrophils, 2 bands, and 70% monocytes.  A urinalysis obtained in the emergency room was noted to be negative.  CRP was noted to be 2.0.  The chest x-ray, reviewed by myself in the emergency room, showed no significant change from previous x-ray, but the patient does has some bronchial wall thickening.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0481 arm=parsimonious -->

## ASSESSMENT

**1. Acute viral bronchiolitis** (most likely)

This 2-month-old presents with a 9-day progressive cough illness beginning with upper respiratory symptoms, now with diffuse bilateral crackles, retractions, hypoxemia (89% on room air), bronchial wall thickening on chest x-ray, and sick contacts in the household. The clinical course — URI prodrome progressing to lower respiratory tract involvement with peak severity around days 5–9 — is classic for bronchiolitis.[1][2] The reactive thrombocytosis (platelet count 715,000) is consistent with secondary thrombocythemia seen in infant respiratory viral infections.[3] The CRP of 2.0 and absence of focal consolidation argue against bacterial pneumonia. Bronchodilators (Xopenex) were appropriately ineffective, as expected in bronchiolitis.[4]

**2. Pertussis**

This diagnosis warrants strong consideration given the patient's **unvaccinated** status, 9-day progressive paroxysmal cough with posttussive emesis, leukocytosis (WBC 20.8), and sick contacts.[5][6][7] Classic pertussis in young infants presents with a deceptively well-appearing child with progressive cough, gagging, and vomiting; leukocytosis with lymphocytosis is characteristic, though the differential here shows monocyte predominance rather than lymphocytosis.[5] The CDC clinical case definition includes cough illness with posttussive vomiting in infants [8] Pertussis in infants [9]

**3. Bacterial superinfection complicating viral bronchiolitis**

The worsening clinical trajectory despite 9 days of illness, leukocytosis with bandemia (2% bands), and posttussive emesis raise concern for secondary bacterial pneumonia or other bacterial infection superimposed on a viral illness.[2] However, the low CRP (2.0), negative urinalysis, absence of focal consolidation on chest x-ray, and nontoxic appearance make this less likely.

**Can't-miss diagnoses:**

- **Pertussis** — already listed above but bears emphasis as a can't-miss given the unvaccinated status, age [10][5][7]
- **Sepsis/serious bacterial infection** — although the infant appears nontoxic with a low CRP and negative urinalysis, age [11][12]
- **Congenital heart disease** — the 2/6 systolic murmur is likely an innocent vibratory murmur given its character, but in the setting of tachycardia, hypoxemia, and feeding difficulty, hemodynamically significant heart disease should be considered.[2]

---

## PLAN

**For bronchiolitis (primary working diagnosis):**

- **Admit to hospital** — multiple criteria for hospitalization are met: age ≤2 months (OR 2.1 for requiring increased respiratory support), oxygen saturation 89% on room air, retractions, and poor feeding with posttussive emesis.[4][13]
- **Supplemental oxygen** via nasal cannula to maintain SpO₂ ≥90% (currently on 0.5L with SpO₂ 100%; wean as tolerated).[14][1]
- **Supportive care**: gentle nasal suctioning before feeds; ensure adequate hydration — if oral intake remains poor with continued posttussive emesis, initiate **nasogastric or IV fluids**.[4][15]
- **Discontinue Xopenex** — bronchodilators are not recommended in bronchiolitis and have not shown benefit.[4][1]
- Do NOT obtain additional chest x-rays, blood gases, or electrolytes unless clinical deterioration occurs.[1][16][17]

**For pertussis (must exclude):**

- Obtain **nasopharyngeal swab for Bordetella pertussis PCR** — this is the key test that will change management.[6][8]
- **Start empiric azithromycin** (10 mg/kg/day × 5 days) now, without waiting for PCR results, given the high clinical suspicion (unvaccinated infant [9][8]
- **Monitor closely for apnea** — infants [5][7]

**For bacterial superinfection:**

- The low CRP, negative urinalysis, nontoxic appearance, and absence of consolidation on CXR make this unlikely. No empiric broad-spectrum antibiotics are indicated at this time. The azithromycin started empirically for pertussis also provides some atypical bacterial coverage. Reassess if the patient develops new fever, clinical deterioration, or focal findings.[1][2]

**For can't-miss diagnoses:**

- **Sepsis**: Blood culture was not mentioned in the ED labs — if not already obtained, send one now given age [18][11]
- **Congenital heart disease**: The murmur is vibratory and consistent with an innocent murmur. If the patient's oxygen requirement does not improve as expected for bronchiolitis, or if there is persistent tachycardia after resolution of respiratory distress, obtain a **4-extremity blood pressure check and pre/post-ductal saturations**. Echocardiography only if these are abnormal or clinical concern persists.

**Follow-up:**

- Reassess respiratory status, feeding tolerance, and oxygen requirement every 4–6 hours. Discharge criteria: tolerating oral feeds, SpO₂ ≥90% on room air for ≥4 hours, and no significant respiratory distress.
- Counsel family on **smoking cessation** — household smoke exposure worsens bronchiolitis severity and recurrence.
- Ensure pertussis PCR result is followed up and reported to public health if positive; prophylactic azithromycin for household contacts if confirmed.

---

Would you like to explore the specific apnea monitoring protocols and ICU escalation criteria for young infants with pertussis or severe bronchiolitis?

### References

1. Bronchiolitis. Dalziel SR, Haskell L, O'Brien S, et al. Lancet (London, England). 2022;400(10349):392-406. doi:10.1016/S0140-6736(22)01016-9.
2. Viral Bronchiolitis. Florin TA, Plint AC, Zorc JJ. Lancet (London, England). 2017;389(10065):211-224. doi:10.1016/S0140-6736(16)30951-5.
3. A Study of the Relationship Between Cough and Wheezing Complicated by Common Respiratory Viral Infections in Infants and Secondary Thrombocythemia. He P, Hu F, Wang F. PloS One. 2025;20(7):e0326369. doi:10.1371/journal.pone.0326369.
4. Respiratory Syncytial Virus Bronchiolitis: Rapid Evidence Review. Oppenlander KE, Chung AA, Clabaugh D. American Family Physician. 2023;108(1):52-57.
5. Pertussis in Young Infants Throughout the World. Cherry JD. Clinical Infectious Diseases : An Official Publication of the Infectious Diseases Society of America. 2016;63(suppl 4):S119-S122. doi:10.1093/cid/ciw550.
6. Pertussis: Common Questions and Answers. Kline JM, Smith EA, Zavala A. American Family Physician. 2021;104(2):186-192.
7. Clinical Characteristics of 967 Children With Pertussis: A Single-Center Analysis Over an 8-Year Period in Beijing, China. Kang L, Cui X, Fu J, et al. European Journal of Clinical Microbiology & Infectious Diseases : Official Publication of the European Society of Clinical Microbiology. 2022;41(1):9-20. doi:10.1007/s10096-021-04336-w.
8. Clinically Diagnosing Pertussis-Associated Cough in Adults and Children: CHEST Guideline and Expert Panel Report. Moore A, Harnden A, Grant CC, Patel S, Irwin RS. Chest. 2019;155(1):147-154. doi:10.1016/j.chest.2018.09.027.
9. Leukocytosis and Delayed Macrolide Administration Were Risk Factors for Severe Pertussis in Newborn Infants. Luo J, Wang Y, Meng Q, et al. Acta Paediatrica (Oslo, Norway : 1992). 2026;115(4):812-820. doi:10.1111/apa.70401.
10. Pertussis Leukocytosis: Mechanisms, Clinical Relevance and Treatment. Carbonetti NH. Pathogens and Disease. 2016;74(7):ftw087. doi:10.1093/femspd/ftw087.
11. Evaluation and Management of Febrile Children: A Review. Cioffredi LA, Jhaveri R. JAMA Pediatrics. 2016;170(8):794-800. doi:10.1001/jamapediatrics.2016.0596.
12. Management of Fever in Infants and Young Children. Hamilton JL, Evans SG, Bakshi M. American Family Physician. 2020;101(12):721-729.
13. Predictors of Intensive Care Admission in Hypoxemic Bronchiolitis Infants, Secondary Analysis of a Randomized Trial. Franklin D, Babl FE, Neutze J, et al. The Journal of Pediatrics. 2023;256:92-97.e1. doi:10.1016/j.jpeds.2022.12.006.
14. Severe Respiratory Syncytial Virus Infection in Children: Burden, Management, and Emerging Therapies. Mazur NI, Caballero MT, Nunes MC. Lancet (London, England). 2024;404(10458):1143-1156. doi:10.1016/S0140-6736(24)01716-1.
15. Nebulised Hypertonic Saline Solution for Acute Bronchiolitis in Infants. Zhang L, Mendoza-Sassi RA, Wainwright CE, Aregbesola A, Klassen TP. The Cochrane Database of Systematic Reviews. 2023;4:CD006458. doi:10.1002/14651858.CD006458.pub5.
16. Clinical Practice Guideline: The Diagnosis, Management, and Prevention of Bronchiolitis. Ralston SL, Lieberthal AS, Meissner HC, et al. Pediatrics. 2014;134(5):e1474-502. doi:10.1542/peds.2014-2742.
17. Investigations for Bronchiolitis in Infants: An Overview of Reviews and Systematic Review of Primary Studies. Loveys K, Borland ML, Oakley E, et al. Pediatric Pulmonology. 2026;61(4):e71582. doi:10.1002/ppul.71582.
18. Evaluation and Management of Well-Appearing Febrile Infants 8 to 60 Days Old. Pantell RH, Roberts KB, Adams WG, et al. Pediatrics. 2021;148(2):e2021052228. doi:10.1542/peds.2021-052228.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT: , Increased work of breathing.,HISTORY OF PRESENT ILLNESS: , The patient is a 2-month-old female with a 9-day history of illness.  Per mom's report, the illness started 9 days ago with a dry cough.  The patient was eating normal up until approximately three days ago.  Mom was using a vaporizer at night, which she feels to have helped.  The patient's cough gradually worsened and three days ago, the patient had a significant increasing cough.  At that time, the patient also had significant increasing congestion.  Two days ago the patient was taken to the primary care physician's office and the patient was given Xopenex 2 puffs every 4 to 6 hours for home regimen, but this per mom's report, did not help the patient's symptoms.  On Wednesday evening, the patient's congestion and work of breathing increased and the patient was gagging after feedings.  The patient was brought to Children's Hospital Emergency Room at which time the patient was evaluated.  A chest x-ray was obtained and was noted to be normal.  The patient's saturations were noted to be normal and the patient was discharged home.  Last night, the patient was having multiple episodes of emesis after feedings with coughing and today was noted to have decreasing activity.  The patient had a 101 temperature on Wednesday evening, but has had no true fevers.  The patient has had a mild decrease in urine output today and secondary to the persistent increased work of breathing, coughing, and posttussive emesis, the patient was brought to Children's Hospital for reevaluation.,REVIEW OF SYSTEMS: , The remainder of the review of system is otherwise negative, all systems being reviewed, outside of pertinent positives as stated above.,ALLERGIES:,  NO KNOWN DRUG ALLERGIES.,MEDICATIONS:  ,As above.,IMMUNIZATIONS:,  None.,PAST MEDICAL HISTORY:  ,No hospitalizations.  No surgeries.,BIRTH HISTORY: , The patient was born to a G8, P2, A6 mom via normal spontaneous vaginal delivery.  Birth weight 6 pounds 12 ounces.  Mom stated she had a uterine infection during her pregnancy and at the time of delivery, but the patient was only in the hospital for 24 hours with mom after delivery.  The patient was full term and mom was noted to have gestational diabetes controlled with diet during her pregnancy.,FAMILY HISTORY: , Brother, mother, and father all have asthma.  Mom was noted to have gestational diabetes.,SOCIAL HISTORY: , The patient lives with mother, father, and a brother.  There is one bird.  There are smokers in the household.  There are sick contacts.,PHYSICAL EXAMINATION:,VITAL SIGNS:  Temperature is 97.7 and pulse is 181, but the patient is fussy.  Respiratory rate ranged between 36 and 44.  The patient is saturating 100% on one-half liter and 89% on room air.,GENERAL APPEARANCE:  Nontoxic child, but with increased work of breathing.  No respiratory distress.,HEENT:  Head is normocephalic and atraumatic.  Anterior fontanelle flat.  Pupils are equal, round, and reactive to light bilaterally.  Tympanic membranes are clear bilaterally.  Nares are congested.  Mucous membranes are moist without erythema.,NECK:  Supple.  No lymphadenopathy.,CHEST:  Exhibits symmetric expansion and retractions.,LUNGS:  The patient has diffuse crackles bilaterally, but no wheezes, rales, or rhonchi.,CARDIOVASCULAR:  Heart has a 2/6 vibratory systolic ejection murmur, best heard over the left sternal boarder.,ABDOMEN:  Soft, nondistended, and nondistended.  Good bowel sounds noted in all 4 quadrants.,GU:  Normal female.  No discharge or erythema.,BACK:  Normal with a normal curvature.,EXTREMITIES:  A 2+ pulses in the bilateral upper lower extremities.  No evidence of clubbing, cyanosis, or edema.  Capillary refill less than 3 seconds.,LABORATORY DATA: , Labs in the emergency room include a CBC, which showed a white blood cell count of 20.8 with a hemoglobin of 10.7, hematocrit of 31.3 with platelet count of 715,000 with 40% neutrophils, 2 bands, and 70% monocytes.  A urinalysis obtained in the emergency room was noted to be negative.  CRP was noted to be 2.0.  The chest x-ray, reviewed by myself in the emergency room, showed no significant change from previous x-ray, but the patient does has some bronchial wall thickening.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0481 arm=costaware -->

### Assessment and Plan

ASSESSMENT:

1. Acute viral bronchiolitis with hypoxemia

2-month-old female presenting with a 9-day progressive course of cough, congestion, increased work of breathing, posttussive emesis, and decreased oral intake. Exam demonstrates diffuse bilateral crackles, retractions, and nasal congestion. Room air oxygen saturation of 89% requiring supplemental oxygen (100% on 0.5L NC). Chest x-ray shows bronchial wall thickening without consolidation. Clinical presentation is consistent with viral bronchiolitis. The elevated WBC of 20.8 with monocyte predominance (70%) is consistent with a viral etiology. CRP of 2.0 mg/L is reassuringly low, making concurrent serious bacterial infection unlikely. Thrombocytosis is reactive and expected in the setting of an acute viral illness. The 2/6 systolic murmur is likely an innocent flow murmur in the setting of tachycardia and fever, but will monitor.

Multiple risk factors for escalated care are present: age ≤2 months, hypoxemia (SpO2

<!-- RESPONSE_END -->


---

## Case 5/10 — MTS_0305  ·  General Medicine

**Why this case:** Under-ordering test: probable stroke where the PHYSICIAN ordered MORE (~$814) than OE. Does parsimony fall dangerously below the physician?

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient presents with probable stroke characterized by expressive aphasia without dysarthria or weakness, with a history of atrial fibrillation, hypertension, hyperlipidemia, hyperglycemia, and mild renal insufficiency.

- **Physician's diagnostic orders:** MRI, MRA, carotid Doppler ultrasound, echocardiogram, fasting lipid profile

- **OpenEvidence (default prompt) ordered:** MRI brain with diffusion-weighted imaging, CT angiography of head and neck, Continuous cardiac telemetry for at least 24-48 hours, Transthoracic echocardiogram, Hemoglobin A1C, Fasting lipid panel, TSH, DVT prophylaxis with sequential compression devices (~$581; physician ~$814)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT:, Altered mental status.,HISTORY OF PRESENT ILLNESS:, The patient is a 69-year-old male transferred from an outlying facility with diagnosis of a stroke. History is taken mostly from the emergency room record. The patient is unable to give any history and no family member is present for questioning. When asked why he came to the emergency room, the patient replies that it started about 2 PM yesterday. However, he is unable to tell me exactly what started at 2 PM yesterday. The patient's speech is clear, but he speaks nonsensically using words in combinations that don't make any sense. No other history of present illness is available.,PAST MEDICAL HISTORY:, Per the emergency room record, significant for atrial fibrillation, hypertension, and hyperlipidemia.,PAST SURGICAL HISTORY:, Unknown.,FAMILY HISTORY:, Unknown.,SOCIAL HISTORY:, The patient denies smoking and drinking.,MEDICATIONS:, Per the emergency room record, medications are Lotensin 20 mg daily, Toprol 50 mg daily, Plavix 75 mg daily and aspirin 81 mg daily.,ALLERGIES:, UNKNOWN.,REVIEW OF SYSTEMS:, Unobtainable secondary to the patient's condition.,PHYSICAL EXAMINATION:,VITAL SIGNS: Temperature: 97.9. Pulse: 79. Respiratory rate: 20. Blood pressure: 117/84.,GENERAL: Well-developed, well-nourished male in no acute distress.,HEENT: Eyes: Pupils are equal, round and reactive. There is no scleral icterus. Ears, nose and throat: His oropharynx is moist. His hearing is normal.,NECK: No JVD. No thyromegaly.,CARDIOVASCULAR: Irregular rhythm. No lower extremity edema.,RESPIRATORY: Clear to auscultation bilaterally with normal effort.,ABDOMEN: Nontender. Nondistended. Bowel sounds are positive.,MUSCULOSKELETAL: There is no clubbing of the digits. The patient's strength is 5/5 throughout.,NEUROLOGICAL: Babinski's are downgoing bilaterally. Deep tendon reflexes are 2+ throughout.,LABORATORY DATA:, By report, head CT from the outlying facility was negative. An EKG showed atrial fibrillation with a rate of 75. There is no indication of any acute cardiac ischemia. A chest x-ray shows no acute pulmonary process, but does show cardiomegaly.,Labs are as follows: White count 9.4, hemoglobin 17.2, hematocrit 52.5, platelet count 219. PTT 24, PT 13, INR 0.96. Sodium 135, potassium 3.6, chloride 99, bicarb 27, BUN 13, creatinine 1.4, glucose 161, calcium 9, magnesium 1.9, total protein 7, albumin 3.7, AST 22, ALT 41, alkaline phosphatase 85, total bilirubin 0.7, total cholesterol 193. Cardiac isoenzymes are negative times one with a troponin of 0.09.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0305 arm=parsimonious -->
High risk of ischemic stroke. Patients with a CHA₂DS₂-VASc score of 4 face a 4.8% risk of ischemic stroke and a 6.7% risk of stroke, TIA, or systemic embolism.[1]

## ASSESSMENT

**1. Acute ischemic stroke (cardioembolic, left MCA territory — Wernicke aphasia)** — Most likely diagnosis. This 69-year-old male with known atrial fibrillation (not anticoagulated, INR 0.96) presents with acute-onset fluent, nonsensical speech with preserved motor strength (5/5 throughout), consistent with **Wernicke aphasia** from a left posterior temporal/parietal infarct.[2][3] Fluent speech with incomprehensible word combinations, intact motor function, and no hemiparesis is the hallmark of a dominant-hemisphere posterior MCA territory stroke. The negative head CT does not exclude ischemic stroke — noncontrast CT is only 47–53% sensitive for acute ischemia within the first hours.[4] AF without anticoagulation is the most likely embolic source. His CHA₂DS₂-VASc score is **4** (age 65–74, hypertension, and now stroke), conferring a high annual stroke risk of ~4.8%.[5][6]

**2. Seizure with postictal aphasia** — Focal seizure activity in the left temporal lobe can produce a transient fluent aphasia that mimics Wernicke aphasia.[7] No witnessed seizure activity is reported, but subclinical seizures remain possible, particularly if an underlying structural lesion is present.

**3. Metabolic encephalopathy / Wernicke encephalopathy** — Glucose of 161 mg/dL (mildly elevated but not in the range to cause AMS), creatinine 1.4, and otherwise unremarkable metabolic panel make a purely metabolic cause less likely. Wernicke encephalopathy (thiamine deficiency) can present with altered mental status, though the classic triad (ophthalmoplegia, ataxia, confusion) is absent, and there is no reported alcohol use or nutritional risk.[8]

**Can't-miss diagnoses:**

- **Intracranial hemorrhage** — Excluded by negative head CT (high sensitivity for hemorrhage).[9]
- **CNS infection (meningitis/encephalitis)** — HSV encephalitis has a predilection for the temporal lobe and can mimic Wernicke aphasia. No fever, meningismus, or leukocytosis is present, making this less likely but important to consider if clinical course worsens.[10]
- **Nonconvulsive status epilepticus** — Can present as isolated altered mental status/aphasia without overt motor seizure activity.

---

## PLAN

**1. Acute ischemic stroke (most likely — cardioembolic)**

- **MRI brain with diffusion-weighted imaging (DWI):** This is the single most important next test. DWI is 88% sensitive and 95% specific for acute infarction and will confirm or exclude ischemic stroke when CT is negative. This directly changes management — confirming stroke determines anticoagulation strategy and timing.[4]
- **Initiate anticoagulation with a DOAC** (e.g., apixaban 5 mg BID): If MRI confirms a small-to-moderate infarct without hemorrhagic transformation, early DOAC initiation (within ≤4 days) is supported by the ELAN and OPTIMAS trials as non-inferior to delayed initiation and safe with respect to intracranial hemorrhage. If a large territorial infarct is found, delay anticoagulation to ~14 days per AHA/ASA guidelines. **Discontinue aspirin and clopidogrel** once anticoagulation is started — combination antiplatelet plus anticoagulation is not recommended for secondary stroke prevention in AF.[11][12][13]
- **Continue current antihypertensives** (benazepril, metoprolol). BP is currently well-controlled at 117/84. Metoprolol also provides rate control for AF. Target outpatient SBP [14][13]
- **Statin therapy:** Initiate moderate-to-high intensity statin (total cholesterol 193, no prior statin). Appropriate for secondary prevention regardless of stroke subtype.
- **Swallow evaluation** before oral intake given aphasia and stroke concern.

**2. Seizure with postictal aphasia**

- If MRI is negative for acute infarction or if the clinical picture does not improve as expected, obtain **EEG** to evaluate for nonconvulsive seizure activity or postictal state. EEG is not needed upfront if MRI confirms stroke.[10]

**3. Metabolic / Wernicke encephalopathy**

- Already largely excluded by labs (electrolytes, glucose, renal/hepatic function, CBC all near-normal). No specific additional workup needed unless clinical trajectory changes.
- Administer **empiric thiamine 100 mg IV** — low cost, no risk, and addresses the rare possibility of Wernicke encephalopathy even without classic risk factors.[8]

**Excluding can't-miss diagnoses:**

- **Intracranial hemorrhage:** Already excluded by negative head CT.[9]
- **CNS infection:** No fever, no meningismus, no leukocytosis — lumbar puncture is not indicated at this time. If fever develops or mental status worsens, pursue LP and empiric acyclovir/antibiotics.[10]
- **Nonconvulsive status epilepticus:** Addressed by EEG if clinical course is atypical or MRI is negative.

**Disposition:** Admit to a monitored bed. Obtain neurology consultation if available. Attempt to contact family/next of kin for collateral history (baseline cognition, medication compliance, symptom timeline).

---

Would you like to explore the optimal timing and choice of DOAC for secondary stroke prevention in this patient, particularly given his borderline creatinine of 1.4?

Figure 2
Stepwise Algorithm for Initial Management of Acute Ischemic Stroke in Adults.
Powers WJ. Acute Ischemic Stroke. The New England Journal of Medicine. 2020;383(3):252-260. doi:10.1056/NEJMcp1917030.

Figure 1
Algorithm for the initial evaluation and management of patients with recent altered mental status. Information from references 2, 3, 10, and 12–18.
Veauthier B, Hornecker JR, Thrasher T. Recent-Onset Altered Mental Status: Evaluation and Management. American Family Physician. 2021;104(5):461-470.

Figure 3
Antithrombotic therapy for the prevention of stroke recurrence. Information from reference 59.
Ford B, Dore MM, Koehn TR. Recurrent Ischemic Stroke: Prevention Strategies. American Family Physician. 2026;113(1):57-69.

Figure 2
Cumulative Incidence of the Primary and Safety Outcomes.
Johnston SC, Amarenco P, Denison H, et al. Ticagrelor and Aspirin or Aspirin Alone in Acute Ischemic Stroke or TIA. The New England Journal of Medicine. 2020;383(3):207-217. doi:10.1056/NEJMoa1916870.

Figure 3
Central Illustration. CHA2DS2-VASc Score for Stroke Prediction in AF: Stroke Rates for All Patients
Kabra R, Girotra S, Vaughan Sarrazin M. Refining Stroke Prediction in Atrial Fibrillation Patients by Addition Of African-American Ethnicity to CHA2DS2-VASc Score. Journal of the American College of Cardiology. 2016;68(5):461-470. doi:10.1016/j.jacc.2016.05.044.

Figure 3
Incidence rates of ischemic stroke per 100 person‐years with 95% confidence intervals in men and women in relation to CHA 2 DS 2 ‐VASc score.
Tomasdottir M, Friberg L, Hijazi Z, Lindbäck J, Oldgren J. Risk of Ischemic Stroke and Utility of CHA2 DS2 -VASc Score in Women and Men With Atrial Fibrillation. Clinical Cardiology. 2019;42(10):1003-1009. doi:10.1002/clc.23257.

### References

1. Evaluation of Risk Stratification Schemes for Ischaemic Stroke and Bleeding in 182 678 Patients With Atrial Fibrillation: The Swedish Atrial Fibrillation Cohort Study. Friberg L, Rosenqvist M, Lip GY. European Heart Journal. 2012;33(12):1500-10. doi:10.1093/eurheartj/ehr488.
2. Aphasia. Damasio AR. The New England Journal of Medicine. 1992;326(8):531-9. doi:10.1056/NEJM199202203260806.
3. Aphasia: Progress in the Last Quarter of a Century. Hillis AE. Neurology. 2007;69(2):200-13. doi:10.1212/01.wnl.0000265600.69385.6f.
4. Diagnosis and Management of Transient Ischemic Attack and Acute Ischemic Stroke: A Review. Mendelson SJ, Prabhakaran S. JAMA. 2021;325(11):1088-1098. doi:10.1001/jama.2020.26867.
5. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Writing Committee Members, Joglar JA, Chung MK, et al. Journal of the American College of Cardiology. 2024;83(1):109-279. doi:10.1016/j.jacc.2023.08.017.
6. Atrial Fibrillation: Common Questions and Answers About Diagnosis and Treatment. Holder S, Amin P. American Family Physician. 2024;109(5):398-404.
7. Postseizure Aphasia in Wernicke's Encephalopathy: A Case Report and Review of Literature. Devaraj S, Muralles SA, Gill CE, Meresh E. Neuropsychiatric Disease and Treatment. 2018;14:2593-2598. doi:10.2147/NDT.S174481.
8. Wernicke's Encephalopathy: New Clinical Settings and Recent Advances in Diagnosis and Management. Sechi G, Serra A. The Lancet. Neurology. 2007;6(5):442-55. doi:10.1016/S1474-4422(07)70104-7.
9. Acute Ischemic Stroke. Powers WJ. The New England Journal of Medicine. 2020;383(3):252-260. doi:10.1056/NEJMcp1917030.
10. Recent-Onset Altered Mental Status: Evaluation and Management. Veauthier B, Hornecker JR, Thrasher T. American Family Physician. 2021;104(5):461-470.
11. Optimal Timing of Anticoagulation After Acute Ischaemic Stroke With Atrial Fibrillation (OPTIMAS): A Multicentre, Blinded-Endpoint, Phase 4, Randomised Controlled Trial. Werring DJ, Dehbi HM, Ahmed N, et al. Lancet (London, England). 2024;:S0140-6736(24)02197-4. doi:10.1016/S0140-6736(24)02197-4.
12. Early versus Later Anticoagulation for Stroke with Atrial Fibrillation. Fischer U, Koga M, Strbian D, et al. The New England Journal of Medicine. 2023;388(26):2411-2421. doi:10.1056/NEJMoa2303048.
13. 2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack: A Guideline From the American Heart Association/American Stroke Association. Kleindorfer DO, Towfighi A, Chaturvedi S, et al. Stroke. 2021;52(7):e364-e467. doi:10.1161/STR.0000000000000375.
14. 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Jones DW, Ferdinand KC, Taler SJ, et al. Journal of the American College of Cardiology. 2025;86(18):1567-1678. doi:10.1016/j.jacc.2025.05.007.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT:, Altered mental status.,HISTORY OF PRESENT ILLNESS:, The patient is a 69-year-old male transferred from an outlying facility with diagnosis of a stroke. History is taken mostly from the emergency room record. The patient is unable to give any history and no family member is present for questioning. When asked why he came to the emergency room, the patient replies that it started about 2 PM yesterday. However, he is unable to tell me exactly what started at 2 PM yesterday. The patient's speech is clear, but he speaks nonsensically using words in combinations that don't make any sense. No other history of present illness is available.,PAST MEDICAL HISTORY:, Per the emergency room record, significant for atrial fibrillation, hypertension, and hyperlipidemia.,PAST SURGICAL HISTORY:, Unknown.,FAMILY HISTORY:, Unknown.,SOCIAL HISTORY:, The patient denies smoking and drinking.,MEDICATIONS:, Per the emergency room record, medications are Lotensin 20 mg daily, Toprol 50 mg daily, Plavix 75 mg daily and aspirin 81 mg daily.,ALLERGIES:, UNKNOWN.,REVIEW OF SYSTEMS:, Unobtainable secondary to the patient's condition.,PHYSICAL EXAMINATION:,VITAL SIGNS: Temperature: 97.9. Pulse: 79. Respiratory rate: 20. Blood pressure: 117/84.,GENERAL: Well-developed, well-nourished male in no acute distress.,HEENT: Eyes: Pupils are equal, round and reactive. There is no scleral icterus. Ears, nose and throat: His oropharynx is moist. His hearing is normal.,NECK: No JVD. No thyromegaly.,CARDIOVASCULAR: Irregular rhythm. No lower extremity edema.,RESPIRATORY: Clear to auscultation bilaterally with normal effort.,ABDOMEN: Nontender. Nondistended. Bowel sounds are positive.,MUSCULOSKELETAL: There is no clubbing of the digits. The patient's strength is 5/5 throughout.,NEUROLOGICAL: Babinski's are downgoing bilaterally. Deep tendon reflexes are 2+ throughout.,LABORATORY DATA:, By report, head CT from the outlying facility was negative. An EKG showed atrial fibrillation with a rate of 75. There is no indication of any acute cardiac ischemia. A chest x-ray shows no acute pulmonary process, but does show cardiomegaly.,Labs are as follows: White count 9.4, hemoglobin 17.2, hematocrit 52.5, platelet count 219. PTT 24, PT 13, INR 0.96. Sodium 135, potassium 3.6, chloride 99, bicarb 27, BUN 13, creatinine 1.4, glucose 161, calcium 9, magnesium 1.9, total protein 7, albumin 3.7, AST 22, ALT 41, alkaline phosphatase 85, total bilirubin 0.7, total cholesterol 193. Cardiac isoenzymes are negative times one with a troponin of 0.09.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0305 arm=costaware -->
### Assessment and Plan

**ASSESSMENT:**

69-year-old male with a history of atrial fibrillation, hypertension, and hyperlipidemia, transferred from an outside facility with altered mental status and concern for stroke. The patient demonstrates fluent but nonsensical speech (consistent with receptive/Wernicke's aphasia), with preserved motor strength (5/5 throughout), normal reflexes, and downgoing Babinski bilaterally. Head CT from the outside facility was negative for hemorrhage. EKG confirms atrial fibrillation with controlled rate. Notably, the patient was on dual antiplatelet therapy (aspirin 81 mg + clopidogrel 75 mg) but was NOT on anticoagulation despite a known history of atrial fibrillation.

The clinical presentation — acute onset of fluent aphasia with paraphasic errors in a patient with atrial fibrillation and no anticoagulation — is most consistent with an **acute ischemic stroke** involving the left temporal/parietal region (Wernicke's area), likely cardioembolic in etiology. The negative head CT does not exclude ischemic stroke, as noncontrast CT has limited sensitivity (47–53%) for acute infarction.

CHA₂DS₂-VASc score: 4 (age 65–74: +1, hypertension: +1, stroke: +2), placing this patient at high risk for thromboembolic events (estimated annual stroke risk ~4.8%).

**PLAN:**

1. **Imaging:**

   - MRI brain with diffusion-weighted imaging (DWI) to confirm acute ischemic infarction and characterize size/location. Approximately 25% of stroke patients with negative head CT will have acute infarction on MRI.
   - CT angiography (or MR angiography) of the head and neck to evaluate for large-vessel occlusion or significant atherosclerotic disease, if not already obtained.

2. **Neurology consultation** for stroke team evaluation, NIHSS scoring, and co-management.
3. **Cardiac workup:**

   - Transthoracic echocardiogram to evaluate for intracardiac thrombus, valvular disease, and left ventricular function (particularly given cardiomegaly on CXR).
   - Continuous telemetry monitoring.

4. **Antithrombotic therapy:**

   - Discontinue dual antiplatelet therapy (aspirin and clopidogrel). Dual antiplatelet therapy is inferior to oral anticoagulation for stroke prevention in atrial fibrillation.
   - Initiate a direct oral anticoagulant (DOAC) for secondary stroke prevention. Timing of initiation to be determined by neurology based on MRI findings (infarct size and presence of hemorrhagic transformation). For minor-to-moderate strokes, early DOAC initiation (within 4 days) has been shown to be non-inferior to delayed initiation (7–14 days) per the OPTIMAS and ELAN trials. For large infarcts, delay of up to 14 days is reasonable.
   - Apixaban 5 mg BID is preferred given favorable safety profile; dose-adjust if indicated (weight, renal function). Creatinine is 1.4 — calculate CrCl to

<!-- RESPONSE_END -->


---

## Case 6/10 — MTS_0159  ·  SOAP / Chart / Progress Notes

**Why this case:** Care-setting confusion: Bell's palsy on a routine note; AI tends to activate a stroke pathway. Does parsimony keep the can't-miss (stroke) while trimming the rest?

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient is diagnosed with Bell’s Palsy and is being treated with Valtrex without steroids, with no acute cardiac or stroke findings on EKG.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** STAT non-contrast head CT, brain MRI with diffusion-weighted imaging within 24 hours, point-of-care glucose, ECG, continuous telemetry monitoring, complete blood count, comprehensive metabolic panel, hemoglobin A1c, lipid panel, carotid duplex ultrasound or CT angiography of head and neck, echocardiogram (~$554; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
SUBJECTIVE:,  The patient is a 75-year-old female who comes in today with concerns of having a stroke.  She states she feels like she has something in her throat.  She started with some dizziness this morning and some left hand and left jaw numbness.  She said that she apparently had something about three weeks ago where she was dizzy and ended up falling down and she saw Dr. XYZ for that who gave her some Antivert.  She said that today though she woke up in the middle of the night and her left hand was numb and she was having numbness on the left side of her face, as well as the left side of her neck.  She said she had an earache a day or so ago.  She has not had any cold symptoms.,ALLERGIES:,  Demerol and codeine.,MEDICATIONS: , Lotensin, Lopid, metoprolol, and Darvocet.,REVIEW OF SYSTEMS:,  The patient says that she feels little bit nauseated at times.  She denies chest pain or shortness of breath and again feels like she has something in her throat.  She has been able to swallow liquids okay.  She said that she did brush her teeth this morning and did not have any fluid dripping out of her mouth.  She does say that she occasionally has numbness in her left hand prior to today.,PHYSICAL EXAMINATION:,General:  She is awake and alert, no acute distress.,Vital Signs:  Blood pressure:  175/86.  Temperature:  She is afebrile.  Pulse:  78.  Respiratory rate:  20.  O2 sat:  93% on room air.,HEENT:  Her TMs are normal bilaterally.  Posterior pharynx is unremarkable.  It should be noted that her uvula did not deviate and neither did her tongue.  When she smiles though she has some drooping of the left side of her face, as well as some mild nasolabial fold flattening.,Neck:  Without adenopathy or thyromegaly.  Carotids pulses are brisk without bruits.,Lungs:  Clear to auscultation.,Heart:  Regular rate and rhythm without murmur.,Extremities:  Her muscle strength is symmetrical and intact bilaterally.  DTRs are 2+/4+ bilaterally and muscle strength is intact in the upper extremities.  She has a positive Tinel’s sign on her left wrist.,Neurological:  I also took monofilament and she could sense it easily when testing her sensation on her face.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0159 arm=parsimonious -->
### Assessment and Plan

## ASSESSMENT

**Three Most Likely Diagnoses:**

1. **Bell's palsy (idiopathic facial nerve paralysis)** — Most likely diagnosis. The exam demonstrates left-sided facial droop with nasolabial fold flattening. Critically, the note does not describe forehead sparing — in central (stroke-related) facial palsy, the forehead is typically spared, whereas in peripheral (Bell's) palsy, the entire hemiface is affected. The preceding earache, acute onset, intact motor strength in all extremities, symmetric DTRs, intact sensation to monofilament, and absence of other focal neurologic deficits all favor a peripheral CN VII palsy. Risk factors include age >70 and hypertension. The left hand numbness is better explained by a separate process (see #3 below), given the positive Tinel's sign and her history of intermittent left hand numbness predating this episode.
2. **Transient ischemic attack (TIA) or minor stroke** — Must remain on the differential given her age (75), hypertension (BP 175/86), vascular risk factors (on gemfibrozil for dyslipidemia), recurrent dizziness with a fall 3 weeks ago, and acute-onset left-sided numbness. However, the facial weakness pattern (lower face with likely forehead involvement), symmetric motor strength, intact DTRs, and absence of limb weakness or speech/language deficits make a central lesion less likely. The O2 sat of 93% is mildly low and warrants monitoring but is nonspecific.
3. **Carpal tunnel syndrome (left)** — The intermittent left hand numbness predating this presentation, combined with a positive Tinel's sign at the left wrist, is consistent with median nerve entrapment. This likely represents a chronic, incidental finding separate from her acute facial symptoms.

**Can't-Miss Diagnoses:**

- **Acute ischemic stroke** — Given her age, hypertension, dyslipidemia, and acute neurologic symptoms, stroke must be excluded even though the exam pattern favors a peripheral process. A missed posterior circulation stroke could present with dizziness, facial numbness, and cranial nerve findings.
- **Ramsay Hunt syndrome (herpes zoster oticus)** — Recent earache and facial palsy raise this possibility; vesicles may not appear for up to 2 weeks after palsy onset. This would change management (higher-dose antivirals, poorer prognosis).

---

## PLAN

**1. Bell's palsy (most likely):**

- Start oral prednisone 60 mg daily for 5 days, then taper over 5 days.
- Add valacyclovir 1 g TID for 7 days (combination therapy may reduce synkinesis risk, and also covers for possible early Ramsay Hunt syndrome given the recent earache).
- Eye protection: artificial tears during the day, lubricating ointment and tape at night if incomplete eye closure develops.
- Counsel on expected course: most patients improve within weeks; follow up in 2–3 weeks to reassess facial function.

**2. Exclude acute stroke/TIA:**

- Obtain a **noncontrast CT head** today — this is the single most important test to rule out intracranial hemorrhage and mass lesion, and is appropriate for this resource-limited setting.
- If CT is negative (expected), the clinical picture strongly favors Bell's palsy. However, given her age, hypertension, recurrent dizziness, and vascular risk factors, arrange **carotid duplex ultrasound** as an outpatient study to screen for significant carotid stenosis, which would change secondary prevention management.
- Start **aspirin 81 mg daily** if not already on antiplatelet therapy — appropriate for both secondary cerebrovascular prevention and her overall cardiovascular risk profile.
- Optimize blood pressure control: her current BP of 175/86 is above goal. She is already on benazepril and metoprolol. Consider uptitrating benazepril or adding a thiazide diuretic, targeting BP
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
SUBJECTIVE:,  The patient is a 75-year-old female who comes in today with concerns of having a stroke.  She states she feels like she has something in her throat.  She started with some dizziness this morning and some left hand and left jaw numbness.  She said that she apparently had something about three weeks ago where she was dizzy and ended up falling down and she saw Dr. XYZ for that who gave her some Antivert.  She said that today though she woke up in the middle of the night and her left hand was numb and she was having numbness on the left side of her face, as well as the left side of her neck.  She said she had an earache a day or so ago.  She has not had any cold symptoms.,ALLERGIES:,  Demerol and codeine.,MEDICATIONS: , Lotensin, Lopid, metoprolol, and Darvocet.,REVIEW OF SYSTEMS:,  The patient says that she feels little bit nauseated at times.  She denies chest pain or shortness of breath and again feels like she has something in her throat.  She has been able to swallow liquids okay.  She said that she did brush her teeth this morning and did not have any fluid dripping out of her mouth.  She does say that she occasionally has numbness in her left hand prior to today.,PHYSICAL EXAMINATION:,General:  She is awake and alert, no acute distress.,Vital Signs:  Blood pressure:  175/86.  Temperature:  She is afebrile.  Pulse:  78.  Respiratory rate:  20.  O2 sat:  93% on room air.,HEENT:  Her TMs are normal bilaterally.  Posterior pharynx is unremarkable.  It should be noted that her uvula did not deviate and neither did her tongue.  When she smiles though she has some drooping of the left side of her face, as well as some mild nasolabial fold flattening.,Neck:  Without adenopathy or thyromegaly.  Carotids pulses are brisk without bruits.,Lungs:  Clear to auscultation.,Heart:  Regular rate and rhythm without murmur.,Extremities:  Her muscle strength is symmetrical and intact bilaterally.  DTRs are 2+/4+ bilaterally and muscle strength is intact in the upper extremities.  She has a positive Tinel’s sign on her left wrist.,Neurological:  I also took monofilament and she could sense it easily when testing her sensation on her face.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0159 arm=costaware -->
### Assessment and Plan

ASSESSMENT:

1. Acute cerebrovascular event — likely transient ischemic attack (TIA) vs. acute ischemic stroke. This 75-year-old woman with hypertension and hyperlipidemia presents with acute-onset left facial droop with nasolabial fold flattening, left hand numbness, left jaw numbness, dizziness, and nausea. The facial droop spares the forehead (lower motor neuron vs. upper motor neuron pattern not fully characterized, but uvula and tongue are midline, and motor strength is symmetric), which is most consistent with a central process. Hypertension at 175/86 and O2 sat of 93% are noted. The episode three weeks ago with dizziness and fall may have represented a prior TIA. The positive Tinel's sign on the left wrist likely reflects concurrent carpal tunnel syndrome and does not explain the facial findings. Bell's palsy is less likely given the concurrent hand numbness and dizziness suggesting a central localization. ABCD2 score is 4 (age ≥60: +1, BP ≥140/90: +1, symptoms >60 min: +2), indicating moderate risk with an estimated 2-day stroke risk of ~4.1%.
2. Uncontrolled hypertension.
3. Left carpal tunnel syndrome (incidental, chronic).

PLAN:

1. Acute stroke/TIA workup:

   - Stat noncontrast CT head to rule out hemorrhage or mass lesion.
   - CT angiography of head and neck to evaluate for large vessel stenosis or occlusion.
   - MRI brain with diffusion-weighted imaging (DWI) within 24 hours to evaluate for acute infarction; DWI positivity would reclassify this as acute ischemic stroke and guide further management.
   - ECG and continuous telemetry to screen for atrial fibrillation.
   - Labs: CBC, BMP, glucose, HbA1c, fasting lipid panel, PT/INR.

2. Antiplatelet therapy:

   - Initiate aspirin 325 mg loading dose now (after hemorrhage excluded on CT), followed by aspirin 81 mg daily plus clopidogrel 300 mg load then 75 mg daily for 21 days, then transition to aspirin monotherapy. Hold dual antiplatelet if atrial fibrillation is identified (anticoagulation would be indicated instead).

3. Blood pressure management:

   - Avoid aggressive acute BP lowering given concern for cerebrovascular event. Permissive hypertension acutely unless BP >220/120 or comorbid indication for urgent treatment. Optimize outpatient BP regimen with goal
---

## Case 7/10 — MTS_0974  ·  Consult - History and Phy.

**Why this case:** Defensive over-ordering: 'increased risk for complications'; physician none, OE ~$1.3k (18 tests).

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient is at increased risk for complications due to diabetes and hypertension, which may be improved with significant weight loss and adjustments to insulin and oral hypoglycemic therapy.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** Hepatitis serologies (HBsAg, anti-HBc, anti-HCV, HCV RNA if indicated), Liver function tests, Abdominal ultrasound with liver elastography, Carotid duplex ultrasound, Echocardiogram, CMP, CBC, HbA1c, Lipid panel, Iron studies, Vitamin B12, Folate, Vitamin D, TSH, Urinalysis, EKG, Polysomnography for OSA screening, Upper endoscopy with H. pylori testing (~$1302; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
PAST MEDICAL HISTORY: , Her medical conditions driving her toward surgery include hypercholesterolemia, hypertension, varicose veins, prior history of stroke.  She denies any history of cancer.  She does have a history of hepatitis which I will need to further investigate.  She complains of multiple joint pains, and heavy snoring.,PAST SURGICAL HISTORY: , Includes hysterectomy in 1995 for fibroids and varicose vein removal.  She had one ovary removed at the time of the hysterectomy as well.,SOCIAL HISTORY:,  She is a single mother of one adopted child.,FAMILY HISTORY:  ,There is a strong family history of heart disease and hypertension, as well as diabetes on both sides of her family.  Her mother is alive.  Her father is deceased from alcohol.  She has five siblings.,MEDICATIONS: , As you know she takes the following medications for her diabetes, insulin 70 units/6 units times four years, aspirin 81 mg a day, Actos 15 mg, Crestor 10 mg and CellCept 500 mg two times a day.,ALLERGIES: , She has no known drug allergies.,PHYSICAL EXAM: , She is a 54-year-old obese female.  She does not appear to have any significant residual deficits from her stroke.  There may be slight left arm weakness.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0974 arm=parsimonious -->

ASSESSMENT:

54-year-old obese woman with type 2 diabetes (on insulin and pioglitazone), prior stroke with residual mild left arm weakness, hypertension, hypercholesterolemia, history of hepatitis (type unspecified), and current use of mycophenolate mofetil (CellCept) 500 mg BID (indication unclear — likely autoimmune condition, needs clarification). She presents with multiple joint pains and heavy snoring, and is being evaluated for possible surgical candidacy.

Three most likely diagnoses:

Degenerative joint disease (osteoarthritis) — Most common cause of multiple joint pains in a 54-year-old obese woman with type 2 diabetes. Obesity and diabetes are independent and synergistic risk factors for OA. No features suggesting inflammatory arthritis are described.

Obstructive sleep apnea (OSA) — Heavy snoring in the setting of obesity, hypertension, diabetes, and prior stroke carries a very high pretest probability for OSA. OSA is an independent cardiovascular risk factor and is underrecognized, particularly in women.

Suboptimally managed cardiometabolic risk / secondary stroke prevention — She has established ASCVD (prior stroke), diabetes, hypertension, and hypercholesterolemia. Current statin (rosuvastatin 10 mg) is moderate-intensity; guidelines recommend high-intensity statin therapy with an LDL-C goal <70 mg/dL for secondary prevention. The indication for pioglitazone is reasonable given its role in secondary stroke prevention, but the indication for mycophenolate is unclear and requires investigation. Aspirin 81 mg is appropriate for secondary prevention.

Can't-miss diagnoses:

Hepatitis B or C reactivation — Patient has a history of hepatitis (type unspecified) and is on mycophenolate, an immunosuppressant with FDA-labeled risk of HBV/HCV viral reactivation. Active viral hepatitis must be excluded.

Underlying autoimmune or systemic disease — The use of mycophenolate in a non-transplant patient suggests an autoimmune condition (e.g., lupus, vasculitis, autoimmune hepatitis, glomerulonephritis) that may itself be contributing to joint pains and requires clarification for safe ongoing management.

Progressive multifocal leukoencephalopathy (PML) — Mild left arm weakness in a patient on mycophenolate warrants consideration, though this is more likely a residual stroke deficit. Any new or progressive neurological symptoms should prompt urgent evaluation.

PLAN:

1. Osteoarthritis

Obtain focused history: which joints, duration, morning stiffness (<30 min favors OA), mechanical vs. inflammatory pattern.

Focused exam of affected joints for bony enlargement, crepitus, effusion, and range of motion.

No imaging needed unless symptoms are severe, monoarticular, or atypical (e.g., concern for inflammatory arthritis).

First-line management: weight loss counseling (even 5% body weight loss reduces knee OA risk by ~50%), structured low-impact exercise program, and trial of acetaminophen. If inadequate, topical NSAIDs preferred over oral NSAIDs given cardiovascular history. Avoid oral NSAIDs if possible given stroke history and likely renal considerations.

2. Obstructive sleep apnea

Administer STOP-Bang questionnaire to quantify risk (likely high-risk given obesity, snoring, hypertension, and history of stroke).

Order home sleep apnea test (HSAT) for diagnostic confirmation. If positive, initiate auto-titrating CPAP.

Reinforce weight loss as a complementary treatment — even modest weight loss improves AHI.

Diagnosing and treating OSA is particularly important in this patient given her established cerebrovascular disease and cardiovascular risk factors.

3. Cardiometabolic risk optimization / secondary stroke prevention

Statin intensification: Rosuvastatin 10 mg is moderate-intensity. Per AHA/ASA secondary stroke prevention guidelines, increase to rosuvastatin 20 mg (or atorvastatin 80 mg) targeting LDL-C <70 mg/dL. Check fasting lipid panel to guide further intensification (add ezetimibe if not at goal).

Blood pressure: Confirm BP is at goal <130/80 mmHg per AHA/ASA guidelines. If not at goal, initiate or uptitrate an ACE inhibitor or ARB (preferred classes for secondary stroke prevention).

Diabetes management: Obtain HbA1c. Target <7%. Pioglitazone is reasonable for secondary stroke prevention in this patient. However, given her established ASCVD, strongly consider adding a GLP-1 receptor agonist (e.g., semaglutide or dulaglutide) or SGLT2 inhibitor for cardiovascular risk reduction, per ADA and AHA/ASA guidelines. These agents would also assist with weight management. Monitor for pioglitazone-related adverse effects (edema, weight gain, fracture risk — particularly relevant in a postmenopausal woman).

Continue aspirin 81 mg daily.

4. Hepatitis history — urgent clarification needed given mycophenolate use

Clarify hepatitis type (A, B, or C) and prior treatment history.

Check hepatitis B serologies (HBsAg, anti-HBs, anti-HBc) and hepatitis C antibody with reflex HCV RNA.

Check LFTs and CBC (the latter also for mycophenolate-related neutropenia monitoring).

Per FDA labeling, patients on mycophenolate with HBV or HCV infection require monitoring for viral reactivation. If active hepatitis is identified, coordinate with the prescribing specialist regarding dose reduction or discontinuation of mycophenolate.

5. Mycophenolate — clarify indication and coordinate care

Determine the indication for CellCept (autoimmune disease, glomerulonephritis, etc.) and identify the prescribing specialist.

Ensure appropriate monitoring is in place: CBC with differential (for neutropenia) and LFTs at regular intervals.

If the indication is autoimmune hepatitis, this has direct implications for hepatitis workup interpretation and management.

6. Follow-up

Return visit in 2–4 weeks to review lab results (lipid panel, HbA1c, hepatitis serologies, CBC, LFTs) and HSAT results.

At that visit, reassess joint symptoms, BP control, and medication tolerability.

Clarify surgical candidacy context and optimize perioperative risk if surgery is being planned.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
PAST MEDICAL HISTORY: , Her medical conditions driving her toward surgery include hypercholesterolemia, hypertension, varicose veins, prior history of stroke.  She denies any history of cancer.  She does have a history of hepatitis which I will need to further investigate.  She complains of multiple joint pains, and heavy snoring.,PAST SURGICAL HISTORY: , Includes hysterectomy in 1995 for fibroids and varicose vein removal.  She had one ovary removed at the time of the hysterectomy as well.,SOCIAL HISTORY:,  She is a single mother of one adopted child.,FAMILY HISTORY:  ,There is a strong family history of heart disease and hypertension, as well as diabetes on both sides of her family.  Her mother is alive.  Her father is deceased from alcohol.  She has five siblings.,MEDICATIONS: , As you know she takes the following medications for her diabetes, insulin 70 units/6 units times four years, aspirin 81 mg a day, Actos 15 mg, Crestor 10 mg and CellCept 500 mg two times a day.,ALLERGIES: , She has no known drug allergies.,PHYSICAL EXAM: , She is a 54-year-old obese female.  She does not appear to have any significant residual deficits from her stroke.  There may be slight left arm weakness.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0974 arm=costaware -->
The note describes a preoperative evaluation (likely for bariatric surgery given the context of obesity and comorbidities "driving her toward surgery"). Below is the Assessment and Plan.

---

**ASSESSMENT:**

This is a 54-year-old obese woman presenting for preoperative evaluation, likely for bariatric surgery, with the following active medical problems:

1. **Morbid obesity** – The primary indication for surgical evaluation. Obesity is contributing to or exacerbating multiple comorbidities including diabetes, hypertension, hypercholesterolemia, obstructive sleep apnea (suggested by heavy snoring), varicose veins, and polyarthralgia.
2. **Type 2 diabetes mellitus on insulin and pioglitazone** – Currently on insulin 70/6 units (likely 70/30 premixed insulin) and Actos 15 mg. She is also on CellCept (mycophenolate mofetil) 500 mg BID, which is an immunosuppressant not typically used for diabetes. The indication for mycophenolate requires clarification — possible indications in a non-transplant patient include an autoimmune condition (e.g., lupus nephritis, autoimmune hepatitis, myasthenia gravis, CNS vasculitis, or other autoimmune/inflammatory disease). The history of stroke, hepatitis, joint pains, and immunosuppressant use raises concern for a possible underlying autoimmune or rheumatologic condition.[1][2][3]
3. **History of stroke** – She is on aspirin 81 mg for secondary prevention. There is possible residual slight left arm weakness. The etiology of her stroke should be clarified, particularly given the use of mycophenolate (CNS vasculitis or lupus cerebrovascular disease are considerations).[4][5][6]
4. **Hypercholesterolemia** – Currently on Crestor (rosuvastatin) 10 mg, which is a low-to-moderate intensity statin. Given her history of stroke (established ASCVD), guidelines recommend high-intensity statin therapy (rosuvastatin 20–40 mg or atorvastatin 40–80 mg) with an LDL-C target [6][7][8]
5. **Hypertension** – No antihypertensive medication is listed. Blood pressure target should be [8]
6. **Suspected obstructive sleep apnea** – Heavy snoring in an obese patient with history of stroke and hypertension is highly suggestive. OSA prevalence approaches 40% in post-stroke patients, and treatment may improve blood pressure control and quality of life.[6][9][10]
7. **History of hepatitis – etiology unclear** – Requires further investigation, particularly given that mycophenolate can cause viral reactivation of HBV or HCV and pioglitazone has rare hepatotoxicity. The hepatitis may also be autoimmune in nature, which could explain the mycophenolate use.[11][12]
8. **Polyarthralgia** – Differential includes osteoarthritis (given obesity), inflammatory arthritis related to an underlying autoimmune condition, or medication-related (mycophenolate can cause acute inflammatory syndrome with arthralgias).[11]
9. **Varicose veins** – Status post prior vein removal; conservative management with weight loss, compression, and leg elevation is appropriate.[13][14]

---

**PLAN:**

**Clarify indication for mycophenolate mofetil:**

- Obtain records from prescribing physician to determine the underlying diagnosis (autoimmune disease, transplant, vasculitis, etc.). This is critical for perioperative risk stratification and medication management.

**Hepatitis workup:**

- Check hepatitis serologies (HBsAg, anti-HBs, anti-HBc, anti-HCV) to determine etiology. If positive, monitor for viral reactivation given immunosuppression with mycophenolate.[11]
- Check liver function tests (AST, ALT, alkaline phosphatase, bilirubin, albumin).

**Laboratory studies (preoperative and chronic disease management):**

- HbA1c, fasting glucose
- Lipid panel (to assess adequacy of statin therapy and guide intensification)
- CBC with differential (monitoring for neutropenia on mycophenolate)[11]
- BMP (renal function, electrolytes)

**Optimize statin therapy:**

- Increase rosuvastatin from 10 mg to **20 mg daily** for high-intensity statin therapy, consistent with secondary stroke prevention guidelines targeting LDL-C [6][7][8]

**Blood pressure management:**

- Confirm current blood pressure and whether she is on any unlisted antihypertensive. If hypertension is uncontrolled, initiate an ACE inhibitor or ARB, which have demonstrated benefit for secondary stroke prevention. Target [8]

**Diabetes management:**

- Obtain HbA1c to assess glycemic control. Consider addition of a **GLP-1 receptor agonist** (e.g., semaglutide or dulaglutide) given her established ASCVD (prior stroke), obesity, and type 2 diabetes — these agents reduce stroke risk by 15–17% and promote weight loss. This would also support weight management goals.[6][15]
- Pioglitazone is reasonable to continue given evidence for recurrent stroke risk reduction in patients with insulin resistance and prior stroke, but weigh against side effects of weight gain and fluid retention, particularly in the context of obesity.[16][17]

**Obstructive sleep apnea evaluation:**

- Refer for **polysomnography or home sleep apnea testing** given heavy snoring, obesity, hypertension, and history of stroke. If confirmed, initiate CPAP therapy.[6][18]

**Polyarthralgia:**

- Focused history and exam to characterize joint symptoms (distribution, inflammatory vs. mechanical features, morning stiffness). If inflammatory features are present, check ESR, CRP, ANA, RF, and anti-CCP, particularly if the underlying autoimmune diagnosis is not yet established.

**Varicose veins:**

- Continue conservative management with compression stockings, leg elevation, exercise, and weight management. Reassess after weight loss.[13][14]

**Follow-up:**

- Return in 4–6 weeks to review laboratory results, blood pressure, and records from the mycophenolate prescriber. Coordinate with the surgical team regarding preoperative optimization and perioperative immunosuppression management.

---

Would you like to explore the perioperative management considerations for bariatric surgery in immunosuppressed patients, including mycophenolate dosing adjustments and infection prophylaxis?

Figure
Practical Approach to Obstructive Sleep Apnea Identification, Evaluation, and Management
Lastra AC, Neborak JM, Mokhlesi B. Diagnosis and Treatment of Obstructive Sleep Apnea. JAMA Internal Medicine. 2025;:2837455. doi:10.1001/jamainternmed.2025.2318.

Figure 1
Secondary Prevention in Patients With Clinical ASCVD
Grundy SM, Stone NJ, Bailey AL, et al. 2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol: Executive Summary: A Report of the American College of Cardiology/American Heart Association Task Force on Clinical Practice Guidelines. Journal of the American College of Cardiology. 2019;73(24):3168-3209. doi:10.1016/j.jacc.2018.11.002.

Figure 1
Secondary Prevention in Patients With Clinical ASCVD
Grundy SM, Stone NJ, Bailey AL, et al. 2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol: A Report of the American College of Cardiology/American Heart Association Task Force on Clinical Practice Guidelines. Journal of the American College of Cardiology. 2019;73(24):e285-e350. doi:10.1016/j.jacc.2018.11.003.

### References

1. Use of Mycophenolate Mofetil in Autoimmune and Renal Diseases. Appel GB, Radhakrishnan J, Ginzler EM. Transplantation. 2005;80(2 Suppl):S265-71. doi:10.1097/01.tp.0000186389.19911.9c.
2. Mycophenolate Mofetil: New Applications for This Immunosuppressant. Moder KG. Annals of Allergy, Asthma & Immunology : Official Publication of the American College of Allergy, Asthma, & Immunology. 2003;90(1):15-19; quiz 20, 78. doi:10.1016/S1081-1206(10)63607-1.
3. Treatment of Neuromyelitis Optica With Mycophenolate Mofetil: Retrospective Analysis of 24 Patients. Jacob A, Matiello M, Weinshenker BG, et al. Archives of Neurology. 2009;66(9):1128-33. doi:10.1001/archneurol.2009.175.
4. Mycophenolate Mofetil as Induction and Maintenance Immunosuppressive Therapy in Adult Primary Central Nervous System Vasculitis: A Prospective Observational Study. Das S, Goswami RP, Sinha D, et al. Clinical Rheumatology. 2023;42(8):2155-2162. doi:10.1007/s10067-023-06602-y.
5. Successful Treatment of Lupus Cerebrovascular Disease With Mycophenolate Mofetil. Higashioka K, Yoshida K, Oryoji K, et al. Internal Medicine (Tokyo, Japan). 2015;54(17):2255-9. doi:10.2169/internalmedicine.54.4582.
6. 2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack: A Guideline From the American Heart Association/American Stroke Association. Kleindorfer DO, Towfighi A, Chaturvedi S, et al. Stroke. 2021;52(7):e364-e467. doi:10.1161/STR.0000000000000375.
7. 2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Blumenthal RS, Morris PB, Gaudino M, et al. Journal of the American College of Cardiology. 2026;:S0735-1097(25)10254-4. doi:10.1016/j.jacc.2025.11.016.
8. Ischemic Stroke Management: Posthospitalization and Transition of Care. Larson ST, Ray BE, Wilbur J. American Family Physician. 2023;108(1):70-77.
9. Sleep Apnoea and Ischaemic Stroke: Current Knowledge and Future Directions. Baillieul S, Dekkers M, Brill AK, et al. The Lancet. Neurology. 2022;21(1):78-88. doi:10.1016/S1474-4422(21)00321-5.
10. Sleep Apnea and Stroke: A Narrative Review. Dharmakulaseelan L, Boulos MI. Chest. 2024;166(4):857-866. doi:10.1016/j.chest.2024.04.028.
11. Mycophenolate mofetil. Food and Drug Administration. Updated date: 2025-12-05.
12. Mixed Hepatocellular-Cholestatic Liver Injury After Pioglitazone Therapy. May LD, Lefkowitch JH, Kram MT, Rubin DE. Annals of Internal Medicine. 2002;136(6):449-52. doi:10.7326/0003-4819-136-6-200203190-00008.
13. Varicose Veins: Diagnosis and Treatment. Raetz J, Wilson M, Collins K. American Family Physician. 2019;99(11):682-688.
14. Nonsurgical Management of Chronic Venous Insufficiency. Fukaya E, Kolluri R. The New England Journal of Medicine. 2024;391(24):2350-2359. doi:10.1056/NEJMcp2310224.
15. American Association of Clinical Endocrinology Consensus Statement: Comprehensive Type 2 Diabetes Management Algorithm - 2023 Update. Samson SL, Vellanki P, Blonde L, et al. Endocrine Practice : Official Journal of the American College of Endocrinology and the American Association of Clinical Endocrinologists. 2023;29(5):305-340. doi:10.1016/j.eprac.2023.02.001.
16. Role of diabetes in stroke: Recent advances in pathophysiology and clinical management. Bradley SA, Spring KJ, Beran RG, et al. Diabetes/Metabolism Research and Reviews. 2022;38(2):e3495. doi:10.1002/dmrr.3495.
17. American Association of Clinical Endocrinology Clinical Practice Guideline: Developing a Diabetes Mellitus Comprehensive Care Plan-2022 Update. Blonde L, Umpierrez GE, Reddy SS, et al. Endocrine Practice : Official Journal of the American College of Endocrinology and the American Association of Clinical Endocrinologists. 2022;28(10):923-1049. doi:10.1016/j.eprac.2022.08.002.
18. Obstructive Sleep Apnea in Adults. Veasey SC, Rosen IM. The New England Journal of Medicine. 2019;380(15):1442-1449. doi:10.1056/NEJMcp1816152.
<!-- RESPONSE_END -->


---

## Case 8/10 — MTS_0255  ·  General Medicine

**Why this case:** High-acuity neuro: right-sided weakness (stroke-like); physician ~$214.

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient presents with right-sided weakness and expressive aphasia concerning for a left MCA stroke or TIA, complicated by a urinary tract infection, dehydration, and uncontrolled type 2 diabetes.

- **Physician's diagnostic orders:** MRI brain, Ultrasound of carotids, Echocardiogram, Urine culture, Hemoglobin A1c

- **OpenEvidence (default prompt) ordered:** head CT, MRI brain with DWI, continuous cardiac monitoring, obtain echocardiogram, monitor glucose every 4-6 hours, obtain urine culture, monitor renal function daily, pneumatic compression devices, repeat neurologic examination every 2 hours for first 24 hours (~$609; physician ~$214)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT:, Right-sided weakness.,HISTORY OF PRESENT ILLNESS:, The patient was doing well until this morning when she was noted to have right-sided arm weakness with speech difficulties. She was subsequently sent to ABC Medical Center for evaluation and treatment. At ABC, the patient was seen by Dr. H including labs and a head CT which is currently pending. The patient has continued to have right-sided arm and hand weakness, and has difficulty expressing herself. She does seem to comprehend words. The daughter states the patient is in the Life Care Center, and she believes this started this morning. The patient denies headache, visual changes, chest pain and shortness of breath. These changes have been constant since onset this morning, have not improved or worsened, and the patient notes no modifying factors.,ALLERGIES:, NO KNOWN DRUG ALLERGIES.,MEDICATIONS:, Medications are taken from the paperwork from Life Care Center and include: Lortab 3-4 times a day for pain, Ativan 0.25 mg by mouth every 12 hours p.r.n. pain, Depakote ER 250 mg p.o. q nightly, Actos 15 mg p.o. t.i.d., Lantus 35 units subcu q nightly, Glipizide 10 mg p.o. q day, Lanoxin 0.125 mg p.o. q day, Lasix 40 mg p.o. q day, Lopressor 50 mg p.o. b.i.d., insulin sliding scale, Lunesta 1 mg p.o. q nightly, Sorbitol 15 mg p.o. q day, Zoloft 50 mg p.o. q nightly, Dulcolax as needed for constipation.,PAST MEDICAL HISTORY:, Significant for moderate to severe aortic stenosis, urinary tract infection, hypertension, chronic kidney disease (although her creatinine is near normal).,SOCIAL HISTORY:, The patient lives at Life Care Center. She does not smoke, drink or use intravenous drugs.,FAMILY HISTORY:, Negative for cerebrovascular accident or cardiac disease.,REVIEW OF SYSTEMS:, As in HPI. Patient and daughter also deny weight loss, fevers, chills, sweats, nausea, vomiting, abdominal pain. She has had some difficulty expressing herself, but seems to comprehend speech as above. The patient has had a history of chronic urinary tract infections and her drainage is similar to past episodes when she has had such infection.,PHYSICAL EXAMINATION:,VITAL SIGNS: The patient is currently with a temperature of 99.1, blood pressure 138/59, pulse 69, respirations 15. She is 95% on room air.,GENERAL: This is a pleasant elderly female who appears stated age, in mild distress.,HEENT: Oropharynx is dry.,NECK: Supple with no jugular venous distention or thyromegaly.,RESPIRATORY: Clear to auscultation. No wheezes, rubs or crackles.,CARDIOVASCULAR: A 4/6 systolic ejection murmur best heard at the 2nd right intercostal space with radiation to the carotids.,ABDOMEN: Soft. Normal bowel sounds.,EXTREMITIES: No clubbing, cyanosis or edema. She does have bilateral above knee amputations.,NEUROLOGIC: Strength 2/5 in her right hand, 4/5 in her left hand. She does have mild right facial droop and an expressive aphasia.,VASCULAR: The patient has good capillary refill in her fingertips.,LABORATORY DATA:, BUN 52, creatinine 1.3. Normal coags. Glucose 220. White blood cell count 10,800. Urinalysis has 608 white cells, 625 RBCs. Head CT is currently pending. EKG shows normal sinus rhythm with mild ST-depression and biphasic T-waves diffusely.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0255 arm=parsimonious -->

### Assessment and Plan

**ASSESSMENT:**

Elderly female nursing home resident presenting with acute-onset right-sided arm/hand weakness (2/5), right facial droop, and expressive aphasia with preserved comprehension, consistent with a left middle cerebral artery (MCA) territory syndrome. Relevant comorbidities include moderate-to-severe aortic stenosis (4/6 SEM with carotid radiation), diabetes mellitus (glucose 220), chronic kidney disease (BUN 52, Cr 1.3), and she is on digoxin (raising concern for underlying atrial fibrillation or heart failure). Concurrent UTI is suggested by urinalysis (608 WBCs, 625 RBCs). Head CT is pending. Normal coagulation studies.

**Three Most Likely Diagnoses:**

1. **Acute ischemic stroke (left MCA territory)** — Most likely. Sudden-onset right hemiparesis with expressive aphasia and right facial droop is the classic presentation of left MCA ischemia. Multiple vascular risk factors (hypertension, diabetes, CKD, aortic stenosis) and use of digoxin (suggesting possible AF or structural heart disease) support a high pretest probability. Deficits have been persistent and non-fluctuating since onset.
2. **Cardioembolic stroke secondary to occult atrial fibrillation or valvular disease** — This is a subtype of #1 rather than a separate entity, but warrants specific mention. The patient is on digoxin and has moderate-to-severe aortic stenosis with a 4/6 murmur. Digoxin use in the absence of documented AF raises the question of paroxysmal AF as the embolic source. Calcific aortic valve disease is also a recognized source of cerebral embolism.
3. **Stroke mimic: hypoglycemia or metabolic encephalopathy** — Less likely given the focal, lateralized deficits and persistent course. However, glucose of 220 mg/dL is notable; severe hyperglycemia can rarely produce focal deficits. Concurrent UTI with low-grade temperature (99.1°F) could exacerbate baseline neurological vulnerability, though this would not typically produce a new dense hemiparesis with aphasia.

**Can't-Miss Diagnoses:**

- **Intracerebral hemorrhage** — Must be excluded by the pending head CT before any antiplatelet or thrombolytic therapy. Hemorrhagic stroke can present identically to ischemic stroke and management differs fundamentally.
- **Seizure with postictal (Todd's) paralysis** — Patient is on valproate, suggesting a seizure history. A postictal state could mimic stroke with unilateral weakness and aphasia. However, no witnessed seizure activity is reported, and deficits have been constant for hours, making this less likely.

---

**PLAN:**

**1. Acute Ischemic Stroke (most likely):**

- **Head CT (pending):** The single most critical test. If no hemorrhage, proceed with acute ischemic stroke pathway.
- **Thrombolysis eligibility:** Determine exact time last known well. If within 4.5 hours and CT shows no hemorrhage or extensive hypodensity, the patient is a candidate for IV alteplase (0.9 mg/kg, max 90 mg). Key eligibility considerations for this patient:
  - Glucose 220 mg/dL — does not preclude alteplase (eligible if glucose >50 mg/dL per AHA/ASA guidelines).
  - CKD with Cr 1.3 and normal coags — not a contraindication.
  - Age >80 in the 3–4.5 hour window is a relative exclusion per 2018 AHA/ASA guidelines; within 3 hours, age is not an exclusion.
  - History of diabetes — relevant only in the 3–4.5 hour window if combined with prior stroke history.
  - If time of onset is uncertain or beyond 4.5 hours, advanced imaging (MRI DWI-FLAIR mismatch or CT perfusion) would be needed to determine extended-window eligibility, but this requires resources that may not be available at this facility; consider transfer if clinically appropriate.
- **Aspirin 325 mg PO** once hemorrhage is excluded (hold 24 hours if alteplase is given).
- **Blood glucose management:** Initiate insulin correction to target glucose
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
CHIEF COMPLAINT:, Right-sided weakness.,HISTORY OF PRESENT ILLNESS:, The patient was doing well until this morning when she was noted to have right-sided arm weakness with speech difficulties. She was subsequently sent to ABC Medical Center for evaluation and treatment. At ABC, the patient was seen by Dr. H including labs and a head CT which is currently pending. The patient has continued to have right-sided arm and hand weakness, and has difficulty expressing herself. She does seem to comprehend words. The daughter states the patient is in the Life Care Center, and she believes this started this morning. The patient denies headache, visual changes, chest pain and shortness of breath. These changes have been constant since onset this morning, have not improved or worsened, and the patient notes no modifying factors.,ALLERGIES:, NO KNOWN DRUG ALLERGIES.,MEDICATIONS:, Medications are taken from the paperwork from Life Care Center and include: Lortab 3-4 times a day for pain, Ativan 0.25 mg by mouth every 12 hours p.r.n. pain, Depakote ER 250 mg p.o. q nightly, Actos 15 mg p.o. t.i.d., Lantus 35 units subcu q nightly, Glipizide 10 mg p.o. q day, Lanoxin 0.125 mg p.o. q day, Lasix 40 mg p.o. q day, Lopressor 50 mg p.o. b.i.d., insulin sliding scale, Lunesta 1 mg p.o. q nightly, Sorbitol 15 mg p.o. q day, Zoloft 50 mg p.o. q nightly, Dulcolax as needed for constipation.,PAST MEDICAL HISTORY:, Significant for moderate to severe aortic stenosis, urinary tract infection, hypertension, chronic kidney disease (although her creatinine is near normal).,SOCIAL HISTORY:, The patient lives at Life Care Center. She does not smoke, drink or use intravenous drugs.,FAMILY HISTORY:, Negative for cerebrovascular accident or cardiac disease.,REVIEW OF SYSTEMS:, As in HPI. Patient and daughter also deny weight loss, fevers, chills, sweats, nausea, vomiting, abdominal pain. She has had some difficulty expressing herself, but seems to comprehend speech as above. The patient has had a history of chronic urinary tract infections and her drainage is similar to past episodes when she has had such infection.,PHYSICAL EXAMINATION:,VITAL SIGNS: The patient is currently with a temperature of 99.1, blood pressure 138/59, pulse 69, respirations 15. She is 95% on room air.,GENERAL: This is a pleasant elderly female who appears stated age, in mild distress.,HEENT: Oropharynx is dry.,NECK: Supple with no jugular venous distention or thyromegaly.,RESPIRATORY: Clear to auscultation. No wheezes, rubs or crackles.,CARDIOVASCULAR: A 4/6 systolic ejection murmur best heard at the 2nd right intercostal space with radiation to the carotids.,ABDOMEN: Soft. Normal bowel sounds.,EXTREMITIES: No clubbing, cyanosis or edema. She does have bilateral above knee amputations.,NEUROLOGIC: Strength 2/5 in her right hand, 4/5 in her left hand. She does have mild right facial droop and an expressive aphasia.,VASCULAR: The patient has good capillary refill in her fingertips.,LABORATORY DATA:, BUN 52, creatinine 1.3. Normal coags. Glucose 220. White blood cell count 10,800. Urinalysis has 608 white cells, 625 RBCs. Head CT is currently pending. EKG shows normal sinus rhythm with mild ST-depression and biphasic T-waves diffusely.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0255 arm=costaware -->
### Assessment and Plan – Acute Ischemic Stroke

ASSESSMENT:

1. Acute ischemic stroke, left middle cerebral artery territory – Presentation with acute-onset right upper extremity weakness (2/5), right facial droop, and expressive aphasia is consistent with a left MCA distribution ischemic stroke. Head CT is pending to rule out hemorrhagic stroke. The patient is on digoxin and has a 4/6 systolic ejection murmur consistent with her known moderate-to-severe aortic stenosis; the EKG shows normal sinus rhythm, though occult atrial fibrillation remains a consideration given her valvular disease and stroke presentation. Cardioembolic etiology (from aortic stenosis-related calcific embolism, occult AF, or both) is the leading suspected mechanism. Time of onset is this morning; exact last-known-well time must be clarified to determine thrombolytic eligibility.
2. Complicated urinary tract infection – Urinalysis with 608 WBCs and 625 RBCs in the setting of low-grade temperature (99.1°F) and history of chronic UTIs is consistent with active UTI. This may also be contributing to the patient's presentation as a stroke mimic or exacerbating factor, though the focal neurologic deficits strongly favor true stroke.
3. Hyperglycemia in the setting of type 2 diabetes mellitus – Glucose 220 mg/dL on presentation. The patient is on Lantus, glipizide, Actos, and a sliding scale. Hyperglycemia in acute stroke is associated with worse outcomes and requires management to a target of 140–180 mg/dL.
4. Moderate-to-severe aortic stenosis – Known history. The 4/6 systolic ejection murmur with radiation to the carotids is consistent. This is a potential embolic source and contributes to overall cardiovascular risk.
5. Chronic kidney disease – BUN 52, creatinine 1.3. Mild elevation; will need to consider renal function in medication dosing and contrast administration.
6. Hypertension – BP 138/59 on presentation. In the acute stroke setting without thrombolytic administration, permissive hypertension up to 220/120 mmHg is appropriate. Current BP does not require acute intervention.

PLAN:

1. Acute ischemic stroke:

   - Clarify exact time of last known well with daughter and Life Care Center staff to determine thrombolytic eligibility (window up to 4.5 hours from onset).
   - Obtain NIHSS score for formal stroke severity assessment.
   - Await head CT results; if no hemorrhage, proceed with stroke protocol.
   - If within thrombolytic window and no contraindications, administer IV alteplase 0.9 mg/kg (max 90 mg), 10% as bolus, remainder over 60 minutes. BP must be maintained
<!-- RESPONSE_END -->


---

## Case 9/10 — MTS_0019  ·  SOAP / Chart / Progress Notes

**Why this case:** Low-acuity, extreme defensive: sleep disruption complaint; physician none, OE ~$1k.

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient has multifactorial sleep disruption characterized primarily by psychophysiologic insomnia, environmental smoking exposure, and daytime sedation from CNS-acting medications.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** Repeat polysomnography in 3 months (~$1010; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
REASON FOR VISIT:,  This 48-year-old woman returns in followup after a full-night sleep study performed to evaluate her for daytime fatigue and insomnia.,HISTORY OF PRESENT ILLNESS: , The patient presented initially to the Pulmonary Clinic with dyspnea on minimal exertion.  At that time, she was evaluated and found to have evidence for sleep disruption and daytime fatigue.  She also complained of nocturnal choking episodes that have since abated over the past several months.  In the meantime, she had been scheduled for an overnight sleep study performed to evaluate her for sleep apnea, returns today to review her study results.,The patient's sleep patterns consist of going to bed between 9.00 and 10.00 p.m. and awakening in the morning between 5.00 and 6.00 a.m.  She reports difficulty in initiating sleep and then recurrent awakenings every 1 to 2 hours throughout the night.  She reports tossing and turning throughout the night and awakening with the sheets in disarray.  She reports that her sleep was much better quality in the sleep laboratory as compared to home.  When she awakens, she might have a dull headache and feels tired in the morning.  Her daughter reports that she has heard the patient talking during sleep and snoring.  There are no apneic episodes.  The patient reports that she used to cough a lot in the middle of the night, but has no longer been doing so in recent weeks.,During the daytime, the patient reports spending a lot of sedentary time reading and watching TV.  She routinely dozes off during these sedentary activities.  She also might nap between 2.00 and 3.00 p.m., and nods off in the evening hours.,The patient smokes perhaps one to two packs of cigarettes per day, particularly after dinner.,She reports that her weight has fluctuated and peaked at 260 pounds approximately 1 year ago.  Since that time, her weight is down by approximately 30 pounds.,The patient is managed in Outpatient Psychiatry and at her Maintenance Clinic.  She takes methadone, trazodone, and Seroquel.,PAST MEDICAL HISTORY:,1.  Depression.,2.  Hepatitis C.,3.  Hypertension.,4.  Inhaled and intravenous drug abuse history.,The patient has a history of smoking two packs per day of cigarettes for approximately 25 pounds.  She also has a history of recurrent atypical chest pain for which she has been evaluated.,FAMILY HISTORY: , As previously documented.,SOCIAL HISTORY:  ,The patient has a history of inhalation on intravenous drug abuse.  She is currently on methadone maintenance.  She is being followed in Psychiatry for depression and substance abuse issues.  She lives with a room-mate.,REVIEW OF SYSTEMS:,  Not contributory.,MEDICATIONS: , Current medications include the following:,1.  Methadone 110 mg by mouth every day.,2.  Paxil 60 mg by mouth every day.,3.  Trazodone 30 mg by mouth nightly.,4.  Seroquel 20 mg by mouth nightly.,5.  Avalide (irbesartan) and hydrochlorothiazide.,6.  Albuterol and Flovent inhalers two puffs by mouth twice a day.,7.  Atrovent as needed.,FINDINGS: , Vital Signs:  Blood pressure 126/84, pulse 67, respiratory rate 18, weight 232 pounds, height 5 feet 8 inches, temperature 97.4 degrees, SaO2 is 99 percent on room air at rest.  HEENT:  Sclerae anicteric.  Conjunctivae pink.  Extraocular movements are intact.  Pupils are equal, round, and reactive to light.  The nasal passages show deviation in the nasal septum to the right.  There is a slight bloody exudate at the right naris.  Some nasal mucosal edema was noted with serous exudate bilaterally.  The jaw is not foreshortened.  The tongue is not large.  Mallampati airway score was 3.  The oropharynx was not shallow.  There is no pharyngeal mucosa hypertrophy.  No tonsillar tissue noted.  The tongue is not large.  Neck is supple.  Thyroid without nodules or masses.  Carotid upstrokes normal.  No bruits.  No jugular venous distention.  Chest is clear to auscultation and percussion.  No wheezing, rales, rhonchi or adventitious sounds.  No prolongation of the expiratory phase.  Cardiac:  PMI not palpable.  Regular rate and rhythm.  S1 and S2 normal.  No murmurs or gallops.  Abdomen:  Nontender.  Bowel sounds normal.  No liver or spleen palpable.  Extremities:  No clubbing or cyanosis.  There is 1+ pretibial edema.  Pulses are 2+ in upper and lower extremities.  Neurologic:  Grossly nonfocal.,LABORATORIES:,  Pulmonary function studies reportedly show a mild restrictive ventilatory defect without obstruction.  Diffusing capacity is well preserved.,An overnight sleep study was performed on this patient at the end of 02/07.  At that time, she reported that her sleep was better in the laboratories compared to home.  She slept for a total sleep time of 398 minutes out of 432 minutes in bed (sleep proficiency 92 percent).  She fell asleep in the middle of latency of less than 1 minute.  She woke up after sleep onset of 34 minutes.  She had stage I sleep that was some elevated at 28 percent of total sleep time, and stage I sleep is predominantly evident in the lateral portion of the night.  The remainders were stage II at 69 percent, stage III and IV at 3 percent of total sleep time.,The patient had no REM sleep.,The patient had no periodic limb movements during sleep.,The patient had no significant sleep-disordered breathing during non-REM sleep with less than one episode per hour.  Oxyhemoglobin saturation remained in the low to mid 90s throughout the night.,Intermittent inspiratory flow limitation compatible with snoring was observed during non-REM sleep.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0019 arm=parsimonious -->
### Assessment and Plan

## ASSESSMENT

**Three Most Likely Diagnoses:**

1. **Medication-induced sleep disruption with REM sleep suppression** — This patient is on multiple REM-suppressing medications: paroxetine (SSRI), methadone (opioid), and trazodone, all of which are known to suppress REM sleep. The complete absence of REM sleep on polysomnography, elevated stage I sleep (28%), reduced slow-wave sleep (3%), and frequent nocturnal awakenings are consistent with a polypharmacy-driven disruption of sleep architecture. Chronic methadone use in particular is associated with decreased N3 and REM sleep. The daytime fatigue, morning headaches, and excessive daytime sleepiness are downstream consequences.
2. **Chronic insomnia disorder** — Difficulty initiating sleep, recurrent awakenings every 1–2 hours, and nonrestorative sleep with daytime impairment meet criteria for chronic insomnia. Contributing factors include depression, sedentary lifestyle, heavy nicotine use (especially after dinner), and suboptimal sleep hygiene (sedentary TV/reading with frequent dozing). The elevated stage I sleep and sleep fragmentation on PSG support this diagnosis.
3. **Upper airway resistance syndrome (UARS)** — Intermittent inspiratory flow limitation compatible with snoring was observed on PSG despite AHI 100 mg) is associated with CSA and ataxic breathing in up to 30% of stable methadone patients. CSA events may have been underdetected on this single-night study, particularly given the absence of REM sleep (when respiratory events may be more prominent).

- **Narcolepsy type 2** — Excessive daytime sleepiness with dozing during sedentary activities and napping could raise concern, though the clinical picture is better explained by medication effects and poor sleep quality. The absence of REM on PSG precludes assessment for sleep-onset REM periods.

---

## PLAN

**1. Medication-induced sleep disruption / REM suppression**

- Coordinate with Psychiatry regarding the cumulative REM-suppressing burden of paroxetine + methadone + trazodone. Discuss whether paroxetine could be switched to mirtazapine, which preserves REM sleep and may improve sleep quality and architecture, while still treating depression.
- Trazodone at 30 mg is a low dose with limited evidence for insomnia efficacy; discuss tapering off if sleep hygiene and other interventions are pursued.
- Quetiapine at 20 mg for sleep has insufficient evidence and carries metabolic risk in an already obese patient; discuss discontinuation with Psychiatry.
- Do not adjust methadone dose, as this is managed by the Maintenance Clinic for opioid use disorder.

**2. Chronic insomnia disorder**

- First-line: Refer for cognitive behavioral therapy for insomnia (CBT-I), which is guideline-recommended as initial treatment and can be delivered via group sessions or digital platforms (low cost).
- Sleep hygiene counseling at this visit: avoid nicotine in the evening (stimulant effect disrupts sleep), eliminate daytime napping, restrict sedentary TV/reading in bed, maintain consistent wake time.
- Avoid prescribing benzodiazepines or Z-drugs given history of substance use disorder.

**3. Upper airway resistance syndrome / snoring**

- Conservative management: continued weight loss (already down 30 lbs — reinforce), lateral sleep positioning, and nasal saline irrigation for mucosal edema/deviated septum.
- No CPAP indicated at this time given AHI
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
REASON FOR VISIT:,  This 48-year-old woman returns in followup after a full-night sleep study performed to evaluate her for daytime fatigue and insomnia.,HISTORY OF PRESENT ILLNESS: , The patient presented initially to the Pulmonary Clinic with dyspnea on minimal exertion.  At that time, she was evaluated and found to have evidence for sleep disruption and daytime fatigue.  She also complained of nocturnal choking episodes that have since abated over the past several months.  In the meantime, she had been scheduled for an overnight sleep study performed to evaluate her for sleep apnea, returns today to review her study results.,The patient's sleep patterns consist of going to bed between 9.00 and 10.00 p.m. and awakening in the morning between 5.00 and 6.00 a.m.  She reports difficulty in initiating sleep and then recurrent awakenings every 1 to 2 hours throughout the night.  She reports tossing and turning throughout the night and awakening with the sheets in disarray.  She reports that her sleep was much better quality in the sleep laboratory as compared to home.  When she awakens, she might have a dull headache and feels tired in the morning.  Her daughter reports that she has heard the patient talking during sleep and snoring.  There are no apneic episodes.  The patient reports that she used to cough a lot in the middle of the night, but has no longer been doing so in recent weeks.,During the daytime, the patient reports spending a lot of sedentary time reading and watching TV.  She routinely dozes off during these sedentary activities.  She also might nap between 2.00 and 3.00 p.m., and nods off in the evening hours.,The patient smokes perhaps one to two packs of cigarettes per day, particularly after dinner.,She reports that her weight has fluctuated and peaked at 260 pounds approximately 1 year ago.  Since that time, her weight is down by approximately 30 pounds.,The patient is managed in Outpatient Psychiatry and at her Maintenance Clinic.  She takes methadone, trazodone, and Seroquel.,PAST MEDICAL HISTORY:,1.  Depression.,2.  Hepatitis C.,3.  Hypertension.,4.  Inhaled and intravenous drug abuse history.,The patient has a history of smoking two packs per day of cigarettes for approximately 25 pounds.  She also has a history of recurrent atypical chest pain for which she has been evaluated.,FAMILY HISTORY: , As previously documented.,SOCIAL HISTORY:  ,The patient has a history of inhalation on intravenous drug abuse.  She is currently on methadone maintenance.  She is being followed in Psychiatry for depression and substance abuse issues.  She lives with a room-mate.,REVIEW OF SYSTEMS:,  Not contributory.,MEDICATIONS: , Current medications include the following:,1.  Methadone 110 mg by mouth every day.,2.  Paxil 60 mg by mouth every day.,3.  Trazodone 30 mg by mouth nightly.,4.  Seroquel 20 mg by mouth nightly.,5.  Avalide (irbesartan) and hydrochlorothiazide.,6.  Albuterol and Flovent inhalers two puffs by mouth twice a day.,7.  Atrovent as needed.,FINDINGS: , Vital Signs:  Blood pressure 126/84, pulse 67, respiratory rate 18, weight 232 pounds, height 5 feet 8 inches, temperature 97.4 degrees, SaO2 is 99 percent on room air at rest.  HEENT:  Sclerae anicteric.  Conjunctivae pink.  Extraocular movements are intact.  Pupils are equal, round, and reactive to light.  The nasal passages show deviation in the nasal septum to the right.  There is a slight bloody exudate at the right naris.  Some nasal mucosal edema was noted with serous exudate bilaterally.  The jaw is not foreshortened.  The tongue is not large.  Mallampati airway score was 3.  The oropharynx was not shallow.  There is no pharyngeal mucosa hypertrophy.  No tonsillar tissue noted.  The tongue is not large.  Neck is supple.  Thyroid without nodules or masses.  Carotid upstrokes normal.  No bruits.  No jugular venous distention.  Chest is clear to auscultation and percussion.  No wheezing, rales, rhonchi or adventitious sounds.  No prolongation of the expiratory phase.  Cardiac:  PMI not palpable.  Regular rate and rhythm.  S1 and S2 normal.  No murmurs or gallops.  Abdomen:  Nontender.  Bowel sounds normal.  No liver or spleen palpable.  Extremities:  No clubbing or cyanosis.  There is 1+ pretibial edema.  Pulses are 2+ in upper and lower extremities.  Neurologic:  Grossly nonfocal.,LABORATORIES:,  Pulmonary function studies reportedly show a mild restrictive ventilatory defect without obstruction.  Diffusing capacity is well preserved.,An overnight sleep study was performed on this patient at the end of 02/07.  At that time, she reported that her sleep was better in the laboratories compared to home.  She slept for a total sleep time of 398 minutes out of 432 minutes in bed (sleep proficiency 92 percent).  She fell asleep in the middle of latency of less than 1 minute.  She woke up after sleep onset of 34 minutes.  She had stage I sleep that was some elevated at 28 percent of total sleep time, and stage I sleep is predominantly evident in the lateral portion of the night.  The remainders were stage II at 69 percent, stage III and IV at 3 percent of total sleep time.,The patient had no REM sleep.,The patient had no periodic limb movements during sleep.,The patient had no significant sleep-disordered breathing during non-REM sleep with less than one episode per hour.  Oxyhemoglobin saturation remained in the low to mid 90s throughout the night.,Intermittent inspiratory flow limitation compatible with snoring was observed during non-REM sleep.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0019 arm=costaware -->
### Assessment and Plan

**ASSESSMENT:**

1. **Chronic insomnia disorder** — The patient meets criteria for chronic insomnia with difficulty initiating sleep, frequent nocturnal awakenings every 1–2 hours, and daytime consequences including fatigue and excessive daytime sleepiness with routine dozing during sedentary activities. Polysomnography (PSG) did not reveal obstructive sleep apnea (AHI
<!-- RESPONSE_END -->


---

## Case 10/10 — MTS_0600  ·  Consult - History and Phy.

**Why this case:** Diagnostic disagreement: possible reactive arthritis (OE diagnosis only 'related' to physician).

<details><summary>Reference context (not part of the prompt — for your eyes)</summary>


- **Physician working diagnosis:** The patient may have had reactive arthritis possibly related to a recent viral or other infection, with no current laboratory or physical examination abnormalities, and the plan is to observe for any recurrence or persistence of symptoms.

- **Physician's diagnostic orders:** (none)

- **OpenEvidence (default prompt) ordered:** Anti-CCP antibodies, Baseline CMP, Hepatic function panel, QuantiFERON-TB Gold, Hepatitis B screening, Hepatitis C screening, Baseline radiographs of hands, wrists, and knees, Monitor CBC every 4-8 weeks initially, Monitor renal function every 4-8 weeks initially (~$360; physician ~$0)

</details>


### Prompt A — Parsimonious + safe  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting that has LIMITED financial and technical resources: diagnostic tests, advanced imaging, and specialist referrals are scarce and costly and should be used only when their result would change management. Practice in the spirit of the Choosing Wisely campaign, delivering high-value, parsimonious care that avoids low-yield testing while never missing a dangerous diagnosis.

Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient, structured as follows:

1. ASSESSMENT:
   - State the THREE most likely diagnoses, most likely first, each with brief clinical reasoning.
   - Then list any "can't-miss" diagnoses: less likely possibilities that could lead to death or serious harm if missed, and that must therefore be actively considered or excluded (for example, for a sudden severe headache, subarachnoid hemorrhage or stroke).

2. PLAN:
   - For each of the three most likely diagnoses, recommend only the initial workup and management whose result would change your decision.
   - Explicitly include the specific test or action needed to exclude each "can't-miss" diagnosis you listed.
   - Do NOT order routine or reflexive tests (for example, broad screening panels) that are unlikely to change management for this patient.
   - Include any necessary medications, referrals, procedures, and follow-up, ordering them only when clearly indicated and choosing the most resource-appropriate option.

CLINICAL NOTE (assessment & plan removed):
HISTORY:  ,We had the pleasure of seeing the patient today in our Pediatric Rheumatology Clinic.  He was sent here with a chief complaint of joint pain in several joints for few months.  This is a 7-year-old white male who has no history of systemic disease, who until 2 months ago, was doing well and 2 months ago, he started to complain of pain in his fingers, elbows, and neck.  At this moment, this is better and is almost gone, but for several months, he was having pain to the point that he would cry at some point.  He is not a complainer according to his mom and he is a very active kid.  There is no history of previous illness to this or had gastrointestinal problems.  He has problems with allergies, especially seasonal allergies and he takes Claritin for it.  Other than that, he has not had any other problem.  Denies any swelling except for that doctor mentioned swelling on his elbow.  There is no history of rash, no stomach pain, no diarrhea, no fevers, no weight loss, no ulcers in his mouth except for canker sores.  No lymphadenopathy, no eye problems, and no urinary problems.,MEDICATIONS: , His medications consist only of Motrin only as needed and Claritin currently for seasonal allergies and rhinitis.,ALLERGIES: , He has no allergies to any drugs.,BIRTH HISTORY:  ,Pregnancy and delivery with no complications.  He has no history of hospitalizations or surgeries.,FAMILY HISTORY: , Positive for arthritis in his grandmother.  No history of pediatric arthritis.  There is history of psoriasis in his dad.,SOCIAL HISTORY: , He lives with mom, dad, brother, sister, and everybody is healthy.  They live in Easton.  They have 4 dogs, 3 cats, 3 mules and no deer.  At school, he is in second grade and he is doing PE without any limitation.,PHYSICAL EXAMINATION: ,VITAL SIGNS:  Temperature is 98.7, pulse is 96, respiratory rate is 24, height is 118.1 cm, weight is 22.1 kg, and blood pressure is 61/44.,GENERAL:  He is alert, active, in no distress, very cooperative.,HEENT:  He has no facial rash.  No lymphadenopathy.  Oral mucosa is clear.  No tonsillitis.  His ear canals are clear and pupils are reactive to light and accommodation.,CHEST:  Clear to auscultation.,HEART:  Regular rhythm and no murmur.,ABDOMEN:  Soft, nontender with no visceromegaly.,MUSCULOSKELETAL:  Shows no limitation in any of his joints or active swelling today.  He has no tenderness either in any of his joints.  Muscle strength is 5/5 in proximal muscles.,LABORATORY DATA:,  Includes an arthritis panel.  It has normal uric acid, sedimentation rate of 2, rheumatoid factor of 6, and antinuclear antibody that is negative and C-reactive protein that is 7.1.  His mother stated that this was done while he was having symptoms.,

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt A between the markers:**

<!-- RESPONSE_START case=MTS_0600 arm=parsimonious -->
## ASSESSMENT

**Three Most Likely Diagnoses:**

1. **Benign arthralgias / joint hypermobility syndrome.** This is the most likely diagnosis. The child has polyarticular pain (fingers, elbows, neck) that is now resolving, with a completely normal exam today — no swelling, tenderness, or limitation of motion. Inflammatory markers are essentially normal (ESR 2, CRP 7.1 mg/L is borderline at most; RF negative, ANA negative). He is active, doing PE without limitation, and has no systemic symptoms. Joint hypermobility is the most common cause of chronic musculoskeletal pain in children referred to pediatric rheumatology, with an average age of symptom onset around 6 years. The absence of inflammatory signs and normal labs strongly favor a non-inflammatory etiology.[1][2][3][4]
2. **Juvenile idiopathic arthritis (JIA), early or resolving.** JIA remains on the differential given the duration of symptoms (approximately 2 months), polyarticular distribution, and the reported elbow swelling noted by the referring physician. However, JIA requires arthritis persisting ≥6 weeks, and the current exam shows no active synovitis, swelling, or limitation. Normal ESR and negative ANA/RF further lower the probability, though these do not exclude JIA, as inflammatory markers can be normal in oligoarticular disease.[5][6][4]
3. **Early psoriatic JIA.** The father's history of psoriasis is notable. Psoriatic JIA can present with oligoarticular or polyarticular joint pain in young children, and in 80% of pediatric cases, arthritis precedes skin disease by 2–3 years. Dactylitis, nail pitting, and enthesitis are supportive features — none of which are documented here. The current absence of active arthritis on exam makes this less likely at present but warrants monitoring.[5][7][8]

**Can't-Miss Diagnoses:**

- **Occult malignancy (e.g., acute leukemia).** Bone and joint pain can be the presenting feature of childhood leukemia, sometimes with normal or near-normal initial labs. The absence of fevers, weight loss, night sweats, limp, bone pain out of proportion to exam, cytopenias, or elevated LDH is reassuring, but a CBC with differential has not been documented.[9][4]

---

## PLAN

**1. Benign arthralgias / joint hypermobility (most likely):**

- Perform a **Beighton score** assessment today to evaluate for generalized joint hypermobility (if not already done during the musculoskeletal exam).
- Continue **ibuprofen as needed** for pain episodes.
- Encourage continued physical activity; if hypermobility is confirmed, provide guidance on joint-protective strengthening exercises and activity modification as needed.
- No imaging or additional labs required at this time given the normal exam.

**2. JIA — watchful waiting:**

- The current exam shows no active arthritis. JIA cannot be diagnosed today.
- Instruct the family to **return promptly if joint swelling, morning stiffness lasting >15 minutes, limp, or functional limitation recurs**, as JIA requires documentation of persistent arthritis ≥6 weeks.[5][10]
- If symptoms recur with objective swelling, obtain **ultrasound of the affected joint(s)** as the initial imaging modality to confirm synovitis.[11]
- Defer ophthalmologic screening for uveitis unless/until JIA is formally diagnosed.

**3. Psoriatic JIA — monitoring:**

- Given the paternal psoriasis history, perform a **focused skin and nail exam** at each visit (scalp, ears, umbilicus, nails for pitting/onycholysis).[5][12]
- No additional workup needed now in the absence of active arthritis, dactylitis, or enthesitis.
- Counsel the family that this family history is relevant and to report any new rash or nail changes.

**4. Excluding occult malignancy:**

- Obtain a **CBC with differential and peripheral smear** if not already done. This is a low-cost, high-value test that can effectively screen for leukemia in a child with unexplained polyarticular pain. If normal, no further workup is needed in the absence of red-flag features.[4]

**Follow-up:**

- Return to clinic in **3 months**, or sooner if symptoms recur with objective joint swelling, new systemic symptoms (fever, weight loss, rash, limp), or functional decline.

---

Would you like to explore the specific clinical features and Beighton score criteria that distinguish symptomatic joint hypermobility from early JIA in the pediatric population?

### References

1. Joint Hypermobility Syndrome: Recognizing a Commonly Overlooked Cause of Chronic Pain. Kumar B, Lenert P. The American Journal of Medicine. 2017;130(6):640-647. doi:10.1016/j.amjmed.2017.02.013.
2. Joint Hypermobility Syndrome in Childhood. A Not So Benign Multisystem Disorder?. Adib N, Davies K, Grahame R, Woo P, Murray KJ. Rheumatology (Oxford, England). 2005;44(6):744-50. doi:10.1093/rheumatology/keh557.
3. Genetic Diseases Mimicking Rheumatic Disorders: Insights From Southeastern Turkey. Akalın A, Karakaş HD, Çelebi C, et al. American Journal of Medical Genetics. Part A. 2025;197(10):e64174. doi:10.1002/ajmg.a.64174.
4. The Child With Joint Pain in Primary Care. Sen ES, Clarke SL, Ramanan AV. Best Practice & Research. Clinical Rheumatology. 2014;28(6):888-906. doi:10.1016/j.berh.2015.04.008.
5. Juvenile Idiopathic Arthritis. Sandborg CI, Schulert GS, Kimura Y. The New England Journal of Medicine. 2025;393(2):162-174. doi:10.1056/NEJMra2402073.
6. Tumor Necrosis Factor (TNF) Inhibitors for Juvenile Idiopathic Arthritis. Cagnotto G, Juhl CB, Ahlström F, et al. The Cochrane Database of Systematic Reviews. 2025;2:CD013715. doi:10.1002/14651858.CD013715.pub2.
7. Joint American Academy of Dermatology-National Psoriasis Foundation Guidelines of Care for the Management and Treatment of Psoriasis in Pediatric Patients. Menter A, Cordoro KM, Davis DMR, et al. Journal of the American Academy of Dermatology. 2020;82(1):161-201. doi:10.1016/j.jaad.2019.08.049.
8. Pediatric Psoriasis Comorbidity Screening Guidelines. Osier E, Wang AS, Tollefson MM, et al. JAMA Dermatology. 2017;153(7):698-704. doi:10.1001/jamadermatol.2017.0499.
9. Differential Diagnosis Portfolio of a Pediatric Rheumatologist: Eight Cases, Eight Stories. Çakan M, Karadağ ŞG, Ayaz NA. Clinical Rheumatology. 2021;40(2):769-774. doi:10.1007/s10067-020-05287-x.
10. 2019 American College of Rheumatology/Arthritis Foundation Guideline for the Treatment of Juvenile Idiopathic Arthritis: Therapeutic Approaches for Non-Systemic Polyarthritis, Sacroiliitis, and Enthesitis. Ringold S, Angeles-Han ST, Beukelman T, et al. Arthritis & Rheumatology (Hoboken, N.J.). 2019;71(6):846-863. doi:10.1002/art.40884.
11. ESR Essentials: Juvenile Idiopathic Arthritis; What Every Radiologist Needs to Know-Practice Recommendations by the European Society of Paediatric Radiology. Costa Dias S, Habre C, Di Paolo PL, et al. European Radiology. 2025;:10.1007/s00330-025-11891-9. doi:10.1007/s00330-025-11891-9.
12. Psoriatic Arthritis. Ritchlin CT, Colbert RA, Gladman DD. The New England Journal of Medicine. 2017;376(10):957-970. doi:10.1056/NEJMra1505557.
<!-- RESPONSE_END -->


### Prompt B — Cost-aware  ·  copy everything in the box into OpenEvidence

```text
You are the physician seeing this patient in a real-world clinical setting. Below is the clinical note from this visit containing the history, exam findings, and available results. The assessment and plan section has been removed.

Write the ASSESSMENT AND PLAN section for this note as you would for a real patient. Include:
1. ASSESSMENT: Your diagnosis/impression with clinical reasoning
2. PLAN: Your recommended next steps including any:
   - Laboratory tests
   - Imaging studies
   - Medications (new prescriptions or adjustments)
   - Referrals or consultations
   - Procedures
   - Follow-up plan

CLINICAL NOTE (assessment & plan removed):
HISTORY:  ,We had the pleasure of seeing the patient today in our Pediatric Rheumatology Clinic.  He was sent here with a chief complaint of joint pain in several joints for few months.  This is a 7-year-old white male who has no history of systemic disease, who until 2 months ago, was doing well and 2 months ago, he started to complain of pain in his fingers, elbows, and neck.  At this moment, this is better and is almost gone, but for several months, he was having pain to the point that he would cry at some point.  He is not a complainer according to his mom and he is a very active kid.  There is no history of previous illness to this or had gastrointestinal problems.  He has problems with allergies, especially seasonal allergies and he takes Claritin for it.  Other than that, he has not had any other problem.  Denies any swelling except for that doctor mentioned swelling on his elbow.  There is no history of rash, no stomach pain, no diarrhea, no fevers, no weight loss, no ulcers in his mouth except for canker sores.  No lymphadenopathy, no eye problems, and no urinary problems.,MEDICATIONS: , His medications consist only of Motrin only as needed and Claritin currently for seasonal allergies and rhinitis.,ALLERGIES: , He has no allergies to any drugs.,BIRTH HISTORY:  ,Pregnancy and delivery with no complications.  He has no history of hospitalizations or surgeries.,FAMILY HISTORY: , Positive for arthritis in his grandmother.  No history of pediatric arthritis.  There is history of psoriasis in his dad.,SOCIAL HISTORY: , He lives with mom, dad, brother, sister, and everybody is healthy.  They live in Easton.  They have 4 dogs, 3 cats, 3 mules and no deer.  At school, he is in second grade and he is doing PE without any limitation.,PHYSICAL EXAMINATION: ,VITAL SIGNS:  Temperature is 98.7, pulse is 96, respiratory rate is 24, height is 118.1 cm, weight is 22.1 kg, and blood pressure is 61/44.,GENERAL:  He is alert, active, in no distress, very cooperative.,HEENT:  He has no facial rash.  No lymphadenopathy.  Oral mucosa is clear.  No tonsillitis.  His ear canals are clear and pupils are reactive to light and accommodation.,CHEST:  Clear to auscultation.,HEART:  Regular rhythm and no murmur.,ABDOMEN:  Soft, nontender with no visceromegaly.,MUSCULOSKELETAL:  Shows no limitation in any of his joints or active swelling today.  He has no tenderness either in any of his joints.  Muscle strength is 5/5 in proximal muscles.,LABORATORY DATA:,  Includes an arthritis panel.  It has normal uric acid, sedimentation rate of 2, rheumatoid factor of 6, and antinuclear antibody that is negative and C-reactive protein that is 7.1.  His mother stated that this was done while he was having symptoms.,

Practice cost-conscious, high-value care: Order laboratory tests, imaging studies, medications, referrals, and procedures only when they are clinically necessary and cost-effective; avoid low-value care that is unlikely to change management.

Write the ASSESSMENT AND PLAN section now.
```

**Paste OpenEvidence's response for Prompt B between the markers:**

<!-- RESPONSE_START case=MTS_0600 arm=costaware -->
**ASSESSMENT AND PLAN**

**Assessment:**

This is a 7-year-old male presenting with a several-month history of polyarticular joint pain involving the fingers, elbows, and neck, now largely resolved. The examination today is unremarkable with no active synovitis, joint swelling, limitation of motion, or tenderness. Laboratory workup obtained during symptomatic period shows a normal ESR (2), negative ANA, negative rheumatoid factor, and normal uric acid. CRP is mildly elevated at 7.1, though this is a nonspecific finding.

The differential includes:

- **Reactive arthritis / post-viral arthralgia** — most likely given the self-limited course, polyarticular distribution, and near-complete resolution without treatment. No preceding illness was identified, though subclinical viral infection is possible.
- **Juvenile idiopathic arthritis (JIA)** — must remain on the differential, as JIA requires 6 weeks of objective arthritis for diagnosis. The absence of documented joint swelling (other than a possible elbow effusion noted by the referring physician), negative ANA, negative RF, and current normal exam make this less likely at this time, but it cannot be excluded. Notably, the family history of psoriasis in the father raises the possibility of psoriatic-type JIA if symptoms recur.
- **Mechanical/overuse pain** — possible in an active child, though the multi-joint involvement and severity (crying with pain) argue against this.

At present, there is no objective evidence of active inflammatory arthritis. The clinical picture is most consistent with a self-limited process, but close monitoring is warranted given the family history of psoriasis and the possibility of early or intermittent JIA.

**Plan:**

1. **Ophthalmology referral** for a baseline slit-lamp examination to screen for uveitis, given the age, joint complaints, and need to exclude subclinical eye inflammation — particularly relevant if JIA is being considered.
2. **Medications:** Continue ibuprofen as needed for any recurrent joint pain. Continue loratadine for seasonal allergies. No new medications indicated at this time.
3. **Monitoring and return precautions:** Parents counseled to monitor closely for any recurrence of joint pain, new joint swelling, morning stiffness lasting >15 minutes, limping, rash (particularly psoriasiform lesions given paternal history), fever, or eye redness/pain. If any of these develop, they should contact the clinic promptly rather than waiting for the scheduled follow-up.
4. **Follow-up:** Return to Pediatric Rheumatology in **3 months**, or sooner if symptoms recur. If symptoms return with objective joint swelling, repeat inflammatory markers (CBC with differential, ESR, CRP) and consider HLA-B27 testing at that time to further risk-stratify. No additional laboratory testing or imaging is indicated today given the normal examination.

---

Would you like to explore the diagnostic criteria and early features that distinguish psoriatic JIA from other JIA subtypes, particularly in the context of a first-degree relative with psoriasis?
<!-- RESPONSE_END -->


---
