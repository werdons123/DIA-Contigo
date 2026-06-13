# Fase 1 — Auditoría

## 1.1 Auditoría UX/UI

### Consistencia visual
El sistema de diseño del mockup (fondo `#F8F9FA`, verde pastel `#D9FDD3`, azul `#5AA9E6`,
contenedores crema, radios de 16px, tipografía SF Pro) es coherente y transmite calma —
adecuado para un usuario con diabetes que ya enfrenta ansiedad por su condición (ver
Historia 1: "se angustia porque no logra identificar qué provocó los picos").

**Hallazgo:** el lenguaje visual está más cerca de iOS/Material que de **Fluent Design 2**
(el sistema de Microsoft). Para una hackatón patrocinada por Bagó pero evaluada con foco en
"Desarrollo de IA aplicada a producto" con stack Azure, conviene declarar explícitamente la
decisión: *"Quinu-IA prioriza un lenguaje de wellness clínico cálido sobre el Fluent puro,
pero adopta tipografía Segoe UI Variable e iconografía Fluent para mantener consistencia
con el ecosistema Microsoft 365 / Copilot."* Esto convierte una posible objeción del jurado
en una decisión de diseño justificada.

**Acción:** reemplazar emojis decorativos por iconos Fluent UI (`@fluentui/react-icons` o,
en Streamlit, `streamlit-extras` + iconos SVG Fluent) en botones de navegación y estados
(bloqueado/desbloqueado), conservando emojis solo en contenido generado por usuarios
(posts de comunidad), donde aportan calidez.

### Navegación
- La barra inferior fija (Inicio / Comunidad) es adecuada para el alcance actual, pero
  **falta un punto de entrada al perfil del usuario y al Plan de Pago/suscripción** — crítico
  ahora que el modelo de negocio es freemium.
- **Riesgo identificado:** sin un tercer ítem o un acceso desde el header, el usuario PRO no
  tiene forma de ver "mi plan actual" ni de gestionar su suscripción. Se resuelve agregando
  un ícono de perfil en el header del Dashboard (ver `02_rediseno_funcional.md`) que abre un
  panel con: datos de cuenta, plan actual, formulario de salud (si es PRO) y cierre de
  sesión.

### Jerarquía visual
- El botón "Descubrir mi balance y análisis metabólico" domina correctamente la pantalla —
  es la acción de mayor valor.
- El badge bloqueado (gris) con tooltip *hover* no funciona en móvil (no hay hover táctil).
  **Acción:** reemplazar el tooltip por un texto visible permanente debajo del badge
  ("Bloqueada — completa el reto para desbloquearla").

### Flujo del usuario
El flujo original era: Login → Registro → *Personalización (eliminada)* → Formulario de
salud → Dashboard. Esto obligaba a **todo** usuario nuevo a llenar un formulario largo antes
de ver valor — una de las causas más comunes de abandono temprano (afecta directamente el
criterio "Probabilidad de retención a 90 días", 20% de la rúbrica).

**Acción (Fase 2):** el formulario de salud completo deja de ser un paso obligatorio de
onboarding y se convierte en el **diferenciador del Plan PRO**. El usuario gratuito llega al
Dashboard en 2 pantallas (Login/Registro → Dashboard) y descubre valor inmediato (análisis
de su primera foto de comida).

### Accesibilidad
- Contraste verificado: texto sobre verde pastel (`#2F6B49` sobre `#D9FDD3`) y sobre azul
  suave (`#2C6FA3` sobre `#EAF4FD`) cumplen WCAG AA para texto normal.
- El banner amarillo de aviso (`#FFF6DD` con texto `#8A6D1F`) cumple AA pero está cerca del
  límite — se recomienda no reducir su tamaño de fuente por debajo de 12.5px.
- Áreas táctiles: todos los botones y pills superan los 40px de alto, adecuado para dedos
  con movilidad reducida (relevante en usuarios de 50+ años, como Carlos, 52 años).
- **Pendiente:** añadir `aria-live` / anuncios de estado cuando se revela el panel de
  resultados (cambio dinámico de contenido), y soporte de "Reducir movimiento" para la
  animación de aparición del panel.

### Diseño mobile-first
Correcto: layout de una columna, tarjetas apiladas, navegación inferior fija. Se mantiene en
el rediseño.

### Alineación con productos Microsoft
Ver nota de "Consistencia visual" — se adopta tipografía Segoe UI Variable como *fallback*
de SF Pro en web/Streamlit (SF Pro no está disponible fuera de macOS/iOS sin licencia), y se
documenta como decisión de portabilidad de marca.

---

## 1.2 Auditoría Funcional

### Funciones existentes (heredadas del mockup)
- Autenticación (login / registro).
- Formulario de salud (diagnóstico, alimentación, preferencias, actividad física).
- Carga de foto de comida/menú.
- Registro de estado de ánimo (4 niveles) y calidad de sueño (3 niveles).
- "Balance del día" con texto generado y reto diario sugerido.
- Sistema de medallas (bloqueada/desbloqueada) ligado a compartir logros.
- Comunidad: feed de posts, usernames anónimos, medallas, botones de motivación.

### Funciones faltantes (críticas para el MVP del hackatón)
1. **Plan de Pago / freemium** — exigido explícitamente por la Fase 2 y por el criterio de
   "Sostenibilidad del modelo de negocio" (30%, el de mayor peso).
2. **Pipeline real de IA nutricional** — el mockup mostraba un resultado *hardcodeado*
   ("Seco de Res con Frijoles"). Se requiere el pipeline Computer Vision + GPT-4o descrito en
   `03_ia_nutricional_bienestar.md`.
3. **Historial / seguimiento longitudinal** — el tab "Progress" aparece en el mockup de
   referencia (`Quinu — Menu Analysis`) pero no estaba especificado; se incorpora como parte
   del Plan PRO ("Historial de hábitos", "Seguimiento longitudinal").
4. **Consentimiento informado de datos de salud** — obligatorio por la Ley 29733 y por la
   sección "Términos y condiciones adicionales sobre tratamiento de datos de terceros" de las
   bases. Se añade una pantalla de consentimiento explícito antes del formulario de salud
   (Plan PRO).
5. **Motor generativo de comunidad** (Fase 8) — actualmente los mensajes de motivación son
   estáticos.
6. **Perfil de usuario / gestión de cuenta y suscripción.**

### Mejoras recomendadas
- Cachear resultados de análisis de imagen por sesión para evitar llamadas repetidas a Azure
  (costo + latencia).
- Mostrar siempre el disclaimer "Estimaciones basadas en visión artificial e IA" de forma
  visible y persistente cerca de cualquier resultado de IA — refuerza el cumplimiento de la
  Sección 7 y genera confianza.
- Registrar feedback explícito del usuario sobre cada recomendación ("¿te sirvió este
  consejo?") para alimentar la estrategia de mejora continua (`06_base_de_datos.md`).

### Riesgos técnicos
| Riesgo | Impacto | Mitigación |
|---|---|---|
| Azure Computer Vision / GPT-4o no reconocen platos peruanos con precisión (sesgo de datasets globales) | Recomendaciones poco creíbles | Usar GPT-4o **multimodal** con *system prompt* que incluya un glosario de platos peruanos (`04_identidad_peruana.md`) en lugar de depender solo de tags de Computer Vision; permitir corrección manual del nombre del plato por el usuario |
| Llamadas síncronas a IA dentro de Streamlit bloquean la UI | Mala UX, percepción de app lenta | `st.spinner` + diseño de *loading states* ya presentes en el mockup ("Descubrir mi balance...") + timeouts y *caching* con `st.cache_data` |
| Datos de salud sensibles en base de datos | Incumplimiento Ley 29733 / descalificación | Cifrado at-rest (Azure SQL TDE / pgcrypto), separación de tabla `formularios_salud` con acceso restringido, consentimiento explícito registrado con timestamp |
| Dependencia de claves de Azure no disponibles durante el desarrollo del hackatón | Bloqueo del equipo | Capa de servicio (`services/`) con modo *offline/demo* documentado que usa datos de ejemplo realistas — no es un "placeholder", es un modo de operación declarado y necesario para demos sin conectividad |

---

## 1.3 Alineación con las bases del Desafío IA – Bagó Perú

| Criterio de la rúbrica | Peso | Cómo lo cubre el rediseño |
|---|---|---|
| Adecuación a necesidades del usuario | 15% | Onboarding corto (2 pantallas), valor inmediato con análisis de foto, lenguaje cálido y sin jerga clínica |
| Impacto humano | 20% | Insight de bienestar combina nutrición + ánimo + sueño → conecta hábitos diarios con cómo se siente Carlos, sin diagnosticar |
| Calidad de la solución técnica | 15% | Uso justificado de GPT-4o multimodal (no decorativo): análisis de imagen, generación de insights, generación de mensajes comunitarios; manejo explícito de límites éticos |
| Experiencia conversacional UI/UX y adopción | 20% | Gamificación (medallas), comunidad de pares, retos diarios cortos y peruanos — diseñados para retención a 90 días |
| Sostenibilidad del modelo de negocio | 30% | Freemium claro (Gratis/PRO) con diferenciación de valor real (más datos → más personalización), descrito en `02_rediseno_funcional.md` y `08_arquitectura_tecnologia.md` |

### Alineación con el perfil técnico (Hackathon-Cursos-Microsoft)
El stack elegido (Azure AI Services, Azure OpenAI, Computer Vision, modelos multimodales,
Azure SQL/PostgreSQL) corresponde directamente al **Perfil 3: Técnico – Desarrollo IA** del
documento de cursos (Microsoft Foundry SDK, RAG con datos propios, optimización y evaluación
de modelos). La capa de contexto peruano (`04_identidad_peruana.md`) se implementa como un
patrón **RAG ligero** (contexto inyectado / recuperación desde un almacén de conocimiento
local), que es exactamente lo que cubre el módulo *"Develop a RAG-based solution with your
own data using Microsoft Foundry"*. Esto da al equipo un argumento sólido para el documento
técnico de uso de IA exigido en la Sección 9 de las bases.
