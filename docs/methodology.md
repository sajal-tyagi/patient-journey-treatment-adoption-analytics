# Methodology — Patient Journey & Treatment Adoption Analytics

> This document explains the methods used in plain language, aimed at beginners.

---

## 1. How Synthetic Data Was Created

The dataset was generated using Python's `numpy.random` library with a fixed random seed (`42`)
to ensure reproducibility. Every time you run `generate_data.py`, you get exactly the same dataset.

**Why synthetic data?**
Real patient data is private and legally protected. Synthetic data lets us build and demonstrate
analytical methods without using real personal information.

**How realism was added:**
Rather than generating random numbers with no meaning, the script introduces *realistic relationships*:

- Insurance status is linked to income band (wealthier patients are more likely to be insured).
- Healthcare Access Score is higher for urban, high-income patients.
- Affordability Score depends on both income and insurance.
- Physician recommendation depends on disease severity.
- Treatment adoption probability is calculated from a weighted combination of several factors,
  then randomness (noise) is added so the relationships are real but not perfect.

This mimics how real-world data behaves: trends exist, but they are never absolute.

---

## 2. How Data Was Cleaned

Cleaning was performed in `clean_data.py`. The steps were:

1. **Duplicate check** — confirmed no duplicate Patient IDs.
2. **Missing value check** — all key columns were checked; any missing values in non-date fields
   were filled with the column median (for numbers) or mode (for categories).
3. **Range validation** — ages were clamped to [18, 100]; all score columns were clamped to [0, 10].
4. **Date logic** — confirmed that no treatment start date appeared before the diagnosis date.
5. **Logical consistency** — ensured that:
   - A physician cannot recommend without consulting first.
   - Treatment cannot continue if it was never started.
   - Follow-up cannot be completed if treatment was not continued.
6. **Drop-off stage re-derivation** — after fixing any inconsistencies above, the `Drop_Off_Stage`
   column was fully recalculated from first principles to ensure it correctly reflected each
   patient's position in the journey.
7. **Derived columns** — `Age_Group` and `Cost_Band` were added as readable groupings for analysis.

The quality of the generated data was very high — no significant issues were found.

---

## 3. How Patient Journey Was Calculated

The patient journey is a **funnel analysis**:

1. Count all diagnosed patients (starting point = 25,000).
2. Count how many consulted a doctor.
3. Count how many received a treatment recommendation.
4. Count how many started Therapy X.
5. Count how many continued treatment.
6. Count how many completed a follow-up.

At each step, we calculate:
- **Conversion vs. Diagnosed** — what % of the original 25,000 reached this stage?
- **Stage-to-stage conversion** — what % of patients at the previous stage made it to this stage?
- **Drop-off rate** — what % of patients at the previous stage were lost?

The largest single drop-off (by percentage) is identified as the most critical intervention point.

---

## 4. How Patient Segments Were Created

Segmentation uses a simple **rule-based approach** rather than complex machine learning.

**Two dimensions were used:**

**Need Level:**
- `High-Need` = Moderate or Severe disease
- `Low-Need` = Mild disease

**Ability Level** (financial/insurance):
- `High-Ability` = Insured AND Affordability Score ≥ 5
- `Low-Ability` = Uninsured OR Affordability Score < 3
- `Medium-Ability` = everyone else

Crossing these two dimensions creates 6 business segments (e.g., `High-Need / High-Ability`).

This approach is intentionally transparent and business-friendly. Unlike clustering algorithms,
anyone can understand and explain these segments.

---

## 5. How Treatment Adoption Was Calculated

**Primary metric:** `Treatment_Started` — a binary column (1 = started, 0 = did not start).

**Adoption rate** = number of patients who started / total patients in the group.

Adoption was calculated across multiple groupings:
- Age group
- Disease severity
- Insurance status
- Region
- Physician recommendation
- Previous treatment
- Treatment cost band

Simple group comparisons reveal which patient characteristics are associated with higher or
lower treatment adoption.

---

## 6. How Logistic Regression Was Used

**What is logistic regression?**
Logistic regression is a simple statistical model that predicts the probability of a binary
outcome (in this case: started treatment = yes or no). It learns a weight (coefficient) for
each input factor. Positive coefficients increase the predicted probability; negative coefficients
decrease it.

**Why logistic regression?**
It is interpretable, fast, requires no complex tuning, and is appropriate for a binary outcome.
It is widely used in healthcare and business analytics as a baseline model.

**How it was applied:**
1. Selected 10 features: Age, Severity, Insurance, Physician Recommendation, Affordability,
   Healthcare Access, Awareness, Previous Treatment, Side Effect Concern.
2. Split data into 75% training and 25% test sets.
3. Standardised all features (scaled to similar ranges) so coefficients are comparable.
4. Fitted the model on the training set.
5. Evaluated on the test set using accuracy, precision, recall, F1, and ROC-AUC.

**Important caveat:**
The logistic regression identifies *associations* — not *causes*. Just because physician
recommendation is strongly associated with treatment adoption does not mean the recommendation
caused the adoption. Other unmeasured factors may be at play.

---

## 7. How Market Opportunity Was Calculated

For each region, we calculated:
- **Total Patients** — how many patients are in the region?
- **Treated Patients** — how many started Therapy X?
- **Untreated Patients** — Total − Treated
- **Adoption Rate %** — Treated / Total × 100
- **Adoption Gap %** — 100 − Adoption Rate (how far from full adoption?)

**Opportunity Score:**
A simple score combining two normalised metrics:
- Normalised Untreated Volume (0–1) — larger untreated pool = higher score
- Normalised Adoption Gap (0–1) — larger gap from maximum adoption = higher score

Opportunity Score = 0.5 × Normalised Untreated + 0.5 × Normalised Gap

This is a simple, transparent formula. Both components contribute equally. Regions with large
untreated populations *and* large adoption gaps score highest.

**Note:** This is a simplified, illustrative framework. A real market opportunity assessment
would also factor in competitor presence, physician density, pricing, and many other variables.

---

## 8. How Power BI Would Use the Data

The cleaned CSV (`data/patient_data_clean.csv`) is imported directly into Power BI Desktop
as a data source. No database or server is required.

From there:
- Pre-defined DAX measures calculate KPIs (adoption rate, continuation rate, etc.)
- Visualisations are built using drag-and-drop tools
- Slicers allow filtering by Region, Severity, Insurance Status, etc.
- Pages are organised by theme (Overview, Journey, Segments, Adoption, Opportunity)

See `powerbi/dashboard_specification.md` and `powerbi/dax_measures.md` for full details.

---

*Disclaimer: This project uses synthetic data created for analytical and educational purposes.
All methods are intentionally kept simple and beginner-friendly.*
