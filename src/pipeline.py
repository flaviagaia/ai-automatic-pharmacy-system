from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from .data_factory import build_sample_dataset


def _read_csv(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _build_interaction_index(rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], Dict[str, str]]:
    index: Dict[Tuple[str, str], Dict[str, str]] = {}
    for row in rows:
        key = tuple(sorted((row["drug_a"], row["drug_b"])))
        index[key] = row
    return index


def _queue_priority(decision: str, risk_score: int, clinical_priority: str) -> str:
    if decision == "BLOCK":
        return "P1"
    if clinical_priority == "high" or risk_score >= 60:
        return "P2"
    return "P3"


def _decision_from_flags(flags: Dict[str, bool], has_stock_shortage: bool, high_risk: bool) -> str:
    if flags["allergy_conflict"] or flags["age_restriction"] or flags["major_interaction"]:
        return "BLOCK"
    if flags["interaction_detected"] or flags["duplicate_therapy"] or has_stock_shortage or high_risk:
        return "PHARMACIST_REVIEW"
    return "AUTO_DISPENSE"


def _explanation_from_flags(
    prescription: Dict[str, str],
    patient: Dict[str, str],
    formulary: Dict[str, str],
    flags: Dict[str, bool],
    stock_shortage: bool,
    interaction_detail: str,
) -> str:
    messages: List[str] = []
    if flags["allergy_conflict"]:
        messages.append(
            f"{patient['name']} tem alergia compatível com o grupo {formulary['allergy_group']}."
        )
    if flags["age_restriction"]:
        messages.append(
            f"{patient['name']} tem {patient['age']} anos e o medicamento exige idade mínima de {formulary['min_age']}."
        )
    if flags["major_interaction"]:
        messages.append(f"Interação maior identificada: {interaction_detail}.")
    elif flags["interaction_detected"]:
        messages.append(f"Interação medicamentosa detectada e enviada para revisão: {interaction_detail}.")
    if flags["duplicate_therapy"]:
        messages.append(
            f"Duplicidade terapêutica detectada na classe {formulary['therapeutic_class']}."
        )
    if stock_shortage:
        messages.append("Estoque insuficiente para dispensação imediata.")
    if not messages:
        messages.append("Prescrição dentro das regras automáticas de segurança e estoque.")
    return " ".join(messages)


def run_pipeline(base_dir: Path) -> Dict[str, object]:
    dataset_info = build_sample_dataset(base_dir)

    patients = _read_csv(dataset_info["patients_path"])
    allergies = _read_csv(dataset_info["allergies_path"])
    formulary_rows = _read_csv(dataset_info["formulary_path"])
    inventory_rows = _read_csv(dataset_info["inventory_path"])
    interaction_rows = _read_csv(dataset_info["interactions_path"])
    prescriptions = _read_csv(dataset_info["prescriptions_path"])

    patient_map = {row["patient_id"]: row for row in patients}
    allergy_map = {row["patient_id"]: row["allergen"] for row in allergies}
    formulary_map = {row["drug_name"]: row for row in formulary_rows}
    inventory_map = {row["drug_name"]: row for row in inventory_rows}
    interaction_map = _build_interaction_index(interaction_rows)

    active_classes_by_patient: Dict[str, List[str]] = defaultdict(list)
    active_ingredients_by_patient: Dict[str, List[str]] = defaultdict(list)
    for prescription in prescriptions:
        if prescription["is_active"] != "yes":
            continue
        drug = formulary_map[prescription["drug_name"]]
        active_classes_by_patient[prescription["patient_id"]].append(drug["therapeutic_class"])
        active_ingredients_by_patient[prescription["patient_id"]].append(drug["active_ingredient"])

    evaluated_rows: List[Dict[str, object]] = []
    decision_counter: Counter[str] = Counter()
    blocked_prescriptions: List[str] = []
    pharmacist_review_prescriptions: List[str] = []

    for prescription in prescriptions:
        patient = patient_map[prescription["patient_id"]]
        drug = formulary_map[prescription["drug_name"]]
        inventory = inventory_map[prescription["drug_name"]]

        patient_age = int(patient["age"])
        quantity = int(prescription["quantity"])
        refill_number = int(prescription["refill_number"])
        available_units = int(inventory["available_units"])
        allergy_conflict = allergy_map[prescription["patient_id"]] == drug["allergy_group"] and drug["allergy_group"] != "none"
        age_restriction = patient_age < int(drug["min_age"])
        duplicate_therapy = active_classes_by_patient[prescription["patient_id"]].count(drug["therapeutic_class"]) > 1

        interaction_detail = ""
        interaction_detected = False
        major_interaction = False
        for ingredient in active_ingredients_by_patient[prescription["patient_id"]]:
            if ingredient == drug["active_ingredient"]:
                continue
            interaction = interaction_map.get(tuple(sorted((ingredient, drug["active_ingredient"]))))
            if interaction:
                interaction_detected = True
                interaction_detail = interaction["mechanism"]
                if interaction["severity"] == "major" and refill_number == 0:
                    major_interaction = True
                break

        stock_shortage = available_units < quantity
        high_risk = drug["high_risk"] == "yes"

        flags = {
            "allergy_conflict": allergy_conflict,
            "age_restriction": age_restriction,
            "interaction_detected": interaction_detected,
            "major_interaction": major_interaction,
            "duplicate_therapy": duplicate_therapy,
        }

        risk_score = 0
        risk_score += 100 if allergy_conflict else 0
        risk_score += 90 if major_interaction else 0
        risk_score += 70 if age_restriction else 0
        risk_score += 50 if duplicate_therapy else 0
        risk_score += 25 if stock_shortage else 0
        risk_score += 15 if high_risk else 0
        risk_score += min(refill_number * 5, 10)

        decision = _decision_from_flags(flags, stock_shortage, high_risk)
        priority = _queue_priority(decision, risk_score, prescription["clinical_priority"])
        explanation = _explanation_from_flags(
            prescription=prescription,
            patient=patient,
            formulary=drug,
            flags=flags,
            stock_shortage=stock_shortage,
            interaction_detail=interaction_detail,
        )

        evaluated = {
            "prescription_id": prescription["prescription_id"],
            "patient_id": prescription["patient_id"],
            "patient_name": patient["name"],
            "drug_name": prescription["drug_name"],
            "rxnorm_code": drug["rxnorm_code"],
            "therapeutic_class": drug["therapeutic_class"],
            "decision": decision,
            "queue_priority": priority,
            "risk_score": risk_score,
            "allergy_conflict": str(allergy_conflict).lower(),
            "age_restriction": str(age_restriction).lower(),
            "major_interaction": str(major_interaction).lower(),
            "duplicate_therapy": str(duplicate_therapy).lower(),
            "stock_shortage": str(stock_shortage).lower(),
            "high_risk_medication": str(high_risk).lower(),
            "available_units": available_units,
            "requested_units": quantity,
            "dailymed_warning_excerpt": drug["dailymed_warning_excerpt"],
            "openfda_signal_count": int(drug["openfda_signal_count"]),
            "explanation": explanation,
        }
        evaluated_rows.append(evaluated)
        decision_counter[decision] += 1
        if decision == "BLOCK":
            blocked_prescriptions.append(prescription["prescription_id"])
        elif decision == "PHARMACIST_REVIEW":
            pharmacist_review_prescriptions.append(prescription["prescription_id"])

    decision_rank = {"P1": 0, "P2": 1, "P3": 2}
    evaluated_rows.sort(key=lambda row: (decision_rank[str(row["queue_priority"])], -int(row["risk_score"])))

    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    queue_path = processed_dir / "dispense_queue.csv"
    report_path = processed_dir / "automatic_pharmacy_report.json"

    with queue_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(evaluated_rows[0].keys()))
        writer.writeheader()
        writer.writerows(evaluated_rows)

    summary = {
        "dataset_source": dataset_info["dataset_source"],
        "patient_count": len(patients),
        "prescription_count": len(prescriptions),
        "blocked_count": decision_counter["BLOCK"],
        "pharmacist_review_count": decision_counter["PHARMACIST_REVIEW"],
        "auto_dispense_count": decision_counter["AUTO_DISPENSE"],
        "blocked_prescriptions": blocked_prescriptions,
        "pharmacist_review_prescriptions": pharmacist_review_prescriptions,
        "top_priority_prescription": evaluated_rows[0]["prescription_id"],
        "top_priority_decision": evaluated_rows[0]["decision"],
        "report_artifact": str(report_path),
        "queue_artifact": str(queue_path),
    }
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
