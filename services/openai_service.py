"""
Servicio de Azure OpenAI — implementa los tres motores de IA del proyecto:

1. `analizar_nutricion`        → Fase 3 (IA Nutricional, GPT-4o multimodal)
2. `generar_insight_bienestar` → Fase 4 (IA de Bienestar, GPT-4o)
3. `generar_mensajes_comunidad`→ Fase 8 (IA de Comunidad, GPT-4o-mini)

Cada función valida su salida contra los esquemas de `services/schemas.py` y,
si `config.OPENAI_DEMO_MODE` es True, devuelve resultados de ejemplo generados
localmente con la misma estructura — para que la app sea 100% navegable sin
credenciales de Azure (ver docs/08_arquitectura_tecnologia.md, sección 9.6).
"""

import base64
import json
import random

import config
from services.peru_knowledge import SYSTEM_PROMPT_BASE
from services.schemas import AnalisisNutricionalIA, InsightBienestarIA

# ---------------------------------------------------------------------------
# Cliente Azure OpenAI (creado de forma diferida)
# ---------------------------------------------------------------------------


def _client():
    from openai import AzureOpenAI

    return AzureOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
    )


# ---------------------------------------------------------------------------
# Fase 3 — IA Nutricional (GPT-4o multimodal)
# ---------------------------------------------------------------------------
def analizar_nutricion(imagen_bytes: bytes, resultado_vision: dict) -> dict:
    """
    Analiza una foto de comida y devuelve el esquema `AnalisisNutricionalIA`
    (como dict), usando GPT-4o multimodal + grounding de Azure AI Vision +
    glosario peruano.
    """
    if config.OPENAI_DEMO_MODE:
        data = _analizar_nutricion_demo(resultado_vision)
    else:
        data = _analizar_nutricion_azure(imagen_bytes, resultado_vision)

    validado = AnalisisNutricionalIA.model_validate(data)
    return validado.model_dump()


def _analizar_nutricion_azure(imagen_bytes: bytes, resultado_vision: dict) -> dict:
    b64 = base64.b64encode(imagen_bytes).decode("utf-8")

    system_prompt = (
        SYSTEM_PROMPT_BASE
        + "\n\nTAREA: analiza la imagen de comida adjunta y devuelve ÚNICAMENTE un "
        "JSON válido con EXACTAMENTE estas claves: tipo_alimento, "
        "cantidad_aproximada, porciones_estimadas (carbohidratos, proteinas, "
        "vegetales), macronutrientes_aproximados (carbohidratos_g, proteinas_g, "
        "grasas_g, calorias_kcal), micronutrientes_relevantes (lista), "
        "carga_glucemica_aproximada ('baja'|'media'|'alta'), carga_nutricional, "
        "calidad_alimentaria (puntaje 1-10, etiqueta), balance_del_plato, "
        "excesos_o_deficiencias (lista), nivel_de_procesamiento "
        "('minimamente procesado'|'procesado'|'ultraprocesado'), "
        "presencia_ultraprocesados (detectado, detalle), diversidad_nutricional, "
        "recomendaciones_de_mejora (lista), disclaimer.\n\n"
        f"Contexto adicional de visión por computadora: {json.dumps(resultado_vision)}"
    )

    response = _client().chat.completions.create(
        model=config.AZURE_OPENAI_DEPLOYMENT_GPT4O,
        response_format={"type": "json_object"},
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analiza este plato y responde con el JSON solicitado.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            },
        ],
    )
    return json.loads(response.choices[0].message.content)


def _analizar_nutricion_demo(resultado_vision: dict) -> dict:
    caption = (resultado_vision or {}).get("caption", "")

    if "ceviche" in caption:
        nombre, carga, etiqueta, puntaje = "Ceviche con camote y cancha", "baja", "Buena", 8
        excesos = ["Sodio (limón + sal en exceso es común en ceviche de restaurante)"]
        mejora = [
            "Acompaña con camote o yuca en lugar de chifle frito para reducir grasas.",
        ]
    elif "stir fry" in caption or "lomo" in caption:
        nombre, carga, etiqueta, puntaje = "Lomo saltado con arroz y papas fritas", "alta", "Mejorable", 5
        excesos = ["Carbohidratos refinados (arroz + papas fritas en el mismo plato)"]
        mejora = [
            "Cambia las papas fritas por una porción de pallares o ensalada de "
            "tomate y cebolla.",
            "Sirve media porción de arroz y complementa con más vegetales.",
        ]
    elif "soup" in caption or "broth" in caption:
        nombre, carga, etiqueta, puntaje = "Caldo de gallina con fideos", "media", "Moderada", 6
        excesos = ["Sodio del caldo"]
        mejora = ["Agrega más verduras de hoja verde al caldo."]
    else:
        nombre, carga, etiqueta, puntaje = "Seco de res con frijoles y arroz", "media", "Moderada", 6
        excesos = ["Porción de arroz algo elevada para acompañar un guiso denso"]
        mejora = [
            "Cambia parte del arroz por una porción de tarwi o pallares para "
            "sumar proteína vegetal.",
        ]

    return {
        "tipo_alimento": nombre,
        "cantidad_aproximada": "1 plato mediano, aprox. 350-400 g",
        "porciones_estimadas": {
            "carbohidratos": "1.5 porciones (arroz/papas)",
            "proteinas": "1 porción (carne o legumbre)",
            "vegetales": "0.5 porción",
        },
        "macronutrientes_aproximados": {
            "carbohidratos_g": 65,
            "proteinas_g": 28,
            "grasas_g": 18,
            "calorias_kcal": 560,
        },
        "micronutrientes_relevantes": ["Hierro", "Vitamina C", "Potasio"],
        "carga_glucemica_aproximada": carga,
        "carga_nutricional": f"Plato {etiqueta.lower()} en balance, con carga glucémica {carga}.",
        "calidad_alimentaria": {"puntaje": puntaje, "etiqueta": etiqueta},
        "balance_del_plato": (
            "Buen aporte de proteína, pero con poca proporción de vegetales "
            "frente a los carbohidratos."
        ),
        "excesos_o_deficiencias": excesos,
        "nivel_de_procesamiento": "procesado",
        "presencia_ultraprocesados": {
            "detectado": False,
            "detalle": "No se identifican ultraprocesados evidentes en este plato.",
        },
        "diversidad_nutricional": "Media — predominan carbohidratos y proteína animal.",
        "recomendaciones_de_mejora": mejora,
        "disclaimer": config.DISCLAIMER_NUTRICIONAL,
    }


# ---------------------------------------------------------------------------
# Fase 4 — IA de Bienestar (GPT-4o)
# ---------------------------------------------------------------------------
def generar_insight_bienestar(
    resultado_nutricional: dict,
    animo: str,
    sueno: str,
    perfil_pro: dict | None = None,
    resumen_longitudinal: dict | None = None,
) -> dict:
    """
    Combina nutrición + ánimo + sueño (+ contexto PRO opcional) y devuelve el
    esquema `InsightBienestarIA` (como dict).
    """
    if config.OPENAI_DEMO_MODE:
        data = _insight_demo(resultado_nutricional, animo, sueno, perfil_pro)
    else:
        data = _insight_azure(
            resultado_nutricional, animo, sueno, perfil_pro, resumen_longitudinal
        )

    validado = InsightBienestarIA.model_validate(data)
    return validado.model_dump()


def _insight_azure(
    resultado_nutricional: dict,
    animo: str,
    sueno: str,
    perfil_pro: dict | None,
    resumen_longitudinal: dict | None,
) -> dict:
    contexto_extra = ""
    if perfil_pro:
        contexto_extra += (
            "\n\nCONTEXTO PREMIUM (Plan PRO) — usa estos datos para personalizar "
            f"la respuesta:\n{json.dumps(perfil_pro, ensure_ascii=False)}\n"
            "IMPORTANTE: si 'restricciones' incluye algún alimento, NUNCA lo "
            "recomiendes."
        )
    if resumen_longitudinal:
        contexto_extra += (
            "\n\nRESUMEN DE HÁBITOS DE LOS ÚLTIMOS 30 DÍAS (datos agregados, "
            "describe tendencias de frecuencia, NO causalidad clínica):\n"
            f"{json.dumps(resumen_longitudinal, ensure_ascii=False)}"
        )

    system_prompt = (
        SYSTEM_PROMPT_BASE
        + "\n\nTAREA: genera un 'Insight de Bienestar' combinando el análisis "
        "nutricional del día, el estado de ánimo y el nivel de sueño del usuario"
        + contexto_extra
        + "\n\nDevuelve ÚNICAMENTE un JSON con EXACTAMENTE estas claves: "
        "nivel_de_bienestar, resumen, factores_detectados (lista), "
        "senales_a_observar (lista, hábitos a vigilar, NO riesgos clínicos), "
        "recomendaciones (lista), consejos_practicos (lista, acciones de menos "
        "de 15 minutos, contextualizadas a Perú), reto_personalizado (titulo, "
        "descripcion, icono), disclaimer."
    )

    user_prompt = (
        f"Análisis nutricional del día: {json.dumps(resultado_nutricional, ensure_ascii=False)}\n"
        f"Estado de ánimo: {animo}\n"
        f"Nivel de sueño: {sueno}"
    )

    response = _client().chat.completions.create(
        model=config.AZURE_OPENAI_DEPLOYMENT_GPT4O,
        response_format={"type": "json_object"},
        temperature=0.6,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


_RETOS_DEMO_POR_PERFIL = {
    "sedentario": {
        "titulo": "Camina 10 minutos post-almuerzo",
        "descripcion": (
            "Una caminata corta, aunque sea hasta la bodega de la esquina, ayuda "
            "a tu cuerpo a procesar mejor los carbohidratos del almuerzo."
        ),
        "icono": "walk",
    },
    "ligero": {
        "titulo": "Súbele un poco al ritmo: 5 minutos de marinera o huayno",
        "descripcion": (
            "Pon una canción criolla y muévete en casa. Es una forma agradable "
            "de activarte y mejorar tu ánimo."
        ),
        "icono": "music",
    },
    "activo": {
        "titulo": "Suma 15 minutos extra de bicicleta o caminata rápida",
        "descripcion": (
            "Ya tienes el hábito — aprovecha hoy para sumar un poco más, "
            "especialmente después de tu comida más fuerte."
        ),
        "icono": "bike",
    },
}


def _insight_demo(
    resultado_nutricional: dict,
    animo: str,
    sueno: str,
    perfil_pro: dict | None,
) -> dict:
    plato = resultado_nutricional.get("tipo_alimento", "tu plato")
    carga = resultado_nutricional.get("carga_glucemica_aproximada", "media")

    nivel_actividad = "sedentario"
    if perfil_pro:
        nivel_actividad = perfil_pro.get("nivel_actividad", "sedentario")
    reto = _RETOS_DEMO_POR_PERFIL.get(
        nivel_actividad, _RETOS_DEMO_POR_PERFIL["sedentario"]
    )

    sueno_texto = {
        "mal_dormido": "dormiste poco",
        "regular": "tu descanso fue regular",
        "descansado": "descansaste bien",
    }.get(sueno, "tu descanso fue regular")

    animo_texto = {
        "triste": "Notamos que no te sientes en tu mejor ánimo hoy",
        "neutral": "Tu ánimo está estable hoy",
        "bien": "Te sientes bien hoy",
        "feliz": "¡Qué bueno que te sientas con energía hoy!",
    }.get(animo, "Tu ánimo está estable hoy")

    if carga == "alta":
        nivel = "En alerta"
        factores = [
            f"{plato} tiene una carga glucémica alta",
            f"Reportaste que {sueno_texto}",
        ]
        senales = [
            "Esta semana podrías estar combinando comidas densas en "
            "carbohidratos con descanso irregular — vale la pena observarlo."
        ]
        resumen = (
            f"Tu balance de hoy: {plato} es denso en carbohidratos. Como "
            f"{sueno_texto}, tu cuerpo podría procesar la energía más lento de "
            "lo habitual. Nada de qué preocuparte, solo ajustemos el resto del día."
        )
    else:
        nivel = "Equilibrado"
        factores = [f"{plato} tiene una carga glucémica {carga}", animo_texto]
        senales = []
        resumen = (
            f"Tu balance de hoy: {plato} está dentro de un rango razonable. "
            f"{animo_texto.lower()} y {sueno_texto}, así que tu cuerpo está en "
            "buen punto para mantener tus hábitos de hoy."
        )

    recomendaciones = resultado_nutricional.get("recomendaciones_de_mejora", [])[:2] or [
        "Intenta acompañar tu próxima comida con una porción extra de vegetales."
    ]

    consejos = [
        "Toma un vaso de agua antes de tu próxima comida.",
        "Si sales a comer, pide el arroz aparte y sírvete la mitad.",
    ]
    if sueno == "mal_dormido":
        consejos.append(
            "Esta noche, intenta una infusión de manzanilla o muña 30 minutos "
            "antes de dormir."
        )

    return {
        "nivel_de_bienestar": nivel,
        "resumen": resumen,
        "factores_detectados": factores,
        "senales_a_observar": senales,
        "recomendaciones": recomendaciones,
        "consejos_practicos": consejos,
        "reto_personalizado": reto,
        "disclaimer": config.DISCLAIMER_BIENESTAR,
    }


# ---------------------------------------------------------------------------
# Fase 8 — IA de Comunidad (GPT-4o-mini)
# ---------------------------------------------------------------------------
def generar_mensajes_comunidad(
    texto_post: str, categoria_reto: str, username: str
) -> list[str]:
    """Genera 3 mensajes cortos de motivación contextualizados al post."""
    if config.OPENAI_DEMO_MODE:
        return _mensajes_demo(categoria_reto, username)

    return _mensajes_azure(texto_post, categoria_reto, username)


def _mensajes_azure(texto_post: str, categoria_reto: str, username: str) -> list[str]:
    system_prompt = (
        SYSTEM_PROMPT_BASE
        + "\n\nTAREA: genera 3 mensajes cortos (máximo 12 palabras cada uno) "
        f"para animar a @{username} por su logro. Tono cálido, cercano, peruano. "
        "Varía el enfoque: 1) celebración, 2) ánimo a continuar, 3) "
        "identificación/empatía. Nunca menciones cifras médicas. "
        "Devuelve ÚNICAMENTE un JSON con la clave 'mensajes' (lista de 3 strings)."
    )
    user_prompt = f"Logro compartido: \"{texto_post}\"\nCategoría: {categoria_reto}"

    response = _client().chat.completions.create(
        model=config.AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI,
        response_format={"type": "json_object"},
        temperature=0.8,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    mensajes = data.get("mensajes", [])
    return mensajes[:3] if mensajes else _mensajes_demo(categoria_reto, username)


_MENSAJES_DEMO = {
    "actividad_fisica": [
        "¡Eso es, @{u}! Pasito a pasito se llega lejos.",
        "Cada caminata cuenta. ¡Sigue así, vas muy bien!",
        "A mí también me cuesta empezar, ¡pero como tú, ya estamos en eso!",
    ],
    "alimentacion": [
        "¡Qué buena elección, @{u}! Esos cambios pequeños suman mucho.",
        "Se nota el esfuerzo, ¡vas por buen camino!",
        "Gracias por compartir, me animas a probarlo también.",
    ],
    "descanso": [
        "¡Bien hecho, @{u}! Descansar también es cuidarte.",
        "Pequeños cambios en la noche, grandes resultados de día. ¡Vamos!",
        "Me motivas a apagar la pantalla más temprano hoy también.",
    ],
    "default": [
        "¡Vamos arriba, @{u}! Cada paso cuenta.",
        "Sigue así, campeón/a, se nota tu esfuerzo.",
        "Gracias por compartir tu logro con la comunidad.",
    ],
}


def _mensajes_demo(categoria_reto: str, username: str) -> list[str]:
    plantillas = _MENSAJES_DEMO.get(categoria_reto, _MENSAJES_DEMO["default"])
    return [m.format(u=username) for m in plantillas]
