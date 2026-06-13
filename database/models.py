"""
Modelos ORM (SQLAlchemy 2.x) — implementan el modelo de datos descrito en
docs/06_base_de_datos.md (Fase 7).

Compatibles con SQLite (desarrollo/demo) y PostgreSQL (Azure Database for
PostgreSQL Flexible Server, producción).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Usuarios y planes
# ---------------------------------------------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username_publico: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    fecha_nacimiento: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pais: Mapped[str | None] = mapped_column(String(60), nullable=True)
    region: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    suscripcion: Mapped["Suscripcion"] = relationship(
        back_populates="usuario", uselist=False
    )
    formulario_salud: Mapped["FormularioSalud"] = relationship(
        back_populates="usuario", uselist=False
    )


class Plan(Base):
    __tablename__ = "planes"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(40))
    precio_mensual: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    descripcion_corta: Mapped[str] = mapped_column(Text)
    features: Mapped[list] = mapped_column(JSON, default=list)


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), unique=True
    )
    plan_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("planes.id"))
    estado: Mapped[str] = mapped_column(String(20), default="activa")
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    usuario: Mapped["Usuario"] = relationship(back_populates="suscripcion")
    plan: Mapped["Plan"] = relationship()


# ---------------------------------------------------------------------------
# Formulario de salud (Plan PRO — datos sensibles)
# ---------------------------------------------------------------------------
class FormularioSalud(Base):
    __tablename__ = "formularios_salud"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuarios.id"), unique=True
    )
    tiempo_diagnostico: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estilo_alimentacion: Mapped[str | None] = mapped_column(String(20), nullable=True)
    preferencias_alimentos: Mapped[list] = mapped_column(JSON, default=list)
    nivel_actividad: Mapped[str | None] = mapped_column(String(20), nullable=True)
    actividades_preferidas: Mapped[list] = mapped_column(JSON, default=list)
    objetivos: Mapped[list] = mapped_column(JSON, default=list)
    restricciones: Mapped[list] = mapped_column(JSON, default=list)
    consentimiento_datos_salud: Mapped[bool] = mapped_column(Boolean, default=False)
    consentimiento_fecha: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="formulario_salud")


# ---------------------------------------------------------------------------
# Registros diarios
# ---------------------------------------------------------------------------
class RegistroAnimo(Base):
    __tablename__ = "registros_animo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    valor: Mapped[str] = mapped_column(String(20))  # triste|neutral|bien|feliz
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RegistroSueno(Base):
    __tablename__ = "registros_sueno"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    valor: Mapped[str] = mapped_column(String(20))  # mal_dormido|regular|descansado
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Análisis nutricional + insight de bienestar (Fase 3 y 4)
# ---------------------------------------------------------------------------
class AnalisisNutricional(Base):
    __tablename__ = "analisis_nutricionales"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resultado_vision: Mapped[dict] = mapped_column(JSON, default=dict)
    resultado_nutricional: Mapped[dict] = mapped_column(JSON, default=dict)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    insight: Mapped["ResultadoIABienestar"] = relationship(
        back_populates="analisis", uselist=False
    )


class ResultadoIABienestar(Base):
    __tablename__ = "resultados_ia_bienestar"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    analisis_nutricional_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analisis_nutricionales.id"), unique=True
    )
    registro_animo_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("registros_animo.id"), nullable=True
    )
    registro_sueno_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("registros_sueno.id"), nullable=True
    )
    resultado: Mapped[dict] = mapped_column(JSON, default=dict)
    usado_contexto_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    analisis: Mapped["AnalisisNutricional"] = relationship(back_populates="insight")


# ---------------------------------------------------------------------------
# Retos y gamificación
# ---------------------------------------------------------------------------
class Reto(Base):
    __tablename__ = "retos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    titulo: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String(30))
    es_generado_por_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    contexto_peruano: Mapped[bool] = mapped_column(Boolean, default=True)


class RetoUsuario(Base):
    __tablename__ = "retos_usuario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    reto_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("retos.id"), nullable=True
    )
    reto_personalizado_texto: Mapped[dict] = mapped_column(JSON, default=dict)
    resultado_ia_bienestar_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("resultados_ia_bienestar.id"), nullable=True
    )
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    medalla_desbloqueada: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    fecha_completado: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )


# ---------------------------------------------------------------------------
# Comunidad (Fase 8)
# ---------------------------------------------------------------------------
class PostComunidad(Base):
    __tablename__ = "posts_comunidad"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    reto_usuario_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("retos_usuario.id"), nullable=True
    )
    texto: Mapped[str] = mapped_column(Text)
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    comentarios_ia: Mapped[list["ComentarioIA"]] = relationship(
        back_populates="post"
    )


class InteraccionComunidad(Base):
    __tablename__ = "interacciones_comunidad"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("posts_comunidad.id"))
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(30), default="motivacion_enviada")
    texto_enviado: Mapped[str] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComentarioIA(Base):
    __tablename__ = "comentarios_ia"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("posts_comunidad.id"))
    texto_generado: Mapped[str] = mapped_column(Text)
    fue_usado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    post: Mapped["PostComunidad"] = relationship(back_populates="comentarios_ia")


# ---------------------------------------------------------------------------
# Feedback y mejora continua (Fase 7.4)
# ---------------------------------------------------------------------------
class FeedbackUsuario(Base):
    __tablename__ = "feedback_usuario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    usuario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"))
    resultado_ia_bienestar_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resultados_ia_bienestar.id")
    )
    util: Mapped[bool] = mapped_column(Boolean)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
