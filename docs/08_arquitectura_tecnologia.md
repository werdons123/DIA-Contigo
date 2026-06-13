# Fase 9 — Tecnología · Fase 10 — Arquitectura de Desarrollo

## 9.1 Diagrama de arquitectura

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (navegador / móvil)                       │
│                    Streamlit app — UI mobile-first                        │
└──────────────────────────────────┬───────────────────────────────────────┘
                                     │ HTTPS
┌────────────────────────────────────────────────────────────────────────────┐
│  Azure Container Apps / Azure App Service (Linux, Python 3.11)             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  app.py  (router de pantallas + estado de sesión)                  │    │
│  │  screens/  (login, registro, dashboard, plan_pago, formulario,     │    │
│  │             compartir, comunidad)                                   │    │
│  │  services/                                                          │    │
│  │   ├─ vision_service.py   → Azure AI Vision (Image Analysis 4.0)    │    │
│  │   ├─ openai_service.py   → Azure OpenAI (GPT-4o, GPT-4o-mini)      │    │
│  │   ├─ content_safety.py   → Azure AI Content Safety                 │    │
│  │   └─ peru_knowledge.py    → Glosario peruano (RAG ligero)          │    │
│  │  database/  (SQLAlchemy ORM + sesión)                               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────┬───────────────────────┬───────────────────────────┬─────────────────┘
       │                        │                           │
       ▼                        ▼                           ▼
┌──────────────┐   ┌─────────────────────────┐   ┌──────────────────────────┐
│ Azure Blob    │   │ Azure Database for       │   │ Azure AI Services        │
│ Storage       │   │ PostgreSQL Flexible      │   │ (Vision, OpenAI,         │
│ (fotos de     │   │ Server                   │   │  Content Safety)         │
│ comida)       │   │                          │   │                          │
└──────────────┘   └─────────────────────────┘   └──────────────────────────┘
```

## 9.2 Justificación del stack

| Componente | Elección | Justificación |
|---|---|---|
| Frontend | **Streamlit** | Exigido por las bases (Fase 9). Streamlit permite construir la UI mobile-first del mockup con `st.session_state` como router y CSS personalizado inyectado vía `st.markdown(..., unsafe_allow_html=True)`, replicando el sistema de diseño (`#F8F9FA`, `#D9FDD3`, radios de 16px) sin un framework JS adicional |
| Backend | **Python 3.11** | Mismo runtime que Streamlit — un solo proceso para el MVP, con capa `services/` desacoplada para poder extraerse a una API FastAPI en una iteración futura sin reescribir lógica de negocio |
| Visión | **Azure AI Vision — Image Analysis 4.0** | *Grounding* objetivo de la imagen (tags, caption, OCR de menús) antes de pasar a GPT-4o |
| Modelo principal | **Azure OpenAI GPT-4o** (multimodal) | Único modelo capaz de **ver la imagen directamente** y razonar en lenguaje natural sobre balance nutricional + contexto peruano en un solo paso — uso justificado, no decorativo |
| Modelo comunidad | **Azure OpenAI GPT-4o-mini** | Costo/latencia óptimos para mensajes cortos de alto volumen (Fase 8) |
| Moderación | **Azure AI Content Safety** | Obligatorio para contenido generado en una comunidad de pacientes |
| Base de datos | **Azure Database for PostgreSQL Flexible Server** | `JSONB` para los esquemas de IA de Fase 3/4, cifrado en tránsito y reposo, costo predecible |
| Almacenamiento de imágenes | **Azure Blob Storage** | Las fotos de comida no se guardan en la base de datos — solo su URL |
| Infraestructura | **Azure Container Apps** | *Scale-to-zero* (costo cero fuera de demo/uso real — clave para "Modelo sostenible" sin depender de terceros) y despliegue simple vía Dockerfile |
| Autenticación | **Hashing local (passlib/argon2)** para el MVP, con ruta de migración a **Microsoft Entra ID External ID** documentada como roadmap (alineado al ecosistema Microsoft) |

## 9.3 Flujo de navegación completo

```
┌──────────┐     ┌───────────┐     ┌────────────────────────────────────┐
│  Login   │────▶│ Registro  │────▶│              Dashboard               │◀───┐
└────┬─────┘     └───────────┘     │  - Subir foto                        │    │
     │                              │  - Ánimo / Sueño                     │    │
     │ "Olvidé mi contraseña"       │  - "Descubrir mi balance..."         │    │
     ▼                              │  - Insight de Bienestar + Reto       │    │
┌──────────────┐                    │  - "Conoce nuestros planes..." ──┐   │    │
│ Recuperar    │                    │  - "Compartir en comunidad" ───┐ │   │    │
│ contraseña   │                    └─────────────────────────────────┼─┼───┘    │
└──────────────┘                                                      │ │        │
                                                                       │ │        │
                              ┌────────────────────────────────────────┘ │        │
                              ▼                                          │        │
                    ┌──────────────────┐                                 │        │
                    │  Plan de Pago     │                                 │        │
                    │  Gratis | PRO     │                                 │        │
                    └────────┬──────────┘                                │        │
                              │ "Pasar a PRO"                             │        │
                              ▼                                          │        │
                    ┌──────────────────┐    ┌─────────────────────┐     │        │
                    │  Consentimiento   │───▶│ Formulario de salud  │────┘ (vuelve│
                    │  de datos PRO     │    └─────────────────────┘      al Dash)│
                    └──────────────────┘                                          │
                                                                                    │
                              ┌─────────────────────────────────────┐             │
                              ▼                                       │             │
                    ┌──────────────────┐     ┌─────────────────┐    │             │
                    │ Compartir logro   │────▶│   Comunidad      │───┴─────────────┘
                    │ (medalla unlock)  │     │  feed + IA       │
                    └──────────────────┘     └─────────────────┘
```

> La pantalla "Personalización" del flujo original queda **eliminada** (Fase 2.1).

## 9.4 Casos de uso principales

| ID | Caso de uso | Actor | Flujo resumido |
|---|---|---|---|
| CU-01 | Registro e ingreso | Usuario nuevo | Registro → Dashboard (sin pasos intermedios) |
| CU-02 | Análisis de comida (Gratis) | Usuario Free | Sube foto → Vision + GPT-4o (contexto base) → Insight de Bienestar + reto general |
| CU-03 | Análisis de comida (PRO) | Usuario PRO | Igual a CU-02, + contexto de formulario de salud y resumen de 30 días → Insight más específico + reto personalizado |
| CU-04 | Activación de Plan PRO | Usuario Free | Dashboard → "Conoce nuestros planes" → Plan de Pago → "Pasar a PRO" → Consentimiento → Formulario de salud → Dashboard actualizado |
| CU-05 | Completar reto y compartir | Usuario (cualquier plan) | Insight muestra reto → usuario lo realiza → "Compartir mi progreso" → medalla se desbloquea → post visible en Comunidad |
| CU-06 | Interacción comunitaria con IA | Usuario (cualquier plan) | Ve post de otro usuario → IA sugiere 2-3 mensajes (Fase 8) → usuario presiona uno → se registra interacción |
| CU-07 | Registro diario de hábitos sin foto | Usuario (cualquier plan) | Usuario actualiza solo ánimo/sueño (sin nueva foto) → sistema reutiliza el análisis nutricional más reciente para generar un Insight actualizado |
| CU-08 | Feedback sobre recomendación | Usuario (cualquier plan) | Tras ver el Insight, usuario indica "¿te sirvió?" → se guarda en `feedback_usuario` (Fase 7.4) |

## 9.5 Mejoras UX/UI incorporadas (resumen ejecutivo de la Fase 1)

1. Onboarding reducido de 4 a 2 pantallas antes de mostrar valor.
2. Sustitución de tooltips por etiquetas visibles permanentes (accesibilidad táctil).
3. Iconografía Fluent en navegación/estado, emojis reservados a contenido generado por
   usuarios.
4. Disclaimers de IA siempre visibles (no en tooltip), reforzando confianza y cumplimiento.
5. Indicador de plan activo en el Dashboard ("Plan PRO activo · IA personalizada
   activada").
6. Acceso a perfil/suscripción desde el header (gap identificado en la auditoría de
   navegación).

## 9.6 Justificación técnica general

- **Una sola capa de servicios (`services/`)** abstrae todas las llamadas a Azure. Esto
  permite (a) testear la lógica de negocio sin credenciales reales mediante una
  implementación de respaldo basada en datos de ejemplo realistas — documentada como **modo
  demo**, no como código temporal — y (b) migrar de Streamlit a una arquitectura
  cliente-servidor (ej. FastAPI + frontend separado) sin reescribir la lógica de IA ni de
  base de datos.
- **El modelo de datos (Fase 7) separa explícitamente lo sensible** (`formularios_salud`)
  del resto, lo que facilita aplicar controles de acceso y cifrado diferenciados — relevante
  para el criterio ético/legal de la rúbrica.
- **El pipeline de IA es aditivo por plan** (Fase 6.2): un solo motor, contexto variable.
  Esto evita mantener dos sistemas de IA distintos (Free/PRO), reduciendo deuda técnica y
  facilitando la narrativa de "escalabilidad" en el pitch.
- **Azure Container Apps con scale-to-zero** convierte el costo de infraestructura en
  variable, alineado directamente con la pregunta de la rúbrica: *"¿Puede sostenerse sin
  depender de terceros?"* — el costo crece con el uso real (y con los ingresos PRO), no
  antes.

## 9.7 Roadmap post-hackatón (para la sección "Roadmap" del pitch)

1. Migrar autenticación a Microsoft Entra ID External ID.
2. Migrar el glosario peruano (Fase 5) a Azure AI Search con indexación por región.
3. Notificaciones push (recordatorios de registro diario) vía Azure Notification Hubs.
4. Exportar "reportes claros para el médico tratante" (PDF) desde el resumen longitudinal
   de Fase 6.3 — requerido explícitamente por la Sección 5 de las bases para la Historia 1.
5. Programa de fidelización de medallas con recompensas reales (alianzas locales) como
   segunda palanca de monetización.
