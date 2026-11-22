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
- LLM: Anthropic (`claude-haiku-4-5`) por defecto. OpenAI (`gpt-4o-mini`) se puede elegir con `LLM_PROVIDER`, y más adelante se añadirán otros proveedores

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
cp .env.example .env               # y rellenar ANTHROPIC_API_KEY

# 3. Arrancar el servidor
uv run uvicorn app.main:app --reload
```

La documentación interactiva (Swagger) queda disponible en <http://localhost:8000/docs>.

Ejecuta los comandos desde la raíz del repositorio para que se lea el `.env`.

## Configuración

La configuración se carga desde las variables de entorno y desde el archivo `.env` (`app/config.py`). Si una variable está definida en los dos sitios, gana la del entorno. Una variable vacía se trata como no definida y toma su valor por defecto.

| Variable            | Descripción                                  | Valor por defecto                                                     |
| ------------------- | -------------------------------------------- | --------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY` | API key de Anthropic                         | Sin valor por defecto (obligatoria si se usa Anthropic)               |
| `OPENAI_API_KEY`    | API key de OpenAI                            | Sin valor por defecto (obligatoria si se usa OpenAI)                  |
| `LLM_PROVIDER`      | Proveedor a utilizar: `anthropic` o `openai` | `anthropic`                                                           |
| `LLM_MODEL`         | Modelo a utilizar                            | El modelo económico del proveedor: `claude-haiku-4-5` o `gpt-4o-mini` |
| `APP_ENV`           | Entorno de ejecución                         | `development`                                                         |
| `LOG_LEVEL`         | Nivel de logging (`DEBUG` … `CRITICAL`)      | `DEBUG`                                                               |

> El enunciado del curso propone OpenAI (`gpt-4o-mini`) como proveedor por defecto. Por ahora este proyecto usa Anthropic, porque es el único proveedor con API key disponible. Con `LLM_PROVIDER=openai` se recupera el comportamiento del enunciado.

`.env` contiene las API keys reales y está en `.gitignore`. `.env.example` documenta las variables sin valores y sí se versiona.

## Contexto (ejemplos)

`app/context/examples.py` contiene `ESTIMATION_EXAMPLES`: 7 estimaciones ficticias que se inyectan en el system prompt como ejemplos _few-shot_. Son todo el "conocimiento" del sistema. Ocupan unos 6.000 tokens.

| #   | Proyecto                                                             | Total            | Duración  |
| --- | -------------------------------------------------------------------- | ---------------- | --------- |
| 1   | Plataforma web de gestión de inventario                              | 230 h · 14.375 € | 6 semanas |
| 2   | Landing page inmobiliaria con integración HubSpot                    | 120 h · 7.500 €  | 3 semanas |
| 3   | SaaS de gestión de suscripciones (MVP)                               | 280 h · 17.500 € | 5 semanas |
| 4   | Web corporativa WordPress multiidioma (12 secciones)                 | 306 h · 19.125 € | 6 semanas |
| 5   | Migración de Joomla a WordPress con rediseño                         | 282 h · 17.625 € | 5 semanas |
| 6   | Tienda WooCommerce con envíos Correos y pagos Redsys                 | 236 h · 14.750 € | 6 semanas |
| 7   | Tienda WooCommerce sincronizada con el TPV de tienda física y Redsys | 308 h · 19.250 € | 6 semanas |

Los tres primeros vienen del material del curso, corregidos. Todos siguen las mismas convenciones:

- Están en inglés para ahorrar tokens. El modelo responde en español.
- Tarifa única de 62,5 €/h, contingencia del 15 % y precios sin IVA.
- Duración en semanas = horas totales / (FTE × 30 h productivas por semana), redondeado hacia arriba.
- Secciones: desglose de tareas, totales, supuestos, fuera de alcance, riesgos, equipo recomendado y duración.

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
  "model": "claude-haiku-4-5",
  "provider": "anthropic"
}
```

## Desarrollo

El código se desarrolla con [OpenSpec](https://github.com/Fission-AI/OpenSpec): cada paso del ejercicio es un cambio (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`) y se entrega en un commit propio.

## Estado

| Paso | Entrega                                                      | Estado    |
| ---- | ------------------------------------------------------------ | --------- |
| 1    | Inicializar el proyecto (uv, dependencias, estructura)       | Hecho     |
| 2    | Configuración con variables de entorno (`config.py`, `.env`) | Hecho     |
| 3    | Contexto estático: ejemplos de estimaciones                  | Hecho     |
| 4    | Servicio de llamada al LLM                                   | Pendiente |
| 5    | Endpoint `POST /api/v1/estimate`                             | Pendiente |
| 6    | Aplicación FastAPI (`GET /health`, Swagger)                  | Pendiente |
| 7    | Verificación                                                 | Pendiente |
| 8    | Pipeline de CI y transcripción de ejemplo                    | Pendiente |
