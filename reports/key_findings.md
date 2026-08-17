# Key Findings — Patient Journey & Treatment Adoption Analytics

> All findings are based on the synthetic dataset of 25,000 patients generated for this project.

---

### Finding 1 — Overall Adoption Rate is Moderate

**Observation:**
The overall treatment adoption rate for Therapy X is **43.3%**, meaning that
roughly 57% of diagnosed patients never start the treatment.

**Why it matters:**
A large pool of eligible but untreated patients represents both unmet medical need
and a commercial growth opportunity for the company.

**Business Implication:**
The company should investigate barriers to adoption and design targeted interventions
to close the gap.

---

### Finding 2 — The Biggest Drop-off is at the "Follow-up Completed" Stage

**Observation:**
The largest single drop-off in the patient journey occurs at the **Follow-up Completed** stage
(47.5% of patients at the previous stage are lost here).

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
**64.0%**, compared to only **33.9%** among those who were not recommended
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
Insured patients show an adoption rate of **48.5%**, while uninsured patients
show only **29.3%** — a meaningful gap that suggests affordability and
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
Patients with severe disease have an adoption rate of **51.4%** vs.
**38.6%** for mild-disease patients. Higher clinical need is associated with
greater willingness to initiate treatment — but the rate is still well below 100%.

**Why it matters:**
Even the highest-need patients do not always start treatment. Barriers persist even
when urgency is highest.

**Business Implication:**
Even for high-severity patients, access barriers (cost, geography, insurance) still
limit adoption. These should not be ignored in the most urgent patient groups.

---

### Finding 6 — The Southeast Region Presents the Highest Market Opportunity

**Observation:**
The **Southeast** region has the highest opportunity score, driven by a large
untreated patient population of **3,118** and a below-average adoption rate.

**Why it matters:**
Concentrating commercial and medical education resources in high-opportunity regions
can deliver the greatest return.

**Business Implication:**
The company should prioritise field force coverage, HCP outreach, and patient
support programmes in the Southeast region.

---

### Finding 7 — Side Effect Concerns are Negatively Associated with Adoption

**Observation:**
The logistic regression identified **Age** as a negative predictor of
treatment adoption — patients with greater side effect concerns are less likely to
start Therapy X.

**Why it matters:**
Fear of side effects is a well-documented barrier to treatment initiation in
chronic disease settings.

**Business Implication:**
Patient education materials and HCP training should explicitly address common side
effect concerns and provide realistic risk–benefit communication.

---

### Finding 8 — Logistic Regression Model Achieves ROC-AUC of 0.686

**Observation:**
A simple logistic regression model using 10 interpretable features achieves a
ROC-AUC of **0.686**, indicating it is meaningfully better than random
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
