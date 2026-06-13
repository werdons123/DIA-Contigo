"""
Servicio de visión por computadora (Fase 3.1, primer paso del pipeline).

Usa Azure AI Vision — Image Analysis 4.0 para obtener un "grounding" objetivo de
la fotografía (tags, descripción/caption y texto OCR si la imagen es un menú).
Este resultado se combina luego con el análisis multimodal de GPT-4o en
`services/openai_service.py`.

Modo demo: si `config.VISION_DEMO_MODE` es True (credenciales no configuradas),
se devuelve un resultado de ejemplo realista basado en platos peruanos comunes,
para que el flujo completo de la app sea demostrable sin conectividad a Azure.
"""

import random

import config


def analizar_imagen(imagen_bytes: bytes) -> dict:
    """
    Devuelve un diccionario con tags, caption y texto OCR detectado.

    Estructura de salida (igual en modo real y modo demo):
        {
            "caption": str,
            "tags": list[str],
            "texto_ocr": str | None,
            "modo": "azure" | "demo",
        }
    """
    if config.VISION_DEMO_MODE:
        return _resultado_demo()

    return _resultado_azure(imagen_bytes)


def _resultado_azure(imagen_bytes: bytes) -> dict:
    from azure.ai.vision.imageanalysis import ImageAnalysisClient
    from azure.ai.vision.imageanalysis.models import VisualFeatures
    from azure.core.credentials import AzureKeyCredential

    client = ImageAnalysisClient(
        endpoint=config.AZURE_VISION_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_VISION_KEY),
    )

    result = client.analyze(
        image_data=imagen_bytes,
        visual_features=[
            VisualFeatures.CAPTION,
            VisualFeatures.TAGS,
            VisualFeatures.READ,
        ],
    )

    caption = result.caption.text if result.caption else ""
    tags = [t.name for t in (result.tags.list if result.tags else [])]

    texto_ocr = None
    if result.read and result.read.blocks:
        lineas = []
        for block in result.read.blocks:
            for line in block.lines:
                lineas.append(line.text)
        texto_ocr = "\n".join(lineas) if lineas else None

    return {"caption": caption, "tags": tags, "texto_ocr": texto_ocr, "modo": "azure"}


def _resultado_demo() -> dict:
    """Resultados de ejemplo realistas, variados, para demos sin Azure."""
    ejemplos = [
        {
            "caption": "a plate of rice, beans and beef stew",
            "tags": ["food", "dish", "rice", "beef", "beans", "tableware", "meal"],
            "texto_ocr": None,
        },
        {
            "caption": "a bowl of ceviche with onions and corn",
            "tags": ["food", "ceviche", "fish", "lime", "onion", "corn", "dish"],
            "texto_ocr": None,
        },
        {
            "caption": "a plate of lomo saltado with french fries and rice",
            "tags": ["food", "stir fry", "beef", "potato", "rice", "tomato", "dish"],
            "texto_ocr": None,
        },
        {
            "caption": "a bowl of chicken soup with vegetables",
            "tags": ["food", "soup", "chicken", "vegetable", "broth", "bowl"],
            "texto_ocr": None,
        },
    ]
    resultado = random.choice(ejemplos)
    resultado["modo"] = "demo"
    return resultado
