from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List

import streamlit as st

from src.data_factory import build_sample_dataset
from src.pipeline import run_pipeline

APP_TITLE = "Central de Farmácia com IA"
APP_SUBTITLE = (
    "Uma central de apoio para o farmacêutico e o estoque: prioriza prescrições críticas, "
    "explica o risco clínico e mostra quais itens exigem reposição ou atenção operacional."
)


def _read_csv(path: str) -> List[Dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _decision_label(decision: str) -> str:
    return {
        "AUTO_DISPENSE": "Dispensação automática",
        "PHARMACIST_REVIEW": "Revisão farmacêutica",
        "BLOCK": "Bloqueada",
    }.get(decision, decision)


def _priority_label(priority: str) -> str:
    return {
        "P1": "Urgente",
        "P2": "Alta atenção",
        "P3": "Rotina",
    }.get(priority, priority)


def _status_tone(decision: str) -> str:
    return {
        "AUTO_DISPENSE": "success",
        "PHARMACIST_REVIEW": "warning",
        "BLOCK": "error",
    }.get(decision, "info")


def _decision_color(decision: str) -> str:
    return {
        "AUTO_DISPENSE": "#143d2f",
        "PHARMACIST_REVIEW": "#5c4107",
        "BLOCK": "#5d2026",
    }.get(decision, "#1f2937")


def _render_status_card(title: str, value: str, subtitle: str, decision: str) -> None:
    st.markdown(
        f"""
        <div style="padding:18px;border-radius:16px;background:{_decision_color(decision)};border:1px solid rgba(255,255,255,0.08);height:100%;">
            <div style="font-size:0.92rem;opacity:0.80;">{title}</div>
            <div style="font-size:1.45rem;font-weight:700;margin-top:6px;">{value}</div>
            <div style="font-size:0.88rem;opacity:0.82;margin-top:8px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _next_action(row: Dict[str, str]) -> str:
    if row["decision"] == "BLOCK":
        if row["allergy_conflict"] == "true":
            return "Segurar a dispensação e falar com o prescritor por conflito de alergia."
        if row["major_interaction"] == "true":
            return "Segurar a dispensação e revisar a interação medicamentosa antes de liberar."
        if row["age_restriction"] == "true":
            return "Segurar a dispensação e validar a adequação para a faixa etária do paciente."
        return "Segurar a dispensação até revisão farmacêutica completa."
    if row["decision"] == "PHARMACIST_REVIEW":
        if row["stock_shortage"] == "true":
            return "Avaliar alternativa terapêutica ou reposição imediata antes de separar o item."
        if row["duplicate_therapy"] == "true":
            return "Confirmar se houve troca terapêutica ou duplicidade indevida na prescrição."
        if row["interaction_detected"] == "true":
            return "Revisar o contexto clínico da interação antes da liberação."
        return "Encaminhar para revisão farmacêutica antes da dispensação."
    return "Liberar para separação e dispensação automática."


def _risk_reasons(row: Dict[str, str]) -> List[str]:
    reasons: List[str] = []
    if row["allergy_conflict"] == "true":
        reasons.append("Conflito de alergia")
    if row["age_restriction"] == "true":
        reasons.append("Restrição etária")
    if row["major_interaction"] == "true":
        reasons.append("Interação medicamentosa maior")
    elif row["interaction_detected"] == "true":
        reasons.append("Interação medicamentosa detectada")
    if row["duplicate_therapy"] == "true":
        reasons.append("Duplicidade terapêutica")
    if row["stock_shortage"] == "true":
        reasons.append("Estoque insuficiente")
    if row["high_risk_medication"] == "true":
        reasons.append("Medicamento de alto risco")
    return reasons or ["Sem gatilhos críticos"]


def _inventory_status(available_units: int, reorder_point: int) -> str:
    if available_units <= reorder_point:
        return "Repor agora"
    if available_units <= reorder_point * 1.5:
        return "Monitorar"
    return "Estável"


def _inventory_rows(base_dir: Path, queue_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    dataset_info = build_sample_dataset(base_dir)
    inventory = _read_csv(dataset_info["inventory_path"])
    queue_by_drug = {}
    for row in queue_rows:
        queue_by_drug.setdefault(row["drug_name"], []).append(row)

    enriched_rows: List[Dict[str, str]] = []
    for item in inventory:
        available = int(item["available_units"])
        reorder_point = int(item["reorder_point"])
        related_rows = queue_by_drug.get(item["drug_name"], [])
        pending_units = sum(int(row["requested_units"]) for row in related_rows)
        blocked_or_review = sum(
            1 for row in related_rows if row["decision"] in {"BLOCK", "PHARMACIST_REVIEW"}
        )
        enriched_rows.append(
            {
                "drug_name": item["drug_name"],
                "available_units": str(available),
                "reorder_point": str(reorder_point),
                "pending_units": str(pending_units),
                "review_or_block_count": str(blocked_or_review),
                "status": _inventory_status(available, reorder_point),
            }
        )
    return sorted(
        enriched_rows,
        key=lambda row: (
            {"Repor agora": 0, "Monitorar": 1, "Estável": 2}[row["status"]],
            int(row["available_units"]),
        ),
    )


def _load_app_state(base_dir: Path) -> tuple[Dict[str, object], List[Dict[str, str]], List[Dict[str, str]]]:
    summary = run_pipeline(base_dir)
    queue_rows = _read_csv(str(summary["queue_artifact"]))
    inventory_rows = _inventory_rows(base_dir, queue_rows)
    return summary, queue_rows, inventory_rows


st.set_page_config(page_title=APP_TITLE, page_icon="💊", layout="wide")

base_dir = Path(__file__).resolve().parent
summary, queue_rows, inventory_rows = _load_app_state(base_dir)

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

st.info(
    "Esta demo foi desenhada para duas rotinas reais da farmácia: "
    "**priorização clínica da fila** e **gestão de estoque antes da dispensação**."
)

with st.sidebar:
    st.subheader("Como usar")
    st.caption("1. Comece pela aba de triagem para ver o que exige ação imediata.")
    st.caption("2. Abra uma prescrição para entender o motivo clínico da decisão.")
    st.caption("3. Use a aba de estoque para identificar itens que travam a operação.")
    st.divider()
    if st.button("Atualizar painel", type="primary", use_container_width=True):
        st.rerun()

metric_a, metric_b, metric_c, metric_d = st.columns(4)
with metric_a:
    st.metric("Prescrições na fila", int(summary["prescription_count"]))
with metric_b:
    st.metric("Bloqueios clínicos", int(summary["blocked_count"]))
with metric_c:
    st.metric("Revisões farmacêuticas", int(summary["pharmacist_review_count"]))
with metric_d:
    st.metric("Dispensações automáticas", int(summary["auto_dispense_count"]))

tabs = st.tabs(["Triagem farmacêutica", "Estoque e reposição", "Resumo operacional"])

with tabs[0]:
    st.subheader("Fila clínica priorizada")
    decision_filter = st.selectbox(
        "Filtrar por tipo de decisão",
        options=["Todas", "Bloqueada", "Revisão farmacêutica", "Dispensação automática"],
        index=0,
        key="decision_filter",
    )
    decision_filter_map = {
        "Todas": None,
        "Bloqueada": "BLOCK",
        "Revisão farmacêutica": "PHARMACIST_REVIEW",
        "Dispensação automática": "AUTO_DISPENSE",
    }
    filtered_rows = [
        row
        for row in queue_rows
        if decision_filter_map[decision_filter] is None
        or row["decision"] == decision_filter_map[decision_filter]
    ]

    table_rows = [
        {
            "Prioridade": _priority_label(row["queue_priority"]),
            "Prescrição": row["prescription_id"],
            "Paciente": row["patient_name"],
            "Medicamento": row["drug_name"],
            "Decisão": _decision_label(row["decision"]),
            "Score de risco": row["risk_score"],
            "Próxima ação": _next_action(row),
        }
        for row in filtered_rows
    ]
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    if not filtered_rows:
        st.warning("Nenhuma prescrição encontrada para esse filtro.")
    else:
        prescription_options = {
            f"{row['prescription_id']} · {row['patient_name']} · {row['drug_name']}": row
            for row in filtered_rows
        }
        selected_label = st.selectbox(
            "Escolha uma prescrição para análise detalhada",
            options=list(prescription_options.keys()),
            key="prescription_detail",
        )
        selected = prescription_options[selected_label]

        card_a, card_b, card_c = st.columns(3)
        with card_a:
            _render_status_card(
                "Status da prescrição",
                _decision_label(selected["decision"]),
                _next_action(selected),
                selected["decision"],
            )
        with card_b:
            _render_status_card(
                "Prioridade na fila",
                _priority_label(selected["queue_priority"]),
                f"Score de risco {selected['risk_score']}",
                selected["decision"],
            )
        with card_c:
            _render_status_card(
                "Paciente / item",
                selected["patient_name"],
                selected["drug_name"],
                selected["decision"],
            )

        message_fn = getattr(st, _status_tone(selected["decision"]), st.info)
        message_fn(_next_action(selected))

        left_col, right_col = st.columns([1.3, 1])
        with left_col:
            st.markdown("**Orientação pronta para ação**")
            st.write(selected["rag_guidance"])

            st.markdown("**Motivo clínico resumido**")
            st.write(selected["explanation"])

            st.markdown("**Principais gatilhos encontrados**")
            for reason in _risk_reasons(selected):
                st.caption(f"• {reason}")

            st.markdown("**Warning farmacêutico associado**")
            st.write(selected["dailymed_warning_excerpt"])

        with right_col:
            st.markdown("**Dados úteis para o farmacêutico**")
            st.write(f"Paciente: `{selected['patient_name']}`")
            st.write(f"Medicamento: `{selected['drug_name']}`")
            st.write(f"RxNorm: `{selected['rxnorm_code']}`")
            st.write(f"Classe terapêutica: `{selected['therapeutic_class']}`")
            st.write(f"Estoque disponível: `{selected['available_units']}`")
            st.write(f"Unidades solicitadas: `{selected['requested_units']}`")
            st.write(f"Sinais openFDA: `{selected['openfda_signal_count']}`")
            st.write(f"Orientação de estoque: `{selected['stock_guidance']}`")
            st.write(f"Base documental usada: `{selected['retrieved_titles']}`")

        checks = [
            ("Conflito de alergia", selected["allergy_conflict"]),
            ("Restrição etária", selected["age_restriction"]),
            ("Interação detectada", selected["interaction_detected"]),
            ("Interação maior", selected["major_interaction"]),
            ("Duplicidade terapêutica", selected["duplicate_therapy"]),
            ("Estoque insuficiente", selected["stock_shortage"]),
            ("Medicamento de alto risco", selected["high_risk_medication"]),
        ]
        st.markdown("**Checagens aplicadas**")
        st.dataframe(
            [{"Regra": rule, "Resultado": "Sim" if value == "true" else "Não"} for rule, value in checks],
            use_container_width=True,
            hide_index=True,
        )

with tabs[1]:
    st.subheader("Estoque e reposição")
    shortage_count = sum(1 for row in inventory_rows if row["status"] == "Repor agora")
    monitor_count = sum(1 for row in inventory_rows if row["status"] == "Monitorar")
    stock_a, stock_b, stock_c = st.columns(3)
    with stock_a:
        st.metric("Itens para repor agora", shortage_count)
    with stock_b:
        st.metric("Itens em monitoramento", monitor_count)
    with stock_c:
        st.metric("Itens estáveis", len(inventory_rows) - shortage_count - monitor_count)

    stock_rows = [
        {
            "Medicamento": row["drug_name"],
            "Status": row["status"],
            "Estoque atual": row["available_units"],
            "Ponto de reposição": row["reorder_point"],
            "Demanda pendente": row["pending_units"],
            "Prescrições travadas/em revisão": row["review_or_block_count"],
        }
        for row in inventory_rows
    ]
    st.dataframe(stock_rows, use_container_width=True, hide_index=True)

    critical_inventory = [row for row in inventory_rows if row["status"] == "Repor agora"]
    if critical_inventory:
        st.warning("Há itens com necessidade imediata de reposição para evitar ruptura na dispensação.")
        for row in critical_inventory:
            st.caption(
                f"• {row['drug_name']}: estoque atual {row['available_units']} para ponto de reposição {row['reorder_point']}."
            )
    else:
        st.success("Nenhum item está abaixo do ponto de reposição neste cenário.")

with tabs[2]:
    st.subheader("Resumo operacional")
    reason_counter = Counter()
    for row in queue_rows:
        for reason in _risk_reasons(row):
            reason_counter[reason] += 1

    summary_left, summary_right = st.columns(2)
    with summary_left:
        st.markdown("**Principais motivos que geram trabalho farmacêutico**")
        summary_rows = [
            {"Motivo": reason, "Ocorrências": count}
            for reason, count in reason_counter.most_common()
        ]
        st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    with summary_right:
        st.markdown("**Leitura rápida da operação**")
        st.write(
            "O sistema foi pensado para reduzir triagem manual simples, puxando para o farmacêutico "
            "apenas os casos que realmente merecem análise clínica ou decisão operacional."
        )
        st.write(
            "Na prática, o ganho aparece em duas frentes: menos tempo gasto em prescrições seguras "
            "e mais visibilidade sobre itens que travam a dispensação por risco ou estoque."
        )
        st.write(
            "Além das regras, a fila agora consulta uma base documental local para devolver orientação "
            "mais acionável ao farmacêutico e ao time de estoque."
        )
