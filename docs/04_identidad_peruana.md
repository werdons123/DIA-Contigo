# Fase 5 — Identidad Peruana

## 5.1 Por qué importa para el concurso

La Sección 4 de las bases exige que las soluciones **"resuelvan problemas reales del
contexto peruano"**. La mayoría de modelos de IA generalista (entrenados con datos
predominantemente estadounidenses/europeos) recomiendan por defecto: "sal a correr", "come
una ensalada de quinoa con kale", "prueba el yoga en casa con una app". Esto es
**culturalmente disonante** para Carlos (contador, 52 años, Lima) y reduce la probabilidad
de adopción real — exactamente el punto que evalúa "Experiencia conversacional UI/UX y
adopción" (20%).

## 5.2 Implementación: Base de conocimiento peruana (RAG ligero)

Se implementa como un archivo de contexto estructurado
(`services/peru_knowledge.py` / `data/contexto_peruano.json`) que se inyecta en **todos**
los prompts de Fase 3, 4 y 8. No requiere una base vectorial para el MVP del hackatón (el
contexto es pequeño y cabe en el prompt), pero la estructura está pensada para migrar a
**Azure AI Search + RAG** (módulo *"Develop a RAG-based solution with your own data using
Microsoft Foundry"*) si el proyecto escala — esto se documenta como roadmap.

### Categorías del glosario

| Categoría | Ejemplos incluidos |
|---|---|
| Alimentos / superalimentos andinos | Quinua, tarwi, kiwicha, cañihua, camote, pallares, olluco, oca, maíz morado |
| Proteínas locales accesibles | Anchoveta, pejerrey, pollo a la brasa (versión casera al horno), huevo de corral |
| Platos tradicionales y su perfil | Lomo saltado, ají de gallina, causa, tacu tacu, seco de res, ceviche, cau cau |
| Actividad física / baile | Marinera, huayno, festejo, caminata al mercado, subir escaleras (zonas urbanas con
  pendiente como Lima/Cusco/Arequipa), bicicleta urbana |
| Costumbres y contexto social | Almuerzo familiar como comida principal, "lonchera", comer fuera por trabajo (combis,
  mercados, polladas), horarios laborales peruanos |
| Bienestar / relajación | Mate de coca / manzanilla / muña, siesta corta, música criolla, espacios verdes
  urbanos (parques, malecones) |

## 5.3 Regla de uso en prompts

El *system prompt* compartido por los tres motores de IA incluye la instrucción:

> "Cuando sugieras alimentos, actividades físicas o formas de relajación, prioriza opciones
> del contexto peruano (ver glosario adjunto) sobre alternativas genéricas. Si sugieres
> baile o ejercicio recreativo, considera marinera, huayno o festejo como opciones válidas.
> Si sugieres alimentos, prioriza quinua, tarwi, kiwicha, anchoveta, camote, pallares u otros
> del glosario cuando sean nutricionalmente apropiados. Evita referencias a comida o cultura
> estadounidense genérica (ej. 'kale', 'smoothie bowl', 'gimnasio CrossFit') salvo que el
> usuario las mencione primero."

## 5.4 Ejemplo aplicado

**Entrada:** análisis nutricional detecta exceso de carbohidratos simples + ánimo "neutral"
+ sueño "regular".

**Salida genérica (no deseada):**
> "Intenta una ensalada de kale con quinoa y sal a caminar al gimnasio."

**Salida con capa peruana (deseada):**
> "Para tu próxima comida, podrías cambiar parte del arroz por una porción de tarwi o
> pallares — aportan proteína vegetal y ayudan a que la glucosa suba más despacio. Y si
> quieres moverte un poco hoy, una caminata de 10 minutos al mercado o un par de canciones
> de marinera en casa pueden ayudarte a sentirte con más energía."

## 5.5 Extensibilidad

El archivo `contexto_peruano.json` está versionado y puede crecer con aportes regionales
(sierra, selva, costa) sin tocar código — cumple el criterio de **escalabilidad** y permite
que, en una iteración futura, el contenido se cargue dinámicamente desde Azure AI Search
indexado por región del usuario (campo `region` en la tabla `usuarios`, ver
`06_base_de_datos.md`).
