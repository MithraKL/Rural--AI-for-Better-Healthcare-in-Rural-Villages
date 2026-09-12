# RuralCare AI — Architecture Notes

## Layers

1. **Geographic Harmonization Layer** (`backend/models/geography.py`) — State → District →
   Block → Village → Facility. Every metric table declares the granularity its real-world
   source actually publishes at (`backend/models/metrics.py`), so district-level surveys
   (NFHS/DLHS/AHS) are never faked down to village level.

2. **Data Ingestion** (`backend/data/ingestion.py`) — column mapping via alias tables →
   numeric normalization → date/quarter normalization → missing-value imputation →
   duplicate detection → geographic matching (rows referencing an unknown village/district
   are rejected, not fabricated) → typed row insertion + `DatasetMetadata` record.

3. **Healthcare Gap Index** (`backend/services/gap_index.py`) — seven independently
   normalized 0-100 dimension scores, combined via configurable weights
   (`backend/services/weights.json`) blended with a "weakest-link" term so one severely
   failing dimension can pull a village into higher risk even when the average looks fine.

4. **Infrastructure-Outcome Paradox Detector** (`backend/services/paradox_detector.py`) —
   pure threshold rule over the computed scores; language is always hedged
   ("possible contributing factors", "requires field validation").

5. **ML Risk Prediction** (`backend/ml/risk_model.py`) — a `RandomForestRegressor` trained
   on pooled quarter-over-quarter transitions across all villages (7 dimension scores +
   a trend-slope feature). Confidence comes from the dispersion of the forest's individual
   tree predictions. Villages with fewer than 3 quarters of history report
   "insufficient historical data" instead of a fabricated number.

6. **Explainability** (`backend/ml/explainability.py`) — combines the model's global
   feature importances with each village's deviation from the population mean, normalized
   to percentages. Deliberately simple and auditable rather than a SHAP dependency, so the
   same technique works identically for real uploaded data.

7. **Prioritization** (`backend/services/prioritization.py`) — weighted composite of
   predicted risk, population affected, severity and trend.

8. **Intervention Engine** (`backend/services/intervention_engine.py`) — a catalogue keyed
   by detected problem tags. Infrastructure expansion is only ever generated when the
   Infrastructure dimension itself is below threshold — never as a first response to a
   utilization, staffing or medicine problem.

9. **Resource Optimizer** (`backend/optimization/resource_optimizer.py`) — greedy
   allocation: candidates sorted by `priority_score × impact_per_resource`, allocated in
   that order while every required resource type remains available.

10. **What-If Simulator** (`backend/simulation/whatif.py`) — combines selected
    interventions' catalog impact scores with diminishing returns, scaled by a
    funding/dosage multiplier derived from the allocated budget/resources versus the
    interventions' estimated requirement.

11. **GenAI Explanation** (`backend/services/genai_explainer.py`) — narrates the
    structured output above into a decision-brief sentence. Ships with a deterministic
    template so the whole product works with zero external credentials; a watsonx.ai call
    can be dropped in behind the same interface for narration only.

## Orchestration

`backend/services/pipeline.py` runs steps 3–8 end-to-end for every village and quarter,
called once at startup/seed time (`scripts/seed_db.py`) and again via
`POST /api/data/recompute` after new data is ingested.

## Why a greedy heuristic, not an LP solver, for optimization

The resource optimizer intentionally uses a fast, fully-explainable greedy heuristic
(sort by priority × impact-per-resource, allocate while resources last) rather than an
exact linear/mixed-integer program. For a live decision console this trades a small
amount of optimality for: (a) sub-second response times, (b) a ranking any official can
audit by eye, and (c) natural extensibility as new resource types are added. This
trade-off is disclosed on the Methodology page rather than hidden.
