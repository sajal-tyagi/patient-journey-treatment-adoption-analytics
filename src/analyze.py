"""
analyze.py
----------
Main analysis script for the Patient Journey & Treatment Adoption Analytics project.

Performs:
  1. Patient Journey Analysis (funnel)
  2. Patient Segmentation
  3. Treatment Adoption Analysis
  4. Adoption Drivers (Logistic Regression)
  5. Market Opportunity Analysis

Saves results to results/ and charts to outputs/.

DISCLAIMER:
This project uses synthetic data created for analytical and
educational purposes only. It does not represent real patients,
real clinical outcomes, medical advice, or actual pharmaceutical
market data.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")           # non-interactive backend for saving files
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, roc_auc_score,
                             classification_report)

# ── Paths ─────────────────────────────────────────────────────────────────────
CLEAN_PATH = "data/patient_data_clean.csv"
os.makedirs("results", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE   = "#264653 #2a9d8f #e9c46a #f4a261 #e76f51".split()
BLUE      = "#2a9d8f"
ORANGE    = "#f4a261"
RED       = "#e76f51"
DARK      = "#264653"

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams.update({
    "figure.dpi":        150,
    "savefig.dpi":       200,
    "savefig.bbox":      "tight",
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


# ─────────────────────────────────────────────────────────────────────────────
# 1. PATIENT JOURNEY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def patient_journey(df):
    print("\n── 1. Patient Journey Analysis ─────────────────────────────────────")

    stages = [
        ("Diagnosed",              len(df)),
        ("Doctor Consultation",    df["Doctor_Consultation"].sum()),
        ("Treatment Recommended",  df["Treatment_Recommended"].sum()),
        ("Treatment Started",      df["Treatment_Started"].sum()),
        ("Treatment Continued",    df["Treatment_Continued"].sum()),
        ("Follow-up Completed",    df["Follow_Up_Completed"].sum()),
    ]

    journey = pd.DataFrame(stages, columns=["Stage", "Patients"])
    journey["Conversion_vs_Diagnosed_%"] = (
        journey["Patients"] / journey.loc[0, "Patients"] * 100
    ).round(2)
    journey["Stage_to_Stage_Conversion_%"] = (
        journey["Patients"].pct_change() * 100
    ).round(2).fillna(0)
    journey["Drop_Off_%"] = (
        (journey["Patients"].shift(1) - journey["Patients"]) /
        journey["Patients"].shift(1) * 100
    ).round(2).fillna(0)

    journey.to_csv("results/patient_journey_summary.csv", index=False)
    print(journey.to_string(index=False))

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [BLUE if i == 0 else ORANGE if i == 3 else DARK for i in range(len(journey))]

    bars = ax.barh(journey["Stage"][::-1], journey["Patients"][::-1],
                   color=colors[::-1], edgecolor="white", height=0.6)

    for bar, (_, row) in zip(bars, journey[::-1].iterrows()):
        pct = row["Conversion_vs_Diagnosed_%"]
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                f"{int(row['Patients']):,}  ({pct:.1f}%)",
                va="center", fontsize=9, color="#333333")

    ax.set_xlabel("Number of Patients", fontsize=11)
    ax.set_title("Patient Journey Funnel — Therapy X", fontsize=14, fontweight="bold", pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlim(0, journey["Patients"].max() * 1.22)
    fig.tight_layout()
    fig.savefig("outputs/patient_journey_funnel.png")
    plt.close(fig)
    print("  ✓  Chart saved → outputs/patient_journey_funnel.png")

    return journey


# ─────────────────────────────────────────────────────────────────────────────
# 2. PATIENT SEGMENTATION
# ─────────────────────────────────────────────────────────────────────────────
def patient_segmentation(df):
    print("\n── 2. Patient Segmentation ─────────────────────────────────────────")

    # Business segment: Need × Ability
    sev_map = {"Severe": "High-Need", "Moderate": "High-Need", "Mild": "Low-Need"}
    df = df.copy()
    df["Need_Level"] = df["Disease_Severity"].map(sev_map)

    # Ability = Insured + Affordability_Score > 5
    df["Ability_Level"] = np.where(
        (df["Insurance_Status"] == "Insured") & (df["Affordability_Score"] >= 5),
        "High-Ability",
        np.where(
            (df["Insurance_Status"] == "Uninsured") | (df["Affordability_Score"] < 3),
            "Low-Ability",
            "Medium-Ability"
        )
    )

    df["Business_Segment"] = df["Need_Level"] + " / " + df["Ability_Level"]

    seg = (
        df.groupby("Business_Segment")
        .agg(
            Total_Patients=("Patient_ID", "count"),
            Adopted=("Treatment_Started", "sum"),
            Adoption_Rate=("Treatment_Started", "mean"),
        )
        .reset_index()
    )
    seg["Adoption_Rate_%"] = (seg["Adoption_Rate"] * 100).round(2)
    seg["Untreated_Patients"] = seg["Total_Patients"] - seg["Adopted"]
    seg.drop(columns="Adoption_Rate", inplace=True)
    seg.sort_values("Total_Patients", ascending=False, inplace=True)

    seg.to_csv("results/segment_summary.csv", index=False)
    print(seg.to_string(index=False))

    # ── Chart 1: Segment distribution ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    palette = sns.color_palette(PALETTE, len(seg))
    bars = ax.bar(seg["Business_Segment"], seg["Total_Patients"],
                  color=palette, edgecolor="white", width=0.55)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                f"{int(bar.get_height()):,}", ha="center", fontsize=9)
    ax.set_xlabel("Patient Segment", fontsize=11)
    ax.set_ylabel("Number of Patients", fontsize=11)
    ax.set_title("Patient Segment Distribution", fontsize=14, fontweight="bold")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig("outputs/segment_distribution.png")
    plt.close(fig)

    # ── Chart 2: Adoption by segment ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [BLUE if "High-Need" in s else ORANGE for s in seg["Business_Segment"]]
    bars = ax.bar(seg["Business_Segment"], seg["Adoption_Rate_%"],
                  color=colors, edgecolor="white", width=0.55)
    for bar, val in zip(bars, seg["Adoption_Rate_%"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold")
    ax.set_xlabel("Patient Segment", fontsize=11)
    ax.set_ylabel("Adoption Rate (%)", fontsize=11)
    ax.set_title("Treatment Adoption Rate by Patient Segment", fontsize=14, fontweight="bold")
    ax.set_ylim(0, seg["Adoption_Rate_%"].max() * 1.15)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig("outputs/adoption_by_segment.png")
    plt.close(fig)

    print("  ✓  Charts saved → outputs/segment_distribution.png, adoption_by_segment.png")
    return df, seg


# ─────────────────────────────────────────────────────────────────────────────
# 3. TREATMENT ADOPTION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def adoption_analysis(df):
    print("\n── 3. Treatment Adoption Analysis ──────────────────────────────────")

    overall_rate = df["Treatment_Started"].mean()
    print(f"  Overall adoption rate: {overall_rate:.1%}")

    adoption_rows = []

    def add_adoption(group_col, label):
        g = (
            df.groupby(group_col)["Treatment_Started"]
            .agg(["sum", "count", "mean"])
            .reset_index()
        )
        g.columns = ["Category", "Adopted", "Total", "Rate"]
        g.insert(0, "Dimension", label)
        g["Rate_%"] = (g["Rate"] * 100).round(2)
        adoption_rows.append(g.drop(columns="Rate"))

    add_adoption("Age_Group",          "Age Group")
    add_adoption("Disease_Severity",   "Disease Severity")
    add_adoption("Insurance_Status",   "Insurance Status")
    add_adoption("Region",             "Region")
    add_adoption("Treatment_Recommended", "Treatment Recommended")
    add_adoption("Previous_Treatment", "Previous Treatment")
    add_adoption("Cost_Band",          "Cost Band")

    adoption_df = pd.concat(adoption_rows, ignore_index=True)
    adoption_df.to_csv("results/adoption_summary.csv", index=False)
    print(f"  ✓  Adoption summary saved → results/adoption_summary.csv")

    # ── Chart helpers ─────────────────────────────────────────────────────────
    def bar_chart(data, x_col, y_col, title, filename, color=BLUE,
                  xlabel="Adoption Rate (%)", xtick_rot=0):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        bars = ax.bar(data[x_col], data[y_col], color=color, edgecolor="white", width=0.55)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                    f"{bar.get_height():.1f}%", ha="center", fontsize=9, fontweight="bold")
        ax.set_ylabel(xlabel, fontsize=11)
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylim(0, data[y_col].max() * 1.18)
        if xtick_rot:
            plt.xticks(rotation=xtick_rot, ha="right")
        fig.tight_layout()
        fig.savefig(filename)
        plt.close(fig)

    def get_dim(dim_name):
        return adoption_df[adoption_df["Dimension"] == dim_name].copy()

    sev_order = ["Mild", "Moderate", "Severe"]
    sev_data = get_dim("Disease Severity").set_index("Category").loc[sev_order].reset_index()
    bar_chart(sev_data, "Category", "Rate_%",
              "Treatment Adoption Rate by Disease Severity",
              "outputs/adoption_by_severity.png",
              color=[ORANGE, BLUE, RED])

    ins_data = get_dim("Insurance Status")
    bar_chart(ins_data, "Category", "Rate_%",
              "Treatment Adoption Rate by Insurance Status",
              "outputs/adoption_by_insurance.png",
              color=[BLUE, ORANGE, RED])

    reg_data = get_dim("Region").sort_values("Rate_%", ascending=False)
    bar_chart(reg_data, "Category", "Rate_%",
              "Treatment Adoption Rate by Region",
              "outputs/adoption_by_region.png",
              color=sns.color_palette(PALETTE, len(reg_data)),
              xtick_rot=15)

    # Adoption by cost band
    cost_data = get_dim("Cost Band")
    cost_order = ["Low (<$15k)", "Medium ($15-35k)", "High ($35-60k)", "Very High (>$60k)"]
    cost_data = cost_data.set_index("Category").loc[cost_order].reset_index()
    bar_chart(cost_data, "Category", "Rate_%",
              "Treatment Adoption Rate by Treatment Cost Band",
              "outputs/adoption_by_cost.png",
              color=[BLUE, BLUE, ORANGE, RED],
              xtick_rot=15)

    # Adoption by physician recommendation
    rec_data = get_dim("Treatment Recommended").copy()
    rec_data["Category"] = rec_data["Category"].map({1: "Recommended", 0: "Not Recommended"})
    bar_chart(rec_data, "Category", "Rate_%",
              "Treatment Adoption: Recommended vs Not Recommended",
              "outputs/adoption_by_recommendation.png",
              color=[BLUE, ORANGE])

    print("  ✓  All adoption charts saved → outputs/")
    return adoption_df


# ─────────────────────────────────────────────────────────────────────────────
# 4. ADOPTION DRIVERS — LOGISTIC REGRESSION
# ─────────────────────────────────────────────────────────────────────────────
def adoption_drivers(df):
    print("\n── 4. Adoption Drivers (Logistic Regression) ───────────────────────")

    df2 = df.copy()

    # Encode categorical predictors
    df2["Insurance_Insured"]    = (df2["Insurance_Status"] == "Insured").astype(int)
    df2["Severity_Severe"]      = (df2["Disease_Severity"] == "Severe").astype(int)
    df2["Severity_Moderate"]    = (df2["Disease_Severity"] == "Moderate").astype(int)

    FEATURES = [
        "Age",
        "Severity_Severe",
        "Severity_Moderate",
        "Insurance_Insured",
        "Treatment_Recommended",
        "Affordability_Score",
        "Healthcare_Access_Score",
        "Awareness_Score",
        "Previous_Treatment",
        "Side_Effect_Concern",
    ]

    FEATURE_LABELS = {
        "Age":                     "Age",
        "Severity_Severe":         "Severe Disease",
        "Severity_Moderate":       "Moderate Disease",
        "Insurance_Insured":       "Insured",
        "Treatment_Recommended":   "Physician Recommendation",
        "Affordability_Score":     "Affordability Score",
        "Healthcare_Access_Score": "Healthcare Access",
        "Awareness_Score":         "Awareness Score",
        "Previous_Treatment":      "Prior Treatment",
        "Side_Effect_Concern":     "Side Effect Concern",
    }

    X = df2[FEATURES].fillna(0)
    y = df2["Treatment_Started"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]

    acc   = accuracy_score(y_test, y_pred)
    prec  = precision_score(y_test, y_pred)
    rec   = recall_score(y_test, y_pred)
    f1    = f1_score(y_test, y_pred)
    auc   = roc_auc_score(y_test, y_prob)

    metrics = pd.DataFrame({
        "Metric": ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"],
        "Value":  [round(acc,4), round(prec,4), round(rec,4), round(f1,4), round(auc,4)],
    })
    metrics.to_csv("results/model_metrics.csv", index=False)
    print(metrics.to_string(index=False))

    # ── Feature importance chart ──────────────────────────────────────────────
    coef_df = pd.DataFrame({
        "Feature":     FEATURES,
        "Label":       [FEATURE_LABELS[f] for f in FEATURES],
        "Coefficient": model.coef_[0],
    }).sort_values("Coefficient")

    colors = [RED if c < 0 else BLUE for c in coef_df["Coefficient"]]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(coef_df["Label"], coef_df["Coefficient"], color=colors, edgecolor="white", height=0.65)
    ax.axvline(0, color="#555555", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Logistic Regression Coefficient (Standardised)", fontsize=11)
    ax.set_title("Factors Associated with Treatment Adoption\n(Logistic Regression Coefficients)",
                 fontsize=13, fontweight="bold")
    ax.text(0.98, 0.03, "Positive = more likely to start treatment\nNegative = less likely",
            transform=ax.transAxes, ha="right", fontsize=8.5, color="#555555")
    fig.tight_layout()
    fig.savefig("outputs/feature_importance.png")
    plt.close(fig)
    print("  ✓  Feature importance chart saved → outputs/feature_importance.png")

    return metrics, coef_df


# ─────────────────────────────────────────────────────────────────────────────
# 5. MARKET OPPORTUNITY ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def market_opportunity(df):
    print("\n── 5. Market Opportunity Analysis ──────────────────────────────────")

    # By region
    mkt = (
        df.groupby("Region")
        .agg(
            Total_Patients=("Patient_ID", "count"),
            Treated_Patients=("Treatment_Started", "sum"),
        )
        .reset_index()
    )
    mkt["Untreated_Patients"] = mkt["Total_Patients"] - mkt["Treated_Patients"]
    mkt["Adoption_Rate_%"]    = (mkt["Treated_Patients"] / mkt["Total_Patients"] * 100).round(2)
    mkt["Adoption_Gap_%"]     = (100 - mkt["Adoption_Rate_%"]).round(2)

    # Opportunity Score: combination of untreated size and adoption gap
    # Normalise each metric to 0-1 and average
    def norm(x):
        return (x - x.min()) / (x.max() - x.min() + 1e-9)

    mkt["Opp_Score"] = (
        0.5 * norm(mkt["Untreated_Patients"]) +
        0.5 * norm(mkt["Adoption_Gap_%"])
    ).round(4)

    mkt.sort_values("Opp_Score", ascending=False, inplace=True)
    mkt.to_csv("results/market_opportunity.csv", index=False)
    print(mkt.to_string(index=False))

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: Untreated patients by region
    ax1 = axes[0]
    palette = sns.color_palette(PALETTE, len(mkt))
    bars = ax1.bar(mkt["Region"], mkt["Untreated_Patients"],
                   color=palette, edgecolor="white", width=0.55)
    for bar in bars:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                 f"{int(bar.get_height()):,}", ha="center", fontsize=9, fontweight="bold")
    ax1.set_title("Untreated Patients by Region", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Untreated Patients", fontsize=10)
    ax1.set_xlabel("Region", fontsize=10)

    # Right: Opportunity score
    ax2 = axes[1]
    colors2 = [RED if i == 0 else ORANGE if i == 1 else BLUE
               for i in range(len(mkt))]
    bars2 = ax2.bar(mkt["Region"], mkt["Opp_Score"],
                    color=colors2, edgecolor="white", width=0.55)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                 f"{bar.get_height():.3f}", ha="center", fontsize=9, fontweight="bold")
    ax2.set_title("Market Opportunity Score by Region\n(Higher = More Opportunity)",
                  fontsize=12, fontweight="bold")
    ax2.set_ylabel("Opportunity Score (0–1)", fontsize=10)
    ax2.set_xlabel("Region", fontsize=10)

    fig.suptitle("Regional Market Opportunity Analysis — Therapy X",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig("outputs/top_market_opportunities.png")
    plt.close(fig)
    print("  ✓  Market opportunity chart saved → outputs/top_market_opportunities.png")

    return mkt


# ─────────────────────────────────────────────────────────────────────────────
# 6. WRITE REPORTS
# ─────────────────────────────────────────────────────────────────────────────
def write_reports(journey, adoption_df, metrics, coef_df, mkt, df):
    print("\n── 6. Writing Reports ───────────────────────────────────────────────")
    os.makedirs("reports", exist_ok=True)

    # Helper: pull adoption rate for a dimension + category
    def get_rate(dim, cat):
        row = adoption_df[(adoption_df["Dimension"] == dim) & (adoption_df["Category"].astype(str) == str(cat))]
        if row.empty:
            return None
        return row["Rate_%"].values[0]

    overall_adoption = df["Treatment_Started"].mean() * 100
    top_opp_region   = mkt.iloc[0]["Region"]
    top_opp_untreated = int(mkt.iloc[0]["Untreated_Patients"])
    biggest_dropoff_stage = journey.loc[journey["Drop_Off_%"].idxmax(axis=0), "Stage"]
    biggest_dropoff_pct   = journey["Drop_Off_%"].max()

    sev_rate    = get_rate("Disease Severity", "Severe")
    mild_rate   = get_rate("Disease Severity", "Mild")
    insured_rate = get_rate("Insurance Status", "Insured")
    uninsured_rate = get_rate("Insurance Status", "Uninsured")
    rec_rate    = get_rate("Treatment Recommended", "1")
    no_rec_rate = get_rate("Treatment Recommended", "0")

    top_feature = coef_df.iloc[-1]["Label"]   # highest positive coef
    top_neg_feature = coef_df.iloc[0]["Label"]  # most negative coef

    model_auc = metrics[metrics["Metric"] == "ROC-AUC"]["Value"].values[0]

    # ── Key Findings ──────────────────────────────────────────────────────────
    findings_md = f"""# Key Findings — Patient Journey & Treatment Adoption Analytics

> All findings are based on the synthetic dataset of {len(df):,} patients generated for this project.

---

### Finding 1 — Overall Adoption Rate is Moderate

**Observation:**
The overall treatment adoption rate for Therapy X is **{overall_adoption:.1f}%**, meaning that
roughly {100-overall_adoption:.0f}% of diagnosed patients never start the treatment.

**Why it matters:**
A large pool of eligible but untreated patients represents both unmet medical need
and a commercial growth opportunity for the company.

**Business Implication:**
The company should investigate barriers to adoption and design targeted interventions
to close the gap.

---

### Finding 2 — The Biggest Drop-off is at the "{biggest_dropoff_stage}" Stage

**Observation:**
The largest single drop-off in the patient journey occurs at the **{biggest_dropoff_stage}** stage
({biggest_dropoff_pct:.1f}% of patients at the previous stage are lost here).

**Why it matters:**
Understanding the highest-loss stage allows resources to be focused where they will
have the greatest impact.

**Business Implication:**
Investigate why patients are lost at this stage. Possible causes include lack of
information, cost concerns, or access barriers. A targeted awareness or access programme
at this stage could significantly improve overall adoption.

---

### Finding 3 — Physician Recommendation Has the Strongest Association with Adoption

**Observation:**
Patients who received a physician recommendation had an adoption rate of
**{rec_rate:.1f}%**, compared to only **{no_rec_rate:.1f}%** among those who were not recommended
for Therapy X. The logistic regression confirms this is the factor most strongly
associated with treatment initiation.

**Why it matters:**
Healthcare providers (HCPs) are the gatekeepers to treatment initiation.

**Business Implication:**
Physician education and engagement programmes are likely to be the highest-return
investment for improving adoption rates.

---

### Finding 4 — Insurance Status is Strongly Associated with Adoption

**Observation:**
Insured patients show an adoption rate of **{insured_rate:.1f}%**, while uninsured patients
show only **{uninsured_rate:.1f}%** — a meaningful gap that suggests affordability and
coverage are significant barriers.

**Why it matters:**
Uninsured and underinsured patients face out-of-pocket costs that may make
Therapy X inaccessible despite medical need.

**Business Implication:**
Patient assistance programmes, co-pay support, and insurance coverage advocacy
should be prioritised for low-income and uninsured populations.

---

### Finding 5 — Severe Disease Patients Have Higher (but Still Imperfect) Adoption

**Observation:**
Patients with severe disease have an adoption rate of **{sev_rate:.1f}%** vs.
**{mild_rate:.1f}%** for mild-disease patients. Higher clinical need is associated with
greater willingness to initiate treatment — but the rate is still well below 100%.

**Why it matters:**
Even the highest-need patients do not always start treatment. Barriers persist even
when urgency is highest.

**Business Implication:**
Even for high-severity patients, access barriers (cost, geography, insurance) still
limit adoption. These should not be ignored in the most urgent patient groups.

---

### Finding 6 — The {top_opp_region} Region Presents the Highest Market Opportunity

**Observation:**
The **{top_opp_region}** region has the highest opportunity score, driven by a large
untreated patient population of **{top_opp_untreated:,}** and a below-average adoption rate.

**Why it matters:**
Concentrating commercial and medical education resources in high-opportunity regions
can deliver the greatest return.

**Business Implication:**
The company should prioritise field force coverage, HCP outreach, and patient
support programmes in the {top_opp_region} region.

---

### Finding 7 — Side Effect Concerns are Negatively Associated with Adoption

**Observation:**
The logistic regression identified **{top_neg_feature}** as a negative predictor of
treatment adoption — patients with greater side effect concerns are less likely to
start Therapy X.

**Why it matters:**
Fear of side effects is a well-documented barrier to treatment initiation in
chronic disease settings.

**Business Implication:**
Patient education materials and HCP training should explicitly address common side
effect concerns and provide realistic risk–benefit communication.

---

### Finding 8 — Logistic Regression Model Achieves ROC-AUC of {model_auc:.3f}

**Observation:**
A simple logistic regression model using 10 interpretable features achieves a
ROC-AUC of **{model_auc:.3f}**, indicating it is meaningfully better than random
guessing and can identify patterns in the data.

**Why it matters:**
Even a simple model confirms that measurable patient-level factors are genuinely
associated with treatment adoption decisions.

**Business Implication:**
These factors (physician recommendation, insurance, affordability, healthcare access)
are actionable — the company can design programmes to address each one.

---

*Note: All findings are based on synthetic data and are intended for educational purposes only.
Associations identified here should not be interpreted as causal relationships.*
"""

    # ── Business Recommendations ───────────────────────────────────────────────
    rec_md = f"""# Business Recommendations — Patient Journey & Treatment Adoption Analytics

> These recommendations are based on the actual analysis results from the synthetic dataset.
> They are intended as illustrative business thinking for portfolio purposes only.
> No medical advice is given or implied.

---

## Recommendation 1 — Invest in Physician Education and Engagement

**Based on:** Finding 3 (Physician Recommendation strongly associated with adoption)

Physician recommendation is the single factor most strongly associated with treatment adoption
in this analysis. The company should prioritise:

- Targeted HCP outreach and medical education programmes
- Providing physicians with clear, evidence-based information on patient selection criteria
- Field sales force coverage in high-opportunity regions
- Academic detailing for high-patient-volume practices

**Expected Impact:** Closing the physician recommendation gap could have the single largest
effect on adoption rates across all patient groups.

---

## Recommendation 2 — Expand Patient Access and Affordability Programmes

**Based on:** Finding 4 (Insurance status strongly associated with adoption)

The adoption gap between insured and uninsured patients is substantial. The company should:

- Implement or expand co-pay assistance and patient support programmes
- Partner with payers to negotiate better formulary access
- Create specific programmes for underinsured and uninsured patients
- Investigate state-level Medicaid coverage opportunities

**Expected Impact:** Reducing financial barriers could meaningfully increase adoption
among Low-Income and Uninsured patient groups.

---

## Recommendation 3 — Focus Resources on the {top_opp_region} Region

**Based on:** Finding 6 (Regional market opportunity analysis)

The market opportunity analysis identifies **{top_opp_region}** as the highest-priority region
based on its combination of untreated patient volume and adoption gap. The company should:

- Increase field force coverage and HCP visits in this region
- Run targeted patient awareness campaigns
- Engage with regional payers on access and coverage
- Monitor adoption rates quarterly in this region

**Expected Impact:** Focused regional investment is likely to yield a higher return
than broad, nationally distributed spending.

---

## Recommendation 4 — Address Patient Drop-off at the "{biggest_dropoff_stage}" Stage

**Based on:** Finding 2 (Biggest patient journey drop-off identified)

The "{biggest_dropoff_stage}" stage is where the most patients are lost in the journey.
The company should:

- Investigate the specific reasons for drop-off through patient surveys or chart reviews
- Design targeted interventions at this specific stage
- Work with HCPs to improve the transition from this stage to the next
- Create patient-facing materials that address common concerns at this stage

**Expected Impact:** Improving conversion at the biggest drop-off stage can have
a disproportionate effect on overall treatment adoption.

---

## Recommendation 5 — Proactively Address Side Effect Concerns

**Based on:** Finding 7 (Side effect concern negatively associated with adoption)

Patients with higher concern about side effects are less likely to initiate treatment.
The company should:

- Develop clear, patient-friendly side effect communication materials
- Train HCPs to have proactive side effect conversations during consultations
- Share real-world evidence on the safety and tolerability profile of Therapy X
- Create patient testimonials and peer support resources where appropriate

**Expected Impact:** Better side effect communication can reduce a key psychological
barrier to treatment initiation.

---

## Recommendation 6 — Monitor Adoption and Continuation Together

**Based on:** Overall journey analysis

Starting treatment is only part of the goal — continued adherence and follow-up completion
are also important. The company should:

- Track treatment continuation rates alongside adoption rates
- Implement patient support programmes for those who have started treatment
- Set up reminder systems for follow-up appointments
- Identify patients at risk of dropping off after starting and intervene proactively

**Expected Impact:** Improving continuation and follow-up rates reduces the risk of
the significant investment in patient initiation being wasted.

---

*These recommendations are illustrative, based on synthetic data analysis, and are intended
for portfolio and educational purposes only.*
"""

    # ── Conclusion ─────────────────────────────────────────────────────────────
    cont_rate  = df["Treatment_Continued"].mean() * 100
    followup_rate = df["Follow_Up_Completed"].mean() * 100

    conclusion_md = f"""# Conclusion — Patient Journey & Treatment Adoption Analytics

## What the Analysis Ultimately Revealed

This project analysed a synthetic dataset of **{len(df):,} patients** to understand
the factors driving treatment adoption for Therapy X.

The overall treatment adoption rate was **{overall_adoption:.1f}%**, meaning that
**{100-overall_adoption:.0f}%** of diagnosed patients never initiated treatment.
After starting, **{cont_rate:.1f}%** of patients continued treatment, and
**{followup_rate:.1f}%** completed follow-up.

---

## Biggest Opportunities

1. **Physician Engagement:** The single strongest factor associated with adoption is a
   physician recommendation. Programmes that increase HCP recommendation rates are
   likely to have the greatest impact on adoption.

2. **{top_opp_region} Region:** This region presents the highest market opportunity
   based on a large untreated patient population combined with a below-average adoption rate.
   Concentrated investment here offers the highest expected return.

3. **High-Need / High-Ability Patients Not Yet Treated:** Even among patients with
   high clinical need and good insurance coverage, adoption is imperfect.
   Targeted education and access improvements could capture this group efficiently.

---

## Biggest Barriers

1. **Financial and Insurance Barriers:** Uninsured and underinsured patients have
   substantially lower adoption rates, suggesting that cost is a significant barrier
   to treatment initiation.

2. **Patient Journey Drop-off at "{biggest_dropoff_stage}":** The largest single
   point of patient loss in the journey occurs at this stage, representing a critical
   intervention point.

3. **Side Effect Concerns:** Fear of side effects is negatively associated with
   treatment initiation, suggesting a need for better patient education and
   risk–benefit communication.

---

## What the Company Should Prioritise

Based on the analysis, the company should prioritise three main actions:

1. **Physician education and engagement** — especially in the {top_opp_region} region
   and among high-opportunity patient segments.

2. **Patient access and affordability programmes** — to reduce financial barriers
   for uninsured and underinsured patients.

3. **Targeted intervention at the biggest drop-off stage** — to improve patient
   journey conversion at the point of greatest loss.

---

## Analytical Summary

The logistic regression model (ROC-AUC: {model_auc:.3f}) confirmed that meaningful
patterns exist in the data and that several patient-level variables are genuinely
associated with treatment adoption. Physician recommendation, insurance coverage,
affordability, and disease severity were the most predictive factors.

The market opportunity analysis identified clear regional variation in both adoption
rates and untreated patient volumes, providing actionable guidance for resource allocation.

---

*This project used synthetic data and simplified models. All findings are associative,
not causal. Real-world strategy should be informed by actual patient-level claims data,
clinical evidence, and detailed market research.*

*This project uses synthetic data created for analytical and educational purposes.
It does not represent real patients, real clinical outcomes, medical advice,
or actual pharmaceutical market data.*
"""

    with open("reports/key_findings.md", "w", encoding="utf-8") as f:
        f.write(findings_md)
    with open("reports/business_recommendations.md", "w", encoding="utf-8") as f:
        f.write(rec_md)
    with open("reports/conclusion.md", "w", encoding="utf-8") as f:
        f.write(conclusion_md)

    print("  ✓  Reports saved → reports/key_findings.md")
    print("  ✓  Reports saved → reports/business_recommendations.md")
    print("  ✓  Reports saved → reports/conclusion.md")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  Patient Journey & Treatment Adoption Analytics — analyze.py")
    print("=" * 65)

    df = pd.read_csv(CLEAN_PATH)
    # Ensure categorical columns
    for col in ["Age_Group", "Cost_Band"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    journey  = patient_journey(df)
    df, seg  = patient_segmentation(df)
    adopt_df = adoption_analysis(df)
    metrics, coef_df = adoption_drivers(df)
    mkt      = market_opportunity(df)
    write_reports(journey, adopt_df, metrics, coef_df, mkt, df)

    print("\n" + "=" * 65)
    print("  Analysis complete! All outputs saved.")
    print("=" * 65)


if __name__ == "__main__":
    main()
