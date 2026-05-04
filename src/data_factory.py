from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List


PUBLIC_DATASET_REFERENCE = {
    "primary_dataset": {
        "name": "Synthea",
        "url": "https://synthetichealth.github.io/synthea/",
        "role": "Synthetic patient, encounter, medication, and allergy backbone for pharmacy workflows.",
    },
    "enrichment_sources": [
        {
            "name": "RxNorm",
            "url": "https://www.nlm.nih.gov/research/umls/rxnorm/index.html",
            "role": "Drug normalization and canonical ingredient naming.",
        },
        {
            "name": "DailyMed",
            "url": "https://dailymed.nlm.nih.gov/",
            "role": "Structured labeling, warnings, contraindications, and administration guidance.",
        },
        {
            "name": "openFDA",
            "url": "https://open.fda.gov/apis/",
            "role": "Safety-signal enrichment using public FDA adverse event and recall data.",
        },
    ],
    "advanced_real_world_option": {
        "name": "MIMIC-IV",
        "url": "https://physionet.org/content/mimiciv/3.0/",
        "role": "Credentialed-access hospital medication data for future production-grade validation.",
    },
}


PATIENTS = [
    {"patient_id": "PAT-1001", "name": "Ana Silva", "age": 34, "sex": "F", "care_setting": "ambulatory"},
    {"patient_id": "PAT-1002", "name": "Bruno Costa", "age": 72, "sex": "M", "care_setting": "chronic_care"},
    {"patient_id": "PAT-1003", "name": "Carla Souza", "age": 8, "sex": "F", "care_setting": "pediatrics"},
    {"patient_id": "PAT-1004", "name": "Diego Lima", "age": 56, "sex": "M", "care_setting": "ambulatory"},
]

ALLERGIES = [
    {"patient_id": "PAT-1001", "allergen": "penicillin", "severity": "high"},
    {"patient_id": "PAT-1002", "allergen": "none", "severity": "none"},
    {"patient_id": "PAT-1003", "allergen": "none", "severity": "none"},
    {"patient_id": "PAT-1004", "allergen": "none", "severity": "none"},
]

FORMULARY = [
    {
        "drug_name": "amoxicillin 500 mg capsule",
        "rxnorm_code": "308182",
        "active_ingredient": "amoxicillin",
        "allergy_group": "penicillin",
        "therapeutic_class": "antibiotic_beta_lactam",
        "min_age": 0,
        "max_daily_dose_mg": 3000,
        "high_risk": "no",
        "dailymed_warning_excerpt": "Avoid use in patients with serious penicillin hypersensitivity.",
        "openfda_signal_count": 12,
    },
    {
        "drug_name": "warfarin 5 mg tablet",
        "rxnorm_code": "855332",
        "active_ingredient": "warfarin",
        "allergy_group": "none",
        "therapeutic_class": "anticoagulant",
        "min_age": 18,
        "max_daily_dose_mg": 15,
        "high_risk": "yes",
        "dailymed_warning_excerpt": "Major bleeding risk requires close monitoring and interaction review.",
        "openfda_signal_count": 38,
    },
    {
        "drug_name": "ibuprofen 400 mg tablet",
        "rxnorm_code": "197806",
        "active_ingredient": "ibuprofen",
        "allergy_group": "nsaid",
        "therapeutic_class": "nsaid",
        "min_age": 12,
        "max_daily_dose_mg": 2400,
        "high_risk": "no",
        "dailymed_warning_excerpt": "NSAIDs may increase bleeding risk when combined with anticoagulants.",
        "openfda_signal_count": 21,
    },
    {
        "drug_name": "doxycycline 100 mg capsule",
        "rxnorm_code": "1650144",
        "active_ingredient": "doxycycline",
        "allergy_group": "tetracycline",
        "therapeutic_class": "antibiotic_tetracycline",
        "min_age": 12,
        "max_daily_dose_mg": 200,
        "high_risk": "no",
        "dailymed_warning_excerpt": "Use in younger children requires specialist review because of tooth discoloration risk.",
        "openfda_signal_count": 9,
    },
    {
        "drug_name": "metformin 500 mg tablet",
        "rxnorm_code": "860975",
        "active_ingredient": "metformin",
        "allergy_group": "none",
        "therapeutic_class": "biguanide",
        "min_age": 10,
        "max_daily_dose_mg": 2550,
        "high_risk": "no",
        "dailymed_warning_excerpt": "Review kidney function before long-term dispensing.",
        "openfda_signal_count": 6,
    },
    {
        "drug_name": "simvastatin 20 mg tablet",
        "rxnorm_code": "312961",
        "active_ingredient": "simvastatin",
        "allergy_group": "none",
        "therapeutic_class": "statin",
        "min_age": 18,
        "max_daily_dose_mg": 40,
        "high_risk": "no",
        "dailymed_warning_excerpt": "Duplicate statin therapy increases myopathy risk.",
        "openfda_signal_count": 11,
    },
    {
        "drug_name": "atorvastatin 20 mg tablet",
        "rxnorm_code": "617314",
        "active_ingredient": "atorvastatin",
        "allergy_group": "none",
        "therapeutic_class": "statin",
        "min_age": 18,
        "max_daily_dose_mg": 80,
        "high_risk": "no",
        "dailymed_warning_excerpt": "Use only one statin regimen unless explicitly justified.",
        "openfda_signal_count": 14,
    },
]

INTERACTIONS = [
    {
        "drug_a": "warfarin",
        "drug_b": "ibuprofen",
        "severity": "major",
        "mechanism": "Bleeding risk amplification",
        "recommendation": "Block automatic dispensing and escalate to pharmacist review.",
    },
    {
        "drug_a": "simvastatin",
        "drug_b": "atorvastatin",
        "severity": "moderate",
        "mechanism": "Therapeutic duplication within statin class",
        "recommendation": "Hold one statin and confirm intentional switch.",
    },
]

INVENTORY = [
    {"drug_name": "amoxicillin 500 mg capsule", "available_units": 120, "reorder_point": 40},
    {"drug_name": "warfarin 5 mg tablet", "available_units": 90, "reorder_point": 25},
    {"drug_name": "ibuprofen 400 mg tablet", "available_units": 6, "reorder_point": 20},
    {"drug_name": "doxycycline 100 mg capsule", "available_units": 20, "reorder_point": 10},
    {"drug_name": "metformin 500 mg tablet", "available_units": 250, "reorder_point": 60},
    {"drug_name": "simvastatin 20 mg tablet", "available_units": 75, "reorder_point": 20},
    {"drug_name": "atorvastatin 20 mg tablet", "available_units": 80, "reorder_point": 20},
]

PRESCRIPTIONS = [
    {
        "prescription_id": "RX-1001",
        "patient_id": "PAT-1001",
        "drug_name": "amoxicillin 500 mg capsule",
        "dose_mg": 500,
        "quantity": 21,
        "days_supply": 7,
        "refill_number": 0,
        "is_active": "yes",
        "clinical_priority": "routine",
    },
    {
        "prescription_id": "RX-1002",
        "patient_id": "PAT-1002",
        "drug_name": "warfarin 5 mg tablet",
        "dose_mg": 5,
        "quantity": 30,
        "days_supply": 30,
        "refill_number": 2,
        "is_active": "yes",
        "clinical_priority": "high",
    },
    {
        "prescription_id": "RX-1003",
        "patient_id": "PAT-1002",
        "drug_name": "ibuprofen 400 mg tablet",
        "dose_mg": 400,
        "quantity": 20,
        "days_supply": 5,
        "refill_number": 0,
        "is_active": "yes",
        "clinical_priority": "high",
    },
    {
        "prescription_id": "RX-1004",
        "patient_id": "PAT-1003",
        "drug_name": "doxycycline 100 mg capsule",
        "dose_mg": 100,
        "quantity": 14,
        "days_supply": 7,
        "refill_number": 0,
        "is_active": "yes",
        "clinical_priority": "routine",
    },
    {
        "prescription_id": "RX-1005",
        "patient_id": "PAT-1004",
        "drug_name": "metformin 500 mg tablet",
        "dose_mg": 500,
        "quantity": 60,
        "days_supply": 30,
        "refill_number": 1,
        "is_active": "yes",
        "clinical_priority": "routine",
    },
    {
        "prescription_id": "RX-1006",
        "patient_id": "PAT-1004",
        "drug_name": "simvastatin 20 mg tablet",
        "dose_mg": 20,
        "quantity": 30,
        "days_supply": 30,
        "refill_number": 1,
        "is_active": "yes",
        "clinical_priority": "routine",
    },
    {
        "prescription_id": "RX-1007",
        "patient_id": "PAT-1004",
        "drug_name": "atorvastatin 20 mg tablet",
        "dose_mg": 20,
        "quantity": 30,
        "days_supply": 30,
        "refill_number": 0,
        "is_active": "yes",
        "clinical_priority": "routine",
    },
]


def _write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_sample_dataset(base_dir: Path) -> Dict[str, str]:
    raw_dir = base_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    patients_path = raw_dir / "patients.csv"
    allergies_path = raw_dir / "allergies.csv"
    formulary_path = raw_dir / "formulary.csv"
    inventory_path = raw_dir / "inventory.csv"
    interactions_path = raw_dir / "drug_interactions.csv"
    prescriptions_path = raw_dir / "prescriptions.csv"
    dataset_reference_path = raw_dir / "public_dataset_reference.json"

    _write_csv(patients_path, PATIENTS)
    _write_csv(allergies_path, ALLERGIES)
    _write_csv(formulary_path, FORMULARY)
    _write_csv(inventory_path, INVENTORY)
    _write_csv(interactions_path, INTERACTIONS)
    _write_csv(prescriptions_path, PRESCRIPTIONS)
    dataset_reference_path.write_text(
        json.dumps(PUBLIC_DATASET_REFERENCE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "dataset_source": "synthea_rxnorm_dailymed_openfda_style_sample",
        "patients_path": str(patients_path),
        "allergies_path": str(allergies_path),
        "formulary_path": str(formulary_path),
        "inventory_path": str(inventory_path),
        "interactions_path": str(interactions_path),
        "prescriptions_path": str(prescriptions_path),
        "dataset_reference_path": str(dataset_reference_path),
    }
