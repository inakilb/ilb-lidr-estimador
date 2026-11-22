# ilb-lidr-estimador

Estimador de proyectos de software con arquitectura **CAG** (Cache-Augmented Generation). Proyecto 1 del curso LIDR, sesión 2.

Es un servicio FastAPI que recibe la transcripción de una reunión con un cliente y devuelve una estimación de software generada por un LLM. Usa como referencia unos ejemplos de estimaciones previas que se inyectan directamente en el prompt.

```text
transcripción → inyectar contexto estático (ejemplos) → LLM → estimación en JSON
```

## Stack

- Python 3.11, gestionado con [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn
- pydantic-settings + python-dotenv para la configuración
- LLM: OpenAI (`gpt-4o-mini`) y/o Anthropic (`claude-haiku-4-5`), seleccionable con `LLM_PROVIDER`

## Estructura

```text
app/
├── __init__.py
├── main.py              # App FastAPI, GET /health, router con prefijo /api/v1
├── config.py            # Configuración cargada desde .env
├── routers/
│   ├── __init__.py
│   └── estimations.py   # POST /api/v1/estimate
├── services/
│   ├── __init__.py
│   └── llm_service.py   # Construcción del prompt y llamada al LLM
└── context/
    ├── __init__.py
    └── examples.py      # Ejemplos de estimaciones previas (few-shot)
openspec/                # Especificaciones y cambios (desarrollo con OpenSpec)
.env.example             # Variables de entorno necesarias (sin valores)
pyproject.toml / uv.lock # Dependencias (requirements.txt se genera desde el lock)
```

## Puesta en marcha

```bash
# 1. Instalar dependencias
uv sync                            # o bien: pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env               # y rellenar las API keys

# 3. Arrancar el servidor
uv run uvicorn app.main:app --reload
```

La documentación interactiva (Swagger) queda disponible en <http://localhost:8000/docs>.

## Uso

```bash
curl -X POST http://localhost:8000/api/v1/estimate \
  -H "Content-Type: application/json" \
  -d '{"transcription": "En la reunión con el equipo de marketing, el cliente explicó que necesita una landing page con formulario de contacto, integración con su CRM actual (HubSpot) y una sección de blog con editor WYSIWYG. El plazo ideal sería tenerlo listo en 4 semanas. El diseño ya existe en Figma."}'
```

Respuesta:

```json
{
  "estimation": "## Estimación: ...\n\n### Desglose de tareas:\n...",
  "model": "gpt-4o-mini",
  "provider": "openai"
}
```

## Desarrollo

El código se desarrolla con [OpenSpec](https://github.com/Fission-AI/OpenSpec): cada paso del ejercicio es un cambio (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`) y se entrega en un commit propio.

## Estado

| Paso | Entrega                                                      | Estado    |
| ---- | ------------------------------------------------------------ | --------- |
| 1    | Inicializar el proyecto (uv, dependencias, estructura)       | Hecho     |
| 2    | Configuración con variables de entorno (`config.py`, `.env`) | Pendiente |
| 3    | Contexto estático: ejemplos de estimaciones                  | Pendiente |
| 4    | Servicio de llamada al LLM                                   | Pendiente |
| 5    | Endpoint `POST /api/v1/estimate`                             | Pendiente |
| 6    | Aplicación FastAPI (`GET /health`, Swagger)                  | Pendiente |
| 7    | Verificación                                                 | Pendiente |
| 8    | Pipeline de CI y transcripción de ejemplo                    | Pendiente |
