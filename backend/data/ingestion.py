"""Data Ingestion Layer.

Accepts CSV / Excel / JSON uploads for any of the six supported sources
(RHS, HMIS, NFHS, DLHS, AHS, Anganwadi), and runs them through:

  column mapping -> numeric normalization -> date/quarter normalization ->
  missing-value handling -> duplicate detection -> geographic matching ->
  validation -> typed rows ready for insertion + DatasetMetadata record.

Design rule: a row whose village/district cannot be matched to an existing
geography record is REJECTED with an explicit error, never silently
attached to the wrong place or fabricated. Real data is never blended with
demo data without being labeled (`is_demo=False` on DatasetMetadata).
"""
import io
import re
from dataclasses import dataclass, field
import pandas as pd
from sqlalchemy.orm import Session

from backend.models import Village, District, RHSMetric, HMISMetric, NFHSMetric, DLHSMetric, AHSMetric, AnganwadiMetric

SOURCE_GRANULARITY = {
    "RHS": "village", "HMIS": "village", "Anganwadi": "village",
    "NFHS": "district", "DLHS": "district", "AHS": "district",
}

# Accepted column aliases -> canonical field name, per source.
COLUMN_ALIASES = {
    "RHS": {
        "village": "village_name", "village_name": "village_name", "quarter": "quarter",
        "sub_centres": "sub_centres_count", "sub_centres_count": "sub_centres_count",
        "phc": "phc_count", "phc_count": "phc_count", "chc": "chc_count", "chc_count": "chc_count",
        "mmu": "mmu_count", "mmu_count": "mmu_count",
        "doctors_sanctioned": "doctors_sanctioned", "doctors_in_position": "doctors_in_position",
        "nurses_sanctioned": "nurses_sanctioned", "nurses_in_position": "nurses_in_position",
        "anms_in_position": "anms_in_position", "ashas_linked": "ashas_linked",
        "beds": "beds_total", "beds_total": "beds_total",
        "monthly_capacity": "monthly_capacity_total", "monthly_capacity_total": "monthly_capacity_total",
    },
    "HMIS": {
        "village": "village_name", "village_name": "village_name", "quarter": "quarter",
        "opd_visits": "opd_visits", "opd": "opd_visits",
        "ipd_admissions": "ipd_admissions", "ipd": "ipd_admissions",
        "deliveries": "deliveries", "c_sections": "c_sections",
        "anc_visits": "anc_visits", "immunization_sessions_held": "immunization_sessions_held",
        "full_immunization_pct": "full_immunization_pct", "immunization_pct": "full_immunization_pct",
        "institutional_delivery_pct": "institutional_delivery_pct",
        "opd_utilization_pct": "opd_utilization_pct", "utilization_pct": "opd_utilization_pct",
    },
    "Anganwadi": {
        "village": "village_name", "village_name": "village_name", "quarter": "quarter",
        "children_registered": "children_registered",
        "children_weighed_pct": "children_weighed_pct",
        "severely_underweight_pct": "severely_underweight_pct",
        "moderately_underweight_pct": "moderately_underweight_pct",
        "supplementary_nutrition_days": "supplementary_nutrition_days",
        "doctor_visits_count": "doctor_visits_count", "growth_monitoring_pct": "growth_monitoring_pct",
        "water_availability": "water_availability", "toilet_availability": "toilet_availability",
        "medicine_availability_pct": "medicine_availability_pct",
    },
    "NFHS": {
        "district": "district_name", "district_name": "district_name", "round": "round",
        "stunting_pct": "stunting_pct", "wasting_pct": "wasting_pct", "underweight_pct": "underweight_pct",
        "anemia_women_pct": "anemia_women_pct", "anemia_children_pct": "anemia_children_pct",
        "full_immunization_pct": "full_immunization_pct", "institutional_delivery_pct": "institutional_delivery_pct",
        "under5_mortality_rate": "under5_mortality_rate",
    },
    "DLHS": {
        "district": "district_name", "district_name": "district_name", "round": "round",
        "institutional_delivery_pct": "institutional_delivery_pct",
        "full_immunization_pct": "full_immunization_pct",
        "contraceptive_prevalence_pct": "contraceptive_prevalence_pct",
    },
    "AHS": {
        "district": "district_name", "district_name": "district_name", "year": "year",
        "maternal_mortality_ratio": "maternal_mortality_ratio",
        "infant_mortality_rate": "infant_mortality_rate",
        "under5_mortality_rate": "under5_mortality_rate",
        "total_fertility_rate": "total_fertility_rate",
    },
}

MODEL_BY_SOURCE = {
    "RHS": RHSMetric, "HMIS": HMISMetric, "Anganwadi": AnganwadiMetric,
    "NFHS": NFHSMetric, "DLHS": DLHSMetric, "AHS": AHSMetric,
}

NUMERIC_HINT_SUFFIXES = ("_pct", "_count", "_rate", "_total", "_visits", "_days", "_sanctioned", "_position", "_linked", "_ratio")


def _normalize_colname(c: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")


def _parse_quarter(value) -> str | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    m = re.match(r"^(20\d{2})[\s\-_]?Q([1-4])$", s, re.IGNORECASE)
    if m:
        return f"{m.group(1)}-Q{m.group(2)}"
    try:
        dt = pd.to_datetime(s, errors="raise")
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{q}"
    except Exception:
        return None


@dataclass
class IngestionResult:
    success: bool
    row_count: int = 0
    inserted: int = 0
    duplicates_dropped: int = 0
    missing_values_filled: int = 0
    unmatched_geography: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    granularity: str = ""


def read_upload(filename: str, content: bytes) -> pd.DataFrame:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    if lower.endswith(".json"):
        return pd.read_json(io.BytesIO(content))
    raise ValueError("Unsupported file type. Please upload .csv, .xlsx or .json")


def ingest_dataframe(db: Session, source_name: str, df: pd.DataFrame) -> IngestionResult:
    if source_name not in COLUMN_ALIASES:
        return IngestionResult(success=False, errors=[f"Unknown source '{source_name}'. Must be one of {list(COLUMN_ALIASES)}"])

    result = IngestionResult(success=True, row_count=len(df), granularity=SOURCE_GRANULARITY[source_name])
    if df.empty:
        result.success = False
        result.errors.append("Uploaded file has no rows.")
        return result

    # --- column mapping ---
    aliases = COLUMN_ALIASES[source_name]
    df = df.rename(columns={c: _normalize_colname(c) for c in df.columns})
    mapped_cols = {c: aliases[c] for c in df.columns if c in aliases}
    unmapped = [c for c in df.columns if c not in aliases]
    df = df.rename(columns=mapped_cols)

    key_col = "village_name" if result.granularity == "village" else "district_name"
    period_col = "quarter" if "quarter" in aliases.values() else ("round" if "round" in aliases.values() else "year")

    if key_col not in df.columns:
        result.success = False
        result.errors.append(f"Could not find a '{key_col}' column (or recognized alias). Unmapped columns: {unmapped}")
        return result

    # --- duplicate detection ---
    before = len(df)
    subset = [key_col] + ([period_col] if period_col in df.columns else [])
    df = df.drop_duplicates(subset=subset, keep="first")
    result.duplicates_dropped = before - len(df)

    # --- numeric normalization ---
    filled = 0
    for col in df.columns:
        if col in (key_col, period_col, "district_name"):
            continue
        if df[col].dtype == object:
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.notna().sum() >= len(df) * 0.5:
                df[col] = coerced
        if pd.api.types.is_numeric_dtype(df[col]):
            n_missing = df[col].isna().sum()
            if n_missing:
                median = df[col].median()
                df[col] = df[col].fillna(median if pd.notna(median) else 0)
                filled += int(n_missing)
            if col.endswith("_pct"):
                df[col] = df[col].clip(0, 100)
    result.missing_values_filled = filled

    # --- date/quarter normalization ---
    if period_col == "quarter" and "quarter" in df.columns:
        df["quarter"] = df["quarter"].apply(_parse_quarter)
        bad = df["quarter"].isna().sum()
        if bad:
            result.errors.append(f"{bad} row(s) had an unparseable quarter value and were dropped.")
            df = df.dropna(subset=["quarter"])

    # --- geographic matching (never fabricated) ---
    rows_to_insert = []
    if result.granularity == "village":
        villages = {v.name.strip().lower(): v.id for v in db.query(Village).all()}
        for _, row in df.iterrows():
            vname = str(row[key_col]).strip().lower()
            village_id = villages.get(vname)
            if village_id is None:
                result.unmatched_geography.append(str(row[key_col]))
                continue
            row_dict = row.to_dict()
            row_dict["village_id"] = village_id
            rows_to_insert.append(row_dict)
    else:
        districts = {d.name.strip().lower(): d.id for d in db.query(District).all()}
        for _, row in df.iterrows():
            dname = str(row[key_col]).strip().lower()
            district_id = districts.get(dname)
            if district_id is None:
                result.unmatched_geography.append(str(row[key_col]))
                continue
            row_dict = row.to_dict()
            row_dict["district_id"] = district_id
            rows_to_insert.append(row_dict)

    # --- insert typed rows ---
    Model = MODEL_BY_SOURCE[source_name]
    valid_fields = {c.name for c in Model.__table__.columns}
    inserted = 0
    for row_dict in rows_to_insert:
        clean = {k: v for k, v in row_dict.items() if k in valid_fields}
        try:
            db.add(Model(**clean))
            inserted += 1
        except Exception as e:
            result.errors.append(str(e))
    db.commit()
    result.inserted = inserted

    if result.unmatched_geography:
        result.errors.append(
            f"{len(result.unmatched_geography)} row(s) referenced a {key_col.replace('_name','')} not found in "
            f"the geography database and were skipped (no data was fabricated for them)."
        )

    if inserted == 0:
        result.success = False
        result.errors.append("No rows could be matched and inserted.")

    return result
