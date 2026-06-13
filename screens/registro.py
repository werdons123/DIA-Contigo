"""
Pantalla 2 — Registro.

Tras un registro exitoso, el flujo va DIRECTO al Dashboard (Fase 2.1 — la
pantalla "Personalización" queda eliminada del onboarding).
"""

import random

import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.db import get_session
from database.models import Usuario
from utils.session import crear_usuario, ir_a


def _username_disponible(username: str) -> bool:
    with get_session() as session:
        existente = session.scalar(
            select(Usuario).where(Usuario.username_publico == username)
        )
    return existente is None


def _sugerir_username() -> str:
    for _ in range(10):
        candidato = f"User{random.randint(100, 999)}"
        if _username_disponible(candidato):
            return candidato
    return f"User{random.randint(1000, 9999)}"


def render() -> None:
    st.markdown('<div class="qi-title">Creemos tu cuenta</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qi-subtitle">Solo lo esencial — en un par de pasos ya '
        'puedes ver tu primer análisis.</div>',
        unsafe_allow_html=True,
    )

    if "username_sugerido" not in st.session_state:
        st.session_state["username_sugerido"] = _sugerir_username()

    st.markdown('<div class="qi-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
    with col2:
        apellido = st.text_input("Apellido")

    correo = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    st.caption(
        "Tu nombre de usuario público para la comunidad será **"
        f"@{st.session_state['username_sugerido']}**. Así protegemos tu "
        "privacidad — nadie verá tu nombre real."
    )

    if st.button("Crear cuenta", type="primary", use_container_width=True):
        if not all([nombre, apellido, correo, password]):
            st.warning("Completa todos los campos.")
        else:
            try:
                usuario_id = crear_usuario(
                    nombre=nombre,
                    apellido=apellido,
                    correo=correo,
                    password=password,
                    username_publico=st.session_state["username_sugerido"],
                )
                st.session_state["usuario_id"] = usuario_id
                ir_a("dashboard")
            except IntegrityError:
                st.error("Ya existe una cuenta con ese correo.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Ya tengo una cuenta", use_container_width=True):
        ir_a("login")
