"""
Pantalla 5 — Dashboard.

Es el centro de la aplicación: sube una foto de comida, registra ánimo y sueño,
y ejecuta el pipeline completo de IA (Fase 3 → Fase 4, con contexto premium si
aplica — Fase 6). También aloja el nuevo enlace hacia "Plan de Pago" (Fase 2.2).
"""

from datetime import datetime

import streamlit as st
from sqlalchemy import select

import config
from components.ui import render_badge, render_balance_ring, render_bottom_nav
from database.db import get_session
from database.models import (
    AnalisisNutricional,
    FeedbackUsuario,
    RegistroAnimo,
    RegistroSueno,
    ResultadoIABienestar,
    RetoUsuario,
)
from services.longitudinal import construir_resumen_longitudinal
from services.openai_service import analizar_nutricion, generar_insight_bienestar
from services.storage_service import guardar_imagen
from services.vision_service import analizar_imagen
from utils.session import (
    cerrar_sesion,
    es_usuario_pro,
    ir_a,
    obtener_formulario_salud,
    obtener_usuario,
)

ANIMOS = {"triste": "😔", "neutral": "😐", "bien": "🙂", "feliz": "😄"}
SUENOS = {"mal_dormido": "😴 Mal dormido", "regular": "😑 Regular", "descansado": "😊 Descansado"}


def _perfil_pro_dict(usuario_id: str) -> dict | None:
    formulario = obtener_formulario_salud(usuario_id)
    if not formulario or not formulario.consentimiento_datos_salud:
        return None
    return {
        "tiempo_diagnostico": formulario.tiempo_diagnostico,
        "estilo_alimentacion": formulario.estilo_alimentacion,
        "preferencias_alimentos": formulario.preferencias_alimentos,
        "nivel_actividad": formulario.nivel_actividad,
        "actividades_preferidas": formulario.actividades_preferidas,
        "objetivos": formulario.objetivos,
        "restricciones": formulario.restricciones,
    }


def _ejecutar_pipeline_ia(usuario_id: str, imagen_bytes: bytes, animo: str, sueno: str) -> None:
    with st.spinner("Descubriendo tu balance y análisis metabólico..."):
        resultado_vision = analizar_imagen(imagen_bytes)
        resultado_nutricional = analizar_nutricion(imagen_bytes, resultado_vision)
        imagen_url = guardar_imagen(imagen_bytes, usuario_id)

        es_pro = es_usuario_pro(usuario_id)
        perfil_pro = _perfil_pro_dict(usuario_id) if es_pro else None
        resumen_longitudinal = (
            construir_resumen_longitudinal(usuario_id) if perfil_pro else None
        )

        insight = generar_insight_bienestar(
            resultado_nutricional=resultado_nutricional,
            animo=animo,
            sueno=sueno,
            perfil_pro=perfil_pro,
            resumen_longitudinal=resumen_longitudinal,
        )

        with get_session() as session:
            registro_animo = RegistroAnimo(usuario_id=usuario_id, valor=animo)
            registro_sueno = RegistroSueno(usuario_id=usuario_id, valor=sueno)
            session.add_all([registro_animo, registro_sueno])
            session.flush()

            analisis = AnalisisNutricional(
                usuario_id=usuario_id,
                imagen_url=imagen_url,
                resultado_vision=resultado_vision,
                resultado_nutricional=resultado_nutricional,
            )
            session.add(analisis)
            session.flush()

            resultado_ia = ResultadoIABienestar(
                analisis_nutricional_id=analisis.id,
                registro_animo_id=registro_animo.id,
                registro_sueno_id=registro_sueno.id,
                resultado=insight,
                usado_contexto_premium=perfil_pro is not None,
            )
            session.add(resultado_ia)
            session.flush()

            reto_usuario = RetoUsuario(
                usuario_id=usuario_id,
                reto_personalizado_texto=insight["reto_personalizado"],
                resultado_ia_bienestar_id=resultado_ia.id,
                estado="pendiente",
            )
            session.add(reto_usuario)
            session.flush()

            st.session_state["ultimo_insight"] = insight
            st.session_state["ultimo_analisis_id"] = analisis.id
            st.session_state["ultimo_resultado_ia_id"] = resultado_ia.id
            st.session_state["ultimo_reto_usuario_id"] = reto_usuario.id
            st.session_state["ultimo_calidad"] = resultado_nutricional["calidad_alimentaria"]
            st.session_state["panel_resultado_visible"] = True


def _marcar_reto_completado() -> None:
    reto_usuario_id = st.session_state.get("ultimo_reto_usuario_id")
    if not reto_usuario_id:
        return
    with get_session() as session:
        reto = session.get(RetoUsuario, reto_usuario_id)
        if reto and reto.estado == "pendiente":
            reto.estado = "completado"
            reto.fecha_completado = datetime.utcnow()
            reto.medalla_desbloqueada = True


def _registrar_feedback(util: bool) -> None:
    resultado_ia_id = st.session_state.get("ultimo_resultado_ia_id")
    if not resultado_ia_id:
        return
    with get_session() as session:
        session.add(
            FeedbackUsuario(
                usuario_id=st.session_state["usuario_id"],
                resultado_ia_bienestar_id=resultado_ia_id,
                util=util,
            )
        )
    st.toast("¡Gracias por tu respuesta!")


def render() -> None:
    usuario_id = st.session_state["usuario_id"]
    usuario = obtener_usuario(usuario_id)
    es_pro = es_usuario_pro(usuario_id)

    # --- Header ---
    col_titulo, col_perfil = st.columns([4, 1])
    with col_titulo:
        st.markdown(
            f'<div class="qi-title">Hola, {usuario.nombre} 👋</div>',
            unsafe_allow_html=True,
        )
    with col_perfil:
        with st.popover("👤"):
            st.markdown(f"**@{usuario.username_publico}**")
            st.caption(f"Plan actual: {'PRO 👑' if es_pro else 'Gratuito'}")
            if not es_pro:
                if st.button("Conocer planes", use_container_width=True):
                    ir_a("plan_pago")
            else:
                if st.button("Editar formulario de salud", use_container_width=True):
                    st.session_state["consentimiento_pendiente"] = True
                    ir_a("formulario_salud")
            if st.button("Cerrar sesión", use_container_width=True):
                cerrar_sesion()

    # --- Banner de plan / link a Plan de Pago (Fase 2.2) ---
    if es_pro:
        st.markdown(
            '<div class="qi-plan-activo">✓ Plan PRO activo · IA personalizada '
            "activada</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="qi-banner-yellow">¡Queremos conocerte más! Tu IA '
            "puede ser mucho más precisa si nos cuentas un poco sobre ti."
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Conoce nuestros planes y desbloquea recomendaciones más "
            "personalizadas.",
            key="link_plan_pago",
        ):
            ir_a("plan_pago")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # --- Captura de datos del día ---
    st.markdown('<div class="qi-card">', unsafe_allow_html=True)
    st.markdown("**¿Qué vas a comer hoy?**")
    foto = st.file_uploader(
        "Sube una foto de tu plato o menú", type=["jpg", "jpeg", "png"]
    )

    st.markdown("**¿Cómo te sientes hoy?**")
    animo = st.radio(
        "Ánimo",
        options=list(ANIMOS.keys()),
        format_func=lambda v: f"{ANIMOS[v]} {v.capitalize()}",
        horizontal=True,
        label_visibility="collapsed",
        key="animo_radio",
    )

    st.markdown("**¿Cómo dormiste?**")
    sueno = st.radio(
        "Sueño",
        options=list(SUENOS.keys()),
        format_func=lambda v: SUENOS[v],
        horizontal=True,
        label_visibility="collapsed",
        key="sueno_radio",
    )

    puede_analizar = foto is not None
    if st.button(
        "Descubrir mi balance y análisis metabólico",
        type="primary",
        use_container_width=True,
        disabled=not puede_analizar,
    ):
        _ejecutar_pipeline_ia(usuario_id, foto.getvalue(), animo, sueno)
        st.rerun()

    if not puede_analizar:
        st.caption("Sube una foto de tu plato para continuar.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Panel de resultados ---
    if st.session_state.get("panel_resultado_visible") and st.session_state.get(
        "ultimo_insight"
    ):
        _render_panel_resultado()

    render_bottom_nav("dashboard")


def _render_panel_resultado() -> None:
    insight = st.session_state["ultimo_insight"]
    calidad = st.session_state.get("ultimo_calidad", {"puntaje": 5, "etiqueta": "Moderada"})

    st.markdown('<div class="qi-card-green">', unsafe_allow_html=True)
    st.markdown("### Tu balance de hoy")
    render_balance_ring(calidad["puntaje"], calidad["etiqueta"])
    st.markdown(f"**{insight['nivel_de_bienestar']}**")
    st.write(insight["resumen"])
    st.markdown(
        f'<div class="qi-banner-yellow">{config.DISCLAIMER_NUTRICIONAL} '
        f"{insight['disclaimer']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Reto del día ---
    reto = insight["reto_personalizado"]
    st.markdown('<div class="qi-card-blue">', unsafe_allow_html=True)
    st.markdown(f"### 🎯 Reto sugerido por IA")
    st.markdown(f"**{reto['titulo']}**")
    st.write(reto["descripcion"])

    with get_session() as session:
        reto_usuario = session.get(RetoUsuario, st.session_state["ultimo_reto_usuario_id"])
        completado = reto_usuario.estado in ("completado", "compartido")
        ya_compartido = reto_usuario.estado == "compartido"

    render_badge(completado, reto["titulo"])

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(
            "Marcar como completado",
            use_container_width=True,
            disabled=completado,
            key="btn_completar_reto",
        ):
            _marcar_reto_completado()
            st.rerun()
    with col_b:
        if st.button(
            "Compartir mi progreso",
            use_container_width=True,
            disabled=not completado or ya_compartido,
            type="primary" if completado and not ya_compartido else "secondary",
            key="btn_compartir",
        ):
            ir_a("compartir")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Detalle expandible ---
    with st.expander("Ver más detalles del análisis"):
        if insight["factores_detectados"]:
            st.markdown("**Lo que detectamos hoy:**")
            for f in insight["factores_detectados"]:
                st.markdown(f"- {f}")
        if insight["senales_a_observar"]:
            st.markdown("**Señales a observar:**")
            for s in insight["senales_a_observar"]:
                st.markdown(f"- {s}")
        if insight["recomendaciones"]:
            st.markdown("**Recomendaciones:**")
            for r in insight["recomendaciones"]:
                st.markdown(f"- {r}")
        if insight["consejos_practicos"]:
            st.markdown("**Consejos prácticos:**")
            for c in insight["consejos_practicos"]:
                st.markdown(f"- {c}")

    # --- Feedback ---
    st.markdown("**¿Te sirvió esta recomendación?**")
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("👍 Sí", use_container_width=True, key="feedback_si"):
            _registrar_feedback(True)
    with col_no:
        if st.button("👎 No tanto", use_container_width=True, key="feedback_no"):
            _registrar_feedback(False)
