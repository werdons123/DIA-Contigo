"""
Hoja de estilos de Quinu-IA para Streamlit.

Replica el sistema de diseño del mockup HTML (`quinu-ia-mockup.html`): paleta de
colores, radios de 16px, tipografía y la barra de navegación inferior fija, e
incluye además las clases nuevas introducidas en el rediseño (Fase 2): tarjetas
de Plan de Pago, badge "Recomendado", banner de plan activo, etc.
"""

import streamlit as st

CSS = """
<style>
:root {
    --bg: #F8F9FA;
    --cream: #FFF8EF;
    --green: #D9FDD3;
    --green-deep: #54B07E;
    --green-text: #2F6B49;
    --blue: #5AA9E6;
    --blue-soft: #EAF4FD;
    --blue-text: #2C6FA3;
    --grey-locked: #6C757D;
    --yellow: #FFF6DD;
    --yellow-text: #8A6D1F;
    --text: #1F2933;
    --text-soft: #6C757D;
    --line: #E3E6EA;
    --radius: 16px;
}

html, body, [class*="css"] {
    font-family: "Segoe UI Variable", "SF Pro Display", -apple-system,
        "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

#MainMenu, header, footer {visibility: hidden;}

.block-container {
    padding-top: 1rem;
    padding-bottom: 5.5rem;
    max-width: 480px;
    margin: 0 auto;
}

/* --- Tarjetas genéricas --- */
.qi-card {
    background: var(--cream);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
}

.qi-card-green {
    background: var(--green);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
}

.qi-card-blue {
    background: var(--blue-soft);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
}

/* --- Banner amarillo de aviso / disclaimers --- */
.qi-banner-yellow {
    background: var(--yellow);
    color: var(--yellow-text);
    border-radius: var(--radius);
    padding: 14px 16px;
    font-size: 13px;
    margin-bottom: 10px;
}

/* --- Link subrayado del Dashboard hacia Plan de Pago --- */
.qi-link-plan {
    color: var(--blue-text);
    font-weight: 600;
    font-size: 13px;
    text-decoration: underline;
    cursor: pointer;
    margin: 4px 0 16px 0;
    display: block;
    background: none;
    border: none;
    text-align: left;
    padding: 0;
}

/* --- Banner de plan activo --- */
.qi-plan-activo {
    background: var(--green);
    color: var(--green-text);
    border-radius: var(--radius);
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 14px;
}

/* --- Botón principal estilo "btn-giant" --- */
div.stButton > button {
    border-radius: var(--radius);
    font-weight: 600;
    width: 100%;
}

div.stButton > button[kind="primary"] {
    background-color: var(--green-deep);
    color: white;
    border: none;
    padding: 14px;
    font-size: 15px;
}

/* --- Plan de Pago: tarjetas --- */
.qi-plan-card {
    border-radius: var(--radius);
    padding: 20px;
    margin-bottom: 16px;
    border: 1px solid var(--line);
    background: var(--cream);
}

.qi-plan-card-pro {
    border: 2px solid var(--blue);
    background: linear-gradient(135deg, var(--green) 0%, var(--blue-soft) 100%);
    position: relative;
}

.qi-plan-badge {
    display: inline-block;
    background: var(--green-deep);
    color: white;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
}

.qi-plan-price {
    font-size: 26px;
    font-weight: 700;
    margin: 4px 0 12px 0;
}

.qi-plan-feature {
    font-size: 13.5px;
    margin: 6px 0;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.qi-check-grey { color: var(--text-soft); }
.qi-check-green { color: var(--green-deep); font-weight: 700; }

/* --- Badges / medallas --- */
.qi-badge-locked {
    background: #ECECEC;
    color: var(--grey-locked);
    border-radius: var(--radius);
    padding: 10px 14px;
    text-align: center;
    font-size: 12.5px;
}

.qi-badge-unlocked {
    background: var(--green);
    color: var(--green-text);
    border-radius: var(--radius);
    padding: 10px 14px;
    text-align: center;
    font-size: 12.5px;
    font-weight: 700;
    box-shadow: 0 0 0 3px rgba(84, 176, 126, 0.25);
}

/* --- Separador antes de la navegación inferior --- */
.qi-bottom-nav {
    margin-top: 8px;
}

.qi-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 4px;
}

.qi-subtitle {
    font-size: 13px;
    color: var(--text-soft);
    margin-bottom: 16px;
}

.qi-pill-row .stButton > button {
    border-radius: 999px;
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--line);
    font-size: 12.5px;
    padding: 8px 14px;
}

.qi-pill-row .stButton > button:hover {
    border-color: var(--green-deep);
    color: var(--green-text);
}
</style>
"""


def inyectar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
