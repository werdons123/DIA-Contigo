"""
Servicio de moderación — Azure AI Content Safety (Fase 8.4).

Filtra los mensajes generados por `services/openai_service.generar_mensajes_comunidad`
antes de guardarlos en la tabla `comentarios_ia`. Si Azure AI Content Safety no
está configurado, se aplica una validación local básica (lista de palabras
bloqueadas) como modo demo — documentado en docs/07_ia_comunidad.md (sección 8.4).
"""

import config

_PALABRAS_BLOQUEADAS_DEMO = {
    "odio",
    "matar",
    "suicid",
    "violencia",
    "sexual",
}


def es_seguro(texto: str) -> bool:
    """Devuelve True si el texto pasa el filtro de moderación."""
    if config.CONTENT_SAFETY_DEMO_MODE:
        return _es_seguro_demo(texto)

    return _es_seguro_azure(texto)


def _es_seguro_azure(texto: str) -> bool:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    from azure.core.credentials import AzureKeyCredential

    client = ContentSafetyClient(
        endpoint=config.AZURE_CONTENT_SAFETY_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_CONTENT_SAFETY_KEY),
    )
    result = client.analyze_text(AnalyzeTextOptions(text=texto))

    # Umbral conservador: cualquier categoría con severidad >= 2 (escala 0-7
    # truncada por la API a niveles 0/2/4/6) se considera no seguro para una
    # comunidad de pacientes.
    for categoria in (
        TextCategory.HATE,
        TextCategory.SELF_HARM,
        TextCategory.SEXUAL,
        TextCategory.VIOLENCE,
    ):
        analisis = next(
            (r for r in result.categories_analysis if r.category == categoria), None
        )
        if analisis and analisis.severity and analisis.severity >= 2:
            return False
    return True


def _es_seguro_demo(texto: str) -> bool:
    texto_lower = texto.lower()
    return not any(palabra in texto_lower for palabra in _PALABRAS_BLOQUEADAS_DEMO)
