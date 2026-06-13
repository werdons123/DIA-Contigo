# Quinu-IA

Acompañamiento diario para personas con diabetes tipo 2, con análisis de
alimentos por IA, insights de bienestar contextualizados a Perú, gamificación y
comunidad de pares.

Proyecto desarrollado para el **Desafío IA – Bagó Perú** (Reto 1, Historia 1).
La documentación completa de arquitectura, auditoría y decisiones de diseño
está en [`docs/`](./docs), organizada por fase del análisis (ver
[`docs/00_RESUMEN_EJECUTIVO.md`](./docs/00_RESUMEN_EJECUTIVO.md)).

## Estructura del proyecto

```
quinu-ia/
├── app.py                  # Punto de entrada (router de pantallas Streamlit)
├── config.py                # Configuración central / variables de entorno
├── requirements.txt
├── Dockerfile
├── docs/                     # Auditoría, rediseño y arquitectura (Fases 1-10)
├── database/
│   ├── models.py             # Modelos SQLAlchemy (Fase 7)
│   └── db.py                 # Engine, sesión y datos semilla
├── services/
│   ├── vision_service.py      # Azure AI Vision (Fase 3.1)
│   ├── openai_service.py      # Azure OpenAI: nutrición, bienestar, comunidad
│   ├── content_safety.py      # Azure AI Content Safety (Fase 8.4)
│   ├── storage_service.py      # Azure Blob Storage
│   ├── peru_knowledge.py       # Glosario peruano / RAG ligero (Fase 5)
│   ├── longitudinal.py         # Resumen de hábitos de 30 días (Fase 6.3)
│   └── schemas.py               # Esquemas Pydantic de salidas de IA
├── screens/                  # Una pantalla por archivo (login, dashboard, ...)
├── components/               # Componentes de UI reutilizables
└── utils/                     # Estilos (CSS) y helpers de sesión/autenticación
```

## Ejecución local (modo demo, sin Azure)

No se necesitan credenciales para probar la app completa: si las variables de
Azure no están configuradas, cada servicio usa datos de ejemplo realistas
("modo demo", documentado en `docs/08_arquitectura_tecnologia.md`, sección 9.6).

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # opcional, deja los valores vacíos para modo demo

streamlit run app.py
```

La base de datos por defecto es SQLite (`quinu_ia.db`, se crea automáticamente
en el primer arranque con los planes y retos semilla).

## Configuración para producción (Azure)

Completa `.env` (o las "Application settings" del servicio en Azure) con:

| Variable | Servicio |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://usuario:password@host:5432/quinu_ia` (Azure Database for PostgreSQL) |
| `AZURE_VISION_ENDPOINT` / `AZURE_VISION_KEY` | Azure AI Vision (Image Analysis 4.0) |
| `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_KEY` | Azure OpenAI |
| `AZURE_OPENAI_DEPLOYMENT_GPT4O` / `AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI` | Nombres de despliegue en Azure AI Foundry |
| `AZURE_CONTENT_SAFETY_ENDPOINT` / `AZURE_CONTENT_SAFETY_KEY` | Azure AI Content Safety |
| `AZURE_STORAGE_CONNECTION_STRING` / `AZURE_STORAGE_CONTAINER` | Azure Blob Storage (fotos de comida) |

Ver `.env.example` para la lista completa.

## Despliegue (Azure Container Apps)

```bash
docker build -t quinu-ia .
az acr build --registry <tu-registro> --image quinu-ia:latest .
az containerapp create \
  --name quinu-ia \
  --resource-group <tu-grupo> \
  --image <tu-registro>.azurecr.io/quinu-ia:latest \
  --target-port 8501 \
  --ingress external \
  --env-vars-file .env
```

Azure Container Apps permite *scale-to-zero*, alineado con el modelo de costos
descrito en `docs/08_arquitectura_tecnologia.md` (sección 9.6).

## Cuentas de prueba

No hay datos precargados de usuarios — regístrate desde la pantalla de
bienvenida. El plan se asigna como "Gratuito" por defecto; usa el flujo
"Conoce nuestros planes" → "Pasar a PRO" para probar el contexto premium
(Fase 6).
