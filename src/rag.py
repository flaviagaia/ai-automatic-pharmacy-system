from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple


STOPWORDS = {
    "a",
    "ao",
    "as",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "no",
    "o",
    "os",
    "ou",
    "para",
    "por",
    "que",
    "um",
    "uma",
}


def _read_csv(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _tokenize(text: str) -> List[str]:
    raw_tokens = re.findall(r"[a-záéíóúàâêôãõç0-9]+", text.lower())
    return [token for token in raw_tokens if token not in STOPWORDS and len(token) > 1]


def _build_query_parts(row: Dict[str, object]) -> List[str]:
    parts = [
        str(row["drug_name"]),
        str(row["therapeutic_class"]),
        str(row["decision"]),
        str(row["dailymed_warning_excerpt"]),
    ]
    if str(row["allergy_conflict"]) == "true":
        parts.append("alergia penicilina bloqueio")
    if str(row["age_restriction"]) == "true":
        parts.append("idade mínima pediatria bloqueio")
    if str(row["major_interaction"]) == "true":
        parts.append("interação maior sangramento bloqueio")
    elif str(row["interaction_detected"]) == "true":
        parts.append("interação medicamentosa revisão")
    if str(row["duplicate_therapy"]) == "true":
        parts.append("duplicidade terapêutica estatina revisão")
    if str(row["stock_shortage"]) == "true":
        parts.append("estoque insuficiente reposição demanda")
    if str(row["high_risk_medication"]) == "true":
        parts.append("medicamento alto risco dupla checagem")
    return parts


def _preferred_topics(row: Dict[str, object]) -> List[str]:
    topics: List[str] = []
    if str(row["allergy_conflict"]) == "true":
        topics.append("allergy_safety")
    if str(row["age_restriction"]) == "true":
        topics.append("age_restriction")
    if str(row["major_interaction"]) == "true":
        topics.append("major_interaction")
    elif str(row["interaction_detected"]) == "true":
        topics.append("major_interaction")
    if str(row["duplicate_therapy"]) == "true":
        topics.append("duplicate_therapy")
    if str(row["stock_shortage"]) == "true":
        topics.append("stock_operations")
    if str(row["high_risk_medication"]) == "true":
        topics.append("high_risk")
    if str(row["decision"]) == "AUTO_DISPENSE":
        topics.append("auto_dispense")
    return topics


def retrieve_knowledge(
    row: Dict[str, object],
    knowledge_base_path: str,
    top_k: int = 3,
) -> List[Dict[str, str]]:
    documents = _read_csv(knowledge_base_path)
    query_tokens = set(_tokenize(" ".join(_build_query_parts(row))))
    preferred_topics = set(_preferred_topics(row))
    scored_documents: List[Tuple[int, int, Dict[str, str]]] = []
    for document in documents:
        doc_text = " ".join(
            [
                document["title"],
                document["topic"],
                document["audience"],
                document["content"],
            ]
        )
        doc_tokens = set(_tokenize(doc_text))
        overlap = len(query_tokens & doc_tokens)
        lexical_bonus = 1 if str(row["drug_name"]).split()[0].lower() in doc_text.lower() else 0
        topic_bonus = 4 if document["topic"] in preferred_topics else 0
        audience_bonus = 1 if document["audience"] in {"pharmacist", "inventory", "operations"} else 0
        scored_documents.append((overlap + lexical_bonus + topic_bonus + audience_bonus, len(doc_tokens), document))

    scored_documents.sort(key=lambda item: (-item[0], item[1], item[2]["document_id"]))
    relevant = [document for score, _, document in scored_documents if score > 0]
    return relevant[:top_k]


def build_guidance(
    row: Dict[str, object],
    retrieved_docs: List[Dict[str, str]],
) -> Dict[str, str]:
    main_clinical_reason = str(row["explanation"])
    stock_action = (
        "Acionar reposição ou validar alternativa terapêutica antes da separação."
        if str(row["stock_shortage"]) == "true"
        else "Sem ação imediata de estoque para este item."
    )

    if str(row["decision"]) == "BLOCK":
        action = "Não liberar automaticamente. Encaminhar para intervenção farmacêutica imediata."
    elif str(row["decision"]) == "PHARMACIST_REVIEW":
        action = "Segurar a liberação automática e direcionar para revisão farmacêutica priorizada."
    else:
        action = "Liberar para dispensação automática com rastreabilidade da checagem."

    supporting_titles = ", ".join(document["title"] for document in retrieved_docs[:2]) or "Base local de segurança farmacêutica"
    guidance = (
        f"{action} Motivo principal: {main_clinical_reason} "
        f"Orientação operacional: {stock_action} "
        f"Base consultada: {supporting_titles}."
    )
    return {
        "rag_guidance": guidance,
        "stock_guidance": stock_action,
        "retrieved_titles": " | ".join(document["title"] for document in retrieved_docs),
        "retrieved_document_ids": " | ".join(document["document_id"] for document in retrieved_docs),
    }
