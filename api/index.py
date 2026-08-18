"""
api/index.py
------------
FastAPI backend for the Patient Journey & Treatment Adoption Analytics project.

Reads from existing result CSV files produced by the Python analytics pipeline.
All values returned are real — derived from actual data, never hard-coded.

Run locally:
    uvicorn api.index:app --reload --port 8000

DISCLAIMER: Synthetic data only. Not real patient data.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
DATA_CLEAN    = ROOT / "data"    / "patient_data_clean.csv"
JOURNEY_CSV   = ROOT / "results" / "patient_journey_summary.csv"
ADOPTION_CSV  = ROOT / "results" / "adoption_summary.csv"
SEGMENT_CSV   = ROOT / "results" / "segment_summary.csv"
MARKET_CSV    = ROOT / "results" / "market_opportunity.csv"
METRICS_CSV   = ROOT / "results" / "model_metrics.csv"
FRONTEND_DIST = ROOT / "frontend" / "dist"

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Patient Journey & Treatment Adoption Analytics API",
    description="REST API exposing analytics results from the Patient Journey project.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Data file not found: {path.name}. Run 'python src/run_project.py' first.",
        )
    return pd.read_csv(path)


def load_patient_data(
    region: Optional[str] = None,
    gender: Optional[str] = None,
    age_group: Optional[str] = None,
    insurance: Optional[str] = None,
    severity: Optional[str] = None,
) -> pd.DataFrame:
    df = load_csv(DATA_CLEAN)
    if region    and region    != "All": df = df[df["Region"]           == region]
    if gender    and gender    != "All": df = df[df["Gender"]           == gender]
    if age_group and age_group != "All": df = df[df["Age_Group"]        == age_group]
    if insurance and insurance != "All": df = df[df["Insurance_Status"] == insurance]
    if severity  and severity  != "All": df = df[df["Disease_Severity"] == severity]
    return df


def safe_round(val, decimals=2):
    if pd.isna(val):
        return None
    return round(float(val), decimals)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/overview")
def overview(
    region:    Optional[str] = Query(None),
    gender:    Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    insurance: Optional[str] = Query(None),
    severity:  Optional[str] = Query(None),
):
    df = load_patient_data(region, gender, age_group, insurance, severity)
    if df.empty:
        raise HTTPException(status_code=404, detail="No patients match selected filters.")

    total         = int(len(df))
    adopted       = int(df["Treatment_Started"].sum())
    continued     = int(df["Treatment_Continued"].sum())
    untreated     = total - adopted
    adoption_rate = safe_round(adopted / total * 100)
    cont_rate     = safe_round(continued / total * 100)
    followup_rate = safe_round(df["Follow_Up_Completed"].sum() / total * 100)

    # Top opportunity region from pre-computed results (or live if filtered)
    mkt = load_csv(MARKET_CSV)
    top_region = mkt.iloc[0]["Region"]
    top_untreated = int(mkt.iloc[0]["Untreated_Patients"])

    return {
        "total_patients":       total,
        "adopted_patients":     adopted,
        "untreated_patients":   untreated,
        "adoption_rate":        adoption_rate,
        "continuation_rate":    cont_rate,
        "followup_rate":        followup_rate,
        "top_opportunity_region": top_region,
        "top_opportunity_untreated": top_untreated,
    }


@app.get("/api/patient-journey")
def patient_journey(
    region:    Optional[str] = Query(None),
    gender:    Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    insurance: Optional[str] = Query(None),
    severity:  Optional[str] = Query(None),
):
    any_filter = any([region, gender, age_group, insurance, severity])

    if any_filter:
        df = load_patient_data(region, gender, age_group, insurance, severity)
        if df.empty:
            raise HTTPException(status_code=404, detail="No patients match filters.")

        stages = [
            ("Diagnosed",             len(df)),
            ("Doctor Consultation",   int(df["Doctor_Consultation"].sum())),
            ("Treatment Recommended", int(df["Treatment_Recommended"].sum())),
            ("Treatment Started",     int(df["Treatment_Started"].sum())),
            ("Treatment Continued",   int(df["Treatment_Continued"].sum())),
            ("Follow-up Completed",   int(df["Follow_Up_Completed"].sum())),
        ]
        diagnosed = stages[0][1]
        result = []
        for i, (stage, count) in enumerate(stages):
            prev = stages[i-1][1] if i > 0 else count
            drop = safe_round((prev - count) / prev * 100) if i > 0 and prev > 0 else 0.0
            conv = safe_round(count / diagnosed * 100)
            result.append({
                "stage": stage,
                "patients": count,
                "conversion_pct": conv,
                "dropoff_pct": drop,
            })
    else:
        jdf = load_csv(JOURNEY_CSV)
        result = []
        for _, row in jdf.iterrows():
            result.append({
                "stage":          row["Stage"],
                "patients":       int(row["Patients"]),
                "conversion_pct": safe_round(row["Conversion_vs_Diagnosed_%"]),
                "dropoff_pct":    safe_round(row["Drop_Off_%"]),
            })

    # Find biggest drop-off (skip first stage)
    max_drop = max(result[1:], key=lambda x: x["dropoff_pct"])
    return {"stages": result, "biggest_dropoff": max_drop}


@app.get("/api/adoption")
def adoption(
    region:    Optional[str] = Query(None),
    gender:    Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    insurance: Optional[str] = Query(None),
    severity:  Optional[str] = Query(None),
):
    any_filter = any([region, gender, age_group, insurance, severity])

    if any_filter:
        df = load_patient_data(region, gender, age_group, insurance, severity)
        if df.empty:
            raise HTTPException(status_code=404, detail="No patients match filters.")

        def compute(col):
            g = df.groupby(col)["Treatment_Started"].agg(["sum","count","mean"]).reset_index()
            g.columns = [col, "adopted", "total", "rate"]
            return [{"category": str(r[col]), "adopted": int(r["adopted"]),
                     "total": int(r["total"]), "rate_pct": safe_round(r["rate"]*100)}
                    for _, r in g.iterrows()]

        return {
            "by_insurance": compute("Insurance_Status"),
            "by_severity":  compute("Disease_Severity"),
            "by_age_group": compute("Age_Group"),
            "by_region":    compute("Region"),
            "by_recommendation": [
                {"category": "Recommended" if r["category"]=="1" else "Not Recommended",
                 **{k:v for k,v in r.items() if k!="category"}}
                for r in compute("Treatment_Recommended")
            ],
            "by_cost_band": compute("Cost_Band"),
            "overall_rate": safe_round(df["Treatment_Started"].mean()*100),
        }
    else:
        adf = load_csv(ADOPTION_CSV)

        def get_dim(dim):
            rows = adf[adf["Dimension"]==dim]
            return [{"category": str(r["Category"]), "adopted": int(r["Adopted"]),
                     "total": int(r["Total"]), "rate_pct": safe_round(r["Rate_%"])}
                    for _, r in rows.iterrows()]

        rec = get_dim("Treatment Recommended")
        rec_mapped = [{"category": "Recommended" if r["category"]=="1" else "Not Recommended",
                       **{k:v for k,v in r.items() if k!="category"}}
                      for r in rec]

        df_full = load_csv(DATA_CLEAN)
        return {
            "by_insurance":      get_dim("Insurance Status"),
            "by_severity":       get_dim("Disease Severity"),
            "by_age_group":      get_dim("Age Group"),
            "by_region":         get_dim("Region"),
            "by_recommendation": rec_mapped,
            "by_cost_band":      get_dim("Cost Band"),
            "overall_rate":      safe_round(df_full["Treatment_Started"].mean()*100),
        }


@app.get("/api/segments")
def segments(
    region:    Optional[str] = Query(None),
    gender:    Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    insurance: Optional[str] = Query(None),
    severity:  Optional[str] = Query(None),
):
    any_filter = any([region, gender, age_group, insurance, severity])

    if any_filter:
        df = load_patient_data(region, gender, age_group, insurance, severity)
        if df.empty:
            raise HTTPException(status_code=404, detail="No patients match filters.")

        df = df.copy()
        df["Need_Level"] = df["Disease_Severity"].map(
            {"Severe":"High-Need","Moderate":"High-Need","Mild":"Low-Need"})
        df["Ability_Level"] = np.where(
            (df["Insurance_Status"]=="Insured") & (df["Affordability_Score"]>=5), "High-Ability",
            np.where(
                (df["Insurance_Status"]=="Uninsured") | (df["Affordability_Score"]<3),
                "Low-Ability","Medium-Ability"))
        df["Business_Segment"] = df["Need_Level"] + " / " + df["Ability_Level"]

        seg = df.groupby("Business_Segment").agg(
            total=("Patient_ID","count"),
            adopted=("Treatment_Started","sum"),
            continued=("Treatment_Continued","sum"),
        ).reset_index()
        seg["adoption_rate"]      = (seg["adopted"]/seg["total"]*100).round(2)
        seg["continuation_rate"]  = (seg["continued"]/seg["total"]*100).round(2)
        seg["untreated"]          = seg["total"] - seg["adopted"]

        return {"segments": [
            {"segment": r["Business_Segment"], "total": int(r["total"]),
             "adopted": int(r["adopted"]), "untreated": int(r["untreated"]),
             "adoption_rate": safe_round(r["adoption_rate"]),
             "continuation_rate": safe_round(r["continuation_rate"])}
            for _, r in seg.sort_values("total", ascending=False).iterrows()
        ]}
    else:
        sdf = load_csv(SEGMENT_CSV)
        df_full = load_csv(DATA_CLEAN)
        df_full = df_full.copy()
        df_full["Need_Level"] = df_full["Disease_Severity"].map(
            {"Severe":"High-Need","Moderate":"High-Need","Mild":"Low-Need"})
        df_full["Ability_Level"] = np.where(
            (df_full["Insurance_Status"]=="Insured") & (df_full["Affordability_Score"]>=5),"High-Ability",
            np.where((df_full["Insurance_Status"]=="Uninsured")|(df_full["Affordability_Score"]<3),
                     "Low-Ability","Medium-Ability"))
        df_full["Business_Segment"] = df_full["Need_Level"]+" / "+df_full["Ability_Level"]
        cont = df_full.groupby("Business_Segment")["Treatment_Continued"].mean().reset_index()
        cont.columns = ["Business_Segment","cont_rate"]

        results = []
        for _, r in sdf.iterrows():
            seg_name = r["Business_Segment"]
            cr_row = cont[cont["Business_Segment"]==seg_name]
            cr = safe_round(cr_row["cont_rate"].values[0]*100) if not cr_row.empty else None
            results.append({
                "segment":           seg_name,
                "total":             int(r["Total_Patients"]),
                "adopted":           int(r["Adopted"]),
                "untreated":         int(r["Untreated_Patients"]),
                "adoption_rate":     safe_round(r["Adoption_Rate_%"]),
                "continuation_rate": cr,
            })
        return {"segments": results}


@app.get("/api/market-opportunity")
def market_opportunity():
    mdf = load_csv(MARKET_CSV)
    return {
        "regions": [
            {
                "region":            r["Region"],
                "total_patients":    int(r["Total_Patients"]),
                "treated_patients":  int(r["Treated_Patients"]),
                "untreated_patients":int(r["Untreated_Patients"]),
                "adoption_rate":     safe_round(r["Adoption_Rate_%"]),
                "adoption_gap":      safe_round(r["Adoption_Gap_%"]),
                "opportunity_score": safe_round(r["Opp_Score"], 4),
            }
            for _, r in mdf.iterrows()
        ],
        "top_region": mdf.iloc[0]["Region"],
    }


@app.get("/api/model-insights")
def model_insights():
    mdf = load_csv(METRICS_CSV)
    metrics = {r["Metric"]: safe_round(r["Value"], 4) for _, r in mdf.iterrows()}

    # Re-run logistic regression to get coefficients (fast — already fitted pattern)
    try:
        df = load_csv(DATA_CLEAN)
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split

        df2 = df.copy()
        df2["Insurance_Insured"]  = (df2["Insurance_Status"]=="Insured").astype(int)
        df2["Severity_Severe"]    = (df2["Disease_Severity"]=="Severe").astype(int)
        df2["Severity_Moderate"]  = (df2["Disease_Severity"]=="Moderate").astype(int)

        FEATURES = ["Age","Severity_Severe","Severity_Moderate","Insurance_Insured",
                    "Treatment_Recommended","Affordability_Score",
                    "Healthcare_Access_Score","Awareness_Score",
                    "Previous_Treatment","Side_Effect_Concern"]
        LABELS = {
            "Age":"Age","Severity_Severe":"Severe Disease",
            "Severity_Moderate":"Moderate Disease","Insurance_Insured":"Insured",
            "Treatment_Recommended":"Physician Recommendation",
            "Affordability_Score":"Affordability Score",
            "Healthcare_Access_Score":"Healthcare Access",
            "Awareness_Score":"Awareness Score",
            "Previous_Treatment":"Prior Treatment",
            "Side_Effect_Concern":"Side Effect Concern",
        }
        X = df2[FEATURES].fillna(0)
        y = df2["Treatment_Started"]
        X_tr, _, y_tr, _ = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        model = LogisticRegression(max_iter=500, random_state=42)
        model.fit(X_tr_s, y_tr)

        coefficients = [
            {"feature": LABELS[f], "coefficient": safe_round(c, 4)}
            for f, c in zip(FEATURES, model.coef_[0])
        ]
        coefficients.sort(key=lambda x: x["coefficient"])
    except Exception as e:
        coefficients = []

    return {
        "metrics": metrics,
        "coefficients": coefficients,
        "model_type": "Logistic Regression",
        "note": "Coefficients indicate statistical association with treatment adoption. "
                "Positive = more likely to start treatment. "
                "These are associations, not causal relationships.",
    }


@app.get("/api/filters/options")
def filter_options():
    """Return valid options for all filter dropdowns."""
    df = load_csv(DATA_CLEAN)
    return {
        "regions":    ["All"] + sorted(df["Region"].dropna().unique().tolist()),
        "genders":    ["All"] + sorted(df["Gender"].dropna().unique().tolist()),
        "age_groups": ["All"] + sorted(df["Age_Group"].dropna().unique().tolist()),
        "insurances": ["All"] + sorted(df["Insurance_Status"].dropna().unique().tolist()),
        "severities": ["All"] + sorted(df["Disease_Severity"].dropna().unique().tolist()),
    }


# ── Static Frontend (SPA) ─────────────────────────────────────────────────────
# Serve the React build for all non-API routes (required for Vercel FastAPI preset)
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes."""
        index = FRONTEND_DIST / "index.html"
        return FileResponse(str(index))

