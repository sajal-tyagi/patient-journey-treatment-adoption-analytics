"""
clean_data.py
-------------
Reads the raw synthetic patient dataset, checks data quality,
fixes any issues, and outputs a clean version ready for analysis.

DISCLAIMER:
This project uses synthetic data created for analytical and
educational purposes only. It does not represent real patients,
real clinical outcomes, medical advice, or actual pharmaceutical
market data.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_PATH   = "data/patient_data.csv"
CLEAN_PATH = "data/patient_data_clean.csv"
QUAL_PATH  = "results/data_quality_summary.csv"


def main():
    print("Running data cleaning …")
    os.makedirs("results", exist_ok=True)

    # ── 1. Load ───────────────────────────────────────────────────────────────
    df = pd.read_csv(RAW_PATH)
    initial_rows = len(df)
    print(f"  Loaded {initial_rows:,} rows, {df.shape[1]} columns")

    # ── 2. Track quality issues ───────────────────────────────────────────────
    quality_log = []

    def log(check, issue_count, action):
        quality_log.append({
            "Check":       check,
            "Issues_Found": issue_count,
            "Action_Taken": action,
        })
        if issue_count > 0:
            print(f"  ⚠  {check}: {issue_count} issues — {action}")
        else:
            print(f"  ✓  {check}: OK")

    # ── 3. Duplicate Patient IDs ──────────────────────────────────────────────
    dupes = df.duplicated(subset="Patient_ID").sum()
    log("Duplicate Patient_IDs", dupes, "Dropped duplicates" if dupes else "No action")
    if dupes:
        df = df.drop_duplicates(subset="Patient_ID")

    # ── 4. Missing values ─────────────────────────────────────────────────────
    # Treatment_Start_Date is legitimately null for non-starters — exclude it
    cols_to_check = [c for c in df.columns if c != "Treatment_Start_Date"]
    missing = df[cols_to_check].isnull().sum().sum()
    log("Missing values (excl. Treatment_Start_Date)", missing,
        "Filled with mode/median" if missing else "No action")
    if missing:
        for col in cols_to_check:
            if df[col].isnull().any():
                if df[col].dtype == "object":
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna(df[col].median())

    # ── 5. Age range ──────────────────────────────────────────────────────────
    invalid_age = ((df["Age"] < 18) | (df["Age"] > 100)).sum()
    log("Invalid age (<18 or >100)", invalid_age,
        "Clamped to [18, 100]" if invalid_age else "No action")
    df["Age"] = df["Age"].clip(18, 100)

    # ── 6. Score ranges (0–10) ────────────────────────────────────────────────
    score_cols = ["Affordability_Score", "Healthcare_Access_Score",
                  "Awareness_Score", "Side_Effect_Concern"]
    for col in score_cols:
        out = ((df[col] < 0) | (df[col] > 10)).sum()
        log(f"{col} out of range [0,10]", out,
            "Clamped" if out else "No action")
        df[col] = df[col].clip(0, 10)

    # ── 7. Treatment cost ─────────────────────────────────────────────────────
    neg_cost = (df["Treatment_Cost"] < 0).sum()
    log("Negative Treatment_Cost", neg_cost,
        "Set to 0" if neg_cost else "No action")
    df["Treatment_Cost"] = df["Treatment_Cost"].clip(lower=0)

    # ── 8. Date logic: Treatment_Start_Date after Diagnosis_Date ─────────────
    df["Diagnosis_Date"] = pd.to_datetime(df["Diagnosis_Date"])
    df["Treatment_Start_Date"] = pd.to_datetime(df["Treatment_Start_Date"])

    bad_dates = (
        df["Treatment_Started"] == 1
    ) & (
        df["Treatment_Start_Date"] < df["Diagnosis_Date"]
    )
    log("Treatment start before diagnosis", bad_dates.sum(),
        "Added 1 day to start date" if bad_dates.sum() else "No action")
    df.loc[bad_dates, "Treatment_Start_Date"] = (
        df.loc[bad_dates, "Diagnosis_Date"] + pd.Timedelta(days=1)
    )

    # ── 9. Logical consistency checks ─────────────────────────────────────────
    # If not consulted, can't have a recommendation
    bad_rec = (df["Doctor_Consultation"] == 0) & (df["Treatment_Recommended"] == 1)
    log("Recommendation without consultation", bad_rec.sum(),
        "Set Treatment_Recommended=0" if bad_rec.sum() else "No action")
    df.loc[bad_rec, "Treatment_Recommended"] = 0

    # If treatment not started, can't have continued or follow-up
    bad_cont = (df["Treatment_Started"] == 0) & (df["Treatment_Continued"] == 1)
    log("Continuation without starting", bad_cont.sum(),
        "Set Treatment_Continued=0" if bad_cont.sum() else "No action")
    df.loc[bad_cont, "Treatment_Continued"] = 0

    bad_fu = (df["Treatment_Continued"] == 0) & (df["Follow_Up_Completed"] == 1)
    log("Follow-up without continuation", bad_fu.sum(),
        "Set Follow_Up_Completed=0" if bad_fu.sum() else "No action")
    df.loc[bad_fu, "Follow_Up_Completed"] = 0

    # If not started, Treatment_Start_Date should be null
    df.loc[df["Treatment_Started"] == 0, "Treatment_Start_Date"] = pd.NaT

    # ── 10. Categorical value checks ──────────────────────────────────────────
    valid_cats = {
        "Gender":           {"Male", "Female", "Non-binary"},
        "Region":           {"Northeast", "Southeast", "Midwest", "Southwest", "West"},
        "Urban_Rural":      {"Urban", "Suburban", "Rural"},
        "Income_Band":      {"Low", "Medium", "High"},
        "Insurance_Status": {"Insured", "Underinsured", "Uninsured"},
        "Disease_Severity": {"Mild", "Moderate", "Severe"},
    }
    for col, valid in valid_cats.items():
        bad = ~df[col].isin(valid)
        log(f"Invalid category in {col}", bad.sum(), "No action needed" if not bad.sum() else "Unexpected")

    # ── 11. Drop-off stage consistency ────────────────────────────────────────
    # Re-derive Drop_Off_Stage to ensure consistency after fixes above
    conditions = [
        df["Doctor_Consultation"] == 0,
        (df["Doctor_Consultation"] == 1) & (df["Treatment_Recommended"] == 0),
        (df["Treatment_Recommended"] == 1) & (df["Treatment_Started"] == 0),
        (df["Treatment_Started"] == 1) & (df["Treatment_Continued"] == 0),
    ]
    choices = [
        "After Diagnosis",
        "After Consultation",
        "After Recommendation",
        "After Starting Treatment",
    ]
    df["Drop_Off_Stage"] = np.select(conditions, choices, default="No Drop-off")
    log("Drop_Off_Stage re-derived for consistency", 0, "Re-derived column")

    # ── 12. Add derived columns useful for analysis ───────────────────────────
    # Age group
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 30, 45, 60, 100],
        labels=["18-30", "31-45", "46-60", "61+"]
    )

    # Cost band
    df["Cost_Band"] = pd.cut(
        df["Treatment_Cost"],
        bins=[0, 15_000, 35_000, 60_000, 999_999],
        labels=["Low (<$15k)", "Medium ($15-35k)", "High ($35-60k)", "Very High (>$60k)"]
    )

    # ── 13. Final row count ───────────────────────────────────────────────────
    final_rows = len(df)
    removed = initial_rows - final_rows
    log(f"Rows removed during cleaning", removed, f"{removed} rows removed")

    # ── 14. Save outputs ──────────────────────────────────────────────────────
    # Reformat dates as strings for CSV
    df["Diagnosis_Date"] = df["Diagnosis_Date"].dt.strftime("%Y-%m-%d")
    df["Treatment_Start_Date"] = df["Treatment_Start_Date"].dt.strftime("%Y-%m-%d")

    df.to_csv(CLEAN_PATH, index=False)
    print(f"\n  ✓  Clean data saved → {CLEAN_PATH}  ({len(df):,} rows)")

    # Quality summary
    qual_df = pd.DataFrame(quality_log)
    qual_df.to_csv(QUAL_PATH, index=False)
    print(f"  ✓  Quality summary saved → {QUAL_PATH}")

    # Quick summary stats
    print("\n── Summary after cleaning ──────────────────────────────────────────")
    print(f"  Total patients:        {len(df):,}")
    print(f"  Consulted doctor:      {df['Doctor_Consultation'].mean():.1%}")
    print(f"  Treatment recommended: {df['Treatment_Recommended'].mean():.1%}")
    print(f"  Treatment started:     {df['Treatment_Started'].mean():.1%}")
    print(f"  Treatment continued:   {df['Treatment_Continued'].mean():.1%}")
    print(f"  Follow-up completed:   {df['Follow_Up_Completed'].mean():.1%}")


if __name__ == "__main__":
    main()
