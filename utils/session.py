"""
Helpers de estado de sesión y autenticación.

`app.py` usa `st.session_state["pantalla"]` como router entre las pantallas
definidas en `screens/`. Este módulo centraliza la inicialización del estado y
las operaciones de autenticación (hash de contraseñas con argon2).
"""

import streamlit as st
from passlib.context import CryptContext
from sqlalchemy import select

from database.db import get_session
from database.models import FormularioSalud, Plan, Suscripcion, Usuario

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
def inicializar_estado() -> None:
    defaults = {
        "pantalla": "login",
        "usuario_id": None,
        "ultimo_analisis_id": None,
        "ultimo_insight": None,
        "animo_hoy": None,
        "sueno_hoy": None,
        "panel_resultado_visible": False,
    }
    for clave, valor in defaults.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def ir_a(pantalla: str) -> None:
    st.session_state["pantalla"] = pantalla
    st.rerun()


def cerrar_sesion() -> None:
    for clave in list(st.session_state.keys()):
        del st.session_state[clave]
    inicializar_estado()
    st.rerun()


# ---------------------------------------------------------------------------
# Operaciones de usuario
# ---------------------------------------------------------------------------
def crear_usuario(
    nombre: str,
    apellido: str,
    correo: str,
    password: str,
    username_publico: str,
) -> str:
    """Crea un usuario nuevo con plan Gratuito y devuelve su id."""
    with get_session() as session:
        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            password_hash=hash_password(password),
            username_publico=username_publico,
        )
        session.add(usuario)
        session.flush()

        suscripcion = Suscripcion(usuario_id=usuario.id, plan_id=1)  # Plan Gratuito por defecto
        session.add(suscripcion)

        return usuario.id


def autenticar(correo: str, password: str) -> str | None:
    """Devuelve el id del usuario si las credenciales son válidas."""
    with get_session() as session:
        usuario = session.scalar(select(Usuario).where(Usuario.correo == correo))
        if usuario and verificar_password(password, usuario.password_hash):
            return usuario.id
    return None


def obtener_usuario(usuario_id: str) -> Usuario | None:
    with get_session() as session:
        return session.get(Usuario, usuario_id)


def obtener_plan_actual(usuario_id: str) -> Plan | None:
    with get_session() as session:
        suscripcion = session.scalar(
            select(Suscripcion).where(Suscripcion.usuario_id == usuario_id)
        )
        if not suscripcion:
            return None
        return session.get(Plan, suscripcion.plan_id)


def es_usuario_pro(usuario_id: str) -> bool:
    plan = obtener_plan_actual(usuario_id)
    return plan is not None and plan.id == 2


def obtener_formulario_salud(usuario_id: str) -> FormularioSalud | None:
    with get_session() as session:
        return session.scalar(
            select(FormularioSalud).where(FormularioSalud.usuario_id == usuario_id)
        )


def activar_plan_pro(usuario_id: str) -> None:
    with get_session() as session:
        suscripcion = session.scalar(
            select(Suscripcion).where(Suscripcion.usuario_id == usuario_id)
        )
        if suscripcion:
            suscripcion.plan_id = 2
        else:
            session.add(Suscripcion(usuario_id=usuario_id, plan_id=2))
