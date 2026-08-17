# Power BI Dashboard Specification
# Patient Journey & Treatment Adoption Analytics

> Import `data/patient_data_clean.csv` into Power BI Desktop as a flat-file data source.
> No database or server is required. All DAX measures are defined in `powerbi/dax_measures.md`.

---

## Getting Started

1. Open **Power BI Desktop** (free download from microsoft.com/en-us/power-bi/desktop).
2. Click **Get Data → Text/CSV**.
3. Navigate to `data/patient_data_clean.csv` and click **Load**.
4. Create the DAX measures listed in `dax_measures.md`.
5. Build each dashboard page as described below.

---

## Dashboard Pages

---

### PAGE 1 — Executive Overview

**Purpose:** Give leadership a single-page summary of the most important metrics.

#### KPI Cards (top row)

| KPI Card | DAX Measure | Format |
|----------|-------------|--------|
| Total Patients | `[Total Patients]` | Number, comma-separated |
| Overall Adoption Rate | `[Adoption Rate %]` | Percentage, 1 decimal |
| Continuation Rate | `[Continuation Rate %]` | Percentage, 1 decimal |
| Untreated Patients | `[Untreated Patients]` | Number, comma-separated |
| Follow-up Rate | `[Follow-up Rate %]` | Percentage, 1 decimal |

#### Visuals

| Visual | Type | Fields |
|--------|------|--------|
| Adoption by Region | Clustered Bar Chart | Axis: `Region`, Value: `[Adoption Rate %]` |
| Patient Journey Summary | Table | Columns: Stage, Patients, Drop-off % |
| Adoption by Severity | Donut Chart | Legend: `Disease_Severity`, Value: `[Adoption Rate %]` |
| Monthly Trend | Line Chart | Axis: `Treatment_Start_Date` (Month), Value: `[Treatment Starts]` |

#### Slicers (filters, place on the right or top)
- `Region`
- `Insurance_Status`
- `Disease_Severity`
- `Year` (derived from `Diagnosis_Date`)

#### Design Tips
- Use a dark navy or white theme.
- Highlight the adoption rate KPI in a contrasting colour (e.g., teal).
- Add a text box with the company name: **"NovaCure Pharma — Therapy X"** and the disclaimer.

---

### PAGE 2 — Patient Journey

**Purpose:** Show where patients drop off along the treatment journey.

#### Visuals

| Visual | Type | Fields / Notes |
|--------|------|----------------|
| Patient Journey Funnel | Funnel Chart | Category: Stage, Value: `[Patients at Stage]` |
| Stage Conversion Table | Table | Columns: Stage, Patients, Conversion %, Drop-off % |
| Drop-off by Stage | Bar Chart | Axis: `Drop_Off_Stage`, Value: COUNT of Patient_ID |
| Drop-off by Region | Matrix | Rows: `Region`, Columns: `Drop_Off_Stage`, Values: COUNT |

#### Funnel Chart Stages (in order)
1. Diagnosed
2. Doctor Consultation
3. Treatment Recommended
4. Treatment Started
5. Treatment Continued
6. Follow-up Completed

#### Annotations
- Add a text box noting the biggest drop-off stage.
- Use red colour for the largest drop-off bar.

---

### PAGE 3 — Patient Segments

**Purpose:** Understand the distribution and behaviour of different patient groups.

#### Visuals

| Visual | Type | Fields |
|--------|------|--------|
| Segment Distribution | Stacked Bar or Treemap | Category: `Business_Segment`, Value: COUNT |
| Adoption by Segment | Bar Chart | Axis: `Business_Segment`, Value: `[Adoption Rate %]` |
| Segment × Severity Matrix | Matrix | Rows: `Disease_Severity`, Columns: `Insurance_Status`, Values: `[Adoption Rate %]` |
| Age Group Adoption | Bar Chart | Axis: `Age_Group`, Value: `[Adoption Rate %]` |

#### Derived Column in Power BI
If `Business_Segment` does not import automatically (it is created in Python), create it in
Power Query:
```
= if [Disease_Severity] = "Severe" or [Disease_Severity] = "Moderate" then "High-Need" else "Low-Need"
```
For the Ability Level, create a separate column similarly.

---

### PAGE 4 — Adoption Analysis

**Purpose:** Deep-dive into treatment adoption across multiple dimensions.

#### Visuals

| Visual | Type | Fields |
|--------|------|--------|
| Adoption by Insurance Status | Bar Chart | Axis: `Insurance_Status`, Value: `[Adoption Rate %]` |
| Adoption by Cost Band | Bar Chart | Axis: `Cost_Band`, Value: `[Adoption Rate %]` |
| Adoption: Recommended vs Not | Clustered Bar | Axis: `Treatment_Recommended`, Value: `[Adoption Rate %]` |
| Adoption by Urban/Rural | Bar Chart | Axis: `Urban_Rural`, Value: `[Adoption Rate %]` |
| Adoption by Previous Treatment | Bar Chart | Axis: `Previous_Treatment`, Value: `[Adoption Rate %]` |
| Scatter: Affordability vs Adoption | Scatter Chart | X: AVG(`Affordability_Score`), Y: `[Adoption Rate %]`, Legend: `Region` |

#### Slicers
- `Region`
- `Disease_Severity`
- `Age_Group`

---

### PAGE 5 — Market Opportunity

**Purpose:** Identify which regions have the most untreated patients and highest commercial potential.

#### Visuals

| Visual | Type | Fields |
|--------|------|--------|
| Untreated Patients by Region | Bar Chart (sorted desc) | Axis: `Region`, Value: `[Untreated Patients]` |
| Adoption Rate by Region | Map (if using US map visual) | Location: `State` or `Region`, Color: `[Adoption Rate %]` |
| Opportunity Score Table | Table | Columns: Region, Total Patients, Untreated, Adoption %, Opportunity Score |
| Top Untreated Segment | Bar Chart | Axis: `Business_Segment`, Value: `[Untreated Patients]` |
| Untreated by Insurance × Region | Matrix | Rows: `Region`, Columns: `Insurance_Status`, Values: COUNT (where Treatment_Started=0) |

#### Opportunity Score Column
Create in Power BI using DAX or calculated column (see `dax_measures.md`).

---

## General Design Guidelines

| Element | Recommendation |
|---------|---------------|
| Theme | Use Power BI's built-in "Executive" or "Citypark" theme, or a custom dark/navy theme |
| Font | Segoe UI (Power BI default) or import a custom theme with Inter |
| Colour palette | Teal (`#2a9d8f`), Orange (`#f4a261`), Red (`#e76f51`), Dark Navy (`#264653`) |
| Page navigation | Add page navigation buttons in the left sidebar |
| Disclaimer text | Add "Synthetic data — for educational purposes only" footer on all pages |
| Title format | Page title in top left, company name and date in top right |

---

## Adding the Disclaimer

On every page, add a text box at the bottom:

> *This dashboard uses synthetic data created for analytical and educational purposes.
> It does not represent real patients, clinical outcomes, or actual pharmaceutical data.*

---

*For DAX measures, see `powerbi/dax_measures.md`.*
