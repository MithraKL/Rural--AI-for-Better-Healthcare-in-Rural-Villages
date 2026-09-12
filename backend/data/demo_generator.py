"""Demo data generator for RuralCare AI — a deliberate mix of REAL and
SYNTHETIC data, clearly separated:

REAL (see backend/data/real_geo_data.py for exact sources):
  - District names, and 2 CD Block names + 5 village names per district
    (Census of India 2011, District Census Handbook Village Directory).
  - NFHS-5 (2019-21) district indicators: stunting, wasting, underweight,
    anemia (women/children), full immunization.
  - AHS (2010-13) district indicators: institutional delivery, infant
    mortality, under-5 mortality, total fertility rate.

SYNTHETIC (generated here, with deliberately embedded patterns —
Infrastructure-Outcome Paradox, declining immunization, high malnutrition,
resource overload, etc. — so every AI module has real signal to detect):
  - Village population, facility infrastructure/workforce (RHS), service
    utilization (HMIS), and Anganwadi nutrition/outreach metrics. These
    require either authorized government login (HMIS) or have no reliable
    public bulk-download (Anganwadi/ICDS, per-village RHS), so they are
    modeled rather than fabricated-as-real.
  - DLHS-4 is not generated at all: both Uttar Pradesh and Madhya Pradesh
    are EAG states, which DLHS-4 excluded entirely in favor of AHS — that
    survey round genuinely does not exist for these districts.

DatasetMetadata.is_demo reflects this per-source, not as one blanket flag —
see scripts/seed_db.py. Archetypes are used only to *seed* believable
synthetic numbers; no downstream service reads the archetype label — every
score, flag and prediction is computed from the generated numbers
themselves, exactly as it would be for real uploaded data.
"""
import random
import numpy as np
import pandas as pd

from backend.data.real_geo_data import REAL_GEO, REAL_NFHS, REAL_AHS

RNG_SEED = 42
QUARTERS = ["2023-Q3", "2023-Q4", "2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"]

STATES = ["Uttar Pradesh", "Madhya Pradesh"]

DISTRICTS = [
    ("Sitapur", "Uttar Pradesh"), ("Barabanki", "Uttar Pradesh"),
    ("Gonda", "Uttar Pradesh"), ("Raebareli", "Uttar Pradesh"),
    ("Chhindwara", "Madhya Pradesh"), ("Betul", "Madhya Pradesh"),
    ("Sagar", "Madhya Pradesh"), ("Damoh", "Madhya Pradesh"),
]

BLOCKS_PER_DISTRICT = 2
VILLAGES_PER_BLOCK = 5

def _seeded_rng():
    return np.random.default_rng(RNG_SEED)


ARCHETYPES = [
    ("paradox", 0.13),
    ("infra_poor", 0.14),
    ("high_performer", 0.14),
    ("underutilized", 0.10),
    ("high_malnutrition", 0.10),
    ("declining_immunization", 0.10),
    ("improving", 0.10),
    ("early_warning", 0.08),
    ("average", 0.11),
]


def _assign_archetypes(n, rng):
    names = [a[0] for a in ARCHETYPES]
    weights = np.array([a[1] for a in ARCHETYPES])
    weights = weights / weights.sum()
    return list(rng.choice(names, size=n, p=weights))


def _clip(v, lo=0.0, hi=100.0):
    return float(np.clip(v, lo, hi))


def _trend_series(start, end_delta_per_q, noise, n=len(QUARTERS), rng=None, floor=0, ceil=100):
    vals = []
    v = start
    for i in range(n):
        v = v + end_delta_per_q + rng.normal(0, noise)
        vals.append(_clip(v, floor, ceil))
    return vals


def generate_all(seed: int = RNG_SEED):
    rng = np.random.default_rng(seed)
    random.seed(seed)

    districts_rows = []
    blocks_rows = []
    villages_rows = []
    facilities_rows = []
    rhs_rows = []
    hmis_rows = []
    anganwadi_rows = []
    nfhs_rows = []
    dlhs_rows = []
    ahs_rows = []

    district_id = 1
    block_id = 1
    village_id = 1
    facility_id = 1

    village_ids_for_district = {}

    for d_name, state in DISTRICTS:
        districts_rows.append({"id": district_id, "name": d_name, "state": state,
                                "population": 0})
        this_district_id = district_id
        village_ids_for_district[this_district_id] = []

        n_villages_total = BLOCKS_PER_DISTRICT * VILLAGES_PER_BLOCK
        archetypes = _assign_archetypes(n_villages_total, rng)
        arch_iter = iter(archetypes)

        for b in range(BLOCKS_PER_DISTRICT):
            block_name, real_villages = REAL_GEO[d_name][b]
            blocks_rows.append({"id": block_id, "name": block_name, "district_id": this_district_id,
                                 "population": 0})
            this_block_id = block_id

            for v in range(VILLAGES_PER_BLOCK):
                archetype = next(arch_iter)
                vname = real_villages[v]

                population = int(rng.integers(900, 15000))
                lat = 24.5 + rng.uniform(-2.5, 2.5) if state == "Madhya Pradesh" else 27.0 + rng.uniform(-2.0, 2.0)
                lon = 78.5 + rng.uniform(-2.5, 2.5) if state == "Madhya Pradesh" else 80.5 + rng.uniform(-2.0, 2.0)

                # --- archetype-driven baseline levels (0-100 "fill" style indices) ---
                if archetype == "paradox":
                    infra_fill = rng.uniform(75, 95)
                    workforce_fill = rng.uniform(55, 80)
                    utilization_rate = rng.uniform(15, 32)
                    immunization_start = rng.uniform(35, 48)
                    malnutrition_severe = rng.uniform(18, 28)
                    distance_km = rng.uniform(1, 4)
                    road = 1
                    imm_slope = rng.uniform(-1.0, 0.5)
                elif archetype == "infra_poor":
                    infra_fill = rng.uniform(10, 32)
                    workforce_fill = rng.uniform(15, 40)
                    utilization_rate = rng.uniform(20, 45)
                    immunization_start = rng.uniform(30, 50)
                    malnutrition_severe = rng.uniform(15, 26)
                    distance_km = rng.uniform(8, 20)
                    road = int(rng.random() > 0.6)
                    imm_slope = rng.uniform(-1.5, 0.5)
                elif archetype == "high_performer":
                    infra_fill = rng.uniform(60, 88)
                    workforce_fill = rng.uniform(65, 90)
                    utilization_rate = rng.uniform(60, 85)
                    immunization_start = rng.uniform(72, 92)
                    malnutrition_severe = rng.uniform(3, 10)
                    distance_km = rng.uniform(0.5, 3)
                    road = 1
                    imm_slope = rng.uniform(0.0, 1.2)
                elif archetype == "underutilized":
                    infra_fill = rng.uniform(45, 65)
                    workforce_fill = rng.uniform(45, 65)
                    utilization_rate = rng.uniform(18, 33)
                    immunization_start = rng.uniform(45, 60)
                    malnutrition_severe = rng.uniform(10, 18)
                    distance_km = rng.uniform(2, 7)
                    road = 1
                    imm_slope = rng.uniform(-0.5, 0.5)
                elif archetype == "high_malnutrition":
                    infra_fill = rng.uniform(35, 60)
                    workforce_fill = rng.uniform(35, 60)
                    utilization_rate = rng.uniform(35, 55)
                    immunization_start = rng.uniform(45, 65)
                    malnutrition_severe = rng.uniform(28, 42)
                    distance_km = rng.uniform(3, 10)
                    road = int(rng.random() > 0.3)
                    imm_slope = rng.uniform(-0.8, 0.3)
                elif archetype == "declining_immunization":
                    infra_fill = rng.uniform(40, 65)
                    workforce_fill = rng.uniform(40, 65)
                    utilization_rate = rng.uniform(40, 60)
                    immunization_start = rng.uniform(68, 80)
                    malnutrition_severe = rng.uniform(10, 20)
                    distance_km = rng.uniform(2, 8)
                    road = 1
                    imm_slope = rng.uniform(-4.5, -2.5)
                elif archetype == "improving":
                    infra_fill = rng.uniform(30, 55)
                    workforce_fill = rng.uniform(35, 55)
                    utilization_rate = rng.uniform(25, 40)
                    immunization_start = rng.uniform(40, 55)
                    malnutrition_severe = rng.uniform(15, 25)
                    distance_km = rng.uniform(3, 9)
                    road = int(rng.random() > 0.3)
                    imm_slope = rng.uniform(2.0, 4.0)
                elif archetype == "early_warning":
                    infra_fill = rng.uniform(45, 65)
                    workforce_fill = rng.uniform(45, 65)
                    utilization_rate = rng.uniform(45, 60)
                    immunization_start = rng.uniform(55, 68)
                    malnutrition_severe = rng.uniform(20, 28)  # will rise steadily (see below)
                    distance_km = rng.uniform(2, 7)
                    road = 1
                    imm_slope = rng.uniform(-1.5, -0.5)
                else:  # average
                    infra_fill = rng.uniform(40, 65)
                    workforce_fill = rng.uniform(40, 65)
                    utilization_rate = rng.uniform(40, 60)
                    immunization_start = rng.uniform(55, 70)
                    malnutrition_severe = rng.uniform(10, 20)
                    distance_km = rng.uniform(2, 8)
                    road = 1
                    imm_slope = rng.uniform(-0.5, 0.5)

                villages_rows.append({
                    "id": village_id, "name": vname, "block_id": this_block_id,
                    "district_id": this_district_id, "state": state,
                    "population": population, "latitude": round(lat, 5), "longitude": round(lon, 5),
                    "distance_to_facility_km": round(distance_km, 2),
                    "has_all_weather_road": road,
                    "_archetype": archetype,  # kept only for CSV documentation, stripped before DB load
                })
                village_ids_for_district[this_district_id].append(village_id)

                # --- Facility ---
                facility_type = "PHC" if infra_fill > 55 else ("Sub-Centre" if infra_fill > 25 else "Sub-Centre")
                doctors_sanc = 2 if facility_type == "PHC" else 1
                nurses_sanc = 4 if facility_type == "PHC" else 2
                doctors_pos = max(0, round(doctors_sanc * (workforce_fill / 100) + rng.normal(0, 0.3)))
                nurses_pos = max(0, round(nurses_sanc * (workforce_fill / 100) + rng.normal(0, 0.4)))
                beds = 6 if (facility_type == "PHC" and infra_fill > 40) else 0
                base_capacity = population * 0.09 if facility_type == "PHC" else population * 0.05
                quality_derate = 0.1 + 0.9 * (infra_fill / 100)  # infra quality directly scales effective capacity
                capacity = int(base_capacity * quality_derate)
                functional = int(infra_fill > 40)

                # facility-level resource-mismatch pattern: ~10% overloaded, ~10% underutilized
                mismatch_roll = rng.random()
                overloaded = mismatch_roll < 0.10
                facility_underutilized = 0.10 <= mismatch_roll < 0.20
                if overloaded:
                    doctors_pos = max(1, doctors_pos - 1)
                elif facility_underutilized:
                    doctors_pos = doctors_sanc  # fully staffed but demand will be forced low below

                facilities_rows.append({
                    "id": facility_id, "name": f"{facility_type} {vname}", "facility_type": facility_type,
                    "village_id": village_id, "block_id": this_block_id, "district_id": this_district_id,
                    "latitude": round(lat + rng.uniform(-0.02, 0.02), 5),
                    "longitude": round(lon + rng.uniform(-0.02, 0.02), 5),
                    "doctors_sanctioned": doctors_sanc, "doctors_in_position": int(doctors_pos),
                    "nurses_sanctioned": nurses_sanc, "nurses_in_position": int(nurses_pos),
                    "anms_in_position": max(1, round(2 * workforce_fill / 100)),
                    "ashas_linked": max(1, round(population / 1000)),
                    "beds": beds, "monthly_patient_capacity": capacity,
                    "has_functional_equipment": functional,
                    "has_medicine_stock": int(rng.random() > (0.35 if infra_fill < 40 else 0.1)),
                    "_overloaded": overloaded, "_facility_underutilized": facility_underutilized,
                })

                # --- Quarterly time series: RHS / HMIS / Anganwadi ---
                imm_series = _trend_series(immunization_start, imm_slope, 2.0, rng=rng, floor=15, ceil=96)
                if archetype == "early_warning":
                    # explicit worsening malnutrition trend mirroring the spec's own example (42->48->56->64)
                    malnutrition_series = [_clip(malnutrition_severe + i * 4.3 + rng.normal(0, 1.0), 5, 70)
                                            for i in range(len(QUARTERS))]
                else:
                    mal_slope = -1.2 if archetype in ("improving", "high_performer") else rng.uniform(-0.3, 0.6)
                    malnutrition_series = _trend_series(malnutrition_severe, mal_slope, 1.5, rng=rng, floor=2, ceil=55)

                util_slope = 3.0 if archetype == "improving" else (-1.0 if archetype == "underutilized" else rng.uniform(-0.5, 0.5))
                util_series = _trend_series(utilization_rate, util_slope, 4.0, rng=rng, floor=5, ceil=140)
                if overloaded:
                    # Module 9 pattern: patient demand persistently exceeds this facility's capacity
                    util_series = [_clip(v + rng.uniform(55, 80), 5, 175) for v in util_series]
                elif facility_underutilized:
                    # Module 9 pattern: adequate staffing but very low demand
                    util_series = [_clip(v * rng.uniform(0.3, 0.5), 5, 175) for v in util_series]

                for qi, quarter in enumerate(QUARTERS):
                    rhs_rows.append({
                        "village_id": village_id, "quarter": quarter,
                        "sub_centres_count": (1 if facility_type == "Sub-Centre" else 0) * functional,
                        "phc_count": (1 if facility_type == "PHC" else 0) * functional,
                        "chc_count": 0, "mmu_count": 1 if (infra_fill > 80 and rng.random() > 0.5) else 0,
                        "doctors_sanctioned": doctors_sanc, "doctors_in_position": int(doctors_pos),
                        "nurses_sanctioned": nurses_sanc, "nurses_in_position": int(nurses_pos),
                        "anms_in_position": max(1, round(2 * workforce_fill / 100)),
                        "ashas_linked": max(1, round(population / 1000)),
                        "beds_total": beds, "monthly_capacity_total": capacity,
                    })

                    opd_visits = int(max(0, capacity * 3 * (util_series[qi] / 100) + rng.normal(0, capacity * 0.05)))
                    deliveries = int(max(0, population * 0.006 * (util_series[qi] / 100) + rng.normal(0, 1)))
                    hmis_rows.append({
                        "village_id": village_id, "quarter": quarter,
                        "opd_visits": opd_visits,
                        "ipd_admissions": int(max(0, deliveries * 0.4)),
                        "deliveries": deliveries,
                        "c_sections": int(max(0, deliveries * 0.12)),
                        "anc_visits": int(max(0, deliveries * 2.8)),
                        "immunization_sessions_held": int(max(0, 3 + workforce_fill / 25)),
                        "full_immunization_pct": round(imm_series[qi], 1),
                        "institutional_delivery_pct": round(_clip(imm_series[qi] * 0.9 + rng.normal(0, 3)), 1),
                        "opd_utilization_pct": round(_clip(util_series[qi], 0, 160), 1),
                    })

                    children_registered = int(population * 0.085)
                    anganwadi_rows.append({
                        "village_id": village_id, "quarter": quarter,
                        "children_registered": children_registered,
                        "children_weighed_pct": round(_clip(60 + workforce_fill / 3 + rng.normal(0, 5)), 1),
                        "severely_underweight_pct": round(malnutrition_series[qi] * 0.35, 1),
                        "moderately_underweight_pct": round(malnutrition_series[qi] * 0.65, 1),
                        "supplementary_nutrition_days": int(_clip(45 + infra_fill / 3 + rng.normal(0, 8), 10, 90)),
                        "doctor_visits_count": int(_clip(workforce_fill / 35 + rng.normal(0, 0.5), 0, 3)),
                        "growth_monitoring_pct": round(_clip(55 + workforce_fill / 2.5 + rng.normal(0, 6)), 1),
                        "water_availability": int(rng.random() > (0.3 if infra_fill < 35 else 0.08)),
                        "toilet_availability": int(rng.random() > (0.35 if infra_fill < 35 else 0.1)),
                        "medicine_availability_pct": round(_clip(50 + infra_fill / 2 + rng.normal(0, 8)), 1),
                    })

                village_id += 1
                facility_id += 1

            block_id += 1
        district_id += 1

    # --- District-level surveys ---
    # NFHS-5 and AHS values below are REAL, published figures for these 8 districts
    # (see backend/data/real_geo_data.py for exact sources/tables). DLHS-4 does not
    # exist for these districts at all (both UP and MP are EAG states, which DLHS-4
    # excluded in favor of AHS) — left as an empty table rather than fabricated.
    # Only maternal_mortality_ratio has no reliable district-level real source (too
    # rare an event for AHS/NFHS district sample sizes) and is a modeled estimate.
    for d in districts_rows:
        d_villages = [v for v in villages_rows if v["district_id"] == d["id"]]
        d["population"] = int(sum(v["population"] for v in d_villages))

        nfhs = REAL_NFHS[d["name"]]
        ahs = REAL_AHS[d["name"]]

        nfhs_rows.append({
            "district_id": d["id"], "round": "NFHS-5",
            "stunting_pct": nfhs["stunting_pct"],
            "wasting_pct": nfhs["wasting_pct"],
            "underweight_pct": nfhs["underweight_pct"],
            "anemia_women_pct": nfhs["anemia_women_pct"],
            "anemia_children_pct": nfhs["anemia_children_pct"],
            "full_immunization_pct": nfhs["full_immunization_pct"],
            "institutional_delivery_pct": ahs["institutional_delivery_pct"],
            "under5_mortality_rate": ahs["under5_mortality_rate"],
        })
        ahs_rows.append({
            "district_id": d["id"], "year": "2011-13",
            # Modeled estimate (not a real district-level AHS/NFHS figure — see module docstring)
            "maternal_mortality_ratio": round(_clip(150 + ahs["under5_mortality_rate"] * 1.1, 80, 450), 1),
            "infant_mortality_rate": ahs["infant_mortality_rate"],
            "under5_mortality_rate": ahs["under5_mortality_rate"],
            "total_fertility_rate": ahs["total_fertility_rate"],
        })

    return {
        "states": pd.DataFrame([{"id": i + 1, "name": s} for i, s in enumerate(STATES)]),
        "districts": pd.DataFrame(districts_rows),
        "blocks": pd.DataFrame(blocks_rows),
        "villages": pd.DataFrame(villages_rows),
        "facilities": pd.DataFrame(facilities_rows),
        "rhs_metrics": pd.DataFrame(rhs_rows),
        "hmis_metrics": pd.DataFrame(hmis_rows),
        "anganwadi_metrics": pd.DataFrame(anganwadi_rows),
        "nfhs_metrics": pd.DataFrame(nfhs_rows),
        "dlhs_metrics": pd.DataFrame(dlhs_rows),
        "ahs_metrics": pd.DataFrame(ahs_rows),
    }


if __name__ == "__main__":
    data = generate_all()
    for k, v in data.items():
        print(k, v.shape)
