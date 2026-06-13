"""
Configuración central de Quinu-IA.

Todas las variables sensibles (claves de Azure, cadenas de conexión) se leen desde
variables de entorno. En desarrollo local, copia `.env.example` a `.env` y completa
los valores; en producción (Azure Container Apps / App Service) se configuran como
"Application settings" / secretos del contenedor.

Si las credenciales de Azure AI no están configuradas, los servicios en `services/`
operan en "modo demo": usan datos de ejemplo realistas para que la aplicación sea
completamente navegable y demostrable sin conectividad. Esto está documentado en
docs/08_arquitectura_tecnologia.md (sección 9.6) como una decisión de arquitectura,
no como un atajo temporal.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
# Por defecto usa SQLite local para desarrollo. En Azure, definir:
#   postgresql+psycopg://usuario:password@host:5432/quinu_ia
DATABASE_URL = _get("DATABASE_URL", "sqlite:///quinu_ia.db")

# ---------------------------------------------------------------------------
# Azure AI Vision (Image Analysis 4.0)
# ---------------------------------------------------------------------------
AZURE_VISION_ENDPOINT = _get("AZURE_VISION_ENDPOINT")
AZURE_VISION_KEY = _get("AZURE_VISION_KEY")

# ---------------------------------------------------------------------------
# Azure OpenAI
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = _get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = _get("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = _get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Nombres de despliegue (deployment names) configurados en Azure AI Foundry
AZURE_OPENAI_DEPLOYMENT_GPT4O = _get("AZURE_OPENAI_DEPLOYMENT_GPT4O", "gpt-4o")
AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI = _get(
    "AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI", "gpt-4o-mini"
)

# ---------------------------------------------------------------------------
# Azure AI Content Safety
# ---------------------------------------------------------------------------
AZURE_CONTENT_SAFETY_ENDPOINT = _get("AZURE_CONTENT_SAFETY_ENDPOINT")
AZURE_CONTENT_SAFETY_KEY = _get("AZURE_CONTENT_SAFETY_KEY")

# ---------------------------------------------------------------------------
# Azure Blob Storage (fotos de comida)
# ---------------------------------------------------------------------------
AZURE_STORAGE_CONNECTION_STRING = _get("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER = _get("AZURE_STORAGE_CONTAINER", "quinu-food-photos")

# ---------------------------------------------------------------------------
# Flags de modo demo (se activan automáticamente si faltan credenciales)
# ---------------------------------------------------------------------------
VISION_DEMO_MODE = not (AZURE_VISION_ENDPOINT and AZURE_VISION_KEY)
OPENAI_DEMO_MODE = not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY)
CONTENT_SAFETY_DEMO_MODE = not (
    AZURE_CONTENT_SAFETY_ENDPOINT and AZURE_CONTENT_SAFETY_KEY
)
STORAGE_DEMO_MODE = not AZURE_STORAGE_CONNECTION_STRING

# ---------------------------------------------------------------------------
# Disclaimers fijos (Sección 7 de las bases del Desafío IA - Bagó Perú)
# ---------------------------------------------------------------------------
DISCLAIMER_NUTRICIONAL = "Estimaciones basadas en visión artificial e IA."
DISCLAIMER_BIENESTAR = (
    "Esto no es un diagnóstico médico. Quinu-IA es una herramienta de "
    "acompañamiento; consulta siempre a tu profesional de salud."
)

# ---------------------------------------------------------------------------
# Planes
# ---------------------------------------------------------------------------
PLAN_GRATUITO = 1
PLAN_PRO = 2
