"""
generate_data.py
----------------
Generates a synthetic patient dataset for the
Patient Journey & Treatment Adoption Analytics project.

This script creates a realistic (but entirely fictional) dataset
of ~25,000 patients for a fictional drug called "Therapy X"
offered by a fictional pharmaceutical company.

DISCLAIMER:
This script generates synthetic data created for analytical and
educational purposes only. It does not represent real patients,
real clinical outcomes, medical advice, or actual pharmaceutical
market data.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
rng = np.random.default_rng(SEED)

# ── Constants ─────────────────────────────────────────────────────────────────
N_PATIENTS = 25_000

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
STATES = {
    "Northeast": ["New York", "Pennsylvania", "Massachusetts", "New Jersey", "Connecticut"],
    "Southeast": ["Florida", "Georgia", "North Carolina", "Virginia", "Tennessee"],
    "Midwest":   ["Illinois", "Ohio", "Michigan", "Indiana", "Wisconsin"],
    "Southwest": ["Texas", "Arizona", "New Mexico", "Oklahoma", "Nevada"],
    "West":      ["California", "Washington", "Oregon", "Colorado", "Utah"],
}

URBAN_RURAL = ["Urban", "Suburban", "Rural"]
INCOME_BANDS = ["Low", "Medium", "High"]
INSURANCE_TYPES = ["Insured", "Underinsured", "Uninsured"]
SEVERITIES = ["Mild", "Moderate", "Severe"]
GENDERS = ["Male", "Female", "Non-binary"]

DROP_OFF_STAGES = [
    "No Drop-off",
    "After Diagnosis",
    "After Consultation",
    "After Recommendation",
    "After Starting Treatment",
]

# ── Helper: random date in a range ───────────────────────────────────────────
def rand_date(start: datetime, end: datetime, size: int) -> np.ndarray:
    delta = (end - start).days
    offsets = rng.integers(0, delta, size=size)
    return np.array([start + timedelta(days=int(d)) for d in offsets])


def main():
    print("Generating synthetic patient dataset …")

    # ── Demographics ──────────────────────────────────────────────────────────
    ages = rng.integers(18, 80, size=N_PATIENTS)
    genders = rng.choice(GENDERS, size=N_PATIENTS, p=[0.48, 0.48, 0.04])

    # Region → State
    region_probs = [0.22, 0.22, 0.20, 0.18, 0.18]
    regions = rng.choice(REGIONS, size=N_PATIENTS, p=region_probs)
    states = np.array(
        [rng.choice(STATES[r]) for r in regions]
    )

    # Urban / Rural  (Urban more common overall)
    urban_rural = rng.choice(URBAN_RURAL, size=N_PATIENTS, p=[0.50, 0.30, 0.20])

    # Income band
    income_band = rng.choice(INCOME_BANDS, size=N_PATIENTS, p=[0.30, 0.45, 0.25])

    # Insurance correlated with income
    insurance_status = []
    for ib in income_band:
        if ib == "High":
            insurance_status.append(rng.choice(INSURANCE_TYPES, p=[0.85, 0.12, 0.03]))
        elif ib == "Medium":
            insurance_status.append(rng.choice(INSURANCE_TYPES, p=[0.60, 0.28, 0.12]))
        else:  # Low
            insurance_status.append(rng.choice(INSURANCE_TYPES, p=[0.35, 0.35, 0.30]))
    insurance_status = np.array(insurance_status)

    # Disease severity (slightly higher in older patients)
    severity_list = []
    for age in ages:
        if age >= 60:
            severity_list.append(rng.choice(SEVERITIES, p=[0.25, 0.45, 0.30]))
        elif age >= 40:
            severity_list.append(rng.choice(SEVERITIES, p=[0.35, 0.45, 0.20]))
        else:
            severity_list.append(rng.choice(SEVERITIES, p=[0.50, 0.38, 0.12]))
    disease_severity = np.array(severity_list)

    # Diagnosis dates: Jan 2021 – Dec 2023
    diagnosis_dates = rand_date(datetime(2021, 1, 1), datetime(2023, 12, 31), N_PATIENTS)

    # ── Scores (0-10) ─────────────────────────────────────────────────────────
    # Healthcare Access: better in Urban/High-income
    hca_base = {
        ("Urban",    "High"):   (7.5, 1.2),
        ("Urban",    "Medium"): (6.5, 1.5),
        ("Urban",    "Low"):    (5.0, 1.8),
        ("Suburban", "High"):   (6.5, 1.3),
        ("Suburban", "Medium"): (5.5, 1.6),
        ("Suburban", "Low"):    (4.2, 1.7),
        ("Rural",    "High"):   (5.0, 1.5),
        ("Rural",    "Medium"): (3.8, 1.6),
        ("Rural",    "Low"):    (2.8, 1.5),
    }
    hca_scores = np.array([
        np.clip(rng.normal(*hca_base.get((ur, ib), (5.0, 1.5))), 0, 10)
        for ur, ib in zip(urban_rural, income_band)
    ])

    # Awareness score: random with slight urban boost
    awareness_base = np.where(urban_rural == "Urban", 5.5, np.where(urban_rural == "Suburban", 4.8, 3.8))
    awareness_scores = np.clip(rng.normal(awareness_base, 1.8), 0, 10)

    # Affordability score: driven by income + insurance
    afford_map = {
        ("High",   "Insured"):      (8.0, 1.0),
        ("High",   "Underinsured"): (6.5, 1.2),
        ("High",   "Uninsured"):    (5.0, 1.5),
        ("Medium", "Insured"):      (6.0, 1.3),
        ("Medium", "Underinsured"): (4.5, 1.5),
        ("Medium", "Uninsured"):    (3.0, 1.5),
        ("Low",    "Insured"):      (4.0, 1.4),
        ("Low",    "Underinsured"): (2.5, 1.3),
        ("Low",    "Uninsured"):    (1.5, 1.0),
    }
    affordability_scores = np.array([
        np.clip(rng.normal(*afford_map.get((ib, ins), (4.0, 1.5))), 0, 10)
        for ib, ins in zip(income_band, insurance_status)
    ])

    # Treatment cost ($5,000 – $80,000)  lower for insured
    cost_base = np.where(
        insurance_status == "Insured", rng.uniform(5_000, 25_000, N_PATIENTS),
        np.where(insurance_status == "Underinsured",
                 rng.uniform(10_000, 50_000, N_PATIENTS),
                 rng.uniform(20_000, 80_000, N_PATIENTS))
    )
    treatment_costs = np.round(cost_base, -2)  # round to nearest 100

    # Previous treatment (binary)
    previous_treatment = rng.choice([0, 1], size=N_PATIENTS, p=[0.60, 0.40])

    # Side effect concern score 1-10
    side_effect_concern = np.round(rng.uniform(1, 10, N_PATIENTS), 1)

    # ── Doctor Consultation ───────────────────────────────────────────────────
    # Higher access → more likely to consult
    consult_prob = np.clip(0.5 + (hca_scores - 5) * 0.06, 0.25, 0.95)
    doctor_consultation = rng.random(N_PATIENTS) < consult_prob

    # ── Treatment Recommended ─────────────────────────────────────────────────
    # Only if consulted; higher for severe disease
    sev_bonus = np.where(disease_severity == "Severe", 0.15,
                np.where(disease_severity == "Moderate", 0.05, -0.05))
    rec_prob = np.clip(0.55 + sev_bonus + rng.normal(0, 0.05, N_PATIENTS), 0.1, 0.95)
    treatment_recommended = np.where(
        doctor_consultation,
        rng.random(N_PATIENTS) < rec_prob,
        False
    )

    # ── Treatment Started ─────────────────────────────────────────────────────
    # Driven by: recommendation, affordability, insurance, severity, awareness
    started_prob = (
        0.25
        + 0.28 * treatment_recommended.astype(float)
        + 0.05 * (affordability_scores / 10)
        + np.where(insurance_status == "Insured", 0.10,
           np.where(insurance_status == "Underinsured", 0.03, -0.05))
        + np.where(disease_severity == "Severe", 0.08,
           np.where(disease_severity == "Moderate", 0.03, -0.02))
        + 0.02 * (awareness_scores / 10)
        - 0.04 * (treatment_costs / 80_000)
        - 0.02 * (side_effect_concern / 10)
        + rng.normal(0, 0.06, N_PATIENTS)
    )
    started_prob = np.clip(started_prob, 0.05, 0.95)
    treatment_started = rng.random(N_PATIENTS) < started_prob

    # ── Treatment Start Date ──────────────────────────────────────────────────
    # 0–180 days after diagnosis
    start_delay = rng.integers(7, 180, size=N_PATIENTS)
    treatment_start_dates = np.where(
        treatment_started,
        np.array([d + timedelta(days=int(dd)) for d, dd in zip(diagnosis_dates, start_delay)]),
        None
    )

    # ── Treatment Continued ───────────────────────────────────────────────────
    # Only if started; higher for high access, lower for high side effect concern
    cont_prob = np.clip(
        0.55
        + 0.05 * (hca_scores / 10)
        - 0.06 * (side_effect_concern / 10)
        + np.where(insurance_status == "Insured", 0.08, 0.0)
        + rng.normal(0, 0.07, N_PATIENTS),
        0.20, 0.95
    )
    treatment_continued = np.where(
        treatment_started,
        rng.random(N_PATIENTS) < cont_prob,
        False
    )

    # ── Follow-up Completed ───────────────────────────────────────────────────
    followup_prob = np.clip(
        0.50 + 0.04 * (hca_scores / 10) + rng.normal(0, 0.06, N_PATIENTS),
        0.20, 0.90
    )
    follow_up_completed = np.where(
        treatment_continued,
        rng.random(N_PATIENTS) < followup_prob,
        False
    )

    # ── Drop-off Stage ────────────────────────────────────────────────────────
    drop_off_stage = []
    for i in range(N_PATIENTS):
        if not doctor_consultation[i]:
            drop_off_stage.append("After Diagnosis")
        elif not treatment_recommended[i]:
            drop_off_stage.append("After Consultation")
        elif not treatment_started[i]:
            drop_off_stage.append("After Recommendation")
        elif not treatment_continued[i]:
            drop_off_stage.append("After Starting Treatment")
        else:
            drop_off_stage.append("No Drop-off")
    drop_off_stage = np.array(drop_off_stage)

    # ── Build DataFrame ───────────────────────────────────────────────────────
    patient_ids = [f"PT{str(i+1).zfill(6)}" for i in range(N_PATIENTS)]

    df = pd.DataFrame({
        "Patient_ID":           patient_ids,
        "Age":                  ages,
        "Gender":               genders,
        "Region":               regions,
        "State":                states,
        "Urban_Rural":          urban_rural,
        "Income_Band":          income_band,
        "Insurance_Status":     insurance_status,
        "Disease_Severity":     disease_severity,
        "Diagnosis_Date":       [d.strftime("%Y-%m-%d") for d in diagnosis_dates],
        "Doctor_Consultation":  doctor_consultation.astype(int),
        "Treatment_Recommended":treatment_recommended.astype(int),
        "Treatment_Cost":       treatment_costs.astype(int),
        "Affordability_Score":  np.round(affordability_scores, 2),
        "Healthcare_Access_Score": np.round(hca_scores, 2),
        "Awareness_Score":      np.round(awareness_scores, 2),
        "Previous_Treatment":   previous_treatment,
        "Side_Effect_Concern":  side_effect_concern,
        "Treatment_Started":    treatment_started.astype(int),
        "Treatment_Start_Date": [
            d.strftime("%Y-%m-%d") if d is not None else None
            for d in treatment_start_dates
        ],
        "Treatment_Continued":  treatment_continued.astype(int),
        "Follow_Up_Completed":  follow_up_completed.astype(int),
        "Drop_Off_Stage":       drop_off_stage,
    })

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs("data", exist_ok=True)
    out_path = "data/patient_data.csv"
    df.to_csv(out_path, index=False)
    print(f"  ✓  Saved {len(df):,} records → {out_path}")
    print(f"  Overall adoption rate: {df['Treatment_Started'].mean():.1%}")
    print(f"  Consultation rate:     {df['Doctor_Consultation'].mean():.1%}")
    print(f"  Continuation rate:     {df['Treatment_Continued'].mean():.1%}")


if __name__ == "__main__":
    main()
