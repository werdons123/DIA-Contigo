"""
Quinu-IA — punto de entrada de la aplicación Streamlit.

Actúa como router entre las pantallas de `screens/`, usando
`st.session_state["pantalla"]`. Esto permite replicar la navegación tipo app
móvil del mockup (sin recargar la página completa) dentro de las limitaciones
de Streamlit.
"""

import streamlit as st

from database.db import init_db
from screens import (
    comunidad,
    compartir,
    consentimiento,
    dashboard,
    formulario_salud,
    login,
    plan_pago,
    registro,
)
from utils.session import inicializar_estado
from utils.styles import inyectar_estilos

st.set_page_config(
    page_title="Quinu-IA",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inyectar_estilos()
inicializar_estado()
init_db()

PANTALLAS_PUBLICAS = {"login", "registro"}

PANTALLAS = {
    "login": login.render,
    "registro": registro.render,
    "dashboard": dashboard.render,
    "plan_pago": plan_pago.render,
    "consentimiento": consentimiento.render,
    "formulario_salud": formulario_salud.render,
    "compartir": compartir.render,
    "comunidad": comunidad.render,
}


def main() -> None:
    pantalla = st.session_state["pantalla"]

    # Guard: las pantallas internas requieren sesión activa.
    if pantalla not in PANTALLAS_PUBLICAS and not st.session_state.get("usuario_id"):
        st.session_state["pantalla"] = "login"
        pantalla = "login"

    render_fn = PANTALLAS.get(pantalla, login.render)
    render_fn()


if __name__ == "__main__":
    main()
