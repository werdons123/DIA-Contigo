"""
Glosario gastronómico y cultural peruano (Fase 5 — Identidad Peruana).

Esta es la "base de conocimiento" que se inyecta como contexto en todos los
prompts de IA (análisis nutricional, insight de bienestar y mensajes de
comunidad), para evitar recomendaciones genéricas no aplicables a Perú.

Está estructurado como un diccionario simple para el MVP. La función
`construir_bloque_contexto_peruano()` lo serializa a texto plano listo para
insertarse en un *system prompt*. En una iteración futura, este módulo puede
sustituirse por una consulta a Azure AI Search (RAG) sin cambiar la interfaz
pública — ver docs/04_identidad_peruana.md (sección 5.5).
"""

CONTEXTO_PERUANO = {
    "alimentos_andinos": [
        "quinua",
        "tarwi",
        "kiwicha",
        "cañihua",
        "camote",
        "pallares",
        "olluco",
        "oca",
        "maíz morado",
    ],
    "proteinas_locales": [
        "anchoveta",
        "pejerrey",
        "pollo a la brasa (versión casera al horno)",
        "huevo de corral",
    ],
    "platos_tradicionales": [
        "lomo saltado",
        "ají de gallina",
        "causa",
        "tacu tacu",
        "seco de res",
        "ceviche",
        "cau cau",
        "arroz con pollo",
        "caldo de gallina",
    ],
    "actividad_fisica_y_baile": [
        "marinera",
        "huayno",
        "festejo",
        "caminata al mercado",
        "subir escaleras (zonas con pendiente como Lima, Cusco, Arequipa)",
        "bicicleta urbana",
    ],
    "costumbres": [
        "almuerzo familiar como comida principal del día",
        "lonchera para el trabajo o estudio",
        "comer fuera por motivos laborales (combis, mercados, polladas)",
        "horarios laborales peruanos (almuerzo entre 12pm y 3pm)",
    ],
    "bienestar_y_relajacion": [
        "mate de coca, manzanilla o muña",
        "siesta corta",
        "música criolla",
        "espacios verdes urbanos (parques, malecones)",
    ],
}


def construir_bloque_contexto_peruano() -> str:
    """Serializa el glosario a un bloque de texto para system prompts."""
    lineas = [
        "GLOSARIO DE CONTEXTO PERUANO (usar como referencia para personalizar "
        "alimentos, actividades y formas de relajación):"
    ]
    titulos = {
        "alimentos_andinos": "Alimentos / superalimentos andinos",
        "proteinas_locales": "Proteínas locales accesibles",
        "platos_tradicionales": "Platos tradicionales peruanos",
        "actividad_fisica_y_baile": "Actividad física y baile",
        "costumbres": "Costumbres y contexto social",
        "bienestar_y_relajacion": "Bienestar y relajación",
    }
    for clave, items in CONTEXTO_PERUANO.items():
        lineas.append(f"- {titulos[clave]}: " + ", ".join(items) + ".")

    lineas.append(
        "\nREGLA DE USO: cuando sugieras alimentos, actividades físicas o formas "
        "de relajación, prioriza opciones de este glosario sobre alternativas "
        "genéricas (ej. evita 'kale', 'smoothie bowl', 'gimnasio CrossFit', salvo "
        "que el usuario las mencione primero)."
    )
    return "\n".join(lineas)


SYSTEM_PROMPT_BASE = (
    "Eres el motor de IA de Quinu-IA, una app peruana de acompañamiento para "
    "personas con diabetes tipo 2. Tu rol es de ACOMPAÑAMIENTO, NUNCA clínico.\n\n"
    "REGLAS NO NEGOCIABLES:\n"
    "- No emitas diagnósticos médicos ni juicios clínicos.\n"
    "- No recomiendes, ajustes ni sugieras cambios de medicación.\n"
    "- No te presentes como médico, nutricionista o psicólogo.\n"
    "- Si detectas posibles señales de urgencia médica, responde sugiriendo "
    "contactar a un profesional de salud de inmediato.\n"
    "- Usa un tono cálido, cercano y en segunda persona.\n\n"
) + construir_bloque_contexto_peruano()
