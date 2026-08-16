#!/usr/bin/env python3
"""
Review of MTSamples physician plans for current guideline adherence.
Assesses whether the ~mid-2000s treatment plans would be the same today (2026).

Scoring:
1 = Fully current — plan would be essentially the same today
2 = Mostly current — minor updates possible, core approach unchanged
3 = Partially outdated — some elements have changed but core approach may still be valid
4 = Significantly outdated — major treatment elements have changed
5 = Substantially outdated — current standard of care is fundamentally different
"""

import pandas as pd

df = pd.read_excel('paper/Supplementary_Table_1.xlsx')

# Each entry: (score, comment, current_plan_if_changed)
# current_plan_if_changed is only filled if score >= 3

assessments = {}

# ============================================================
# CASE 0: MTS_0001 — Uterine Papillary Serous Carcinoma
# Follow-up q3mo, CT q6mo x 2yr
assessments[0] = (2,
    "Surveillance approach is still broadly appropriate. Current NCCN guidelines recommend imaging every 3-6 months for the first 2-3 years. Consider PET/CT rather than CT alone for high-grade serous histology.",
    "")

# CASE 1: MTS_0002 — Wound Check Post APR
# Ileostomy care, BRAT diet, Percocet refill
assessments[1] = (3,
    "Ileostomy care and dietary counseling remain appropriate. Percocet refill for occasional post-surgical pain is outdated: current guidelines emphasize non-opioid alternatives (NSAIDs, acetaminophen) first, with opioids only for short courses when needed.",
    "Continue ileostomy care and dietary counseling. For occasional pain: ibuprofen 400-600mg PRN or acetaminophen 500-1000mg PRN. Avoid routine opioid refills for chronic post-surgical pain.")

# CASE 2: MTS_0003 — Weight Loss on Phentermine
assessments[2] = (4,
    "Phentermine monotherapy with a plateau is significantly outdated. GLP-1 receptor agonists (semaglutide/Wegovy, tirzepatide/Zepbound) are now preferred for sustained weight loss with superior efficacy data. Phentermine/topiramate (Qsymia) is another option.",
    "Discuss transitioning from phentermine to a GLP-1 receptor agonist (semaglutide 2.4mg weekly or tirzepatide) for more effective and sustained weight loss. These agents show 15-22% body weight reduction vs 5-7% for phentermine.")

# CASE 3: MTS_0004 — Wasp Sting
# Solu-Medrol IM, Benadryl, ice
assessments[3] = (2,
    "Acute treatment with IM corticosteroid and antihistamine for local reaction is still appropriate. Today would also consider prescribing an epinephrine auto-injector if any systemic symptoms, and referral to allergist for venom testing.",
    "")

# CASE 4: MTS_0005 — Tethered Cord Evaluation
assessments[4] = (1,
    "MRI for tethered cord evaluation is still the gold standard. Plan is current.",
    "")

# CASE 5: MTS_0006 — URI
# Symptomatic treatment with Levall
assessments[5] = (1,
    "Symptomatic treatment for viral URI is still the standard approach. Supportive care with fluids, rest, and OTC symptomatic relief remains appropriate.",
    "")

# CASE 6: MTS_0008 — Three-Week Postpartum Checkup
# Allegra, Patanol, ProctoFoam HC, Micronor
assessments[6] = (2,
    "Medications are still appropriate. Micronor (norethindrone) is reasonable for breastfeeding contraception. Today would more strongly discuss LARC options (IUD, implant) as preferred postpartum contraception per ACOG.",
    "")

# CASE 7: MTS_0010 — Thrombocytopenia (ITP)
# Prednisone taper, bisphosphonate, weekly CBC
assessments[7] = (2,
    "Prednisone taper for ITP is still first-line. Today TPO-receptor agonists (eltrombopag, romiplostim) are available as second-line and may be considered earlier. Weekly CBC monitoring is appropriate.",
    "")

# CASE 8: MTS_0013 — Substance Abuse (IV heroin)
# Fluoxetine only, refuses to prescribe MAT
assessments[8] = (5,
    "SUBSTANTIALLY OUTDATED. The physician's refusal to prescribe MAT ('I am not in the practice of trading one addiction for another') directly contradicts current evidence and guidelines. Medication-assisted treatment with buprenorphine or methadone is now the standard of care for opioid use disorder (ASAM, SAMHSA, APA). Untreated OUD has high mortality. Additionally, naloxone should be prescribed, and HIV/HepB/HepC screening is mandatory for IV drug users (USPSTF).",
    "1. Initiate MAT: buprenorphine-naloxone (Suboxone) or refer for methadone maintenance. 2. Prescribe naloxone (Narcan) rescue kit. 3. Screen for HIV, Hepatitis B, and Hepatitis C (USPSTF A recommendation for IVDU). 4. CBC, CMP (patient has single kidney). 5. Fluoxetine for depression can continue. 6. Refer to comprehensive SUD treatment program. 7. Harm reduction counseling.")

# CASE 9: MTS_0017 — Carpal Tunnel Syndrome
# Anaprox + wrist splint, plan for EMG if no improvement
assessments[9] = (1,
    "NSAID + wrist splint as initial treatment for CTS is still first-line. Conditional EMG for persistent symptoms is still standard.",
    "")

# CASE 10: MTS_0018 — Temporal Mass (probable GBM)
# Craniotomy with biopsy/resection planned
assessments[10] = (2,
    "Surgical resection for probable GBM is still first-line. Today would also plan for molecular profiling (IDH mutation, MGMT methylation, 1p/19q codeletion) and discuss temozolomide + radiation (Stupp protocol) and tumor-treating fields (Optune).",
    "")

# CASE 11: MTS_0019 — Sleep Study Followup
# Insomnia counseling, environmental factors
assessments[11] = (2,
    "Sleep hygiene and environmental modification counseling still appropriate. Today CBT-I (cognitive behavioral therapy for insomnia) is explicitly recommended as first-line treatment for chronic insomnia per AASM guidelines, before pharmacotherapy.",
    "")

# CASE 12: MTS_0021 — Sleep Apnea
# CPAP, weight loss, ENT referral for nasal obstruction
assessments[12] = (1,
    "CPAP management, weight loss counseling, and ENT evaluation for nasal obstruction all remain current standard of care.",
    "")

# CASE 13: MTS_0022 — Refractory Hypertension Followup
assessments[13] = (2,
    "Hypertension management approach is still appropriate. Blood pressure targets have been lowered (ACC/AHA 2017: <130/80 vs old <140/90). Otherwise follow-up approach is current.",
    "")

# CASE 14: MTS_0023 — Sexual Dysfunction
# Testosterone level, Cialis sample
assessments[14] = (1,
    "PDE5 inhibitor (tadalafil/Cialis) and testosterone testing for ED with decreased desire is still first-line per AUA guidelines.",
    "")

# CASE 15: MTS_0024 — Epicondylitis/Lupus
# Kenalog injection, CBC/UA, consider methotrexate
assessments[15] = (2,
    "Local steroid injection for epicondylitis and considering methotrexate for lupus flare are still appropriate. Today belimumab (Benlysta) is available as an add-on for active SLE. Anifrolumab (Saphnelo) is also now available.",
    "")

# CASE 16: MTS_0025 — COPD/Emphysema Followup
assessments[16] = (2,
    "Continuing current respiratory medications and oxygen use with activity/sleep is still appropriate. Would now verify GOLD-concordant therapy (LAMA/LABA ± ICS based on exacerbation history) and ensure up-to-date vaccinations (influenza, pneumococcal, COVID-19, RSV).",
    "")

# CASE 17: MTS_0026 — Rotator Cuff Tear + Cervical Stenosis
assessments[17] = (1,
    "Surgical plan for rotator cuff repair and conservative management with epidural steroid injection for cervical radiculopathy are still current approaches.",
    "")

# CASE 18: MTS_0027 — ADHD Medication Recheck
# Adderall XR 15mg AM + Adderall 5mg PM
assessments[18] = (1,
    "Amphetamine-based ADHD medications (Adderall XR + short-acting booster) remain first-line. Dose titration approach is appropriate.",
    "")

# CASE 19: MTS_0028 — Lupus with Pneumonitis Followup
assessments[19] = (2,
    "Conservative monitoring with PFTs and CT follow-up for stable lupus pneumonitis is still appropriate. Today might also consider mycophenolate or rituximab if progression occurs.",
    "")

# CASE 20: MTS_0035 — Prostate Fossa Irradiation Followup
assessments[20] = (1,
    "Post-radiation surveillance for prostate cancer with PSA monitoring remains standard.",
    "")

# CASE 21: MTS_0037 — Liver Cirrhosis
# Inderal for portal HTN, hepatitis panel, AFP, ANA, INR
assessments[21] = (3,
    "Workup for cirrhosis etiology is appropriate. However, carvedilol is now generally preferred over propranolol for portal hypertension (AASLD). Would also screen for MASLD (metabolic-associated steatotic liver disease, formerly NAFLD), check anti-smooth muscle antibodies for autoimmune hepatitis, and consider FibroScan.",
    "Switch propranolol to carvedilol 6.25mg BID (titrate to HR 55-60). Add screening for MASLD and autoimmune hepatitis (anti-smooth muscle antibodies, anti-LKM). Consider FibroScan for fibrosis staging. Continue AFP, hepatitis panel, INR.")

# CASE 22: MTS_0041 — Polycythemia Vera/JAK2+ MPN
# Seeking JAK inhibitor trial
assessments[22] = (1,
    "This plan was actually ahead of its time. Ruxolitinib (Jakafi, approved 2011) and other JAK inhibitors are now standard therapy for MPN. The plan to seek a JAK inhibitor trial was prescient.",
    "")

# CASE 23: MTS_0042 — Plantar Fasciitis
assessments[23] = (1,
    "Steroid injection, strapping, and heel lift for plantar fasciitis remain current first-line treatments.",
    "")

# CASE 24: MTS_0043 — Post-Transplant DLBCL
# 6th cycle chemo, PET scan, CBC/CMP/LDH follow-up
assessments[24] = (1,
    "PET scan for response assessment after completing chemotherapy for DLBCL remains standard per NCCN guidelines.",
    "")

# CASE 25: MTS_0050 — Insect Bite with Lymphangitis
# Duricef x7 days
assessments[25] = (1,
    "First-generation cephalosporin (cefadroxil/Duricef) for skin/soft tissue infection with lymphangitis remains appropriate.",
    "")

# CASE 26: MTS_0052 — ORIF Followup
assessments[26] = (1,
    "Post-operative ROM exercises and non-weightbearing status are standard post-ORIF care.",
    "")

# CASE 27: MTS_0059 — ICU: Respiratory Arrest/COPD Exacerbation
assessments[27] = (2,
    "ICU management of COPD exacerbation with mechanical ventilation, IV antibiotics, and electrolyte repletion is still appropriate. TPN initiation may be questioned earlier today (enteral nutrition preferred when possible).",
    "")

# CASE 28: MTS_0060 — Alzheimer's + Multiple Problems
# Aricept 10mg, digoxin level, nutritional supplement
assessments[28] = (3,
    "Donepezil (Aricept) is still used for Alzheimer's. However, anti-amyloid antibodies (lecanemab/Leqembi, approved 2023) are now available for early-stage AD. Digoxin for AF rate control is less favored today (beta-blockers preferred). Digoxin monitoring is still necessary if continued. Consider whether lecanemab is appropriate based on disease stage.",
    "Continue donepezil. Evaluate eligibility for lecanemab (Leqembi) if early-stage AD. Re-evaluate need for digoxin for AF — consider beta-blocker if tolerated. Continue nutritional support. Ensure vitamin B12 repletion and osteoporosis treatment.")

# CASE 29: MTS_0062 — Mantle Cell Lymphoma, Remission
assessments[29] = (1,
    "Post-transplant surveillance approach for MCL in remission at 4.5 years is reasonable. Iron supplementation for anemia with hematochezia is appropriate.",
    "")

# CASE 30: MTS_0068 — Statin-Related Leg Pain
# Stop Lipitor, check CMP/lipids/A1c, consider Crestor
assessments[30] = (1,
    "Switching statins for myalgia (from atorvastatin to rosuvastatin) and checking labs is still an appropriate clinical approach.",
    "")

# CASE 31: MTS_0070 — Lap Band Adjustment
assessments[31] = (3,
    "Lap-Band (adjustable gastric band) has largely fallen out of favor due to high complication and reoperation rates. Sleeve gastrectomy is now the most common bariatric procedure. If the patient is experiencing inadequate weight loss or band complications, conversion to sleeve gastrectomy or Roux-en-Y would now be discussed. GLP-1 receptor agonists are also a pharmacological alternative.",
    "For ongoing weight management, discuss: 1) GLP-1 RA therapy (semaglutide, tirzepatide) as adjunct or alternative, 2) If band complications or inadequate loss, consider conversion to sleeve gastrectomy. Lap-Band revision/adjustment if still functioning well.")

# CASE 32: MTS_0072 — Post-Lobectomy Lung Cancer Followup
# CT in 6mo, US for DVT, nifedipine for esophageal spasm
assessments[32] = (2,
    "Follow-up CT and DVT screening are still appropriate. Nifedipine for esophageal spasm is less commonly used; smooth muscle relaxants and PPI are alternatives. Low-dose CT surveillance per NCCN is current.",
    "")

# CASE 33: MTS_0076 — HIV on Trizivir, HepC stable
assessments[33] = (5,
    "SUBSTANTIALLY OUTDATED. 1) Trizivir (AZT/3TC/abacavir) is an obsolete triple-NRTI regimen. Current ART uses integrase inhibitor-based regimens (bictegravir/emtricitabine/TAF = Biktarvy, or dolutegravir-based). HLA-B*5701 testing required before abacavir. 2) Hepatitis C: 'stable transaminases' monitoring is no longer acceptable. HCV is now CURABLE with 8-12 weeks of direct-acting antiviral therapy (sofosbuvir/velpatasvir = Epclusa). All patients with HCV should be treated.",
    "1. Switch ART to modern integrase inhibitor-based regimen (e.g., Biktarvy = bictegravir/emtricitabine/TAF) after HLA-B*5701 testing if continuing abacavir. 2. CURE hepatitis C: initiate DAA therapy (sofosbuvir/velpatasvir x 12 weeks). 3. Viral load and CD4 monitoring per current DHHS guidelines. 4. Screen for HCV treatment eligibility (check genotype, fibrosis staging).")

# CASE 34: MTS_0077 — URI, Tinea, Wart, Hyperlipidemia, Tobacco
# Amoxicillin for persistent URI, PSA screening
assessments[34] = (3,
    "1) Amoxicillin for 'persistent URI' — current guidelines recommend against antibiotics for most viral URIs even if persistent. 2) Routine PSA screening is no longer recommended by USPSTF; shared decision-making is required (Grade C for men 55-69). 3) Tobacco cessation counseling should include pharmacotherapy options (varenicline, NRT).",
    "Avoid antibiotics for viral URI. PSA screening only with shared decision-making discussion. Add tobacco cessation pharmacotherapy (varenicline preferred). Continue Nizoral for tinea and liquid nitrogen for wart.")

# CASE 35: MTS_0078 — Weight Loss, Depression, Dementia
assessments[35] = (2,
    "Conservative monitoring approach is reasonable for this complex elderly patient. Would now consider newer dementia therapies (lecanemab) if early-stage, and ensure falls risk assessment.",
    "")

# CASE 36: MTS_0079 — Hematuria on Coumadin
# Stopping Coumadin, starting aspirin 81mg, Lortab for pain
assessments[36] = (4,
    "SIGNIFICANTLY OUTDATED. 1) Stopping warfarin for AF and substituting aspirin alone provides inadequate stroke prevention. After hematuria workup, should restart anticoagulation with a DOAC (apixaban or rivaroxaban) which has lower bleeding risk. 2) Lortab for chronic non-cancer pain contradicts current CDC opioid guidelines. 3) BPH evaluation for hematuria is still appropriate.",
    "1. Evaluate hematuria (UA, urology referral for cystoscopy if indicated). 2. After resolution, restart anticoagulation with DOAC (apixaban 5mg BID) instead of aspirin alone. 3. For pain: acetaminophen, topical NSAIDs, physical therapy — avoid chronic opioids. 4. Continue BPH evaluation.")

# CASE 37: MTS_0081 — C. diff, Thrush, CAD
# Diflucan for thrush, finishing metronidazole for C. diff
assessments[37] = (3,
    "Metronidazole for C. difficile is now second-line. IDSA/SHEA 2021 guidelines recommend oral vancomycin 125mg QID x 10 days or fidaxomicin 200mg BID x 10 days as first-line. Diflucan for oral thrush remains appropriate.",
    "Switch from metronidazole to oral vancomycin 125mg QID or fidaxomicin 200mg BID for C. difficile. Continue fluconazole for thrush.")

# CASE 38: MTS_0082 — SLE, CTS, URI
# Wrist splint, azithromycin for URI, Robitussin, Atarax
assessments[38] = (3,
    "Azithromycin for viral URI is no longer recommended (antibiotic stewardship). Wrist splint for CTS is still appropriate. Atarax (hydroxyzine) as antihistamine is still used.",
    "Avoid azithromycin for viral URI — supportive care only (OTC decongestants, antipyretics). Continue wrist splint for CTS. OTC antihistamines acceptable for URI symptoms.")

# CASE 39: MTS_0083 — Febrile Seizure
assessments[39] = (1,
    "Admission for observation and temperature control after febrile seizure in a child is still appropriate.",
    "")

# CASE 40: MTS_0084 — Inpatient: SBO, Pulmonary Fibrosis, Leukocytosis
assessments[40] = (2,
    "Inpatient management approach for these conditions is still broadly appropriate. Anti-fibrotic agents (nintedanib, pirfenidone) now available for IPF if applicable.",
    "")

# CASE 41: MTS_0085 — DM2, HTN, CAD post-CABG, Hyperlipidemia
# Follow-up labs, mammogram
assessments[41] = (3,
    "In a patient with diabetes, CAD, and CKD (renal azotemia), current guidelines strongly recommend adding an SGLT2 inhibitor (empagliflozin or dapagliflozin) for cardiorenal protection, regardless of A1c. GLP-1 RA is also indicated for CV risk reduction. The term 'NIDDM' is obsolete (now 'Type 2 DM').",
    "Add SGLT2 inhibitor (empagliflozin 10mg daily or dapagliflozin 10mg daily) for cardiorenal protection. Consider GLP-1 RA for CV risk reduction. Continue current medications. Mammogram still appropriate.")

# CASE 42: MTS_0089 — Palpitations, Anxiety, GI symptoms
# Ativan 0.5mg TID PRN
assessments[42] = (3,
    "Benzodiazepines (Ativan/lorazepam) are no longer recommended as first-line for anxiety disorders. Current guidelines (APA) recommend SSRIs or SNRIs. Short-term benzodiazepine use in acute settings may still be acceptable, but prescription for ongoing TID use is concerning.",
    "For anxiety: start SSRI (sertraline 50mg daily) or SNRI as first-line. Reserve benzodiazepines for short-term crisis management only. Comprehensive workup (labs, stress test) still appropriate.")

# CASE 43: MTS_0091 — Left Leg Swelling, Shoulder Pain, Obesity
# Venous Doppler, labs, Detrol, Mobic
assessments[43] = (2,
    "Venous Doppler and lab workup are still appropriate. Mobic (meloxicam) still used. Detrol (tolterodine) for frequency still appropriate, though mirabegron (Myrbetriq) is a newer option with fewer anticholinergic side effects. Would now also discuss GLP-1 RA for obesity.",
    "")

# CASE 44: MTS_0093 — Pediatric: Vomiting from Raw Vegetables
assessments[44] = (1,
    "Conservative approach with dietary avoidance and monitoring is still appropriate.",
    "")

# CASE 45: MTS_0094 — Pediatric: Viral Gastroenteritis
assessments[45] = (2,
    "Supportive care is appropriate. Would now recommend oral rehydration solution (Pedialyte) rather than Gatorade, which has excessive sugar and inadequate electrolytes for pediatric rehydration.",
    "")

# CASE 46: MTS_0095 — Weight Gain, HTN, Lipids, Rectal Bleeding
# Labs, sleep study recommended
assessments[46] = (2,
    "Lab workup is still appropriate. Minor updates: colon cancer screening now starts at age 45 (USPSTF 2021, previously 50). FIT test preferred over guaiac-based FOBT. Sleep study referral for suspected OSA is still appropriate.",
    "")

# CASE 47: MTS_0096 — Severe Anxiety, Multiple Comorbidities
# Klonopin 6mg AM + 8mg PM
assessments[47] = (4,
    "SIGNIFICANTLY OUTDATED. Clonazepam 14mg/day is an extraordinarily high and dangerous dose. Current guidelines strongly advise against high-dose benzodiazepines, especially with chronic renal failure (increased risk of accumulation). FDA has issued black box warnings about benzodiazepine risks. SSRIs/SNRIs are first-line for anxiety disorders.",
    "Initiate gradual benzodiazepine taper (10-25% reduction every 2-4 weeks) with concurrent SSRI/SNRI initiation (e.g., sertraline, venlafaxine). Target elimination of benzodiazepines. Consider gabapentin or buspirone as adjunct. Monitor closely given CRF.")

# CASE 48: MTS_0097 — Sepsis/UTI, Cardiomyopathy, DM2, PE on Coumadin
assessments[48] = (3,
    "Antibiotic management based on culture is appropriate. However, for AF/PE management, warfarin should be transitioned to a DOAC (apixaban) for more stable anticoagulation and fewer drug interactions. Uncontrolled DM2 should have treatment intensification with GLP-1 RA or SGLT2i.",
    "After acute infection resolves: transition warfarin to apixaban 5mg BID for PE/AF. Intensify diabetes management with SGLT2i (dapagliflozin has cardiac benefit). Continue doripenem per culture.")

# CASE 49: MTS_0098 — Rhabdomyolysis from Statin + Gemfibrozil
assessments[49] = (1,
    "Immediate discontinuation of the offending agents, IV fluid resuscitation, and monitoring is still the correct approach for statin-induced rhabdomyolysis.",
    "")

# CASE 50: MTS_0100 — HTN, Compression Fracture, OA
# CRP-cardiac, Fosamax, colonoscopy
assessments[50] = (2,
    "Lab workup and colonoscopy screening are appropriate. Fosamax (alendronate) for osteoporosis remains first-line. hs-CRP for cardiac risk stratification has modest evidence.",
    "")

# CASE 51: MTS_0102 — Foot Pain (Drug-Seeking Behavior)
assessments[51] = (2,
    "Identification of drug-seeking behavior is appropriate. Today, PDMP (prescription drug monitoring program) would be checked before prescribing. The decision to not prescribe more opioids is current practice.",
    "")

# CASE 52: MTS_0103 — FUO, Dehydration, BPH
# DVT prophylaxis with subQ heparin
assessments[52] = (2,
    "LMWH (enoxaparin) is now generally preferred over unfractionated heparin for DVT prophylaxis in hospitalized medical patients. Otherwise management appropriate.",
    "")

# CASE 53: MTS_0106 — DM2, HTN, Hyperlipidemia
# A1c, BMP, lipids, CPK, LFTs, microalbumin, mammogram
assessments[53] = (3,
    "Lab workup is comprehensive and still relevant. In a patient with DM2, HTN, and hyperlipidemia, current guidelines strongly recommend SGLT2 inhibitor or GLP-1 RA for cardiorenal protection beyond glycemic control.",
    "Add SGLT2 inhibitor (empagliflozin or dapagliflozin) or GLP-1 RA (semaglutide) given DM2 with cardiovascular risk factors. Continue current workup. Ibuprofen for shoulder pain still appropriate short-term.")

# CASE 54: MTS_0108 — Fifth Disease + Sinusitis
# Omnicef x10 days
assessments[54] = (3,
    "Cefdinir (Omnicef) is not first-line for acute bacterial sinusitis; amoxicillin or amoxicillin-clavulanate is preferred (IDSA 2012). Current guidelines also recommend watchful waiting for uncomplicated sinusitis before starting antibiotics.",
    "If antibiotics needed: amoxicillin-clavulanate (first-line per IDSA). Consider watchful waiting first if symptoms <10 days and not severe.")

# CASE 55: MTS_0109 — Gastric Bypass Pre-op Eval
assessments[55] = (2,
    "Pre-operative evaluation and risk discussion for bariatric surgery is still appropriate. Sleeve gastrectomy is now more common than Roux-en-Y as the primary procedure, but both are offered.",
    "")

# CASE 56: MTS_0112 — Post-ORIF Followup
assessments[56] = (1,
    "Physical therapy and progressive weight-bearing are standard post-ORIF care.",
    "")

# CASE 57: MTS_0113 — Dietary Consult for Weight Reduction
assessments[57] = (2,
    "Dietary counseling approach is still valid. Would now also discuss pharmacological options (GLP-1 RAs) for patients with BMI ≥30 or ≥27 with comorbidities.",
    "")

# CASE 58: MTS_0117 — Down Syndrome, Onychomycosis, Hypothyroidism
# Lamisil, ALT/TSH monitoring
assessments[58] = (1,
    "Terbinafine (Lamisil) for onychomycosis with hepatic monitoring remains current. TSH monitoring for hypothyroidism is standard.",
    "")

# CASE 59-64: Dietary consults — all essentially current
for i in range(59, 65):
    assessments[i] = (1,
        "Dietary counseling approach remains current. Individualized nutrition therapy is still the standard for weight management and diabetes dietary education.",
        "")

# CASE 65: MTS_0124 — Diabetes with Morning Hypoglycemia
# Adjusting Lantus timing and dose
assessments[65] = (2,
    "Insulin dose adjustment for hypoglycemia is still appropriate. Newer basal insulins (insulin degludec/Tresiba, insulin glargine U-300/Toujeo) have lower hypoglycemia risk and more stable pharmacokinetics.",
    "")

# CASE 66: MTS_0125 — Diabetes Education
assessments[66] = (1,
    "Diabetes self-management education and blood glucose monitoring remain standard care.",
    "")

# CASE 67: MTS_0130 — Deviated Septum Repair Followup
assessments[67] = (1,
    "Management of septal perforation with saline nasal wash and discussion of surgical repair options remains current.",
    "")

# CASE 68: MTS_0131 — Dietary Consult (Hyperlipidemia)
assessments[68] = (1,
    "Dietary counseling for hyperlipidemia management is still appropriate.",
    "")

# CASE 69: MTS_0132 — DM on Insulin Pump + Lipitor
assessments[69] = (2,
    "Insulin pump management is still current. Lipitor (atorvastatin) for hyperlipidemia is still first-line. For diabetes, would now consider adding GLP-1 RA if A1c not at goal, given cardiovascular benefits.",
    "")

# CASE 70: MTS_0134 — Post-CyberKnife Lung Cancer Followup
assessments[70] = (1,
    "Follow-up PET/CT after SBRT/CyberKnife for early-stage lung cancer is still standard per NCCN.",
    "")

# CASE 71: MTS_0136 — C. diff + UTI
# Flagyl + Levaquin
assessments[71] = (4,
    "SIGNIFICANTLY OUTDATED. 1) Metronidazole (Flagyl) is no longer first-line for C. difficile — oral vancomycin or fidaxomicin now preferred (IDSA/SHEA 2021). 2) Levofloxacin (Levaquin) has FDA black box warnings for serious adverse effects (tendon rupture, neuropathy, CNS effects) and should be avoided when safer alternatives exist for UTI.",
    "1. Switch C. diff treatment to oral vancomycin 125mg QID x 10 days or fidaxomicin 200mg BID x 10 days. 2. For UTI: use a narrower-spectrum agent based on culture (e.g., cephalexin, nitrofurantoin, TMP-SMX). Avoid fluoroquinolones for uncomplicated UTI.")

# CASE 72: MTS_0140 — Chiropractic: OA, Sacroiliitis, Migraine
assessments[72] = (2,
    "Multidisciplinary approach to chronic pain is still appropriate. Rheumatology referral for bone density and thyroid/parathyroid studies is reasonable. For migraine, CGRP inhibitors (erenumab, fremanezumab) are now available as preventive therapy.",
    "")

# CASE 73: MTS_0142 — Diabetes with CKD, Insulin Pump
# Fasting labs, C-peptide, A1c
assessments[73] = (3,
    "Insulin pump management and lab monitoring are appropriate. However, for diabetic kidney disease, an SGLT2 inhibitor (dapagliflozin or empagliflozin) and/or finerenone should now be added for nephroprotection per KDIGO 2024 guidelines.",
    "Add SGLT2 inhibitor (dapagliflozin 10mg daily) for diabetic kidney disease nephroprotection. Consider finerenone if albuminuria persists on maximal RAAS blockade. Continue insulin pump management and lab monitoring.")

# CASE 74: MTS_0143 — Cervicalgia
assessments[74] = (1,
    "Workup with EKG and imaging for cervical pathology with dysphagia is still appropriate.",
    "")

# CASE 75: MTS_0145 — Cervical Spinal Stenosis
assessments[75] = (1,
    "Discussion of operative vs non-operative management for cervical stenosis with myelopathy/radiculopathy is still current.",
    "")

# CASE 76: MTS_0149 — Cardiology Progress Note
# Requesting previous echo, ordering CXR/EKG
assessments[76] = (2,
    "Obtaining baseline cardiac studies is appropriate. Would now ensure guideline-directed medical therapy (GDMT) for post-MI including high-intensity statin, ACEi/ARB or ARNI, beta-blocker, antiplatelet therapy, and SGLT2i.",
    "")

# CASE 77: MTS_0151 — CHF with AF
# ACEi pending renal function, digoxin, beta-blocker, Coumadin
assessments[77] = (4,
    "SIGNIFICANTLY OUTDATED. Major changes in HF and AF management: 1) ARNI (sacubitril/valsartan) now preferred over ACEi for HFrEF (PARADIGM-HF trial). 2) SGLT2 inhibitor (dapagliflozin or empagliflozin) is now a mandatory fourth pillar of HF therapy (DAPA-HF, EMPEROR-Reduced). 3) DOACs (apixaban) preferred over warfarin for AF anticoagulation. 4) Digoxin use has declined; less favored for rate control.",
    "1. Once renal function stabilizes: start sacubitril/valsartan (ARNI) instead of ACEi. 2. Add SGLT2 inhibitor (dapagliflozin 10mg daily). 3. Continue beta-blocker and spironolactone. 4. Switch warfarin to apixaban 5mg BID for AF. 5. Consider de-emphasizing digoxin for rate control.")

# CASE 78: MTS_0152 — Carbohydrate Counting (Diabetes)
assessments[78] = (1,
    "Insulin-to-carbohydrate ratio education and carbohydrate counting remain fundamental to diabetes self-management.",
    "")

# CASE 79: MTS_0153 — Cataracts with AMD
assessments[79] = (2,
    "Assessment of AMD impact on cataract surgery outcomes is still relevant. Today anti-VEGF injections (ranibizumab, aflibercept, faricimab) are standard for wet AMD management.",
    "")

# CASE 80: MTS_0157 — Asperger's + OCD
# Decrease Abilify, start Luvox
assessments[80] = (2,
    "Medication management is still clinically appropriate. Minor update: Asperger's disorder was eliminated as a separate diagnosis in DSM-5 (2013); now classified as Autism Spectrum Disorder (ASD). Luvox for OCD and Abilify for ASD-related irritability are still used.",
    "")

# CASE 81: MTS_0159 — Bell's Palsy
# Valtrex 1g TID x 7 days (no steroids mentioned)
assessments[81] = (3,
    "Bell's palsy treatment with antiviral alone is incomplete. AAN guidelines recommend oral corticosteroids (prednisone 60-80mg/day x 7 days) as the PRIMARY treatment, with or without antiviral. Antivirals alone have not shown consistent benefit without concurrent steroids.",
    "Prednisone 60mg daily x 7 days (primary treatment), started within 72 hours of onset. May add valacyclovir 1g TID x 7 days for severe cases (House-Brackmann IV-VI). Eye protection with lubricating drops and nighttime taping.")

# CASE 82: MTS_0162 — Hypothyroidism Post-Thyroidectomy for Cancer
# TSH, free T4, thyroglobulin monitoring
assessments[82] = (1,
    "Thyroid cancer surveillance with TSH, free T4, and thyroglobulin monitoring post-thyroidectomy remains standard per ATA guidelines.",
    "")

# CASE 83: MTS_0164 — Allergic Rhinitis
# Zyrtec + Nasonex
assessments[83] = (1,
    "Second-generation antihistamine + intranasal corticosteroid combination remains first-line for allergic rhinitis.",
    "")

# CASE 84: MTS_0179 — Right Hand Lacerations
# Augmentin + Vicoprofen
assessments[84] = (3,
    "Augmentin for contaminated wound prophylaxis is still appropriate. However, Vicoprofen (hydrocodone/ibuprofen) for simple laceration pain is not current practice. Non-opioid analgesia (ibuprofen alone or acetaminophen) is preferred per CDC opioid prescribing guidelines.",
    "Continue Augmentin. For pain: ibuprofen 400-600mg q6h PRN (the ibuprofen component of Vicoprofen) without the opioid. Acetaminophen as alternative or adjunct.")

# CASE 85: MTS_0189 — Perioperative Hypertension
# Restart lisinopril
assessments[85] = (2,
    "Restarting ACE inhibitor for perioperative hypertension is still appropriate. Target BP now <130/80 per ACC/AHA 2017.",
    "")

# CASE 86: MTS_0213 — Normal Newborn
# Routine care, HepB vaccine
assessments[86] = (1,
    "Routine newborn care with hepatitis B immunization prior to discharge remains standard per AAP.",
    "")

# CASE 87: MTS_0230 — Motor Vehicle Accident
# Vicodin + Flexeril
assessments[87] = (3,
    "Opioid prescribing (Vicodin/hydrocodone) for minor MVA contusions is outdated. Current guidelines recommend NSAIDs (ibuprofen, naproxen) and acetaminophen as first-line for acute musculoskeletal pain. Cyclobenzaprine (Flexeril) is still used for short courses.",
    "For pain: ibuprofen 600mg q8h PRN + acetaminophen 500mg q6h PRN. Cyclobenzaprine 5-10mg at bedtime x 5-7 days if muscle spasm. Avoid opioids for uncomplicated contusions.")

# CASE 88: MTS_0231 — Anemia + Hyponatremia
# Advised salt on food, follow-up
assessments[88] = (2,
    "Management of mild hyponatremia with dietary salt is reasonable for outpatient treatment. Would now want to determine etiology (SIADH, volume status, medications) more explicitly.",
    "")

# CASE 89: MTS_0235 — Insect Sting, Local Reaction
# Claritin
assessments[89] = (1,
    "Antihistamine for local insect sting reaction is still appropriate.",
    "")

# CASE 90: MTS_0238 — Allergic Reaction
# Treated with Benadryl + epinephrine
assessments[90] = (2,
    "Acute treatment is appropriate. Today would also prescribe an epinephrine auto-injector (EpiPen) for home use in case of recurrence, and consider allergy referral.",
    "")

# CASE 91: MTS_0239 — Newly Diagnosed High-Risk ALL
# Bone marrow biopsy, LP, Doppler studies
assessments[91] = (2,
    "Diagnostic workup is still appropriate. Today would also include molecular profiling (flow cytometry, cytogenetics, FISH, PCR for BCR-ABL, MRD assessment), HLA typing if transplant candidate, and fertility preservation discussion per ASCO guidelines. Echocardiography before anthracycline-based chemotherapy is also standard.",
    "")

# CASE 92: MTS_0244 — Nonischemic Cardiomyopathy, NYHA III
# Lasix, increased hydralazine, added Aldactone, Toprol, lisinopril
assessments[92] = (4,
    "SIGNIFICANTLY OUTDATED. The four-pillar therapy for HFrEF has changed substantially: 1) ARNI (sacubitril/valsartan) replaces ACEi/ARB unless contraindicated. 2) SGLT2 inhibitor (dapagliflozin or empagliflozin) is now mandatory. 3) MRA (spironolactone) — appropriately added here. 4) Beta-blocker — appropriately continued. Hydralazine is now reserved for African-American patients (A-HeFT) as add-on or for those who cannot tolerate ARNI.",
    "1. Switch lisinopril to sacubitril/valsartan (ARNI) 24/26mg BID, titrate to 97/103mg BID. 2. Add SGLT2 inhibitor (dapagliflozin 10mg daily or empagliflozin 10mg daily). 3. Continue Aldactone 25mg and Toprol. 4. Discontinue hydralazine unless African-American patient. 5. Continue Lasix for volume management. 6. Labs in 1 week.")

# CASE 93: MTS_0254 — Pancreatitis
# Morphine, Zofran, IV fluids, NPO
assessments[93] = (2,
    "Overall management approach is still appropriate. One concern: morphine for pancreatitis is debated (sphincter of Oddi spasm), though recent evidence suggests it may not be worse than other opioids. Goal-directed fluid resuscitation and early enteral nutrition (vs prolonged NPO) are now emphasized.",
    "")

# CASE 94: MTS_0255 — Probable Stroke
# MRI, carotid US, echo, antiplatelet, ceftriaxone for UTI, A1c
assessments[94] = (2,
    "Stroke workup is comprehensive and still appropriate. Would now also add high-intensity statin (atorvastatin 80mg) immediately. For AF with stroke, would transition from antiplatelet to DOAC anticoagulation. CT angiography is now often obtained acutely in addition to MRI.",
    "")

# CASE 95: MTS_0285 — Anxiety + HTN
# No med changes, lipid profile, mammogram, sigmoidoscopy offered
assessments[95] = (3,
    "Lipid profile and mammogram still appropriate. Sigmoidoscopy for colorectal cancer screening is outdated — colonoscopy is now preferred. Screening age lowered to 45 (USPSTF 2021). Annual mammogram recommendations also evolved (biennial 40-74 per USPSTF 2024).",
    "Replace sigmoidoscopy with colonoscopy (or alternative: FIT annually, Cologuard q3yr). Screening starts at age 45. Mammogram per USPSTF: biennial 40-74. Consider lipid-lowering therapy if lipid profile abnormal.")

# CASE 96: MTS_0286 — Diabetes + HTN, poor control
# Increasing Lantus, labs, sigmoidoscopy, Elocon, Zyrtec, Flonase
assessments[96] = (4,
    "SIGNIFICANTLY OUTDATED. 1) For T2DM with HTN and poor control: SGLT2 inhibitor or GLP-1 RA should be added regardless of A1c for cardiorenal protection. Lantus titration alone is insufficient given modern evidence. 2) Sigmoidoscopy replaced by colonoscopy (starts at 45). 3) Weight loss with GLP-1 RA would address multiple comorbidities simultaneously.",
    "1. Add GLP-1 RA (semaglutide 0.25mg weekly, titrate up) for glycemic control AND weight loss AND cardiorenal protection. 2. Add SGLT2 inhibitor for additional cardiorenal benefit. 3. Continue Lantus titration. 4. Replace sigmoidoscopy with colonoscopy. 5. Continue allergy medications.")

# CASE 97: MTS_0287 — Multiple Problems, No Detailed Plan
assessments[97] = (2,
    "The plan text is largely absent (just the assessment with no specific interventions noted). Cannot fully assess, but the diagnoses listed are managed similarly today. Essential thrombocythemia may now benefit from newer therapies (ruxolitinib if high-risk).",
    "")

# CASE 98: MTS_0292 — Ovarian Cancer with DVT
# Lovenox + Coumadin bridge
assessments[98] = (4,
    "SIGNIFICANTLY OUTDATED. For cancer-associated VTE, the Lovenox-to-Coumadin bridge is no longer recommended. Current guidelines (ASCO, CHEST 2021) recommend either: 1) LMWH alone (no transition to warfarin), or 2) DOAC (rivaroxaban or apixaban) which are now preferred for most cancer-associated VTE.",
    "Switch from Lovenox-to-Coumadin bridge to either: 1) Apixaban 10mg BID x 7 days then 5mg BID (CARAVAGGIO trial), or 2) Continue LMWH (enoxaparin) alone for at least 6 months. DOACs preferred unless high GI bleeding risk or drug interactions with chemotherapy.")

# CASE 99: MTS_0304 — Dysuria, Flank Pain, Pharyngitis
# Rocephin IM + Omnicef
assessments[99] = (2,
    "Ceftriaxone IM for complicated UTI is still appropriate. Cefdinir as step-down is reasonable. Would now culture-directed therapy. Strep testing for pharyngitis is appropriate.",
    "")

# CASE 100: MTS_0305 — Probable Stroke with AF
# MRI/MRA, carotid US, echo, lipid panel, sliding scale insulin
assessments[100] = (3,
    "Stroke workup is comprehensive and still appropriate. However, for AF with stroke, a DOAC should be initiated for secondary prevention (not just aspirin/Plavix). Sliding scale insulin alone is inadequate for glycemic management.",
    "Workup: continue MRI/MRA, carotid Doppler, echo, lipid panel. Add: DOAC (apixaban 5mg BID) for AF-related stroke prevention. High-intensity statin. Optimize glycemic management beyond sliding scale. Neurology consultation appropriate.")

# CASE 101: MTS_0314 — Back Pain
# Tylenol No. 3 at bedtime
assessments[101] = (3,
    "Codeine-containing analgesics (Tylenol #3) for chronic pain are now generally avoided. Current guidelines recommend non-opioid approaches: acetaminophen, NSAIDs, physical therapy, and consideration of gabapentinoids for neuropathic component.",
    "For back pain: acetaminophen 500-1000mg q6h PRN, ibuprofen 400mg q8h PRN. Physical therapy referral. Avoid codeine/opioids for chronic non-cancer pain.")

# CASE 102: MTS_0316 — HTN, Depression on Cymbalta, Bowel Regimen
assessments[102] = (1,
    "Cymbalta (duloxetine) for depression remains appropriate. Bowel regimen adjustment is standard care. Blood pressure management is current.",
    "")

# CASE 103: MTS_0317 — Needlestick Exposure (HepC source)
assessments[103] = (2,
    "Follow-up monitoring after needlestick with HepC+ source is appropriate. Key update: if HCV seroconversion occurs, it is now CURABLE with 8-12 weeks of DAA therapy. This significantly changes the counseling regarding prognosis.",
    "")

# CASE 104: MTS_0321 — Pediatric Allergic Rhinitis
# Zyrtec + Nasonex
assessments[104] = (2,
    "Antihistamine + nasal steroid remains standard. Minor update: egg allergy is no longer a contraindication to flu vaccine (AAP/CDC updated guidance). Patient should receive flu vaccine.",
    "")

# CASE 105: MTS_0324 — Allergic Rhinitis
assessments[105] = (1,
    "Switching antihistamines and monitoring asthma with peak flows is still appropriate.",
    "")

# CASE 106: MTS_0325 — Purulent Rhinitis/Sinusitis
# Omnicef, saline, Neosporin
assessments[106] = (2,
    "Antibiotic for purulent rhinosinusitis with impetigo is reasonable. Amoxicillin-clavulanate would be first-line per IDSA, but cefdinir is an alternative.",
    "")

# CASE 107: MTS_0327 — Pediatric: Allergic Rhinitis, Teething
assessments[107] = (1,
    "Supportive care with antihistamine continuation is appropriate.",
    "")

# CASE 108: MTS_0328 — Chronic Lung Disease in Infant
assessments[108] = (1,
    "Continued nutritional support and close follow-up for an infant with chronic lung disease is still standard care.",
    "")

# CASE 109: MTS_0329 — Congestion, Possible Adenoids
# ENT referral
assessments[109] = (1,
    "ENT referral for evaluation of nasal obstruction/possible adenoid hypertrophy is still appropriate.",
    "")

# CASE 110: MTS_0331 — Serous Otitis + Atopic Dermatitis
# Nasacort, Duraphen, Cutivate
assessments[110] = (2,
    "Nasal steroid for serous otitis and topical steroid for atopic dermatitis remain standard. Duraphen (decongestant) is an older combination product. For atopic dermatitis, dupilumab (Dupixent) is now available for moderate-to-severe cases.",
    "")

# CASE 111: MTS_0332 — Pediatric Sinusitis
# Amoxicillin x 10 days
assessments[111] = (2,
    "Amoxicillin remains first-line for pediatric acute bacterial sinusitis. Duration of 10 days is appropriate. Current guidelines (AAP) also support watchful waiting for mild cases.",
    "")

# CASE 112: MTS_0333 — Arthralgias, DM2
assessments[112] = (2,
    "Assessment approach is appropriate. For the well-controlled DM2, would now consider SGLT2i or GLP-1RA for cardiorenal protection. Inflammatory arthritis workup (RF, anti-CCP, ESR/CRP) should be ordered.",
    "")

# CASE 113: MTS_0334 — Dyspnea, HTN, DM
# Consider stress test
assessments[113] = (2,
    "Workup approach with cardiac risk assessment is still appropriate. Would now also check BNP/NT-proBNP if concern for HF.",
    "")

# CASE 114: MTS_0336 — Foreign Body (Fingernail)
assessments[114] = (1,
    "Wound care instructions with bacitracin are still appropriate. Tetanus status should be verified.",
    "")

# CASE 115: MTS_0337 — Foreign Body (Nose) + Constipation
# Amoxicillin
assessments[115] = (1,
    "Amoxicillin for secondary infection after nasal foreign body removal is still appropriate.",
    "")

# CASE 116: MTS_0338 — Post-Surgical Menopause, Mood Swings
# Wellbutrin XL, labs (CBC, UA, TSH, chem, lipid), breast exam
assessments[116] = (2,
    "Wellbutrin for mood symptoms in surgical menopause is still appropriate, especially given patient's reluctance for HRT. Lab workup is comprehensive. Would now add bone density screening (DEXA) post-menopause and discuss vasomotor symptom management (fezolinetant/Veozah is a newer non-hormonal option).",
    "")

# CASE 117: MTS_0339 — Asthma on Daily Albuterol
# Adding Flovent, restart Allegra/Flonase, fluoxetine, repeat UA
assessments[117] = (3,
    "Adding ICS (Flovent) for asthma with daily SABA use is appropriate (Step 2). However, GINA 2019+ now recommends ICS-formoterol (budesonide-formoterol) as both maintenance and reliever therapy, rather than separate ICS + SABA. This approach reduces exacerbations. The SABA-only reliever strategy is being phased out.",
    "For asthma: switch to ICS-formoterol (budesonide-formoterol) as both maintenance and reliever (GINA preferred approach). If staying with separate inhalers, continue Flovent + albuterol PRN. Consider step-up to ICS-LABA (Advair/Symbicort) if not controlled. Continue allergy medications and fluoxetine.")

# CASE 118: MTS_0340 — Ureteral Stone
# Laser lithotripsy planned
assessments[118] = (1,
    "Ureteroscopy with laser lithotripsy for ureteral stone is still standard treatment.",
    "")

# CASE 119: MTS_0343 — Folliculitis, Pelvic Pain, Mood Swings
# Cephalexin, labs, referrals
assessments[119] = (1,
    "Cephalexin for folliculitis, lab workup, gynecology referral for pelvic pain, and psychiatry referral are all still appropriate.",
    "")

# CASE 120: MTS_0344 — HTN, Hypothyroid, Arthritis, Osteoporosis
# Comprehensive labs, CXR, DEXA, lipids
assessments[120] = (1,
    "Comprehensive workup including DEXA scan for osteoporosis, lipid profile, and labs is still appropriate. Flex sigmoidoscopy reference is outdated (colonoscopy preferred), but noted as 'up to date' in the plan.",
    "")

# CASE 121: MTS_0346 — Uncontrolled HTN, Alcohol Withdrawal
# Atenolol, diazepam, thiamine
assessments[121] = (3,
    "Thiamine and benzodiazepine for alcohol withdrawal are still appropriate. However, atenolol is no longer first-line for hypertension per ACC/AHA guidelines (associated with higher stroke risk vs. other agents). ACEi/ARB, CCB, or thiazide-like diuretics (chlorthalidone) are preferred.",
    "For hypertension: switch atenolol to amlodipine 5mg daily, lisinopril 10mg daily, or chlorthalidone 12.5-25mg daily. Continue diazepam taper for alcohol withdrawal and thiamine supplementation. Refer for alcohol use disorder treatment.")

# CASE 122: MTS_0356 — Infant URI
assessments[122] = (1,
    "Supportive care (bulb syringe, saline drops, frequent feeds) for infant URI is still standard.",
    "")

# CASE 123: MTS_0380 — Heroin Detox
# Clonidine + Phenergan only
assessments[123] = (5,
    "SUBSTANTIALLY OUTDATED. Clonidine-only detox for opioid use disorder is no longer considered adequate treatment. Medication-assisted treatment (MAT) with buprenorphine is now the standard of care for opioid withdrawal and maintenance (ASAM 2020). Buprenorphine can be initiated in the ED/outpatient setting. Naloxone should be prescribed. Clonidine is only an adjunct.",
    "1. Initiate buprenorphine-naloxone (Suboxone) — can start when patient is in moderate withdrawal (COWS ≥8). 2. Prescribe naloxone (Narcan) rescue kit. 3. Clonidine 0.1mg q6h PRN for adjunctive symptom relief. 4. Refer to comprehensive opioid treatment program. 5. Screen for HIV, Hepatitis B/C. 6. Ondansetron (Zofran) preferred over Phenergan for nausea (less sedation, fewer adverse effects).")

# CASE 124: MTS_0395 — 2-Month-Old with Fever
# Pertussis PCR, urine culture, CXR
assessments[124] = (1,
    "Workup for febrile infant including pertussis testing, urine culture, and chest X-ray is still standard. Admission for monitoring is appropriate.",
    "")

# CASE 125: MTS_0396 — Chest Pain (GERD)
# Increase Aciphex, punch biopsy of skin lesions, CBC
assessments[125] = (2,
    "PPI dose escalation for GERD-related chest pain and skin biopsy for suspicious lesions are both still appropriate. Would now also discuss long-term PPI risks (bone loss, C. diff, kidney).",
    "")

# CASE 126: MTS_0398 — 21-Day-Old, Rule Out Sepsis
# Ampicillin + gentamicin
assessments[126] = (1,
    "Ampicillin + gentamicin for empiric neonatal sepsis coverage (covering GBS, E. coli, Listeria) remains standard of care.",
    "")

# CASE 127: MTS_0402 — Breast Calcifications Pre-Op
assessments[127] = (2,
    "Excisional biopsy with guidewire localization for suspicious calcifications is still performed, though vacuum-assisted biopsy is now more commonly used and less invasive.",
    "")

# CASE 128: MTS_0415 — Choledocholithiasis
# IV antibiotics, US, cholecystectomy with IOC
assessments[128] = (1,
    "IV antibiotics, ultrasound, and cholecystectomy with intraoperative cholangiogram for choledocholithiasis remains standard management.",
    "")

# CASE 129: MTS_0418 — Severe Hyponatremia (Na 107)
# Admit for treatment
assessments[129] = (2,
    "Admission for hyponatremia treatment is appropriate. Today there is more emphasis on controlled correction rate (<8 mEq/L per 24h) to prevent osmotic demyelination syndrome. Would also determine etiology (SIADH, volume status, TSH, cortisol).",
    "")

# CASE 130: MTS_0419 — DM2 Uncontrolled + Acute Cystitis
# Micronase (glyburide) + Bactrim
assessments[130] = (4,
    "SIGNIFICANTLY OUTDATED. Glyburide (Micronase) is no longer recommended as a preferred sulfonylurea (higher hypoglycemia risk per ADA). Metformin is first-line for T2DM. SGLT2 inhibitors and GLP-1 RAs are preferred second-line agents. Bactrim for uncomplicated UTI is still acceptable if local resistance allows.",
    "1. Start metformin 500mg BID (titrate to 1000mg BID) as first-line for T2DM. Do NOT start glyburide. 2. Add SGLT2 inhibitor or GLP-1 RA as second agent. 3. A1c target individualized. 4. Bactrim for UTI is acceptable if local resistance <20%. Consider nitrofurantoin as alternative. 5. Endocrinology consult for uncontrolled diabetes.")

# CASE 131: MTS_0420 — Accidental Celexa Ingestion
assessments[131] = (1,
    "Observation and discharge after accidental SSRI ingestion in a child with stable vitals is still appropriate.",
    "")

# CASE 132: MTS_0425 — Testicular Torsion
# Scrotal exploration, possible detorsion, bilateral fixation
assessments[132] = (1,
    "Emergent scrotal exploration with possible detorsion and bilateral orchiopexy for suspected testicular torsion remains the standard of care.",
    "")

# CASE 133: MTS_0426 — Syncope with HTN
# Maxzide, outpatient Holter, carotid Doppler
assessments[133] = (2,
    "Syncope workup with Holter and carotid Doppler is still appropriate. Maxzide (HCTZ/triamterene) is a reasonable antihypertensive though chlorthalidone is now preferred over HCTZ. Current syncope guidelines (ESC 2018) emphasize risk stratification.",
    "")

# CASE 134: MTS_0440 — Penile Mass
# Urology referral for excision/biopsy
assessments[134] = (1,
    "Urology referral for excision and biopsy of a penile mass is still the standard approach.",
    "")

# CASE 135: MTS_0441 — LLQ Pain in Pregnancy
# Transfer to L&D for monitoring
assessments[135] = (1,
    "Transfer to Labor and Delivery for fetal monitoring and evaluation of abdominal pain at 28 weeks is still appropriate.",
    "")

# CASE 136: MTS_0449 — Pathological Hip Fracture
# Bone scan, X-rays, surgical planning
assessments[136] = (2,
    "Workup for pathological fracture is still appropriate. Today would also obtain CT chest/abdomen/pelvis or PET/CT for metastatic staging rather than bone scan alone. MRI may provide more information than additional X-rays.",
    "")

# CASE 137: MTS_0452 — AF on Coumadin with INR 12
# Vitamin K, switch to aspirin 81mg
assessments[137] = (4,
    "SIGNIFICANTLY OUTDATED. While vitamin K for supratherapeutic INR is appropriate, switching from warfarin to aspirin 81mg alone for AF is inadequate stroke prevention. The correct approach today is to transition to a DOAC (apixaban or rivaroxaban) once INR normalizes, which provides predictable anticoagulation without INR monitoring and a better safety profile in elderly patients.",
    "1. Give vitamin K for acute INR of 12 (appropriate). 2. Once INR normalizes, transition to apixaban 5mg BID (or 2.5mg BID if meets dose-reduction criteria) rather than aspirin alone. 3. DOACs do not require INR monitoring, reducing the risk of supratherapeutic levels. 4. Assess CHA2DS2-VASc score to confirm need for anticoagulation (almost certainly indicated).")

# CASE 138: MTS_0459 — Bacterial Vaginosis
# Metronidazole 500mg BID x 7 days
assessments[138] = (1,
    "Oral metronidazole 500mg BID x 7 days remains first-line treatment for bacterial vaginosis per CDC STI guidelines.",
    "")

# CASE 139: MTS_0468 — Dental Pain
# Dental block, empiric antibiotics, follow-up with dentist
assessments[139] = (2,
    "Dental block for pain relief is appropriate. Empiric antibiotics and dental follow-up are still standard. Today would specify non-opioid analgesia (ibuprofen/acetaminophen combination) for discharge.",
    "")

# CASE 140: MTS_0471 — Rib Cage Pain
# Transfer for further evaluation
assessments[140] = (1,
    "Transfer for evaluation of unexplained chest/abdominal pain in a stable patient is a clinical judgment call that remains reasonable.",
    "")

# CASE 141: MTS_0473 — Dental Abscess
# Vicodin + Keflex
assessments[141] = (3,
    "Keflex (cephalexin) for dental abscess is still appropriate (though amoxicillin or amox/clav is more common first-line). Vicodin (hydrocodone) for dental pain is outdated — ibuprofen 400-600mg + acetaminophen 500mg combination has been shown equally or more effective than opioids for dental pain (multiple RCTs).",
    "Continue Keflex (or switch to amoxicillin). For pain: ibuprofen 400-600mg q6h + acetaminophen 500mg q6h (alternating). This combination is as or more effective than opioids for dental pain. Avoid Vicodin.")

# CASE 142: MTS_0476 — Suicide Attempt in Pregnancy
# HCG, transvaginal US, prenatal vitamins
assessments[142] = (1,
    "Workup with quantitative HCG, transvaginal ultrasound for dating, and prenatal vitamin initiation after suicide attempt in pregnancy is still appropriate.",
    "")

# CASE 143: MTS_0480 — Closed Head Injury
# Admit to trauma surgery
assessments[143] = (1,
    "Admission for observation after closed head injury is still appropriate.",
    "")

# CASE 144: MTS_0481 — Bronchiolitis in 2-Month-Old
# Supportive care (suctioning, O2)
assessments[144] = (1,
    "Supportive care with suctioning and supplemental oxygen for bronchiolitis is still the standard per AAP guidelines. Decision not to use bronchodilators is evidence-based.",
    "")

# CASE 145: MTS_0497 — Well-Child Check (2 weeks)
assessments[145] = (1,
    "Standard 2-week well-child visit with anticipatory guidance remains current.",
    "")

# CASE 146: MTS_0498 — Worker's Comp (Thumb Trauma)
# Td booster, Keflex
assessments[146] = (2,
    "Tetanus booster and Keflex for cellulitis are still appropriate. Today would give Tdap instead of Td if not previously received.",
    "")

# CASE 147: MTS_0499 — Well-Child Check (5 years)
# MMR, DTaP, IPV
assessments[147] = (2,
    "Immunizations and well-child check are appropriate. Current immunization schedule may have minor updates but core vaccines are the same.",
    "")

# CASE 148: MTS_0500 — Well-Woman Checkup
# UA, mammogram, hemoccult x3, DEXA, chem-12, lipid, CBC
assessments[148] = (3,
    "Several screening tests are outdated: 1) Hemoccult x3 (guaiac FOBT) replaced by FIT test or colonoscopy. 2) Chem-12 not routinely recommended as screening. 3) CBC as routine screening is not evidence-based. Mammogram and DEXA are still appropriate. Lipid screening is appropriate.",
    "Update screening: 1) Replace hemoccult with FIT annually or colonoscopy q10yr (starting age 45). 2) Targeted lab screening (lipid panel, glucose/A1c) rather than broad Chem-12 + CBC. 3) Continue mammogram (biennial per USPSTF) and DEXA. 4) UA/culture for UTI evaluation still appropriate.")

# CASE 149: MTS_0502 — Well-Child Check (1 year)
# Pediarix, HIB, screening CBC, lead level
assessments[149] = (2,
    "Immunizations and screening labs are appropriate for age. Lead screening recommendations have narrowed but are still done in many areas. Current immunization schedule may have minor updates.",
    "")

# CASE 150: MTS_0503 — Well-Child Check (Newborn)
assessments[150] = (1,
    "Newborn well-child check with hepatitis B immunization is standard.",
    "")

# CASE 151: MTS_0504 — Well-Child Check (2 weeks)
assessments[151] = (1,
    "Standard 2-week well-child visit remains current.",
    "")

# CASE 152: MTS_0505 — Well-Child Check (9 months)
assessments[152] = (1,
    "Well-child check with monitoring of molluscum contagiosum and resolved otitis media is appropriate.",
    "")

# CASE 153: MTS_0506 — Well-Child Check (1 year)
# MMR, Varivax
assessments[153] = (1,
    "MMR and varicella vaccines at 12 months are still standard per CDC/AAP immunization schedule.",
    "")

# CASE 154: MTS_0507 — Viral Gastroenteritis
# Compazine + Imodium
assessments[154] = (2,
    "Symptomatic treatment is appropriate. Ondansetron (Zofran) is now often preferred over prochlorperazine (Compazine) due to better side effect profile. Dietary instructions are still appropriate.",
    "")

# CASE 155: MTS_0510 — Severe Uveitis
# Oral steroids, Pred Forte, atropine, labs for infectious workup
assessments[155] = (2,
    "Aggressive treatment with oral and topical steroids is appropriate for severe uveitis. Labs to rule out infectious etiologies are standard. For refractory uveitis, adalimumab (Humira) is now FDA-approved (2016). Consider QuantiFERON instead of PPD for TB screening.",
    "")

# CASE 156: MTS_0511 — BPH with Urinary Retention
# Flomax + Proscar
assessments[156] = (1,
    "Combination alpha-blocker (tamsulosin/Flomax) + 5-alpha reductase inhibitor (finasteride/Proscar) remains standard therapy for BPH with retention per AUA guidelines.",
    "")

# CASE 157: MTS_0516 — URI with Sinus Congestion
# Advil Cold & Sinus + Afrin x 3-5 days
assessments[157] = (1,
    "Decongestant and short-course topical nasal decongestant (≤3-5 days) for viral URI with sinus congestion is still appropriate.",
    "")

# CASE 158: MTS_0530 — Sports Physical
assessments[158] = (1,
    "Sports physical with anticipatory guidance is standard.",
    "")

# CASE 159: MTS_0536 — Sports Physical
# Clarinex, Rhinocort-AQ
assessments[159] = (2,
    "Clarinex (desloratadine) is still used but more expensive than generic loratadine or cetirizine with similar efficacy. Rhinocort nasal spray is still appropriate.",
    "")

# CASE 160: MTS_0538 — Speech Therapy Evaluation (Aphasia)
assessments[160] = (1,
    "Speech therapy assessment and treatment plan for global aphasia remains standard rehabilitation approach.",
    "")

# CASE 161: MTS_0539 — School Physical
assessments[161] = (1,
    "Standard school physical with developmental assessment.",
    "")

# CASE 162: MTS_0544 — Sports Physical, Asthma
# Albuterol rescue inhalers
assessments[162] = (2,
    "Albuterol rescue inhalers for well-controlled asthma are still appropriate. GINA now recommends ICS-formoterol as reliever even for Step 1, but for a well-controlled child with good adherence to controller, this approach is acceptable.",
    "")

# CASE 163: MTS_0545 — School Physical
# Atarax, Elocon for rash
assessments[163] = (2,
    "Hydroxyzine (Atarax) and Elocon (mometasone ointment) for allergic dermatitis are still used. Second-gen antihistamines (cetirizine, loratadine) are now preferred over hydroxyzine for chronic use (less sedation).",
    "")

# CASE 164: MTS_0546 — Rheumatoid Arthritis
# On longstanding prednisone, no DMARD
assessments[164] = (3,
    "Long-term prednisone without DMARD therapy for RA is below current standard of care. ACR/EULAR guidelines emphasize early DMARD initiation (methotrexate first-line) with the goal of steroid-free remission. In this case, DMARD was deferred due to recent surgery/infection, which is reasonable temporarily, but should be started as soon as possible.",
    "Once infection resolved: initiate methotrexate (7.5-15mg weekly) as DMARD. If inadequate response, consider biologic (anti-TNF, tocilizumab, or JAK inhibitor like tofacitinib). Goal: steroid-free remission. Taper prednisone as DMARD takes effect.")

# CASE 165: MTS_0555 — Pediatric Nasal Obstruction
# Nasacort AQ
assessments[165] = (1,
    "Intranasal corticosteroid trial for possible allergic rhinitis with nasal obstruction in a child is still appropriate.",
    "")

# CASE 166: MTS_0559 — Cough from GERD/Aspiration
assessments[166] = (1,
    "Conservative management of cough from GERD/aspiration with speech pathology evaluation and dietary modifications remains appropriate.",
    "")

# CASE 167: MTS_0560 — IME for Epicondylitis
assessments[167] = (1,
    "Independent medical examination with work capacity assessment — format has not changed.",
    "")

# CASE 168: MTS_0574 — New-Onset Psychosis
# No workup ordered, wait for patient to leave seclusion
assessments[168] = (3,
    "For new-onset psychosis, current APA guidelines recommend laboratory workup to exclude medical/toxic causes BEFORE initiating antipsychotics: TSH, CMP, blood alcohol, urine drug screen, CBC, urinalysis, RPR, and urine culture (especially given leukocytosis and possible UTI). The plan to defer all workup until out of seclusion delays important diagnostic evaluation.",
    "Order: TSH, CMP, CBC, blood alcohol, urine drug screen, urine culture, RPR. Consider CT/MRI brain if no prior imaging. Start UTI treatment if symptomatic. APA first-episode psychosis workup should not be deferred.")

# CASE 169: MTS_0578 — Depression in GBM Patient
# Ritalin 5mg AM and noon
assessments[169] = (2,
    "Methylphenidate (Ritalin) for cancer-related fatigue and depression is still used, particularly in palliative settings where rapid onset of action is desired.",
    "")

# CASE 170: MTS_0582 — Rapid-Onset Dementia in 32yo
# Plan: wait for neurological tests
assessments[170] = (3,
    "The plan to simply 'wait for results' is too passive for rapid-onset dementia in a young patient. This is a neurological emergency requiring urgent and comprehensive workup: MRI brain, EEG, lumbar puncture with 14-3-3 protein and RT-QuIC (prion markers), autoimmune encephalitis panel (NMDA-R, LGI1, CASPR2), and basic labs. The differential includes treatable autoimmune encephalitis vs fatal prion disease.",
    "URGENT workup: 1) MRI brain with contrast. 2) EEG. 3) Lumbar puncture: protein, glucose, cell count, cytology, 14-3-3, RT-QuIC, autoimmune encephalitis panel (NMDA-R, LGI1, CASPR2, GABA-B, AMPA). 4) Basic labs: TSH, B12, HIV, RPR, ESR/CRP. 5) This workup was standard even in the mid-2000s; the plan was inadequate regardless of era.")

# CASE 171: MTS_0586 — Pseudotumor Cerebri
# Shunt adjustment, skull X-ray
assessments[171] = (2,
    "Shunt management for pseudotumor cerebri is still appropriate. Today would also emphasize weight loss (GLP-1 RAs now available) and acetazolamide as medical therapy per the IIHTT trial results.",
    "")

# CASE 172: MTS_0593 — GYN Exam with Annual Pap
assessments[172] = (3,
    "Annual Pap smears are no longer recommended. Current USPSTF guidelines: Pap every 3 years (ages 21-65), or HPV co-testing every 5 years (ages 30-65), or HPV primary testing every 5 years (ages 25-65).",
    "Pap smear screening per current guidelines: every 3 years with cytology alone, or every 5 years with HPV co-testing or HPV primary testing. Annual Paps are not indicated.")

# CASE 173: MTS_0599 — GYN: Chest Pain, Hypothyroid, RA, Osteoporosis
# TSH, DEXA, mammogram
assessments[173] = (2,
    "TSH monitoring, DEXA scan, and mammogram are all still appropriate. Management approach is current.",
    "")

# CASE 174: MTS_0600 — Pediatric Reactive Arthritis
assessments[174] = (1,
    "Conservative observation for probable reactive arthritis with plan for follow-up if recurrence is still appropriate.",
    "")

# CASE 175: MTS_0611 — Oligoarticular Arthritis, Vitamin D Deficiency
# Vitamin D, calcium, Mobic
assessments[175] = (2,
    "Vitamin D and calcium supplementation with NSAID (Mobic) for arthritis is still appropriate. Mobic 50mg seems unusually high — typical dose is 7.5-15mg daily. Physical therapy referral is appropriate.",
    "")

# CASE 176: MTS_0613 — Post-TKR
assessments[176] = (1,
    "Post-operative management with DVT prophylaxis and monitoring is standard.",
    "")

# CASE 177: MTS_0621 — Oligoarticular Arthritis
# Indocin 75mg SR
assessments[177] = (2,
    "Indomethacin (Indocin) for oligoarticular arthritis is still used but carries higher GI risk than other NSAIDs. Naproxen or meloxicam may be preferred. Otherwise approach is appropriate.",
    "")

# CASE 178: MTS_0622 — ASCUS Pap
# HPV DNA testing, ECC
assessments[178] = (1,
    "HPV testing for ASCUS triage is still standard per ASCCP guidelines.",
    "")

# CASE 179: MTS_0625 — Ovarian Cyst, Irregular Periods
# Lo/Ovral (OCP)
assessments[179] = (2,
    "OCP for menstrual regulation and ovarian cyst management is still a standard approach. Lo/Ovral is an older formulation; many newer low-dose OCPs are available.",
    "")

# CASE 180: MTS_0655 — Metastatic Non-Small Cell Lung Cancer
# Carboplatin + gemcitabine
assessments[180] = (5,
    "SUBSTANTIALLY OUTDATED. First-line treatment for metastatic NSCLC has changed dramatically. Current standard requires: 1) Molecular profiling (PD-L1, EGFR, ALK, ROS1, BRAF, KRAS G12C, MET, RET, NTRK, HER2). 2) For patients without targetable mutations: immunotherapy (pembrolizumab) ± chemotherapy based on PD-L1 status. 3) For patients with targetable mutations: matched targeted therapy (osimertinib for EGFR, alectinib for ALK, etc.). Carboplatin/gemcitabine alone is no longer first-line.",
    "1. Obtain comprehensive molecular profiling: PD-L1 (IHC), EGFR, ALK (FISH/IHC), ROS1, BRAF, KRAS G12C, MET, RET, NTRK. 2. If no targetable mutations and PD-L1 ≥50%: pembrolizumab monotherapy. 3. If PD-L1 <50%: pembrolizumab + carboplatin/pemetrexed. 4. If targetable mutation: matched TKI (osimertinib, alectinib, sotorasib, etc.). 5. Carboplatin/gemcitabine alone is no longer adequate.")

# CASE 181: MTS_0656 — New Onset Seizure (Pediatric)
# EEG, medication adjustments
assessments[181] = (1,
    "EEG and anticonvulsant optimization for pediatric seizures is still the standard approach.",
    "")

# CASE 182: MTS_0670 — Possible Normal Pressure Hydrocephalus
assessments[182] = (2,
    "Assessment and observation for NPH is appropriate. Large-volume lumbar puncture tap test (mentioned elsewhere for similar case) is the key diagnostic step. MRI assessment for hydrocephalus vs small vessel disease is still the diagnostic challenge.",
    "")

# CASE 183: MTS_0675 — Seizure Breakthrough
assessments[183] = (1,
    "Conservative management with observation during intercurrent illness and maintaining current anticonvulsant is appropriate.",
    "")

# CASE 184: MTS_0677 — Neuroblastoma
# CT abdomen for restaging
assessments[184] = (2,
    "CT for restaging neuroblastoma is still appropriate. Current protocols may also use MIBG scan and urine catecholamines for surveillance.",
    "")

# CASE 185: MTS_0680 — ESRD, Pre-Transplant Workup
assessments[185] = (1,
    "Pre-transplant workup evaluation with pulmonary clearance is still standard.",
    "")

# CASE 186: MTS_0687 — Multiple Neurological Symptoms
# EMG/NCS, physical therapy
assessments[186] = (1,
    "EMG/NCS and physical therapy for peripheral neuropathy with gait instability is still appropriate.",
    "")

# CASE 187: MTS_0692 — Concussion
# Admit for observation
assessments[187] = (1,
    "Admission for observation after head injury with mental status changes in elderly patient is appropriate.",
    "")

# CASE 188: MTS_0697 — Malignant Meningioma
# Discussion of limited surgical/chemo options
assessments[188] = (2,
    "For unresectable meningioma with significant disability, limited treatment options are still the reality. Proton beam therapy and newer targeted agents are being studied but options remain limited.",
    "")

# CASE 189: MTS_0699 — Lumbar Radiculopathy
# X-rays, EMG, epidural steroid injections
assessments[189] = (1,
    "Diagnostic workup and epidural steroid injection for lumbar radiculopathy is still a standard approach.",
    "")

# CASE 190: MTS_0706 — Low Back Pain + DM
# Conservative pain management
assessments[190] = (1,
    "Conservative approach to back pain with PRN analgesia in a patient who prefers minimal intervention is appropriate.",
    "")

# CASE 191: MTS_0717 — Kyphoplasty
assessments[191] = (1,
    "Kyphoplasty for non-healing compression fracture is still an appropriate intervention.",
    "")

# CASE 192: MTS_0718 — Kyphosis (Adolescent)
# Observation, PT, possible bracing, repeat films
assessments[192] = (1,
    "Conservative management with observation, physical therapy, and repeat imaging for adolescent kyphosis is still standard.",
    "")

# CASE 193: MTS_0727 — Impairment Rating
assessments[193] = (1,
    "Impairment rating methodology per AMA Guides is still the standard approach, though the edition used may have been updated.",
    "")

# CASE 194: MTS_0733 — Huntington's Disease with Depression/Suicide
# Nortriptyline, Haldol, Artane, Xanax, lorazepam, Prilosec, amlodipine
assessments[194] = (4,
    "SIGNIFICANTLY OUTDATED. 1) Nortriptyline (TCA): higher risk profile, especially post-overdose. SSRIs/SNRIs now preferred for depression. 2) Haldol for chorea: tetrabenazine (Xenazine, approved 2008) and deutetrabenazine (Austedo, approved 2017) are now specifically indicated for Huntington's chorea. 3) Two concurrent benzodiazepines (Xanax + lorazepam) is problematic — risk of respiratory depression, falls, dependence. 4) Artane (trihexyphenidyl) for antipsychotic side effects is still used but anticholinergic burden is concerning.",
    "1. Switch nortriptyline to SSRI (sertraline or citalopram) for depression — safer post-overdose. 2. Consider switching Haldol to deutetrabenazine (Austedo) for chorea — specifically FDA-approved for HD. 3. Consolidate to ONE benzodiazepine at lowest effective dose; taper the other. 4. Continue suicidal precautions. 5. Continue amlodipine for HTN.")

# CASE 195: MTS_0736 — HPV/Genital Warts
# CO2 laser or Condylox
assessments[195] = (2,
    "Treatment options for genital warts are still similar. Key update: HPV vaccination (Gardasil 9) should be discussed for prevention of future HPV-related disease, approved for ages 9-45.",
    "")

# CASE 196: MTS_0749 — Hand Fracture/Dislocation
assessments[196] = (1,
    "Cast immobilization with follow-up imaging and transition to OT splint is standard post-reduction care.",
    "")

# CASE 197: MTS_0823 — Gastric Bypass Pre-Op
# Labs, upper GI series, Medifast
assessments[197] = (2,
    "Pre-operative workup is still appropriate. Sleeve gastrectomy is now more commonly performed than Roux-en-Y. Medifast/liquid diet for pre-op weight loss is still used but GLP-1 RAs are now sometimes used pre-operatively.",
    "")

# CASE 198: MTS_0829 — UTI, GERD, Dysphagia
# Cipro 500mg BID, omeprazole + famotidine, barium swallow, OCP
assessments[198] = (3,
    "Multiple issues: 1) Ciprofloxacin for uncomplicated UTI is now discouraged — FDA black box warnings for serious adverse effects. Nitrofurantoin or TMP-SMX preferred. 2) Combining PPI (omeprazole) AND H2 blocker (famotidine) is pharmacologically redundant and not recommended. 3) Barium swallow for dysphagia — EGD is now preferred for evaluation. 4) Ortho Tri-Cyclen Lo is still available but many newer OCP options exist.",
    "1. For uncomplicated UTI: nitrofurantoin 100mg BID x 5 days or TMP-SMX DS BID x 3 days. Avoid fluoroquinolones. 2. For GERD: omeprazole 20mg daily alone (do not add famotidine — redundant). 3. For dysphagia: EGD (esophagogastroduodenoscopy) preferred over barium swallow for evaluation. 4. Continue OCP.")

# CASE 199: MTS_0834 — Post-Shunt Surgery Followup
assessments[199] = (1,
    "Post-shunt follow-up with assessment of improvement and shunt settings is standard neurosurgical care.",
    "")

# CASE 200: MTS_0835 — Menorrhagia, Pelvic Pain, New Migraines
# CBC, UA, TSH, pelvic US, CT brain, Anaprox DS
assessments[200] = (3,
    "Workup is mostly appropriate, but CT scan of the brain for headache evaluation is outdated — MRI brain is now preferred (no radiation, better sensitivity for most pathology). Pelvic ultrasound for menorrhagia/pelvic pain is still appropriate.",
    "Replace CT brain with MRI brain (without contrast initially) for headache workup — more sensitive, no radiation. Continue pelvic ultrasound, CBC, UA, TSH. NSAIDs (Anaprox DS) for dysmenorrhea/headache still appropriate.")

# CASE 201: MTS_0837 — Erythema Nodosum
# Extensive workup: PPD, echo, labs, ergocalciferol
assessments[201] = (2,
    "Comprehensive workup for erythema nodosum is still appropriate. Would now use QuantiFERON-TB Gold (IGRA) instead of PPD for TB screening. Ergocalciferol for vitamin D deficiency is still appropriate.",
    "")

# CASE 202: MTS_0840 — Essential Tremor + Torticollis
# MRI brain
assessments[202] = (1,
    "MRI brain for tremor/torticollis evaluation is still appropriate. Botox for torticollis remains an option when patient is ready.",
    "")

# CASE 203: MTS_0851 — Pediatric Ear Pain
# Omeprazole for GERD, Augmentin for otitis
assessments[203] = (2,
    "Augmentin for treatment-failure otitis media (after amoxicillin) and PPI for suspected GERD are still appropriate management.",
    "")

# CASE 204: MTS_0857 — Otitis Media with Otorrhea
# Ceftin + Ciprodex drops
assessments[204] = (2,
    "Oral antibiotic + topical antibiotic drops for otitis media with drainage is still appropriate. Some would now use topical drops alone for draining ears.",
    "")

# CASE 205: MTS_0859 — Discoid Lupus
# Switch to Protopic, continue Plaquenil
assessments[205] = (1,
    "Tacrolimus (Protopic) for facial discoid lupus and hydroxychloroquine (Plaquenil) maintenance remain standard therapy per dermatology and rheumatology guidelines.",
    "")

# CASE 206: MTS_0862 — AMD + Glaucoma Suspect
# Ocuvite PreserVision, visual fields, disc photos
assessments[206] = (1,
    "AREDS2 supplementation, visual field testing, and disc photography for AMD with glaucoma suspect are still standard ophthalmic practice.",
    "")

# CASE 207: MTS_0863 — Dietary Consult (Diabetes)
assessments[207] = (1,
    "Dietary counseling for blood sugar management remains standard diabetes care.",
    "")

# CASE 208: MTS_0867 — Dietary Consult (Weight Loss)
assessments[208] = (1,
    "Dietary counseling with calorie counting and food diary review is still appropriate.",
    "")

# CASE 209: MTS_0881 — Colostomy Reversal Consult
# Barium enema
assessments[209] = (2,
    "Pre-reversal assessment is appropriate. Barium enema has been largely replaced by CT colonography or colonoscopy for evaluating the distal colon.",
    "")

# CASE 210: MTS_0898 — Normal Pressure Hydrocephalus
assessments[210] = (1,
    "Clinical assessment for NPH vs progressive supranuclear palsy is still the diagnostic challenge. Large-volume LP tap test remains the key diagnostic intervention.",
    "")

# CASE 211: MTS_0915 — Lumbar Disc Disruption
# Diclofenac 75mg BID, back brace
assessments[211] = (2,
    "NSAIDs (diclofenac) and bracing for back pain are still appropriate. Would now emphasize active physical therapy over passive bracing.",
    "")

# CASE 212: MTS_0917 — Cerebral Peduncle Infarction
assessments[212] = (2,
    "Post-stroke evaluation is appropriate. Would now ensure high-intensity statin, adequate BP control (<130/80), and secondary prevention measures per AHA/ASA guidelines.",
    "")

# CASE 213: MTS_0962 — Bunion Deformity
assessments[213] = (1,
    "Surgical planning for bunion deformity with osteotomy is still the standard approach.",
    "")

# CASE 214: MTS_0971 — Bariatric Surgery Consult
# Labs, upper GI, Medifast
assessments[214] = (2,
    "Pre-operative workup is appropriate. Sleeve gastrectomy is now more commonly performed than Roux-en-Y. GLP-1 RAs are sometimes used for pre-operative weight loss and may be considered as primary treatment.",
    "")

# CASE 215: MTS_0974 — Bariatric Surgery Consult
assessments[215] = (2,
    "Pre-operative nutritional and psychosocial assessment is still standard. GLP-1 RAs (semaglutide, tirzepatide) should now be discussed as a non-surgical option that may avoid or complement bariatric surgery.",
    "")

# CASE 216: MTS_0976 — Bariatric Surgery (Lap-Band Interest)
assessments[216] = (3,
    "Lap-Band has fallen significantly out of favor due to high failure and reoperation rates. Sleeve gastrectomy is now the most common bariatric procedure. GLP-1 RAs should also be discussed as pharmacological alternatives.",
    "Discuss sleeve gastrectomy (preferred over Lap-Band). GLP-1 RA therapy (semaglutide, tirzepatide) as non-surgical option. If patient still prefers minimally invasive, endoscopic sleeve gastroplasty is a newer option. Complete pre-op workup still appropriate.")

# CASE 217: MTS_0977 — Bariatric Surgery (Gastric Bypass Interest)
assessments[217] = (2,
    "Gastric bypass is still performed and appropriate. Sleeve gastrectomy is now more common as primary procedure. GLP-1 RAs should be discussed as non-surgical alternative. Upper endoscopy prior to bypass is still appropriate.",
    "")

# CASE 218: MTS_0986 — Ankle Sprain
assessments[218] = (1,
    "Discharge with follow-up for ankle sprain is standard. RICE protocol remains appropriate.",
    "")

# CASE 219: MTS_0995 — Possible Adult Hydrocephalus
# Large volume LP
assessments[219] = (1,
    "Large-volume lumbar puncture (tap test) for suspected normal pressure hydrocephalus is still the key diagnostic intervention.",
    "")

# ============================================================
# Build the output DataFrame
# ============================================================

rows = []
for i in range(220):
    row = df.iloc[i]
    score, comment, current_plan = assessments[i]
    rows.append({
        'Case ID': row['Case ID'],
        'Sample Name': row['Sample Name'],
        'Specialty': row['Specialty'],
        'Human Diagnoses': row['Human Diagnoses'],
        'Human A&P (summary)': str(row['Human A&P'])[:500],
        'Human Medications': row['Human Medications'] if pd.notna(row['Human Medications']) else '',
        'Human Tests': row['Human Tests'] if pd.notna(row['Human Tests']) else '',
        'Guideline Currency Score (1-5)': score,
        'Assessment Comment': comment,
        'Current Plan (if changed)': current_plan if current_plan else 'No major changes needed'
    })

out_df = pd.DataFrame(rows)

# Write to xlsx with formatting
output_path = 'data/guideline_currency_review.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    out_df.to_excel(writer, index=False, sheet_name='Guideline Review')

    # Auto-adjust column widths
    ws = writer.sheets['Guideline Review']
    for col_idx, col in enumerate(out_df.columns):
        max_len = max(out_df[col].astype(str).map(len).max(), len(col)) + 2
        max_len = min(max_len, 80)  # cap width
        ws.column_dimensions[chr(65 + col_idx) if col_idx < 26 else 'A' + chr(65 + col_idx - 26)].width = max_len

print(f"Written {len(out_df)} cases to {output_path}")
print()

# Summary statistics
print("=== SUMMARY ===")
scores = out_df['Guideline Currency Score (1-5)']
print(f"Score distribution:")
for s in range(1, 6):
    n = (scores == s).sum()
    pct = n / len(scores) * 100
    label = {1: 'Fully current', 2: 'Mostly current', 3: 'Partially outdated',
             4: 'Significantly outdated', 5: 'Substantially outdated'}[s]
    print(f"  {s} ({label}): {n} cases ({pct:.1f}%)")
print(f"Mean score: {scores.mean():.2f}")
print(f"Cases with score >= 3 (outdated): {(scores >= 3).sum()} ({(scores >= 3).sum()/len(scores)*100:.1f}%)")
print(f"Cases with score >= 4 (significantly outdated): {(scores >= 4).sum()} ({(scores >= 4).sum()/len(scores)*100:.1f}%)")

# List score 4-5 cases
print()
print("=== SIGNIFICANTLY/SUBSTANTIALLY OUTDATED CASES (Score 4-5) ===")
for _, r in out_df[out_df['Guideline Currency Score (1-5)'] >= 4].iterrows():
    print(f"  {r['Case ID']} | {r['Sample Name']} | Score {r['Guideline Currency Score (1-5)']}")
    print(f"    {r['Assessment Comment'][:150]}...")
    print()
