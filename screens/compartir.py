"""
Pantalla — Compartir logro.

Al publicar, se crea el post en `posts_comunidad`, se marca el reto como
"compartido" y se generan (Fase 8) los mensajes de motivación sugeridos que
otros usuarios verán en la Comunidad.
"""

from datetime import datetime

import streamlit as st

from components.ui import render_badge
from database.db import get_session
from database.models import ComentarioIA, PostComunidad, RetoUsuario
from services.content_safety import es_seguro
from services.openai_service import generar_mensajes_comunidad
from utils.session import ir_a, obtener_usuario


def render() -> None:
    reto_usuario_id = st.session_state.get("ultimo_reto_usuario_id")
    if not reto_usuario_id:
        ir_a("dashboard")
        return

    with get_session() as session:
        reto_usuario = session.get(RetoUsuario, reto_usuario_id)
        if reto_usuario is None or reto_usuario.estado not in ("completado", "compartido"):
            ir_a("dashboard")
            return
        reto_texto = reto_usuario.reto_personalizado_texto

    usuario = obtener_usuario(st.session_state["usuario_id"])

    if st.button("← Volver"):
        ir_a("dashboard")

    st.markdown('<div class="qi-title">¡Lo lograste! 🎉</div>', unsafe_allow_html=True)
    render_badge(True, reto_texto.get("titulo", "Reto completado"))

    texto_sugerido = (
        f"Hoy completé mi reto: \"{reto_texto.get('titulo', '')}\". "
        "¡Un paso más para sentirme mejor!"
    )

    st.markdown('<div class="qi-card">', unsafe_allow_html=True)
    texto_post = st.text_area("Comparte cómo te sentiste", value=texto_sugerido, height=100)

    if st.button("Publicar en la comunidad", type="primary", use_container_width=True):
        with get_session() as session:
            reto_usuario = session.get(RetoUsuario, reto_usuario_id)
            reto_usuario.estado = "compartido"

            post = PostComunidad(
                usuario_id=usuario.id,
                reto_usuario_id=reto_usuario_id,
                texto=texto_post,
            )
            session.add(post)
            session.flush()

            # Fase 8: generar mensajes de motivación sugeridos para este post
            categoria_reto = "actividad_fisica"
            mensajes = generar_mensajes_comunidad(
                texto_post=texto_post,
                categoria_reto=categoria_reto,
                username=usuario.username_publico,
            )
            for mensaje in mensajes:
                if es_seguro(mensaje):
                    session.add(ComentarioIA(post_id=post.id, texto_generado=mensaje))

        st.session_state["panel_resultado_visible"] = False
        st.success("¡Publicado! Tu comunidad ya puede animarte.")
        ir_a("comunidad")
    st.markdown("</div>", unsafe_allow_html=True)
