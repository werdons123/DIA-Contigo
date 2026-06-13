"""
Inicialización de la base de datos: motor, sesión y datos semilla (planes y
catálogo de retos). Funciona igual con SQLite (desarrollo) o PostgreSQL (Azure),
gracias a `config.DATABASE_URL`.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import config
from database.models import Base, Plan, Reto

_connect_args = {}
if config.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(config.DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Datos semilla
# ---------------------------------------------------------------------------
PLANES_SEED = [
    Plan(
        id=config.PLAN_GRATUITO,
        nombre="Gratuito",
        precio_mensual=0,
        descripcion_corta="Lo esencial para empezar a entender tus hábitos.",
        features=[
            "Análisis de fotografía de alimentos",
            "Registro de estado de ánimo",
            "Registro de nivel de sueño",
            "Recomendaciones generales",
            "Retos generales",
        ],
    ),
    Plan(
        id=config.PLAN_PRO,
        nombre="PRO",
        precio_mensual=19.90,
        descripcion_corta="IA con tu contexto completo, recomendaciones a tu medida.",
        features=[
            "Todo lo del plan Gratuito",
            "Formulario de salud completo",
            "Perfil nutricional avanzado",
            "Historial de hábitos y seguimiento longitudinal",
            "Recomendaciones y retos altamente personalizados",
            "Mayor precisión de IA",
        ],
    ),
]

RETOS_SEED = [
    Reto(
        titulo="Camina 10 minutos post-almuerzo",
        descripcion=(
            "Una caminata corta después de almorzar ayuda a tu cuerpo a procesar "
            "mejor los carbohidratos."
        ),
        categoria="actividad_fisica",
        es_generado_por_ia=False,
        contexto_peruano=True,
    ),
    Reto(
        titulo="Cambia media porción de arroz por tarwi o pallares",
        descripcion=(
            "El tarwi y los pallares aportan proteína vegetal y ayudan a que la "
            "glucosa suba más despacio."
        ),
        categoria="alimentacion",
        es_generado_por_ia=False,
        contexto_peruano=True,
    ),
    Reto(
        titulo="5 minutos de marinera o huayno en casa",
        descripcion=(
            "Mover el cuerpo con música criolla es una forma agradable de "
            "activarte y mejorar tu ánimo."
        ),
        categoria="actividad_fisica",
        es_generado_por_ia=False,
        contexto_peruano=True,
    ),
    Reto(
        titulo="Apaga pantallas 30 minutos antes de dormir",
        descripcion="Ayuda a mejorar la calidad de tu descanso esta noche.",
        categoria="descanso",
        es_generado_por_ia=False,
        contexto_peruano=False,
    ),
]


def init_db() -> None:
    """Crea las tablas si no existen y siembra planes/retos base."""
    Base.metadata.create_all(engine)

    with get_session() as session:
        if session.query(Plan).count() == 0:
            session.add_all(PLANES_SEED)
        if session.query(Reto).count() == 0:
            session.add_all(RETOS_SEED)
