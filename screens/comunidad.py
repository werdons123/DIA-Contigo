"""
Pantalla 7 — Comunidad.

Feed de posts de la comunidad. Para cada post, se muestran los mensajes de
motivación generados por IA (Fase 8) como botones de un toque: el usuario
presiona uno para enviarlo, lo cual se registra en `interacciones_comunidad`
y marca el `comentarios_ia.fue_usado = True` (métrica de éxito, Fase 8.5).
"""

import streamlit as st
from sqlalchemy import select

from components.ui import render_bottom_nav
from database.db import get_session
from database.models import ComentarioIA, InteraccionComunidad, PostComunidad, Usuario


def _enviar_motivacion(post_id: str, comentario_id: str, usuario_id: str, texto: str) -> None:
    with get_session() as session:
        session.add(
            InteraccionComunidad(
                post_id=post_id,
                usuario_id=usuario_id,
                texto_enviado=texto,
            )
        )
        comentario = session.get(ComentarioIA, comentario_id)
        if comentario:
            comentario.fue_usado = True
    st.toast("¡Mensaje enviado!")


def render() -> None:
    st.markdown('<div class="qi-title">Comunidad</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="qi-subtitle">Personas como tú, dando pequeños pasos cada '
        "día.</div>",
        unsafe_allow_html=True,
    )

    usuario_actual_id = st.session_state["usuario_id"]

    with get_session() as session:
        posts = session.scalars(
            select(PostComunidad).order_by(PostComunidad.fecha.desc()).limit(20)
        ).all()

        for post in posts:
            autor = session.get(Usuario, post.usuario_id)
            comentarios = session.scalars(
                select(ComentarioIA).where(ComentarioIA.post_id == post.id)
            ).all()

            st.markdown('<div class="qi-card">', unsafe_allow_html=True)
            st.markdown(f"**@{autor.username_publico}**")
            st.write(post.texto)

            if comentarios:
                st.caption("Opciones para motivar:")
                cols = st.columns(len(comentarios))
                for col, comentario in zip(cols, comentarios):
                    with col:
                        etiqueta = "✓ Enviado" if comentario.fue_usado else comentario.texto_generado
                        if st.button(
                            etiqueta,
                            key=f"motiv_{comentario.id}",
                            disabled=comentario.fue_usado,
                            use_container_width=True,
                        ):
                            _enviar_motivacion(
                                post.id, comentario.id, usuario_actual_id, comentario.texto_generado
                            )
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if not posts:
            st.info(
                "Todavía no hay publicaciones. ¡Completa un reto y comparte tu "
                "primer logro!"
            )

    render_bottom_nav("comunidad")
