"""
Resumen longitudinal de hábitos (Fase 6.3).

Calcula agregados estadísticos simples (frecuencias, promedios) sobre los
últimos N días del usuario PRO. Estos agregados —NO la IA— son los que generan
los números; la IA solo los describe en lenguaje natural dentro del prompt de
`services/openai_service.generar_insight_bienestar`.
"""

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import select

from database.db import get_session
from database.models import AnalisisNutricional, RegistroAnimo, RegistroSueno, RetoUsuario


def construir_resumen_longitudinal(usuario_id: str, dias: int = 30) -> dict | None:
    """
    Devuelve un resumen agregado de los últimos `dias`, o None si el usuario no
    tiene suficiente historial (evita generar un resumen vacío/poco útil).
    """
    desde = datetime.utcnow() - timedelta(days=dias)

    with get_session() as session:
        animos = session.scalars(
            select(RegistroAnimo).where(
                RegistroAnimo.usuario_id == usuario_id,
                RegistroAnimo.fecha >= desde,
            )
        ).all()
        suenos = session.scalars(
            select(RegistroSueno).where(
                RegistroSueno.usuario_id == usuario_id,
                RegistroSueno.fecha >= desde,
            )
        ).all()
        analisis = session.scalars(
            select(AnalisisNutricional).where(
                AnalisisNutricional.usuario_id == usuario_id,
                AnalisisNutricional.fecha >= desde,
            )
        ).all()
        retos = session.scalars(
            select(RetoUsuario).where(
                RetoUsuario.usuario_id == usuario_id,
                RetoUsuario.fecha_creacion >= desde,
            )
        ).all()

    dias_con_registro = len({a.fecha.date() for a in analisis})
    if dias_con_registro < 2:
        return None

    platos = [
        a.resultado_nutricional.get("tipo_alimento")
        for a in analisis
        if a.resultado_nutricional.get("tipo_alimento")
    ]

    return {
        "dias_con_registro": dias_con_registro,
        "promedio_animo": dict(Counter(a.valor for a in animos)),
        "promedio_sueno": dict(Counter(s.valor for s in suenos)),
        "platos_mas_frecuentes": [p for p, _ in Counter(platos).most_common(3)],
        "retos_sugeridos": len(retos),
        "retos_completados": sum(1 for r in retos if r.estado in ("completado", "compartido")),
    }
