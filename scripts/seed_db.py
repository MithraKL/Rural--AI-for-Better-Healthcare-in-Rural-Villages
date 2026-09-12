"""Seed the RuralCare AI database with synthetic demo data and run the full
AI pipeline (gap index -> paradox detection -> risk prediction ->
explainability -> prioritization -> interventions).

Usage:
    python -m scripts.seed_db [--reset]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import Base, engine, SessionLocal
from backend.data.demo_generator import generate_all
from backend.models import (
    State, District, Block, Village, Facility,
    RHSMetric, HMISMetric, AnganwadiMetric, NFHSMetric, DLHSMetric, AHSMetric,
    DatasetMetadata,
)
from backend.services.pipeline import recompute_all

DATA_SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample"))


def save_sample_csvs(data: dict):
    os.makedirs(DATA_SAMPLE_DIR, exist_ok=True)
    for name, df in data.items():
        export_df = df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore")
        export_df.to_csv(os.path.join(DATA_SAMPLE_DIR, f"{name}.csv"), index=False)
    print(f"Saved {len(data)} sample CSVs to {DATA_SAMPLE_DIR}")


def load_into_db(db, data: dict):
    for _, row in data["states"].iterrows():
        db.add(State(id=int(row["id"]), name=row["name"]))
    db.commit()

    state_id_by_name = {s.name: s.id for s in db.query(State).all()}
    for _, row in data["districts"].iterrows():
        db.add(District(id=int(row["id"]), name=row["name"], state_id=state_id_by_name[row["state"]],
                         population=int(row["population"])))
    db.commit()

    for _, row in data["blocks"].iterrows():
        db.add(Block(id=int(row["id"]), name=row["name"], district_id=int(row["district_id"]),
                      population=int(row["population"])))
    db.commit()

    for _, row in data["villages"].iterrows():
        state_id = state_id_by_name[row["state"]]
        db.add(Village(
            id=int(row["id"]), name=row["name"], block_id=int(row["block_id"]),
            district_id=int(row["district_id"]), state_id=state_id, population=int(row["population"]),
            latitude=float(row["latitude"]), longitude=float(row["longitude"]),
            distance_to_facility_km=float(row["distance_to_facility_km"]),
            has_all_weather_road=int(row["has_all_weather_road"]), is_demo=1,
        ))
    db.commit()

    for _, row in data["facilities"].iterrows():
        db.add(Facility(
            id=int(row["id"]), name=row["name"], facility_type=row["facility_type"],
            village_id=int(row["village_id"]), block_id=int(row["block_id"]), district_id=int(row["district_id"]),
            latitude=float(row["latitude"]), longitude=float(row["longitude"]),
            doctors_sanctioned=int(row["doctors_sanctioned"]), doctors_in_position=int(row["doctors_in_position"]),
            nurses_sanctioned=int(row["nurses_sanctioned"]), nurses_in_position=int(row["nurses_in_position"]),
            anms_in_position=int(row["anms_in_position"]), ashas_linked=int(row["ashas_linked"]),
            beds=int(row["beds"]), monthly_patient_capacity=int(row["monthly_patient_capacity"]),
            has_functional_equipment=int(row["has_functional_equipment"]),
            has_medicine_stock=int(row["has_medicine_stock"]),
        ))
    db.commit()

    def bulk(model, df, cols):
        for _, row in df.iterrows():
            db.add(model(**{c: row[c] for c in cols}))
        db.commit()

    bulk(RHSMetric, data["rhs_metrics"], [
        "village_id", "quarter", "sub_centres_count", "phc_count", "chc_count", "mmu_count",
        "doctors_sanctioned", "doctors_in_position", "nurses_sanctioned", "nurses_in_position",
        "anms_in_position", "ashas_linked", "beds_total", "monthly_capacity_total",
    ])
    bulk(HMISMetric, data["hmis_metrics"], [
        "village_id", "quarter", "opd_visits", "ipd_admissions", "deliveries", "c_sections", "anc_visits",
        "immunization_sessions_held", "full_immunization_pct", "institutional_delivery_pct", "opd_utilization_pct",
    ])
    bulk(AnganwadiMetric, data["anganwadi_metrics"], [
        "village_id", "quarter", "children_registered", "children_weighed_pct", "severely_underweight_pct",
        "moderately_underweight_pct", "supplementary_nutrition_days", "doctor_visits_count",
        "growth_monitoring_pct", "water_availability", "toilet_availability", "medicine_availability_pct",
    ])
    bulk(NFHSMetric, data["nfhs_metrics"], [
        "district_id", "round", "stunting_pct", "wasting_pct", "underweight_pct", "anemia_women_pct",
        "anemia_children_pct", "full_immunization_pct", "institutional_delivery_pct", "under5_mortality_rate",
    ])
    bulk(DLHSMetric, data["dlhs_metrics"], [
        "district_id", "round", "institutional_delivery_pct", "full_immunization_pct", "contraceptive_prevalence_pct",
    ])
    bulk(AHSMetric, data["ahs_metrics"], [
        "district_id", "year", "maternal_mortality_ratio", "infant_mortality_rate",
        "under5_mortality_rate", "total_fertility_rate",
    ])

    dataset_notes = {
        "RHS": (True, "Synthetic: village names/blocks are real (Census 2011 Village Directory), "
                      "but infrastructure/workforce figures are modeled (per-village RHS has no public bulk source)."),
        "HMIS": (True, "Synthetic: HMIS requires an authorized government login with no public bulk-download "
                       "source, so utilization/service-delivery figures are modeled."),
        "Anganwadi": (True, "Synthetic: Anganwadi/ICDS has no reliable public bulk-download source, "
                            "so nutrition/outreach figures are modeled."),
        "NFHS": (False, "Real: National Family Health Survey-5 (2019-21), district-level, IIPS/ICF/DHS Program "
                        "(dhsprogram.com). institutional_delivery_pct and under5_mortality_rate sourced from AHS "
                        "(NFHS's own district delivery table could not be reliably extracted from the source PDF)."),
        "DLHS": (False, "Not available: DLHS-4 (2012-13) excluded all EAG states. Uttar Pradesh and Madhya Pradesh "
                        "are both EAG states (covered by AHS instead), so this survey round does not exist for "
                        "any of these districts. No data fabricated."),
        "AHS": (False, "Real: Annual Health Survey (2010-13), district-level, Registrar General of India "
                       "(Key Indicators of AHS, data.gov.in). maternal_mortality_ratio is a modeled estimate — "
                       "no source publishes a statistically reliable district-level MMR."),
    }
    for source, df, gran in [
        ("RHS", data["rhs_metrics"], "village"), ("HMIS", data["hmis_metrics"], "village"),
        ("Anganwadi", data["anganwadi_metrics"], "village"), ("NFHS", data["nfhs_metrics"], "district"),
        ("DLHS", data["dlhs_metrics"], "district"), ("AHS", data["ahs_metrics"], "district"),
    ]:
        is_demo, notes = dataset_notes[source]
        db.add(DatasetMetadata(source_name=source, file_name=f"{source.lower()}_demo.csv" if len(df) else None,
                                granularity=gran, row_count=len(df), is_demo=is_demo, notes=notes))
    db.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding")
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(Village).count()
        if existing > 0 and not args.reset:
            print(f"Database already has {existing} villages. Use --reset to regenerate. Recomputing pipeline only.")
        else:
            print("Generating synthetic demo data...")
            data = generate_all()
            save_sample_csvs(data)
            print("Loading into database...")
            load_into_db(db, data)
            print(f"Loaded {len(data['villages'])} villages across {len(data['districts'])} districts.")

        print("Running AI pipeline (gap index, risk prediction, prioritization, interventions)...")
        summary = recompute_all(db)
        print("Pipeline summary:", summary)
    finally:
        db.close()


if __name__ == "__main__":
    main()
