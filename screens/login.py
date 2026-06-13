"""
Pantalla 1 — Inicio de sesión.
"""

import streamlit as st

from utils.session import autenticar, ir_a


def render() -> None:
    st.markdown('<div class="qi-title">Hola de nuevo 👋</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qi-subtitle">Ingresa para continuar con tu acompañamiento '
        'diario.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="qi-card">', unsafe_allow_html=True)
    correo = st.text_input("Correo electrónico", placeholder="tu@correo.com")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", type="primary", use_container_width=True):
        if not correo or not password:
            st.warning("Completa tu correo y contraseña.")
        else:
            usuario_id = autenticar(correo, password)
            if usuario_id:
                st.session_state["usuario_id"] = usuario_id
                ir_a("dashboard")
            else:
                st.error("Correo o contraseña incorrectos.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center; font-size:13px; color:var(--text-soft);">'
        "¿No tienes cuenta?</div>",
        unsafe_allow_html=True,
    )
    if st.button("Crear una cuenta nueva", use_container_width=True):
        ir_a("registro")
