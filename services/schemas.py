"""
Esquemas Pydantic para validar las salidas estructuradas de los modelos de IA.

Corresponden exactamente a los esquemas documentados en:
- docs/03_ia_nutricional_bienestar.md, sección 3.2 (análisis nutricional)
- docs/03_ia_nutricional_bienestar.md, sección 3.3 (insight de bienestar)

Validar con Pydantic antes de persistir en BD evita guardar respuestas de IA
mal formadas y es parte del "Validador de esquema" del pipeline (Fase 3.1).
"""

from typing import Literal

from pydantic import BaseModel, Field

import config


class Porciones(BaseModel):
    carbohidratos: str = ""
    proteinas: str = ""
    vegetales: str = ""


class Macronutrientes(BaseModel):
    carbohidratos_g: float = 0
    proteinas_g: float = 0
    grasas_g: float = 0
    calorias_kcal: float = 0


class CalidadAlimentaria(BaseModel):
    puntaje: int = Field(ge=1, le=10, default=5)
    etiqueta: str = "Moderada"


class PresenciaUltraprocesados(BaseModel):
    detectado: bool = False
    detalle: str = ""


class AnalisisNutricionalIA(BaseModel):
    """Esquema de salida de la Fase 3 (IA Nutricional)."""

    tipo_alimento: str
    cantidad_aproximada: str
    porciones_estimadas: Porciones
    macronutrientes_aproximados: Macronutrientes
    micronutrientes_relevantes: list[str] = Field(default_factory=list)
    carga_glucemica_aproximada: Literal["baja", "media", "alta"] = "media"
    carga_nutricional: str
    calidad_alimentaria: CalidadAlimentaria
    balance_del_plato: str
    excesos_o_deficiencias: list[str] = Field(default_factory=list)
    nivel_de_procesamiento: Literal[
        "minimamente procesado", "procesado", "ultraprocesado"
    ] = "procesado"
    presencia_ultraprocesados: PresenciaUltraprocesados
    diversidad_nutricional: str
    recomendaciones_de_mejora: list[str] = Field(default_factory=list)
    disclaimer: str = config.DISCLAIMER_NUTRICIONAL


class RetoPersonalizado(BaseModel):
    titulo: str
    descripcion: str
    icono: str = "target"


class InsightBienestarIA(BaseModel):
    """Esquema de salida de la Fase 4 (IA de Bienestar)."""

    nivel_de_bienestar: str
    resumen: str
    factores_detectados: list[str] = Field(default_factory=list)
    senales_a_observar: list[str] = Field(default_factory=list)
    recomendaciones: list[str] = Field(default_factory=list)
    consejos_practicos: list[str] = Field(default_factory=list)
    reto_personalizado: RetoPersonalizado
    disclaimer: str = config.DISCLAIMER_BIENESTAR
