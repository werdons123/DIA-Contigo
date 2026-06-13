"""
Componentes de interfaz reutilizables entre pantallas.
"""

import streamlit as st


def render_bottom_nav(activo: str) -> None:
    """
    Barra de navegación inferior (Inicio / Comunidad), replicando el patrón del
    mockup. `activo` es "dashboard" o "comunidad".

    Nota técnica: Streamlit no permite anclar widgets nativos (st.button)
    dentro de un contenedor HTML personalizado con `position: fixed` — los
    widgets siempre se renderizan en el flujo normal del documento. Por eso
    esta barra se muestra al final del contenido como una sección fija de
    navegación, en lugar de superpuesta. La clase `.qi-bottom-nav` queda
    definida en `utils/styles.py` para una futura migración a un frontend con
    control total del DOM (ver roadmap, docs/08_arquitectura_tecnologia.md).
    """
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        tipo = "primary" if activo == "dashboard" else "secondary"
        if st.button("🏠 Inicio", use_container_width=True, type=tipo, key="nav_inicio"):
            st.session_state["pantalla"] = "dashboard"
            st.rerun()
    with col2:
        tipo = "primary" if activo == "comunidad" else "secondary"
        if st.button(
            "👥 Comunidad", use_container_width=True, type=tipo, key="nav_comunidad"
        ):
            st.session_state["pantalla"] = "comunidad"
            st.rerun()


def render_balance_ring(puntaje: int, nivel_texto: str) -> None:
    """
    Anillo SVG de balance metabólico (0-10), basado en `calidad_alimentaria.puntaje`.
    Verde si >=7, azul si 4-6, amarillo si <4 — coherente con la semántica de
    color del sistema de diseño (verde = positivo, amarillo = atención).
    """
    puntaje = max(0, min(10, puntaje))
    porcentaje = puntaje / 10
    circunferencia = 2 * 3.14159 * 54
    offset = circunferencia * (1 - porcentaje)

    if puntaje >= 7:
        color = "#54B07E"
    elif puntaje >= 4:
        color = "#5AA9E6"
    else:
        color = "#E8B23B"

    svg = f"""
    <div style="display:flex; justify-content:center; margin: 8px 0 16px 0;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="54" fill="none" stroke="#E3E6EA" stroke-width="14"/>
        <circle cx="70" cy="70" r="54" fill="none" stroke="{color}" stroke-width="14"
                stroke-linecap="round"
                stroke-dasharray="{circunferencia:.1f}"
                stroke-dashoffset="{offset:.1f}"
                transform="rotate(-90 70 70)"/>
        <text x="70" y="65" text-anchor="middle" font-size="28" font-weight="700"
              fill="#1F2933" font-family="Segoe UI Variable, sans-serif">{puntaje}/10</text>
        <text x="70" y="86" text-anchor="middle" font-size="11" fill="#6C757D"
              font-family="Segoe UI Variable, sans-serif">{nivel_texto}</text>
      </svg>
    </div>
    """
    st.markdown(svg, unsafe_allow_html=True)


def render_badge(desbloqueada: bool, titulo: str) -> None:
    if desbloqueada:
        st.markdown(
            f'<div class="qi-badge-unlocked">🏅 ¡Medalla desbloqueada!<br>{titulo}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="qi-badge-locked">🔒 Medalla bloqueada — completa el reto '
            f'para desbloquearla<br><strong>{titulo}</strong></div>',
            unsafe_allow_html=True,
        )
