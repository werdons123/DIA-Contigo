"""
Pantalla — Consentimiento de datos de salud (Plan PRO).

Requerida por la Sección 16 de las bases del Desafío (consentimiento explícito
sobre datos sensibles) y documentada en docs/05_usuario_premium.md (sección
6.4). Sin aceptar este consentimiento, el formulario de salud no se activa y
la IA no recibe el contexto premium (Fase 6.2).
"""

import streamlit as st

from utils.session import ir_a


def render() -> None:
    if st.button("← Volver"):
        ir_a("plan_pago")

    st.markdown(
        '<div class="qi-title">Antes de continuar</div>', unsafe_allow_html=True
    )
    st.markdown('<div class="qi-card-blue">', unsafe_allow_html=True)
    st.markdown(
        "Si activas el **Plan PRO**, Quinu-IA también usará tus respuestas del "
        "formulario de salud (cuándo fuiste diagnosticado, cómo comes "
        "normalmente, tu actividad física y tus preferencias) junto con tu "
        "historial de los últimos 30 días para darte recomendaciones más "
        "precisas.\n\n"
        "- Tus datos de salud se almacenan de forma separada y cifrada.\n"
        "- Nunca se comparten con otros usuarios ni se muestran en la "
        "comunidad.\n"
        "- Puedes desactivar esto en cualquier momento desde tu perfil."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    acepto = st.checkbox(
        "He leído y acepto que Quinu-IA use mis datos de salud para "
        "personalizar mis recomendaciones."
    )

    if st.button("Aceptar y continuar", type="primary", use_container_width=True, disabled=not acepto):
        st.session_state["consentimiento_pendiente"] = True
        ir_a("formulario_salud")
