"""Real, publicly-sourced geography and district-survey data for RuralCare AI's
8 demo districts. Everything in this file was extracted directly from official
government publications (see citations below) — it is NOT synthetic.

Village/block names + village-level population are still generated
synthetically on top of these real names (see demo_generator.py), because:
  - HMIS (utilization/service delivery) requires authorized government login
    and has no public bulk-download source.
  - Anganwadi/ICDS granular data has no reliable public bulk-download source.
  - Per-village Census population would require deep-parsing a much larger
    wide-format table; out of scope for this pass (village *names* and
    *blocks* were prioritized as the highest-value real substitution).

Sources:
  - Village/Block (CD Block) names: Census of India 2011, District Census
    Handbook Part-A, Village Directory section, for each district
    (censusindia.gov.in/nada). Real Census 2011 location-coded villages.
  - NFHS-5 indicators (stunting/wasting/underweight/anemia/full immunization):
    National Family Health Survey (NFHS-5) 2019-21, District Tables (Table 60,
    72, 81), state reports FR374 (Uttar Pradesh, Madhya Pradesh) — IIPS/ICF/
    DHS Program (dhsprogram.com).
  - AHS indicators (institutional delivery, IMR, U5MR, TFR): Annual Health
    Survey 2010-13, Registrar General of India — Key Indicators of AHS,
    district-wise (data.gov.in / Government Open Data License - India).

NOT available for these districts:
  - DLHS-4: excluded all EAG states. Both Uttar Pradesh and Madhya Pradesh are
    EAG states (covered by AHS instead), so DLHS-4 simply does not exist for
    any of these 8 districts. Left empty rather than fabricated.
  - Maternal Mortality Ratio at district level: neither NFHS nor AHS publish
    a statistically reliable district-level MMR (sample sizes too small for
    a rare event) — kept as a modeled estimate, not a real figure, and
    labelled as such.
"""

# 2 real CD Blocks x 5 real villages each, per district (Census 2011 Village Directory)
REAL_GEO: dict[str, list[tuple[str, list[str]]]] = {
    "Sitapur": [
        ("Pisawan", ["Abdipur", "Akabarpur", "Akohra", "Allipur", "Amanullapur"]),
        ("Maholi", ["Adora", "Adori", "Amlia", "Andapur", "Bada Gaon"]),
    ],
    "Barabanki": [
        ("Nindaura", ["Agasand", "Ahamad Nagar", "Akbarpur", "Akhaipur", "Alampur"]),
        ("Fatehpur", ["Achaicha", "Agauli", "Ahmadpur", "Allahapur Bharali", "Asohna"]),
    ],
    "Gonda": [
        ("Rupaidih", ["Achal Nagar", "Achlapur", "Achlapur Bargadhi", "Adbadwa", "Akbarpur"]),
        ("Itia Thok", ["Ahrolia", "Akdega", "Ameha", "Amreebharia Khas", "Arjunpur"]),
    ],
    "Raebareli": [
        ("Bachhrawan", ["Amawa", "Ashan Jagatpur", "Bachhrawan", "Bahadur Nagar", "Bahadurpur"]),
        ("Shivgarh", ["Aimapur", "Badaver", "Bahuda Kalan", "Bahuda Khurd", "Baiti"]),
    ],
    "Chhindwara": [
        ("Tamia", ["Aliwada", "Amdhana", "Anhoni", "Babai Pathar", "Bakhari"]),
        ("Harrai", ["Acharkund", "Aharwada", "Amari", "Andol", "Ankhawadi"]),
    ],
    "Betul": [
        ("Bhimpura", ["Adarsh Dhanora", "Amadhana", "Amapathar", "Anki Raiyat", "Bagda Biran"]),
        ("Bhainsdehi", ["Adaumar", "Ambhori", "Amla", "Badgaon", "Balner"]),
    ],
    "Sagar": [
        ("Bina", ["Agasod", "Amkheda", "Bagaspur", "Bagdawli", "Balarkhedi"]),
        ("Khurai", ["Achanwara", "Alkhedi", "Asoli", "Bachhu", "Badoli"]),
    ],
    "Damoh": [
        ("Hatta", ["Abda", "Achalpura", "Adanwara", "Amajhir", "Bachhama"]),
        ("Patera", ["Bagha", "Bagsari", "Bamanpura", "Bamhori Kudai", "Bamni"]),
    ],
}

# Real NFHS-5 (2019-21) district indicators
REAL_NFHS: dict[str, dict[str, float]] = {
    "Sitapur":    {"stunting_pct": 47.8, "wasting_pct": 18.2, "underweight_pct": 37.9, "anemia_women_pct": 55.3, "anemia_children_pct": 66.4, "full_immunization_pct": 65.9},
    "Barabanki":  {"stunting_pct": 41.9, "wasting_pct": 18.1, "underweight_pct": 31.9, "anemia_women_pct": 55.3, "anemia_children_pct": 65.5, "full_immunization_pct": 64.4},
    "Gonda":      {"stunting_pct": 45.9, "wasting_pct": 12.1, "underweight_pct": 28.0, "anemia_women_pct": 49.3, "anemia_children_pct": 62.0, "full_immunization_pct": 59.9},
    "Raebareli":  {"stunting_pct": 47.0, "wasting_pct": 13.0, "underweight_pct": 28.8, "anemia_women_pct": 48.2, "anemia_children_pct": 76.4, "full_immunization_pct": 71.4},
    "Chhindwara": {"stunting_pct": 23.9, "wasting_pct": 18.1, "underweight_pct": 32.8, "anemia_women_pct": 41.7, "anemia_children_pct": 50.5, "full_immunization_pct": 65.3},
    "Betul":      {"stunting_pct": 30.8, "wasting_pct": 21.7, "underweight_pct": 31.4, "anemia_women_pct": 56.2, "anemia_children_pct": 57.8, "full_immunization_pct": 80.9},
    "Sagar":      {"stunting_pct": 42.7, "wasting_pct": 15.2, "underweight_pct": 35.7, "anemia_women_pct": 49.8, "anemia_children_pct": 83.3, "full_immunization_pct": 75.9},
    "Damoh":      {"stunting_pct": 40.3, "wasting_pct": 16.2, "underweight_pct": 32.3, "anemia_women_pct": 48.1, "anemia_children_pct": 76.2, "full_immunization_pct": 60.8},
}

# Real AHS (2010-13) district indicators. institutional_delivery_pct is reused
# for NFHSMetric.institutional_delivery_pct too (NFHS's own district delivery
# table could not be reliably text-extracted from the source PDF's font
# encoding; AHS measures the same real-world indicator).
REAL_AHS: dict[str, dict[str, float]] = {
    "Sitapur":    {"institutional_delivery_pct": 56.05, "infant_mortality_rate": 80.19, "under5_mortality_rate": 114, "total_fertility_rate": 4.42},
    "Barabanki":  {"institutional_delivery_pct": 59.91, "infant_mortality_rate": 67.83, "under5_mortality_rate": 97, "total_fertility_rate": 3.85},
    "Gonda":      {"institutional_delivery_pct": 50.69, "infant_mortality_rate": 71.22, "under5_mortality_rate": 97, "total_fertility_rate": 4.01},
    "Raebareli":  {"institutional_delivery_pct": 67.77, "infant_mortality_rate": 53.24, "under5_mortality_rate": 80, "total_fertility_rate": 3.29},
    "Chhindwara": {"institutional_delivery_pct": 81.8, "infant_mortality_rate": 69.02, "under5_mortality_rate": 77, "total_fertility_rate": 2.6},
    "Betul":      {"institutional_delivery_pct": 86.2, "infant_mortality_rate": 60.8, "under5_mortality_rate": 70, "total_fertility_rate": 2.8},
    "Sagar":      {"institutional_delivery_pct": 72.1, "infant_mortality_rate": 69.37, "under5_mortality_rate": 92, "total_fertility_rate": 3.3},
    "Damoh":      {"institutional_delivery_pct": 57.6, "infant_mortality_rate": 70.58, "under5_mortality_rate": 106, "total_fertility_rate": 3.5},
}
