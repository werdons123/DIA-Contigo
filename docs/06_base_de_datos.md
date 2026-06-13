# Fase 7 — Base de Datos

## 7.1 Motor recomendado

**PostgreSQL** (vía Azure Database for PostgreSQL Flexible Server) sobre Azure SQL para el
MVP: tipos `JSONB` nativos (ideal para guardar las salidas estructuradas de IA sin perder su
forma), extensión `pgcrypto` para cifrado de campos sensibles, y costo más predecible para
una hackatón. El modelo es portable a Azure SQL si el equipo lo prefiere (se documenta en
`08_arquitectura_tecnologia.md`).

## 7.2 Diagrama entidad-relación (resumen)

```
usuarios ──┬── 1:1 ── suscripciones ──── N:1 ── planes
           │
           ├── 1:1 ── formularios_salud
           │
           ├── 1:N ── registros_animo
           ├── 1:N ── registros_sueno
           ├── 1:N ── analisis_nutricionales ── 1:1 ── resultados_ia_bienestar
           │                                                  │
           │                                                  └── 1:1 ── retos_usuario ── N:1 ── retos
           │
           ├── 1:N ── posts_comunidad ── 1:N ── interacciones_comunidad
           │                          └── 1:N ── comentarios_ia
           │
           └── 1:N ── historial_recomendaciones
           └── 1:N ── feedback_usuario
```

## 7.3 Tablas

### `usuarios`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `username_publico` | VARCHAR(20), UNIQUE | Alfanumérico anónimo (ej. `@User404`) — Sección 7 de las bases |
| `nombre`, `apellido` | VARCHAR | |
| `correo` | VARCHAR, UNIQUE | |
| `password_hash` | VARCHAR | bcrypt/argon2 |
| `fecha_nacimiento` | DATE | |
| `pais`, `region` | VARCHAR | `region` habilita el roadmap de Fase 5.5 |
| `fecha_registro` | TIMESTAMP | |

### `planes`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | SMALLINT, PK | `1 = Gratuito`, `2 = PRO` |
| `nombre` | VARCHAR | |
| `precio_mensual` | NUMERIC(6,2) | |
| `descripcion_corta` | TEXT | |
| `features` | JSONB | lista de features para renderizar la pantalla Plan de Pago sin hardcodear texto |

### `suscripciones`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | UUID, FK → usuarios | |
| `plan_id` | SMALLINT, FK → planes | |
| `estado` | VARCHAR | `activa`, `cancelada`, `vencida` |
| `fecha_inicio`, `fecha_fin` | TIMESTAMP | |

### `formularios_salud` (datos sensibles — solo PRO)
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | UUID, FK → usuarios, UNIQUE | |
| `tiempo_diagnostico` | VARCHAR | `reciente \| 1-5_anios \| mas_5_anios` |
| `estilo_alimentacion` | VARCHAR | `casera \| delivery \| dieta_estricta` |
| `preferencias_alimentos` | JSONB (array) | |
| `nivel_actividad` | VARCHAR | `sedentario \| ligero \| activo` |
| `actividades_preferidas` | JSONB (array) | |
| `objetivos`, `restricciones` | JSONB | campos abiertos, tratados como reglas duras (Fase 6.1) |
| `consentimiento_datos_salud` | BOOLEAN | |
| `consentimiento_fecha` | TIMESTAMP | requerido por la Sección 16 de las bases (consentimiento explícito y por escrito) |

### `registros_animo`
| Campo | Tipo |
|---|---|
| `id` | UUID, PK |
| `usuario_id` | UUID, FK |
| `valor` | VARCHAR (`triste\|neutral\|bien\|feliz`) |
| `fecha` | TIMESTAMP |

### `registros_sueno`
| Campo | Tipo |
|---|---|
| `id` | UUID, PK |
| `usuario_id` | UUID, FK |
| `valor` | VARCHAR (`mal_dormido\|regular\|descansado`) |
| `fecha` | TIMESTAMP |

### `analisis_nutricionales`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | UUID, FK | |
| `imagen_url` | VARCHAR | ruta en Azure Blob Storage |
| `resultado_vision` | JSONB | salida cruda de Azure AI Vision (tags, caption, OCR) |
| `resultado_nutricional` | JSONB | esquema de Fase 3.2 |
| `fecha` | TIMESTAMP | |

### `resultados_ia_bienestar`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `analisis_nutricional_id` | UUID, FK → analisis_nutricionales | |
| `registro_animo_id`, `registro_sueno_id` | UUID, FK | |
| `resultado` | JSONB | esquema de Fase 3.3 (Insight de Bienestar) |
| `usado_contexto_premium` | BOOLEAN | trazabilidad — ¿este insight usó datos PRO? |
| `fecha` | TIMESTAMP | |

### `retos`
Catálogo maestro de retos (incluye versión "general" y "personalizada" — Fase 2 del
documento original distinguía "retos generales" vs "retos personalizados").
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `titulo`, `descripcion` | VARCHAR/TEXT | |
| `categoria` | VARCHAR | `actividad_fisica \| alimentacion \| descanso \| social` |
| `es_generado_por_ia` | BOOLEAN | distingue retos del catálogo vs. generados dinámicamente |
| `contexto_peruano` | BOOLEAN | |

### `retos_usuario`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | UUID, FK | |
| `reto_id` | UUID, FK → retos (nullable si fue generado ad-hoc por IA) |
| `reto_personalizado_texto` | JSONB | snapshot del reto generado por IA (título/descripción/ícono) |
| `resultado_ia_bienestar_id` | UUID, FK | de qué insight surgió |
| `estado` | VARCHAR | `pendiente \| completado \| compartido` |
| `medalla_desbloqueada` | BOOLEAN | |
| `fecha_creacion`, `fecha_completado` | TIMESTAMP | |

### `posts_comunidad`
| Campo | Tipo |
|---|---|
| `id` | UUID, PK |
| `usuario_id` | UUID, FK |
| `reto_usuario_id` | UUID, FK, nullable |
| `texto` | TEXT |
| `imagen_url` | VARCHAR, nullable |
| `fecha` | TIMESTAMP |

### `interacciones_comunidad`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `post_id` | UUID, FK | |
| `usuario_id` | UUID, FK | quién interactúa |
| `tipo` | VARCHAR | `motivacion_enviada` |
| `texto_enviado` | TEXT | el mensaje específico que se envió (de catálogo o IA) |
| `fecha` | TIMESTAMP | |

### `comentarios_ia`
Mensajes generados por el motor de Fase 8, **sugeridos** a los pares antes de enviarse
(quedan registrados aunque no se usen, para medir efectividad).
| Campo | Tipo |
|---|---|
| `id` | UUID, PK |
| `post_id` | UUID, FK |
| `texto_generado` | TEXT |
| `fue_usado` | BOOLEAN |
| `fecha` | TIMESTAMP |

### `historial_recomendaciones`
Vista desnormalizada / tabla de auditoría que une cada `resultado_ia_bienestar` con sus
`retos_usuario` derivados — facilita reportes y el resumen longitudinal de Fase 6.3 sin
recalcular joins complejos en cada request.

### `feedback_usuario`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | UUID, FK | |
| `resultado_ia_bienestar_id` | UUID, FK | |
| `util` | BOOLEAN | "¿te sirvió esta recomendación?" |
| `comentario` | TEXT, nullable | |
| `fecha` | TIMESTAMP | |

## 7.4 Estrategia para mejorar futuras recomendaciones

1. **Few-shot dinámico:** las filas de `feedback_usuario` con `util = true` y mayor
   *engagement* (reto completado y compartido) se seleccionan periódicamente como ejemplos
   *few-shot* para el prompt de Fase 4 — el modelo "aprende" qué tono y tipo de reto
   funciona mejor para perfiles similares, sin necesidad de *fine-tuning*.
2. **Segmentación por agregados, no por individuo:** el resumen longitudinal (Fase 6.3) se
   calcula por usuario, pero los patrones que mejoran el *prompt global* se calculan por
   **cohortes** (ej. "usuarios con `nivel_actividad = sedentario` y `estilo_alimentacion =
   delivery`"), evitando perfiles individuales sensibles en el prompt compartido.
3. **Catálogo de retos vivo:** cada `reto_personalizado_texto` generado por IA y marcado
   como `completado` + `medalla_desbloqueada = true` es candidato a promoverse al catálogo
   `retos` (con `es_generado_por_ia = true`), creando un ciclo de mejora continua curado por
   uso real.
4. **Migración a vector store:** cuando el volumen de `feedback_usuario` y
   `historial_recomendaciones` crezca, estos datos agregados pueden indexarse en **Azure AI
   Search** para alimentar el patrón RAG mencionado en Fase 5.5, cerrando el ciclo
   dato → insight → producto → mejor dato.
