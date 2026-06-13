# Fase 8 — IA para Comunidad

## 8.1 Objetivo

Reemplazar los botones de motivación estáticos del mockup ("¡Muy bien hecho, WERdons!") por
mensajes **generados dinámicamente**, contextualizados al contenido específico del post,
manteniendo el patrón de UI ya validado: **botones de un toque** que el usuario presiona
para enviar (no un chat libre — reduce riesgo de moderación y mantiene la simplicidad
mobile-first).

## 8.2 Pipeline

```
Nuevo post en posts_comunidad
   (texto + tipo de reto completado, vía reto_usuario_id)
        │
        ▼
Azure OpenAI · GPT-4o-mini (modelo económico, baja latencia — apto para alto volumen)
   + Glosario peruano (tono y expresiones locales)
   + Filtro de moderación (Azure AI Content Safety)
        │
        ▼
2-3 mensajes cortos guardados en comentarios_ia
   (se muestran como botones "Opciones para motivar")
        │
        ▼
Usuario presiona uno → se registra en interacciones_comunidad
   y comentarios_ia.fue_usado = true
```

### Por qué GPT-4o-mini
Los mensajes comunitarios son de **alto volumen y bajo riesgo** (frases cortas de aliento).
Usar un modelo más liviano que el de Fase 3/4 (que sí requiere razonamiento multimodal
complejo) es una decisión de **arquitectura costo-consciente** — relevante para el criterio
de "Escalabilidad digital" (parte del 30% de sostenibilidad del modelo de negocio).

## 8.3 Prompt (resumen)

```
Eres un compañero de la comunidad Quinu. Genera 3 mensajes cortos (máx. 12 palabras cada
uno) para animar a @{username} por lo siguiente:

Logro: "{texto_del_post}"
Tipo de reto: "{categoria_del_reto}"  # ej. actividad_fisica, alimentacion

Reglas:
- Tono cálido, cercano, peruano (puedes usar expresiones como "¡Vamos arriba!", "Sigue
  así, campeón/a").
- Nunca menciones cifras médicas (glucosa, peso, presión).
- Nunca emitas consejos médicos.
- Varía el primer mensaje, el segundo y el tercero (distintos enfoques: celebración,
  ánimo a continuar, identificación/empatía).
```

### Ejemplo
**Post:** "Completé mi reto de caminar 10 minutos después del almuerzo. ¡Me sentí genial!"
**Categoría:** `actividad_fisica`

**Salida generada:**
1. "¡Eso es, @WERdons! Pasito a pasito se llega lejos 🚶"
2. "10 minutos que valen oro para tu energía. ¡Sigue así!"
3. "A mí también me cuesta empezar, pero como tú, ¡ya estamos en eso!"

## 8.4 Moderación

Antes de guardar en `comentarios_ia`, cada mensaje pasa por **Azure AI Content Safety**
(categorías: odio, autolesión, sexual, violencia). Si algún mensaje es rechazado, se
regenera una vez; si falla de nuevo, se usa un mensaje de respaldo del catálogo estático
(`retos.categoria` → mapa de frases genéricas seguras), garantizando que la UI **nunca** se
quede sin opciones — importante para no romper la experiencia en demo.

## 8.5 Métrica de éxito

`comentarios_ia.fue_usado` es la señal principal para evaluar si los mensajes generados
resuenan con la comunidad (criterio "Estrategias de engagement" del jurado). Un *fallback*
a frases estáticas con baja tasa de uso, comparado con frases generadas con alta tasa de
uso, es un dato concreto y demostrable en el pitch.
