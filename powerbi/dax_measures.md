# DAX Measures — Patient Journey & Treatment Adoption Analytics

> Copy and paste these measures into Power BI Desktop.
> In Power BI: **Modeling → New Measure** for each measure below.
> Assumes the table is named **patient_data_clean**.

---

## Core KPI Measures

### Total Patients
```dax
Total Patients =
COUNTROWS(patient_data_clean)
```

### Adopted Patients
```dax
Adopted Patients =
SUM(patient_data_clean[Treatment_Started])
```

### Untreated Patients
```dax
Untreated Patients =
[Total Patients] - [Adopted Patients]
```

### Adoption Rate %
```dax
Adoption Rate % =
DIVIDE(
    [Adopted Patients],
    [Total Patients],
    0
) * 100
```

*Tip: Format this measure as a percentage with 1 decimal place in the Format pane.*

---

### Continued Treatment
```dax
Continued Treatment =
SUM(patient_data_clean[Treatment_Continued])
```

### Continuation Rate % (of Starters)
```dax
Continuation Rate % =
DIVIDE(
    SUM(patient_data_clean[Treatment_Continued]),
    SUM(patient_data_clean[Treatment_Started]),
    0
) * 100
```

### Follow-up Completed
```dax
Follow-up Completed =
SUM(patient_data_clean[Follow_Up_Completed])
```

### Follow-up Rate % (of Continuers)
```dax
Follow-up Rate % =
DIVIDE(
    SUM(patient_data_clean[Follow_Up_Completed]),
    SUM(patient_data_clean[Treatment_Continued]),
    0
) * 100
```

---

## Patient Journey Funnel Measures

### Doctor Consultations
```dax
Doctor Consultations =
SUM(patient_data_clean[Doctor_Consultation])
```

### Treatment Recommendations
```dax
Treatment Recommendations =
SUM(patient_data_clean[Treatment_Recommended])
```

### Treatment Starts
```dax
Treatment Starts =
SUM(patient_data_clean[Treatment_Started])
```

### Consultation Rate %
```dax
Consultation Rate % =
DIVIDE(
    SUM(patient_data_clean[Doctor_Consultation]),
    [Total Patients],
    0
) * 100
```

### Recommendation Rate %
```dax
Recommendation Rate % =
DIVIDE(
    SUM(patient_data_clean[Treatment_Recommended]),
    SUM(patient_data_clean[Doctor_Consultation]),
    0
) * 100
```

### Start from Recommendation Rate %
```dax
Start from Recommendation Rate % =
DIVIDE(
    SUM(patient_data_clean[Treatment_Started]),
    SUM(patient_data_clean[Treatment_Recommended]),
    0
) * 100
```

---

## Adoption Gap Measures

### Adoption Gap %
```dax
Adoption Gap % =
100 - [Adoption Rate %]
```

### Physician Recommended Adoption Rate %
```dax
Recommended Adoption Rate % =
CALCULATE(
    [Adoption Rate %],
    patient_data_clean[Treatment_Recommended] = 1
)
```

### Not Recommended Adoption Rate %
```dax
Not Recommended Adoption Rate % =
CALCULATE(
    [Adoption Rate %],
    patient_data_clean[Treatment_Recommended] = 0
)
```

### Insured Adoption Rate %
```dax
Insured Adoption Rate % =
CALCULATE(
    [Adoption Rate %],
    patient_data_clean[Insurance_Status] = "Insured"
)
```

### Uninsured Adoption Rate %
```dax
Uninsured Adoption Rate % =
CALCULATE(
    [Adoption Rate %],
    patient_data_clean[Insurance_Status] = "Uninsured"
)
```

---

## Market Opportunity Measures

### Average Treatment Cost
```dax
Avg Treatment Cost =
AVERAGE(patient_data_clean[Treatment_Cost])
```

### Average Affordability Score
```dax
Avg Affordability Score =
AVERAGE(patient_data_clean[Affordability_Score])
```

### Average Healthcare Access Score
```dax
Avg Healthcare Access Score =
AVERAGE(patient_data_clean[Healthcare_Access_Score])
```

---

## Opportunity Score (Calculated Column)

> Create this as a **Calculated Column**, not a measure.
> In Power BI: **Modeling → New Column**

```dax
Opportunity_Score_Simple =
VAR MaxUntreated =
    MAXX(
        ALL(patient_data_clean[Region]),
        CALCULATE(
            COUNTROWS(patient_data_clean)
            - SUM(patient_data_clean[Treatment_Started])
        )
    )
VAR MaxGap =
    MAXX(
        ALL(patient_data_clean[Region]),
        CALCULATE(100 - [Adoption Rate %])
    )
VAR RegionUntreated =
    CALCULATE(
        COUNTROWS(patient_data_clean)
        - SUM(patient_data_clean[Treatment_Started])
    )
VAR RegionGap =
    CALCULATE(100 - [Adoption Rate %])
RETURN
    0.5 * DIVIDE(RegionUntreated, MaxUntreated, 0)
    + 0.5 * DIVIDE(RegionGap, MaxGap, 0)
```

*Note: For a simpler approach, use the pre-calculated `Opp_Score` column from
`results/market_opportunity.csv` and join it to the main table in Power Query.*

---

## Useful Calculated Columns

> Create these in **Modeling → New Column** (not as measures).

### Age Group
```dax
Age_Group_DAX =
SWITCH(
    TRUE(),
    patient_data_clean[Age] <= 30, "18-30",
    patient_data_clean[Age] <= 45, "31-45",
    patient_data_clean[Age] <= 60, "46-60",
    "61+"
)
```

*Use this only if `Age_Group` is not already in the CSV.*

### Need Level
```dax
Need_Level =
IF(
    patient_data_clean[Disease_Severity] IN {"Moderate", "Severe"},
    "High-Need",
    "Low-Need"
)
```

### Ability Level
```dax
Ability_Level =
SWITCH(
    TRUE(),
    patient_data_clean[Insurance_Status] = "Insured"
        && patient_data_clean[Affordability_Score] >= 5,
    "High-Ability",
    patient_data_clean[Insurance_Status] = "Uninsured"
        || patient_data_clean[Affordability_Score] < 3,
    "Low-Ability",
    "Medium-Ability"
)
```

### Business Segment
```dax
Business_Segment =
[Need_Level] & " / " & [Ability_Level]
```

---

## Formatting Tips

| Measure | Recommended Format |
|---------|-------------------|
| `Adoption Rate %` | Percentage, 1 decimal |
| `Continuation Rate %` | Percentage, 1 decimal |
| `Follow-up Rate %` | Percentage, 1 decimal |
| `Total Patients` | Whole number, comma separator |
| `Untreated Patients` | Whole number, comma separator |
| `Avg Treatment Cost` | Currency ($), 0 decimals |
| `Avg Affordability Score` | Decimal number, 1 decimal |

---

*All DAX measures above are compatible with Power BI Desktop (any version from 2022 onwards).
This project uses synthetic data for educational purposes only.*
