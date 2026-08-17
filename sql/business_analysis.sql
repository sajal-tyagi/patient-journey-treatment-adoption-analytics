-- ============================================================
-- business_analysis.sql
-- Patient Journey & Treatment Adoption Analytics
-- SQL Business Analysis Queries
--
-- Dataset: data/patient_data_clean.csv
-- Import instructions: See sql/README.md
--
-- DISCLAIMER: This project uses synthetic data created for
-- analytical and educational purposes only.
-- ============================================================


-- ============================================================
-- QUERY 1
-- Business Question:
-- What is the overall treatment adoption rate for Therapy X?
-- ============================================================

SELECT
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted_Patients,
    COUNT(*) - SUM(Treatment_Started)               AS Unadopted_Patients,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean;


-- ============================================================
-- QUERY 2
-- Business Question:
-- What is the treatment adoption rate in each region?
-- Which region has the highest and lowest adoption?
-- ============================================================

SELECT
    Region,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct,
    COUNT(*) - SUM(Treatment_Started)               AS Untreated_Patients
FROM patient_data_clean
GROUP BY Region
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 3
-- Business Question:
-- How does insurance status affect treatment adoption?
-- ============================================================

SELECT
    Insurance_Status,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Insurance_Status
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 4
-- Business Question:
-- Does disease severity influence treatment adoption?
-- ============================================================

SELECT
    Disease_Severity,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Disease_Severity
ORDER BY
    CASE Disease_Severity
        WHEN 'Mild'     THEN 1
        WHEN 'Moderate' THEN 2
        WHEN 'Severe'   THEN 3
    END;


-- ============================================================
-- QUERY 5
-- Business Question:
-- Which age groups have the highest treatment adoption rates?
-- ============================================================

SELECT
    Age_Group,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Age_Group
ORDER BY Age_Group;


-- ============================================================
-- QUERY 6
-- Business Question:
-- What is the average treatment cost, and how does it vary
-- by insurance status?
-- ============================================================

SELECT
    Insurance_Status,
    COUNT(*)                                        AS Total_Patients,
    ROUND(AVG(Treatment_Cost), 0)                   AS Avg_Cost_USD,
    ROUND(MIN(Treatment_Cost), 0)                   AS Min_Cost_USD,
    ROUND(MAX(Treatment_Cost), 0)                   AS Max_Cost_USD
FROM patient_data_clean
GROUP BY Insurance_Status
ORDER BY Avg_Cost_USD;


-- ============================================================
-- QUERY 7
-- Business Question:
-- How does treatment cost range affect adoption?
-- ============================================================

SELECT
    Cost_Band,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Cost_Band
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 8
-- Business Question:
-- Does a physician recommendation significantly improve
-- treatment adoption?
-- ============================================================

SELECT
    CASE
        WHEN Treatment_Recommended = 1 THEN 'Recommended'
        ELSE 'Not Recommended'
    END                                             AS Recommendation_Status,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Treatment_Recommended
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 9
-- Business Question:
-- What is the treatment continuation rate among patients
-- who started Therapy X?
-- ============================================================

SELECT
    COUNT(*)                                            AS Started_Treatment,
    SUM(Treatment_Continued)                            AS Continued_Treatment,
    ROUND(
        100.0 * SUM(Treatment_Continued) / COUNT(*), 2
    )                                                   AS Continuation_Rate_Pct,
    COUNT(*) - SUM(Treatment_Continued)                 AS Dropped_After_Starting,
    ROUND(
        100.0 * (COUNT(*) - SUM(Treatment_Continued)) / COUNT(*), 2
    )                                                   AS Drop_After_Starting_Pct
FROM patient_data_clean
WHERE Treatment_Started = 1;


-- ============================================================
-- QUERY 10
-- Business Question:
-- Where in the patient journey are the largest drop-offs?
-- ============================================================

WITH funnel AS (
    SELECT
        25000                                   AS Stage_0_Diagnosed,
        SUM(Doctor_Consultation)                AS Stage_1_Consulted,
        SUM(Treatment_Recommended)              AS Stage_2_Recommended,
        SUM(Treatment_Started)                  AS Stage_3_Started,
        SUM(Treatment_Continued)                AS Stage_4_Continued,
        SUM(Follow_Up_Completed)                AS Stage_5_Followup
    FROM patient_data_clean
)
SELECT
    'Diagnosed → Consulted'          AS Transition,
    Stage_0_Diagnosed                AS From_Stage,
    Stage_1_Consulted                AS To_Stage,
    Stage_0_Diagnosed - Stage_1_Consulted AS Lost_Patients,
    ROUND(
        100.0 * (Stage_0_Diagnosed - Stage_1_Consulted) / Stage_0_Diagnosed, 2
    )                                AS Drop_Off_Pct
FROM funnel

UNION ALL

SELECT
    'Consulted → Recommended',
    Stage_1_Consulted,
    Stage_2_Recommended,
    Stage_1_Consulted - Stage_2_Recommended,
    ROUND(
        100.0 * (Stage_1_Consulted - Stage_2_Recommended) / Stage_1_Consulted, 2
    )
FROM funnel

UNION ALL

SELECT
    'Recommended → Started',
    Stage_2_Recommended,
    Stage_3_Started,
    Stage_2_Recommended - Stage_3_Started,
    ROUND(
        100.0 * (Stage_2_Recommended - Stage_3_Started) / Stage_2_Recommended, 2
    )
FROM funnel

UNION ALL

SELECT
    'Started → Continued',
    Stage_3_Started,
    Stage_4_Continued,
    Stage_3_Started - Stage_4_Continued,
    ROUND(
        100.0 * (Stage_3_Started - Stage_4_Continued) / Stage_3_Started, 2
    )
FROM funnel

UNION ALL

SELECT
    'Continued → Follow-up',
    Stage_4_Continued,
    Stage_5_Followup,
    Stage_4_Continued - Stage_5_Followup,
    ROUND(
        100.0 * (Stage_4_Continued - Stage_5_Followup) / Stage_4_Continued, 2
    )
FROM funnel

ORDER BY Drop_Off_Pct DESC;


-- ============================================================
-- QUERY 11
-- Business Question:
-- Which regions have the highest market opportunity based on
-- untreated patient volume?
-- ============================================================

SELECT
    Region,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Treated_Patients,
    COUNT(*) - SUM(Treatment_Started)               AS Untreated_Patients,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct,
    ROUND(
        100.0 * (COUNT(*) - SUM(Treatment_Started)) / COUNT(*), 2
    )                                               AS Untreated_Rate_Pct
FROM patient_data_clean
GROUP BY Region
ORDER BY Untreated_Patients DESC;


-- ============================================================
-- QUERY 12
-- Business Question:
-- Within untreated patients, which region and insurance
-- combination has the most patients? (Priority targeting)
-- ============================================================

SELECT
    Region,
    Insurance_Status,
    COUNT(*)                                        AS Untreated_Patients
FROM patient_data_clean
WHERE Treatment_Started = 0
GROUP BY Region, Insurance_Status
ORDER BY Untreated_Patients DESC
LIMIT 10;


-- ============================================================
-- QUERY 13
-- Business Question:
-- How do monthly treatment starts trend over time?
-- ============================================================

SELECT
    SUBSTR(Treatment_Start_Date, 1, 7)              AS Year_Month,
    COUNT(*)                                        AS New_Treatment_Starts
FROM patient_data_clean
WHERE Treatment_Started = 1
  AND Treatment_Start_Date IS NOT NULL
GROUP BY SUBSTR(Treatment_Start_Date, 1, 7)
ORDER BY Year_Month;


-- ============================================================
-- QUERY 14
-- Business Question:
-- Does having a prior treatment history affect adoption of
-- Therapy X?
-- ============================================================

SELECT
    CASE
        WHEN Previous_Treatment = 1 THEN 'Prior Treatment: Yes'
        ELSE 'Prior Treatment: No'
    END                                             AS Prior_Treatment,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
GROUP BY Previous_Treatment
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 15
-- Business Question:
-- How does healthcare access score relate to treatment adoption?
-- (Grouped into Low / Medium / High access tiers)
-- ============================================================

SELECT
    CASE
        WHEN Healthcare_Access_Score < 4  THEN 'Low Access (< 4)'
        WHEN Healthcare_Access_Score < 7  THEN 'Medium Access (4-7)'
        ELSE                                   'High Access (7-10)'
    END                                             AS Access_Tier,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct,
    ROUND(AVG(Healthcare_Access_Score), 2)          AS Avg_Access_Score
FROM patient_data_clean
GROUP BY Access_Tier
ORDER BY Avg_Access_Score;


-- ============================================================
-- QUERY 16
-- Business Question:
-- Among high-severity patients, what is the breakdown by
-- insurance and adoption? (Priority segment detail)
-- ============================================================

SELECT
    Insurance_Status,
    COUNT(*)                                        AS Total_Severe_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    COUNT(*) - SUM(Treatment_Started)               AS Untreated,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct
FROM patient_data_clean
WHERE Disease_Severity = 'Severe'
GROUP BY Insurance_Status
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 17
-- Business Question:
-- What is the follow-up completion rate by region?
-- ============================================================

SELECT
    Region,
    SUM(Treatment_Continued)                        AS Continued_Patients,
    SUM(Follow_Up_Completed)                        AS Followup_Completed,
    ROUND(
        100.0 * SUM(Follow_Up_Completed) /
        NULLIF(SUM(Treatment_Continued), 0), 2
    )                                               AS Followup_Rate_Pct
FROM patient_data_clean
GROUP BY Region
ORDER BY Followup_Rate_Pct DESC;


-- ============================================================
-- QUERY 18
-- Business Question:
-- Using a CTE, identify patients at high risk of not starting
-- treatment (high severity, uninsured, no recommendation).
-- How many are there per region?
-- ============================================================

WITH high_risk_untreated AS (
    SELECT
        Patient_ID,
        Region,
        Disease_Severity,
        Insurance_Status,
        Treatment_Recommended,
        Treatment_Started
    FROM patient_data_clean
    WHERE
        Disease_Severity    = 'Severe'
        AND Insurance_Status = 'Uninsured'
        AND Treatment_Started = 0
)
SELECT
    Region,
    COUNT(*) AS High_Risk_Untreated_Patients
FROM high_risk_untreated
GROUP BY Region
ORDER BY High_Risk_Untreated_Patients DESC;


-- ============================================================
-- QUERY 19
-- Business Question:
-- What is the adoption rate by urban/rural setting?
-- ============================================================

SELECT
    Urban_Rural,
    COUNT(*)                                        AS Total_Patients,
    SUM(Treatment_Started)                          AS Adopted,
    ROUND(
        100.0 * SUM(Treatment_Started) / COUNT(*), 2
    )                                               AS Adoption_Rate_Pct,
    COUNT(*) - SUM(Treatment_Started)               AS Untreated_Patients
FROM patient_data_clean
GROUP BY Urban_Rural
ORDER BY Adoption_Rate_Pct DESC;


-- ============================================================
-- QUERY 20
-- Business Question:
-- Rank each region by opportunity score using a window function.
-- Opportunity = weighted combination of untreated volume and
-- adoption gap.
-- ============================================================

WITH region_stats AS (
    SELECT
        Region,
        COUNT(*)                                        AS Total_Patients,
        SUM(Treatment_Started)                          AS Treated,
        COUNT(*) - SUM(Treatment_Started)               AS Untreated,
        ROUND(
            100.0 * (COUNT(*) - SUM(Treatment_Started)) / COUNT(*), 2
        )                                               AS Adoption_Gap_Pct
    FROM patient_data_clean
    GROUP BY Region
),
max_vals AS (
    SELECT
        MAX(Untreated)          AS Max_Untreated,
        MAX(Adoption_Gap_Pct)   AS Max_Gap
    FROM region_stats
)
SELECT
    rs.Region,
    rs.Total_Patients,
    rs.Untreated,
    rs.Adoption_Gap_Pct,
    ROUND(
        0.5 * (rs.Untreated * 1.0 / mv.Max_Untreated) +
        0.5 * (rs.Adoption_Gap_Pct / mv.Max_Gap),
        4
    )                                               AS Opportunity_Score,
    RANK() OVER (
        ORDER BY
            0.5 * (rs.Untreated * 1.0 / mv.Max_Untreated) +
            0.5 * (rs.Adoption_Gap_Pct / mv.Max_Gap) DESC
    )                                               AS Opportunity_Rank
FROM region_stats rs, max_vals mv
ORDER BY Opportunity_Rank;
