"""
Pantalla 4 — Formulario de salud.

En el flujo rediseñado (Fase 2), este formulario ya no es parte del onboarding
obligatorio: es el segundo paso para activar el Plan PRO (después de la
pantalla de consentimiento). Al guardar, se activa la suscripción PRO y estos
datos quedan disponibles para el motor de bienestar (Fase 6).
"""

from datetime import datetime

import streamlit as st
from sqlalchemy import select

from database.db import get_session
from database.models import FormularioSalud
from services.peru_knowledge import CONTEXTO_PERUANO
from utils.session import activar_plan_pro, ir_a

OPCIONES_ALIMENTOS = (
    CONTEXTO_PERUANO["alimentos_andinos"]
    + CONTEXTO_PERUANO["proteinas_locales"]
    + CONTEXTO_PERUANO["platos_tradicionales"]
)

OPCIONES_ACTIVIDADES = CONTEXTO_PERUANO["actividad_fisica_y_baile"]


def render() -> None:
    if not st.session_state.get("consentimiento_pendiente"):
        ir_a("plan_pago")
        return

    st.markdown(
        '<div class="qi-title">Cuéntanos un poco más</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="qi-subtitle">Esta información solo se usa para '
        "personalizar tus recomendaciones — puedes editarla luego desde tu "
        "perfil.</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="qi-card">', unsafe_allow_html=True)

    tiempo_diagnostico = st.selectbox(
        "¿Hace cuánto te diagnosticaron diabetes tipo 2?",
        options=["reciente", "1-5_anios", "mas_5_anios"],
        format_func=lambda v: {
            "reciente": "Hace poco (menos de 1 año)",
            "1-5_anios": "Entre 1 y 5 años",
            "mas_5_anios": "Más de 5 años",
        }[v],
    )

    estilo_alimentacion = st.selectbox(
        "¿Cómo describirías tu alimentación habitual?",
        options=["casera", "delivery", "dieta_estricta"],
        format_func=lambda v: {
            "casera": "Mayormente comida casera",
            "delivery": "Suelo comer fuera / pedir delivery",
            "dieta_estricta": "Sigo una dieta indicada por mi médico/nutricionista",
        }[v],
    )

    preferencias_alimentos = st.multiselect(
        "¿Qué alimentos disfrutas o consumes seguido?",
        options=OPCIONES_ALIMENTOS,
    )

    nivel_actividad = st.selectbox(
        "¿Cómo describirías tu nivel de actividad física?",
        options=["sedentario", "ligero", "activo"],
        format_func=lambda v: {
            "sedentario": "Sedentario (poco movimiento durante el día)",
            "ligero": "Ligero (camino o me muevo de forma ocasional)",
            "activo": "Activo (ejercicio o actividad física regular)",
        }[v],
    )

    actividades_preferidas = st.multiselect(
        "¿Qué actividades te gustaría incluir en tus retos?",
        options=OPCIONES_ACTIVIDADES,
    )

    objetivos_texto = st.text_area(
        "¿Cuál es tu principal objetivo? (ej. 'sentirme con más energía', "
        "'mejorar mi alimentación en el trabajo')"
    )

    restricciones_texto = st.text_input(
        "¿Tienes alergias o alimentos que debamos evitar recomendarte? "
        "(separados por comas)"
    )

    if st.button("Guardar y activar Plan PRO", type="primary", use_container_width=True):
        usuario_id = st.session_state["usuario_id"]
        restricciones = [r.strip() for r in restricciones_texto.split(",") if r.strip()]

        with get_session() as session:
            existente = session.scalar(
                select(FormularioSalud).where(FormularioSalud.usuario_id == usuario_id)
            )
            if existente is None:
                existente = FormularioSalud(usuario_id=usuario_id)
                session.add(existente)

            existente.tiempo_diagnostico = tiempo_diagnostico
            existente.estilo_alimentacion = estilo_alimentacion
            existente.preferencias_alimentos = preferencias_alimentos
            existente.nivel_actividad = nivel_actividad
            existente.actividades_preferidas = actividades_preferidas
            existente.objetivos = [objetivos_texto] if objetivos_texto else []
            existente.restricciones = restricciones
            existente.consentimiento_datos_salud = True
            existente.consentimiento_fecha = datetime.utcnow()

        activar_plan_pro(usuario_id)
        st.session_state["consentimiento_pendiente"] = False
        st.success("¡Listo! Tu Plan PRO ya está activo.")
        ir_a("dashboard")

    st.markdown("</div>", unsafe_allow_html=True)
