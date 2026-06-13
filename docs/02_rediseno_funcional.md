# Fase 2 — Rediseño Funcional

## 2.1 Eliminación de "Personalización"

La pantalla interstitial **"¿Quisieras una atención más personalizada?"** se elimina por
completo del flujo de onboarding.

**Razón:** duplicaba la decisión que ahora vive, de forma más clara y con valor de negocio
explícito, en la pantalla **Plan de Pago** (Fase 2.2). Mantenerla generaba dos preguntas
redundantes sobre "personalización" en pantallas distintas, lo que confunde al usuario y
alarga el onboarding (afecta retención).

### Flujo anterior
```
Login → Registro → Personalización → Formulario de salud → Dashboard
```

### Flujo nuevo
```
Login → Registro → Dashboard
                       │
                       ├─ (link) "Conoce nuestros planes..." → Plan de Pago
                       │                                          │
                       │                                          └─ Plan PRO → Consentimiento → Formulario de salud
                       │
                       └─ Análisis de comida / ánimo / sueño → Insight de Bienestar
```

El Formulario de salud (pantalla 4 del mockup original) **no se elimina**: se reposiciona
como el paso de activación del Plan PRO, precedido por una pantalla de consentimiento de
datos sensibles.

---

## 2.2 Dashboard — nuevo enlace a Plan de Pago

Debajo del banner existente:

> "¡Queremos conocerte más! Por favor completa tu formulario base aquí."

se agrega una segunda línea, en texto subrayado, de menor peso visual (para no competir con
el CTA principal):

> **"Conoce nuestros planes y desbloquea recomendaciones más personalizadas."**

### Especificación visual
- Tipografía: 13px, peso 600, color `var(--blue-text)` (`#2C6FA3`), `text-decoration:
  underline`.
- Posición: línea independiente, alineada a la izquierda, con 6px de separación respecto al
  banner amarillo.
- Interacción: `onClick` navega a la nueva pantalla **Plan de Pago** (transición tipo
  *push*, con botón de retorno).
- Accesibilidad: el elemento es un `<button>`/`<a>` real (no un `<div>` con `onClick`), con
  `aria-label="Ver planes de Quinu-IA"`.

---

## 2.3 Nueva pantalla: Plan de Pago

### Objetivo
Comunicar la propuesta de valor freemium en una sola pantalla, sin fricción, dejando claro
**qué gana el usuario** al pasar a PRO — no solo qué pierde si se queda gratis (enfoque
positivo, alineado con la guía de "Diseño para desarrollo de la app": lenguaje activo y
orientado al usuario).

### Estructura

1. **Encabezado:** "Elige tu plan Quinu" + subtítulo: "Cambia de plan cuando quieras."
2. **Selector de facturación** (opcional para MVP, recomendado para el pitch): toggle
   "Mensual / Anual (2 meses gratis)" — refuerza el criterio de "Modelo sostenible en el
   tiempo".
3. **Dos tarjetas apiladas** (mobile-first; en pantallas anchas se muestran lado a lado):

#### Tarjeta — Plan Gratuito
- Fondo: `var(--bg)` (`#F8F9FA`), borde 1px `var(--line)`.
- Encabezado: "Gratuito" + "S/ 0 / siempre".
- Lista con ícono de check (`var(--text-soft)`):
  - Análisis de fotografía de alimentos
  - Registro de estado de ánimo
  - Registro de nivel de sueño
  - Recomendaciones generales
  - Retos generales
- CTA secundario: "Tu plan actual" (deshabilitado) o "Continuar gratis".

#### Tarjeta — Plan PRO
- Fondo: gradiente sutil `var(--green)` → `var(--blue-soft)`, borde 2px `var(--blue)`
  (mismo patrón de "acento" que ya usa la app para estados desbloqueados).
- Badge superior: "Recomendado" sobre `var(--green)` con texto `var(--green-text)`.
- Encabezado: "PRO" + precio (ej. "S/ 19.90 / mes").
- Lista con ícono de check en `var(--green-deep)`, **incluye explícitamente "Todo lo del
  plan Gratuito" como primer ítem** y luego:
  - Formulario de salud completo
  - Perfil nutricional avanzado
  - Historial de hábitos y seguimiento longitudinal
  - Recomendaciones y retos altamente personalizados
  - Mayor precisión de IA (acceso a tu contexto completo)
- CTA primario: "Pasar a PRO" (`btn-giant`, mismo estilo que "Descubrir mi balance...").

### Diferenciación visual
La diferenciación no es solo de color: la tarjeta PRO usa **borde de 2px** (vs 1px en
Gratuito), **badge "Recomendado"**, **iconos de check en verde** (vs gris en Gratuito) y un
**ícono de corona** junto al título "PRO". Esto sigue el patrón ya validado en el mockup
(badge bloqueado gris vs. desbloqueado verde con glow) — coherencia de sistema: *"gris =
bloqueado/básico, verde = desbloqueado/premium"*.

### Microcopy (tono del documento "Guía de diseño")
- Free → PRO CTA: **"Pasar a PRO"** (verbo activo, sin jerga de "upgrade").
- Texto de apoyo bajo el CTA PRO: *"Cancela cuando quieras desde tu perfil."* (reduce
  fricción de compra, refuerza confianza — importante para retención a 90 días).

### Tras seleccionar PRO
1. Pantalla de **consentimiento de datos de salud** (texto claro, casilla de aceptación
   explícita, requerido por la Sección 16 de las bases).
2. Pantalla **Formulario de salud** (la del mockup original, sin cambios de contenido).
3. Retorno al Dashboard, ahora con la franja superior cambiada de "completa tu formulario
   base" a un indicador de plan: **"Plan PRO activo · IA personalizada activada"** sobre
   fondo `var(--green)`.
