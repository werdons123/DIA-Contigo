# Fase 6 — Usuario Premium (Plan PRO)

## 6.1 Datos adicionales accesibles para la IA

Cuando `usuarios.plan_id` corresponde al Plan PRO **y** existe un registro en
`formularios_salud` con `consentimiento_datos_salud = true`, el motor de bienestar
(`03_ia_nutricional_bienestar.md`) recibe un bloque adicional de contexto:

| Dato del formulario de salud | Campo en BD | Uso en el prompt |
|---|---|---|
| Tiempo desde el diagnóstico | `formularios_salud.tiempo_diagnostico` | Ajusta el tono: usuarios "recientes" reciben explicaciones más básicas; "más de 5 años" reciben sugerencias más específicas |
| Estilo de alimentación habitual | `formularios_salud.estilo_alimentacion` | Si es "Delivery/Calle", las recomendaciones priorizan ajustes realistas para comer fuera (ej. "pide el arroz aparte y sírvete media porción") |
| Preferencias alimentarias | `formularios_salud.preferencias_alimentos` (array) | Filtra qué alimentos del glosario peruano (Fase 5) se priorizan en sugerencias |
| Nivel de actividad física | `formularios_salud.nivel_actividad` | Calibra la intensidad del reto diario (un usuario "Activo" recibe retos más exigentes que uno "Sedentario") |
| Actividades de preferencia | `formularios_salud.actividades_preferidas` (array) | El reto personalizado prioriza estas actividades cuando es coherente con el insight del día |
| Objetivos y restricciones | `formularios_salud.objetivos`, `formularios_salud.restricciones` | Restricciones (ej. alergias) se tratan como **reglas duras** — el prompt indica explícitamente "nunca sugieras alimentos listados en restricciones" |
| Historial de hábitos (longitudinal) | `registros_animo`, `registros_sueno`, `analisis_nutricionales` de los últimos 30 días | Permite frases como "esta es la tercera vez esta semana que duermes regular después de cenar fuera" — patrones, no diagnósticos |

## 6.2 Regla de composición del prompt

```
[Contexto base — todos los usuarios]
  + Glosario peruano (Fase 5)
  + Análisis nutricional del día (Fase 3)
  + Ánimo + Sueño del día

[SI usuario.plan == PRO Y consentimiento == true]
  + Perfil del formulario de salud
  + Resumen longitudinal (últimos 30 días, agregado — no datos crudos)
  + Restricciones alimentarias (reglas duras, no negociables)
```

Esta composición es **aditiva**: el usuario gratuito recibe exactamente el mismo motor de
IA, solo con menos contexto. Esto es importante para la justificación técnica — no hay dos
modelos distintos, hay **un único pipeline con contexto variable según el plan**, lo cual es
más simple de mantener y de escalar.

## 6.3 Resumen longitudinal — cómo se genera sin "inventar precisión clínica"

El resumen de 30 días **no** se calcula con fórmulas médicas. Se genera mediante una
agregación estadística simple (promedios y frecuencias) que luego se describe en lenguaje
natural por GPT-4o con instrucción explícita:

> "Describe tendencias de hábitos (frecuencia, no causalidad clínica). Usa frases como 'has
> registrado X varias veces' en lugar de 'esto está causando Y'."

Ejemplo de agregación (calculada en Python, no por IA):
```python
{
  "dias_con_registro": 18,
  "promedio_sueno": {"mal_dormido": 7, "regular": 9, "descansado": 2},
  "promedio_animo": {"triste": 2, "neutral": 10, "bien": 5, "feliz": 1},
  "platos_mas_frecuentes": ["arroz con pollo", "lomo saltado", "caldo de gallina"],
  "retos_completados": 11,
  "retos_sugeridos": 18
}
```

## 6.4 Transparencia con el usuario

En la pantalla de consentimiento (Fase 2.3, paso previo al formulario de salud), se muestra
una lista explícita y en lenguaje simple de qué datos adicionales usará la IA, replicando el
principio de "privacidad desde el diseño" exigido en la Sección 16 de las bases:

> "Si activas el Plan PRO, Quinu-IA también usará tus respuestas del formulario de salud
> (cuándo fuiste diagnosticado, cómo comes normalmente, tu actividad física y tus
> preferencias) junto con tu historial de los últimos 30 días para darte recomendaciones más
> precisas. Puedes desactivar esto en cualquier momento desde tu perfil."
