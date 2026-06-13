# Fase 3 — IA Nutricional · Fase 4 — IA de Bienestar

## 3.1 Arquitectura del análisis de imagen

```
[Foto del usuario]
      │
      ▼
┌─────────────────────────────┐
│ Azure AI Vision              │  → tags, objetos detectados, descripción (caption),
│ (Image Analysis 4.0)         │     OCR si la foto es un menú/carta
└──────────────┬────────────────┘
               │ (tags + caption + texto OCR como contexto adicional)
               ▼
┌─────────────────────────────┐
│ Azure OpenAI · GPT-4o        │  → recibe la imagen directamente (modelo multimodal) +
│ (modelo multimodal)          │     el contexto de Vision + el "Glosario gastronómico
│ + Glosario peruano (RAG)     │     peruano" (04_identidad_peruana.md) como system prompt
└──────────────┬────────────────┘
               │ salida en JSON estructurado (esquema fijo)
               ▼
┌─────────────────────────────┐
│ Validador de esquema         │  → valida tipos/rangos, agrega disclaimer fijo,
│ (pydantic)                   │     guarda en BD (tabla analisis_nutricionales)
└─────────────────────────────┘
```

**Por qué dos modelos:** Azure AI Vision aporta *grounding* objetivo (qué objetos/colores/
texturas hay realmente en la imagen, y OCR de menús), mientras que GPT-4o multimodal aporta
el *razonamiento nutricional contextualizado* (qué significa ese plato en términos de
balance, y cómo se relaciona con la gastronomía peruana). Combinar ambos reduce
alucinaciones y es defendible ante el jurado como **"uso justificado de IA generativa, no
ornamental"**.

## 3.2 Esquema de salida — Información nutricional

```json
{
  "tipo_alimento": "string",
  "cantidad_aproximada": "string (ej. '1 plato mediano, ~350g')",
  "porciones_estimadas": {
    "carbohidratos": "string (ej. '1.5 porciones de arroz')",
    "proteinas": "string",
    "vegetales": "string"
  },
  "macronutrientes_aproximados": {
    "carbohidratos_g": "number",
    "proteinas_g": "number",
    "grasas_g": "number",
    "calorias_kcal": "number"
  },
  "micronutrientes_relevantes": ["string"],
  "carga_glucemica_aproximada": "baja | media | alta",
  "carga_nutricional": "string (resumen de 1 línea)",
  "calidad_alimentaria": {
    "puntaje": "number (1-10)",
    "etiqueta": "string (ej. 'Buena', 'Moderada', 'Mejorable')"
  },
  "balance_del_plato": "string",
  "excesos_o_deficiencias": ["string"],
  "nivel_de_procesamiento": "minimamente procesado | procesado | ultraprocesado",
  "presencia_ultraprocesados": {
    "detectado": "boolean",
    "detalle": "string"
  },
  "diversidad_nutricional": "string",
  "recomendaciones_de_mejora": ["string"],
  "disclaimer": "Estimaciones basadas en visión artificial e IA."
}
```

> **Nota sobre "nivel glutamínico":** se interpreta como **carga glucémica aproximada**
> (impacto estimado en la glucosa post-prandial), que es el dato clínicamente relevante para
> el Reto 1 (diabetes). El término se documenta así para evitar ambigüedad en el pitch.

### Reglas de cumplimiento (Sección 7 de las bases)
- El campo `disclaimer` se renderiza **siempre**, en texto visible, nunca solo en un tooltip.
- Ningún campo usa palabras como "diagnóstico", "tratamiento" o "enfermedad". Se usa
  "balance", "calidad alimentaria", "recomendación".
- El *system prompt* de GPT-4o incluye explícitamente:
  > "No emitas juicios clínicos ni recomiendes cambios de medicación. Limítate a hábitos de
  > alimentación, sueño y actividad física. Si detectas una posible urgencia (ej. el usuario
  > menciona síntomas graves), responde sugiriendo contactar a un profesional de salud."

## 3.3 Motor de Bienestar (Fase 4)

### Entradas combinadas
1. JSON de análisis nutricional (Fase 3).
2. Estado de ánimo seleccionado (`triste | neutral | bien | feliz`).
3. Nivel de sueño seleccionado (`mal_dormido | regular | descansado`).
4. *(Solo PRO)* Datos del formulario de salud — ver `05_usuario_premium.md`.

### Prompt de orquestación (resumen)
El servicio `services/openai_service.py` construye un prompt único que combina estas
entradas con el **Glosario peruano** y, si aplica, el perfil PRO, y solicita un JSON con el
siguiente esquema — el **"Insight de Bienestar IA"**:

```json
{
  "nivel_de_bienestar": "string (ej. 'Equilibrado', 'En alerta', 'Necesita atención')",
  "resumen": "string (1-2 frases, tono cálido, en segunda persona)",
  "factores_detectados": ["string"],
  "senales_a_observar": ["string (NO 'riesgos clínicos' — patrones de hábito a vigilar)"],
  "recomendaciones": ["string"],
  "consejos_practicos": ["string (acciones de <15 min, contextualizadas a Perú)"],
  "reto_personalizado": {
    "titulo": "string",
    "descripcion": "string",
    "icono": "string (nombre de ícono Fluent)"
  },
  "disclaimer": "Esto no es un diagnóstico médico. Quinu-IA es una herramienta de
                  acompañamiento; consulta siempre a tu profesional de salud."
}
```

### Mapeo a la UI existente
- `nivel_de_bienestar` + `resumen` → alimentan el **anillo de balance metabólico** y el
  texto "Tu balance de hoy" del Dashboard (sin cambios de layout).
- `reto_personalizado` → alimenta la pieza "Reto diario sugerido por IA" (el badge
  bloqueado/desbloqueado se mantiene igual).
- `senales_a_observar` y `recomendaciones` → se muestran en una sección expandible
  ("Ver más") debajo del panel de resultados, para no sobrecargar la pantalla principal
  (jerarquía visual).

### Ejemplo de salida (para Carlos, Historia 1)
> *Nivel de bienestar:* "Equilibrado, con un punto de atención"
> *Resumen:* "Tu plato de hoy fue denso en carbohidratos y dormiste regular — por eso tu
> cuerpo procesará la energía más lento de lo habitual. Nada de qué preocuparte, solo
> ajustemos el resto del día."
> *Reto personalizado:* "Camina 10 minutos después del almuerzo, igual que cuando vas a la
> bodega de la esquina."
