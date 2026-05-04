from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

import streamlit as st

from src.pipeline import run_pipeline

APP_TITLE = "Farmácia Automática com IA"
APP_SUBTITLE = (
    "Teste uma fila de dispensação inteligente que valida alergia, idade, interação medicamentosa, "
    "duplicidade terapêutica e estoque antes de liberar o medicamento."
)


def _read_csv(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _decision_label(decision: str) -> str:
    mapping = {
        "AUTO_DISPENSE": "Dispensação automática",
        "PHARMACIST_REVIEW": "Revisão farmacêutica",
        "BLOCK": "Bloqueada",
    }
    return mapping.get(decision, decision)


def _decision_color(decision: str) -> str:
    mapping = {
        "AUTO_DISPENSE": "#133c2e",
        "PHARMACIST_REVIEW": "#5b3b09",
        "BLOCK": "#5a1f24",
    }
    return mapping.get(decision, "#1f2937")


def _render_status_card(title: str, value: str, decision: str) -> None:
    st.markdown(
        f"""
        <div style="padding:16px;border-radius:14px;background:{_decision_color(decision)};border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:0.9rem;opacity:0.85;">{title}</div>
            <div style="font-size:1.4rem;font-weight:700;margin-top:6px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _load_app_state(base_dir: Path) -> tuple[Dict[str, object], List[Dict[str, str]]]:
    summary = run_pipeline(base_dir)
    queue_rows = _read_csv(str(summary["queue_artifact"]))
    return summary, queue_rows


st.set_page_config(page_title=APP_TITLE, page_icon="💊", layout="wide")

base_dir = Path(__file__).resolve().parent
summary, queue_rows = _load_app_state(base_dir)

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

st.info(
    "Esta demo usa uma base sintética inspirada em Synthea e enriquecimento conceitual de RxNorm, "
    "DailyMed e openFDA para simular a decisão da farmácia antes da dispensação."
)

with st.sidebar:
    st.subheader("Como testar")
    st.caption("1. Veja a fila geral da farmácia.")
    st.caption("2. Filtre o tipo de decisão que quer analisar.")
    st.caption("3. Abra uma prescrição para entender por que ela foi liberada, revisada ou bloqueada.")
    st.divider()
    if st.button("Atualizar simulação", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

left, middle, right, extra = st.columns(4)
with left:
    st.metric("Prescrições", int(summary["prescription_count"]))
with middle:
    st.metric("Bloqueadas", int(summary["blocked_count"]))
with right:
    st.metric("Em revisão", int(summary["pharmacist_review_count"]))
with extra:
    st.metric("Automáticas", int(summary["auto_dispense_count"]))

st.subheader("Fila de dispensação")
decision_filter = st.selectbox(
    "Filtrar por decisão",
    options=["Todas", "Bloqueada", "Revisão farmacêutica", "Dispensação automática"],
    index=0,
)

decision_filter_map = {
    "Todas": None,
    "Bloqueada": "BLOCK",
    "Revisão farmacêutica": "PHARMACIST_REVIEW",
    "Dispensação automática": "AUTO_DISPENSE",
}

filtered_rows = [
    row for row in queue_rows
    if decision_filter_map[decision_filter] is None or row["decision"] == decision_filter_map[decision_filter]
]

table_rows = [
    {
        "Prioridade": row["queue_priority"],
        "Prescrição": row["prescription_id"],
        "Paciente": row["patient_name"],
        "Medicamento": row["drug_name"],
        "Decisão": _decision_label(row["decision"]),
        "Risco": row["risk_score"],
    }
    for row in filtered_rows
]
st.dataframe(table_rows, use_container_width=True, hide_index=True)

if not filtered_rows:
    st.warning("Nenhuma prescrição encontrada para esse filtro.")
    st.stop()

prescription_options = {
    f"{row['prescription_id']} · {row['patient_name']} · {row['drug_name']}": row for row in filtered_rows
}
selected_label = st.selectbox(
    "Escolha uma prescrição para inspecionar",
    options=list(prescription_options.keys()),
)
selected = prescription_options[selected_label]

st.subheader("Decisão do sistema")
card_a, card_b, card_c = st.columns(3)
with card_a:
    _render_status_card("Status", _decision_label(selected["decision"]), selected["decision"])
with card_b:
    _render_status_card("Prioridade da fila", selected["queue_priority"], selected["decision"])
with card_c:
    _render_status_card("Score de risco", selected["risk_score"], selected["decision"])

detail_left, detail_right = st.columns([1.2, 1])
with detail_left:
    st.markdown("**Explicação da decisão**")
    st.write(selected["explanation"])

    st.markdown("**Sinal farmacêutico**")
    st.write(selected["dailymed_warning_excerpt"])

with detail_right:
    st.markdown("**Dados da prescrição**")
    st.write(f"Paciente: `{selected['patient_name']}`")
    st.write(f"Medicamento: `{selected['drug_name']}`")
    st.write(f"RxNorm: `{selected['rxnorm_code']}`")
    st.write(f"Classe terapêutica: `{selected['therapeutic_class']}`")
    st.write(f"Estoque disponível: `{selected['available_units']}`")
    st.write(f"Unidades solicitadas: `{selected['requested_units']}`")
    st.write(f"Sinais openFDA: `{selected['openfda_signal_count']}`")

st.subheader("Checagens aplicadas")
checks = [
    ("Conflito de alergia", selected["allergy_conflict"]),
    ("Restrição etária", selected["age_restriction"]),
    ("Interação detectada", selected["interaction_detected"]),
    ("Interação maior", selected["major_interaction"]),
    ("Duplicidade terapêutica", selected["duplicate_therapy"]),
    ("Estoque insuficiente", selected["stock_shortage"]),
    ("Medicamento de alto risco", selected["high_risk_medication"]),
]

check_rows = [
    {"Regra": rule, "Resultado": "Sim" if value == "true" else "Não"}
    for rule, value in checks
]
st.dataframe(check_rows, use_container_width=True, hide_index=True)
