# Data Dictionary — Patient Journey & Treatment Adoption Analytics

> This dictionary describes every column in `data/patient_data_clean.csv`.
> The dataset contains **synthetic data** created for analytical and educational purposes only.

---

## Patient Demographics

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Patient_ID` | Unique identifier for each patient | String | `PT000001` | Used to join tables and count unique patients |
| `Age` | Patient's age in years at time of diagnosis | Integer | `52` | Older patients may have different severity and adoption patterns |
| `Gender` | Patient's reported gender | String | `Female` | Allows demographic analysis of adoption differences |
| `Region` | US geographic region | String | `Southeast` | Used for regional market opportunity analysis |
| `State` | US state of the patient | String | `Georgia` | More granular geographic breakdown |
| `Urban_Rural` | Patient's residential setting | String | `Urban` | Rural patients may face greater access challenges |

---

## Socioeconomic Factors

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Income_Band` | Household income category | String | `Medium` | Key affordability driver; `Low`, `Medium`, `High` |
| `Insurance_Status` | Patient's health insurance coverage | String | `Insured` | Strongly associated with treatment adoption; `Insured`, `Underinsured`, `Uninsured` |
| `Affordability_Score` | Composite score of financial ability to afford treatment | Float (0–10) | `6.8` | 10 = most affordable; derived from income and insurance |
| `Treatment_Cost` | Estimated out-of-pocket treatment cost (USD) | Integer | `18500` | Higher cost is associated with lower adoption |

---

## Clinical Factors

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Disease_Severity` | Severity classification of the patient's condition | String | `Moderate` | `Mild`, `Moderate`, `Severe`; higher severity is associated with greater treatment urgency |
| `Diagnosis_Date` | Date the patient was diagnosed | Date (YYYY-MM-DD) | `2022-03-15` | Used to track time-to-treatment and patient cohort analysis |
| `Previous_Treatment` | Whether the patient had a prior treatment before Therapy X | Integer (0/1) | `1` | Prior treatment experience may affect openness to new therapy |
| `Side_Effect_Concern` | Patient's self-reported concern about potential side effects | Float (1–10) | `7.2` | 10 = very concerned; higher concern is associated with lower adoption |

---

## Healthcare Access & Awareness

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Healthcare_Access_Score` | Composite measure of access to healthcare services | Float (0–10) | `5.4` | 10 = best access; includes proximity, availability, and quality of care |
| `Awareness_Score` | Patient's level of awareness about Therapy X | Float (0–10) | `4.1` | 10 = fully aware; lower awareness may reduce initiation rates |

---

## Patient Journey Stages

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Doctor_Consultation` | Whether the patient had a consultation with a doctor | Integer (0/1) | `1` | First step in the treatment journey after diagnosis |
| `Treatment_Recommended` | Whether a physician recommended Therapy X | Integer (0/1) | `1` | Key gateway to treatment initiation |
| `Treatment_Started` | Whether the patient started Therapy X | Integer (0/1) | `1` | **Primary adoption metric** used throughout the analysis |
| `Treatment_Start_Date` | Date the patient began Therapy X | Date (YYYY-MM-DD) or blank | `2022-05-01` | Blank if treatment was never started |
| `Treatment_Continued` | Whether the patient continued treatment after initiation | Integer (0/1) | `1` | Measures adherence / persistence |
| `Follow_Up_Completed` | Whether the patient completed a follow-up appointment | Integer (0/1) | `0` | Indicator of full care pathway completion |
| `Drop_Off_Stage` | The stage at which the patient dropped out of the journey | String | `After Consultation` | Identifies where patients are lost; key intervention point |

---

## Derived Columns (Added During Cleaning)

| Column | Description | Data Type | Example | Business Meaning |
|--------|-------------|-----------|---------|-----------------|
| `Age_Group` | Categorical age band | String | `31-45` | Groups: `18-30`, `31-45`, `46-60`, `61+`; simplifies age analysis |
| `Cost_Band` | Treatment cost category | String | `Medium ($15-35k)` | Groups: `Low (<$15k)`, `Medium ($15-35k)`, `High ($35-60k)`, `Very High (>$60k)` |

---

## Drop-Off Stage Values

| Value | Meaning |
|-------|---------|
| `After Diagnosis` | Patient never consulted a doctor |
| `After Consultation` | Patient consulted a doctor but was not recommended Therapy X |
| `After Recommendation` | Therapy X was recommended but the patient did not start |
| `After Starting Treatment` | Patient started but did not continue treatment |
| `No Drop-off` | Patient completed the full journey (started + continued + follow-up) |

---

## Key Binary Columns

All columns with values `0` or `1` follow this convention:

| Value | Meaning |
|-------|---------|
| `1` | Yes / True / Completed |
| `0` | No / False / Not completed |

---

*Disclaimer: This dataset is entirely synthetic and was generated for analytical and educational purposes.
It does not represent real patients, real clinical outcomes, medical advice, or actual pharmaceutical market data.*
