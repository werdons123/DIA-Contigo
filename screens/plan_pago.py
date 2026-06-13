"""
Pantalla nueva — Plan de Pago (Fase 2.3).

Muestra los planes Gratuito y PRO con diferenciación visual clara. Las
features se leen desde la tabla `planes` (sembrada en database/db.py), así que
el contenido no está hardcodeado en la UI.
"""

import streamlit as st
from sqlalchemy import select

from database.db import get_session
from database.models import Plan
from utils.session import es_usuario_pro, ir_a


def _obtener_planes() -> dict[int, Plan]:
    with get_session() as session:
        planes = session.scalars(select(Plan)).all()
        # Desvinculamos de la sesión para poder leer atributos fuera del with
        return {p.id: Plan(**{c.name: getattr(p, c.name) for c in p.__table__.columns}) for p in planes}


def render() -> None:
    if st.button("← Volver"):
        ir_a("dashboard")

    st.markdown('<div class="qi-title">Elige tu plan Quinu</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qi-subtitle">Cambia de plan cuando quieras.</div>',
        unsafe_allow_html=True,
    )

    planes = _obtener_planes()
    usuario_id = st.session_state["usuario_id"]
    es_pro = es_usuario_pro(usuario_id)

    # --- Tarjeta Gratuito ---
    gratis = planes.get(1)
    st.markdown('<div class="qi-plan-card">', unsafe_allow_html=True)
    st.markdown(f"#### {gratis.nombre}")
    st.markdown('<div class="qi-plan-price">S/ 0 <span style="font-size:13px; '
                'font-weight:400; color:var(--text-soft);">/ siempre</span></div>',
                unsafe_allow_html=True)
    for feature in gratis.features:
        st.markdown(
            f'<div class="qi-plan-feature"><span class="qi-check-grey">✓</span> '
            f'{feature}</div>',
            unsafe_allow_html=True,
        )
    if not es_pro:
        st.markdown(
            '<div style="margin-top:10px; font-size:12.5px; color:var(--text-soft);">'
            "Tu plan actual</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Tarjeta PRO ---
    pro = planes.get(2)
    st.markdown('<div class="qi-plan-card qi-plan-card-pro">', unsafe_allow_html=True)
    st.markdown('<div class="qi-plan-badge">Recomendado</div>', unsafe_allow_html=True)
    st.markdown(f"#### 👑 {pro.nombre}")
    st.markdown(
        f'<div class="qi-plan-price">S/ {pro.precio_mensual:.2f} '
        '<span style="font-size:13px; font-weight:400; color:var(--text-soft);">'
        "/ mes</span></div>",
        unsafe_allow_html=True,
    )
    for feature in pro.features:
        st.markdown(
            f'<div class="qi-plan-feature"><span class="qi-check-green">✓</span> '
            f'{feature}</div>',
            unsafe_allow_html=True,
        )

    if es_pro:
        st.success("Ya tienes el Plan PRO activo. ¡Gracias por tu confianza!")
    else:
        if st.button("Pasar a PRO", type="primary", use_container_width=True):
            ir_a("consentimiento")
        st.markdown(
            '<div style="text-align:center; font-size:12px; color:var(--text-soft); '
            'margin-top:6px;">Cancela cuando quieras desde tu perfil.</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
