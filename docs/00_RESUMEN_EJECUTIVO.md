# Quinu-IA — Documento Técnico Maestro
### Desafío IA – Bagó Perú · Por un Futuro Más Sano en Todo

Este paquete documenta el rediseño funcional, la arquitectura de IA, el modelo de datos y la
arquitectura técnica de **Quinu-IA**, una aplicación B2C de acompañamiento para pacientes
crónicos (Reto 1, Historia 1 — "Vivir con diabetes sin sentirse perdido").

## Mapa del documento

| Archivo | Fase del prompt maestro | Contenido |
|---|---|---|
| `01_auditoria_ux_funcional_concurso.md` | Fase 1 | Auditoría UX/UI, funcional y de alineación con las bases del Desafío |
| `02_rediseno_funcional.md` | Fase 2 | Eliminación de "Personalización", nuevo enlace en Dashboard, pantalla Plan de Pago |
| `03_ia_nutricional_bienestar.md` | Fase 3 + 4 | Arquitectura de visión + IA nutricional y motor de bienestar |
| `04_identidad_peruana.md` | Fase 5 | Capa de contextualización cultural peruana |
| `05_usuario_premium.md` | Fase 6 | Reglas de acceso a datos del Plan PRO |
| `06_base_de_datos.md` | Fase 7 | Modelo de datos, tablas, relaciones, estrategia de mejora continua |
| `07_ia_comunidad.md` | Fase 8 | Motor generativo de mensajes de motivación |
| `08_arquitectura_tecnologia.md` | Fase 9 + 10 | Arquitectura completa, flujo de navegación, casos de uso, stack Azure, justificación técnica |

## Principio rector

Toda decisión de diseño se evaluó contra tres restricciones no negociables de las bases del
Desafío IA – Bagó Perú:

1. **Límites y exclusiones (Sección 7 de las bases):** la solución nunca diagnostica, nunca
   ajusta tratamientos ni simula ser un profesional de la salud. Por eso, en este documento
   se reemplaza el término *"Diagnóstico IA"* por **"Insight de Bienestar IA"**, y toda
   pantalla de resultados incluye el texto fijo:

   > *"Esto no es un diagnóstico médico. Quinu-IA es una herramienta de acompañamiento;
   > consulta siempre a tu profesional de salud."*

2. **Sostenibilidad del modelo de negocio (30% de la rúbrica):** la pantalla "Plan de Pago"
   no es un añadido cosmético — es el eje que conecta producto, datos e ingresos
   (freemium → PRO), y se diseñó para ser el centro de la narrativa del pitch.

3. **Privacidad y datos sensibles (Ley 29733):** usernames alfanuméricos, consentimiento
   explícito para datos de salud, y separación de datos PRO en la base de datos (ver
   `06_base_de_datos.md`).
