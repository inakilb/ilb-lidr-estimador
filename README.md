# ilb-lidr-estimador

[![CI](https://github.com/inakilb/ilb-lidr-estimador/actions/workflows/ci.yml/badge.svg)](https://github.com/inakilb/ilb-lidr-estimador/actions/workflows/ci.yml)

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
transcripciones/         # Peticiones de ejemplo ({"transcription": ...}) para probar el endpoint
tests/                   # Tests automáticos (pytest), sin llamadas al LLM
.github/workflows/ci.yml # Pipeline de CI (GitHub Actions)
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

Ejecuta los comandos desde la raíz del repositorio para que se lea el `.env`. Si cambias el `.env`, reinicia el servidor: `--reload` solo detecta cambios en el código.

Con el servidor arrancado:

| URL                            | Qué hay                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| <http://localhost:8000/docs>   | Documentación interactiva (Swagger UI), desde donde también se puede probar el endpoint |
| <http://localhost:8000/redoc>  | La misma documentación en formato ReDoc                                                 |
| <http://localhost:8000/health> | Estado del servicio                                                                     |
| <http://localhost:8000/>       | Redirige a `/docs`                                                                      |

`GET /health` no llama al LLM: solo indica si el servicio está levantado y si su configuración es válida.

```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development",
  "llm": { "provider": "anthropic", "model": "claude-haiku-4-5" }
}
```

Siempre responde 200. Si la configuración no es válida (por ejemplo, falta la API key), devuelve `"status": "degraded"`, `"llm": null` y un `detail` con el problema. Por eso un monitor o la pipeline de CI deben comprobar el campo `status`, no solo el código HTTP. Los logs de la aplicación usan el nivel de `LOG_LEVEL`.

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

## Servicio LLM

`app/services/llm_service.py` genera la estimación en una única llamada al LLM:

```text
[system]    → rol de estimador experto + reglas + los 7 ejemplos (en etiquetas XML)
[user]      → la transcripción, dentro de <transcription>…</transcription>
[assistant] → la estimación, en español y en Markdown
```

- **Respuesta en español.** Los ejemplos están en inglés, pero el prompt exige escribir en español, con encabezados fijos: Desglose de tareas, Totales, Supuestos, Fuera de alcance, Riesgos, Equipo recomendado y Duración estimada.
- **La transcripción se trata como datos.** Si contiene instrucciones ("ignora lo anterior…"), el modelo no las sigue.
- **Caché del prompt.** El system prompt (~6.700 tokens) es idéntico en cada llamada y se guarda en caché durante 5 minutos. Las llamadas siguientes lo leen al 10 % del precio.
- **Proveedores y modelos.** Cada proveedor está registrado en `PROVIDERS` y comparte el mismo prompt y el mismo formato de resultado:

  | Proveedor            | Cómo activarlo en `.env`                     | Modelo por defecto                                                                                      |
  | -------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
  | Anthropic            | (por defecto) `ANTHROPIC_API_KEY=...`        | `claude-haiku-4-5`, el que indica el curso                                                              |
  | Anthropic, Haiku 5.5 | `LLM_MODEL=claude-haiku-5-5`                 | `claude-haiku-5-5`: más barato y piensa antes de responder (el servicio lo usa con `effort: low`)       |
  | OpenAI               | `LLM_PROVIDER=openai` y `OPENAI_API_KEY=...` | `gpt-4o-mini`, con caché automática del prompt                                                          |
  | OpenAI, GPT-6 Luna   | `LLM_MODEL=gpt-6-luna`                       | `gpt-6-luna`: más reciente y razona antes de responder (el servicio lo usa con `reasoning_effort: low`) |

  OpenAI marca `gpt-4o-mini` como obsoleto (_deprecated_). Se mantiene por defecto porque es el modelo del curso, y `gpt-6-luna` es la alternativa actual.

- **Deja `LLM_MODEL` vacío** en `.env` para que el modelo siga al proveedor (`claude-haiku-4-5` o `gpt-4o-mini`). Si `LLM_MODEL` es un modelo del otro proveedor (por ejemplo `claude-haiku-4-5` con `LLM_PROVIDER=openai`), la configuración falla al arrancar con un error que lo indica.
- **Sin crédito.** Si la cuenta del proveedor no tiene crédito, el servicio lo indica con un error claro ("no credits") y no lo reintenta como si fuera un límite de peticiones.

- **Añadir un proveedor** (por ejemplo Gemini):
  1. En `app/config.py`, añade el proveedor a `LLMProvider`, junto con su API key, su modelo por defecto y el patrón de nombres de sus modelos (`MODEL_PATTERNS`).
  2. En `llm_service.py`, escribe la función `_generate_with_<proveedor>` y regístrala en `PROVIDERS`.
  3. Añade su precio a la tabla de costes y, si lo necesita, sus opciones de petición a `MODEL_REQUEST_OPTIONS`.

| Modelo             | Coste aproximado por estimación                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| `claude-haiku-4-5` | ~0,013 $ la primera llamada y ~0,005 $ con caché                                                              |
| `claude-haiku-5-5` | ~0,002 $                                                                                                      |
| `gpt-4o-mini`      | ~0,0011 $ la primera llamada y ~0,0007 $ con caché                                                            |
| `gpt-6-luna`       | ~0,0011 $ la primera llamada y ~0,0007 $ con caché (más barato por token, pero genera tokens de razonamiento) |

## Uso

```bash
curl -X POST http://localhost:8000/api/v1/estimate \
  -H "Content-Type: application/json" \
  -d '{"transcription": "En la reunión con el equipo de marketing, el cliente explicó que necesita una landing page con formulario de contacto, integración con su CRM actual (HubSpot) y una sección de blog con editor WYSIWYG. El plazo ideal sería tenerlo listo en 4 semanas. El diseño ya existe en Figma."}'
```

Respuesta (200):

```json
{
  "estimation": "## Estimación: Landing Page con Blog y Integración HubSpot\n\n### Desglose de tareas\n...",
  "model": "claude-haiku-4-5",
  "provider": "anthropic",
  "usage": {
    "input_tokens": 111,
    "output_tokens": 878,
    "cache_read_input_tokens": 0,
    "cache_creation_input_tokens": 6736
  },
  "estimated_cost_usd": 0.012921,
  "generated_at": "2026-11-22T21:26:50.505759Z"
}
```

`estimation`, `model` y `provider` son los campos que pide el curso. `usage`, `estimated_cost_usd` y `generated_at` son extras: los tokens consumidos (incluidos los leídos o escritos en la caché), el coste estimado en dólares y la fecha de generación (UTC).

La `transcription` es obligatoria, no puede estar vacía y admite como máximo 50.000 caracteres. Los errores devuelven `{"detail": "..."}`:

| Código | Cuándo                                                                                                                        | Qué hacer                              |
| ------ | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 422    | La petición no es válida (falta `transcription`, está vacía o es demasiado larga)                                             | Corregir la petición                   |
| 500    | La configuración del servicio no es válida (por ejemplo, falta la API key)                                                    | Revisar `.env`                         |
| 501    | El proveedor configurado no está implementado                                                                                 | Cambiar `LLM_PROVIDER`                 |
| 502    | El proveedor falla y reintentar no sirve (API key inválida, sin crédito, modelo inexistente), o la estimación sale incompleta | Revisar la cuenta o la configuración   |
| 503    | El proveedor no está disponible en este momento (límite de peticiones, sobrecarga, timeout)                                   | Reintentar tras `Retry-After` segundos |

## Verificación

Verificación del checklist del curso con el servicio arrancado (`uv run uvicorn app.main:app --reload`), realizada el 22/11/2026 con Anthropic `claude-haiku-4-5`. Los otros proveedores y modelos se verificaron en vivo durante el paso 4.

| Punto del checklist                                               | Cómo se ha comprobado                                                                                                         | Resultado                                                      | Cómo repetirlo                                                                               |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| El proyecto arranca sin errores                                   | Arranque con `--reload` y revisión del log                                                                                    | ✅ Sin errores, con la configuración en el log                 | `uv run uvicorn app.main:app --reload`                                                       |
| Las API keys se cargan desde `.env` y nunca aparecen en el código | Búsqueda de patrones de clave en los ficheros versionados; solo `app/config.py` lee las variables; `.env.example` sin valores | ✅ Ninguna clave en el repositorio                             | `git ls-files \| xargs grep -lE 'sk-(ant\|proj)-[A-Za-z0-9_-]{10,}'` (no debe devolver nada) |
| `GET /health` responde 200                                        | `curl`                                                                                                                        | ✅ 200, `"status": "ok"`                                       | `curl -i localhost:8000/health`                                                              |
| `POST /api/v1/estimate` devuelve una estimación                   | El `curl` del curso, sin cambios                                                                                              | ✅ 200 en ~9 s, estimación en español                          | ver [Uso](#uso) o `curso-landing.json` abajo                                                 |
| La estimación se inspira en los ejemplos inyectados               | Comparación con el ejemplo 6 y prueba sin ejemplos (ver abajo)                                                                | ✅ Influencia clara                                            | ver [Influencia de los ejemplos](#influencia-de-los-ejemplos)                                |
| Swagger accesible en `/docs`                                      | `curl` a `/docs` y `/openapi.json`                                                                                            | ✅ 200, Swagger UI con `POST /api/v1/estimate` y `GET /health` | <http://localhost:8000/docs>                                                                 |
| `.env` está en `.gitignore`                                       | `git check-ignore`                                                                                                            | ✅ Ignorado (`.gitignore:13`)                                  | `git check-ignore -v .env`                                                                   |

### Pruebas manuales

La carpeta `transcripciones/` contiene peticiones listas para enviar, en formato `{"transcription": "..."}`. Con el servidor arrancado, ejecútalas desde otra terminal en la raíz del repositorio:

```bash
curl -X POST localhost:8000/api/v1/estimate -H "Content-Type: application/json" -d @transcripciones/curso-landing.json
```

| Fichero               | Qué prueba                                                                                                | Resultado esperado                               |
| --------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `curso-landing.json`  | La transcripción de ejemplo del curso (landing page + HubSpot)                                            | 200, estimación en español                       |
| `tienda-vinos.json`   | Una tienda WooCommerce con Correos y Redsys, parecida al ejemplo 6                                        | 200, estimación con tareas de Correos y Redsys   |
| `no-es-proyecto.json` | Un texto que no es un proyecto de software                                                                | 200, una frase indicando que no se puede estimar |
| `vacia.json`          | Una transcripción solo con espacios                                                                       | 422, sin llamar al LLM                           |
| `inyeccion.json`      | Un proyecto con una instrucción que intenta cambiar el comportamiento ("ignora todas las instrucciones…") | 200, estimación normal que ignora la instrucción |

Para lanzarlas todas y ver el código HTTP y el inicio de cada respuesta:

```bash
for f in transcripciones/*.json; do
  echo "== $f"
  curl -s -w "\nHTTP %{http_code}\n" -X POST localhost:8000/api/v1/estimate \
    -H "Content-Type: application/json" -d @"$f" | head -c 300; echo
done
```

En Swagger (<http://localhost:8000/docs>), abre `POST /api/v1/estimate`, pulsa _Try it out_ y pega el contenido de cualquiera de estos ficheros.

### Influencia de los ejemplos

Se ha estimado `tienda-vinos.json` dos veces: con los 7 ejemplos en el prompt, como funciona el servicio, y sin ejemplos, con el mismo prompt al que se le quitan solo los ejemplos.

|                                 | Ejemplo 6 (en el prompt)  | Con ejemplos                       | Sin ejemplos                                                        |
| ------------------------------- | ------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| Tareas                          | 18                        | 18: las mismas y en el mismo orden | 12, más gruesas y con otros nombres                                 |
| Horas (subtotal + contingencia) | 206 + 30 = 236 h          | 206 + 30 = 236 h                   | 176 + 26 = 202 h                                                    |
| Coste total (sin IVA)           | 14.750 €                  | 14.750 €                           | 12.625 €                                                            |
| Equipo y duración               | 1,5 FTE, 6 semanas        | 1,5 FTE, 6 semanas                 | 2,0 FTE, 4 semanas                                                  |
| Formato de totales y secciones  | Plantilla de los ejemplos | Igual que el ejemplo               | Distinto (subtotal dentro de la tabla, sin horas totales ni tarifa) |

- **Con ejemplos**, la estimación es prácticamente el ejemplo 6 traducido: 15 de las 18 tareas tienen las mismas horas. Esto demuestra que los ejemplos guían la estimación, pero también muestra un exceso de anclaje: no se ajusta a las diferencias del encargo (120 productos en lugar de 150, sin envíos a Portugal). Es algo a mejorar en la sesión en vivo.
- **Sin ejemplos** se siguen cumpliendo las reglas que están en las instrucciones del prompt: la tarifa de 62,5 €/h, la contingencia del 15 %, el IVA excluido, la fórmula de duración y los encabezados en español. En cambio, cambian la granularidad, las tareas, las horas, el equipo y el formato, y faltan partes como el descubrimiento, las páginas legales y el SEO. Es decir, las reglas vienen de las instrucciones, y la plantilla y las cifras de referencia vienen de los ejemplos.
- Detalles observados en esta verificación: una respuesta usó el formato inglés para los miles (`9,375 EUR`) y otra dejó sin traducir "Tarifa blended". Los resultados varían entre ejecuciones.

## Tests y CI

```bash
uv run pytest            # 143 tests, unos 3 segundos
```

Los tests no llaman a ningún LLM, no necesitan API keys y no leen tu `.env`: cada test se ejecuta en una carpeta temporal y sin variables de configuración. Los clientes de Anthropic y OpenAI se sustituyen por versiones falsas que registran las llamadas.

| Módulo                          | Qué comprueba                                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `tests/test_structure.py`       | La estructura de carpetas del curso, que `.env` esté en `.gitignore` y que `.env.example` no tenga valores |
| `tests/test_config.py`          | Carga desde `.env` y desde el entorno, valores por defecto, validaciones y que las claves no se muestren   |
| `tests/test_examples.py`        | Forma, cobertura, secciones y aritmética de los 7 ejemplos                                                 |
| `tests/test_llm_service.py`     | Prompt, peticiones a cada proveedor y modelo, caché, tokens, coste y errores                               |
| `tests/test_estimations.py`     | Validación de la petición, respuesta y códigos de error HTTP del endpoint                                  |
| `tests/test_app.py`             | Swagger, router montado, `/health` (ok y degraded), redirección de `/` y logging                           |
| `tests/test_transcripciones.py` | Que los ficheros de `transcripciones/` sean peticiones válidas                                             |

**Pipeline** (`.github/workflows/ci.yml`, GitHub Actions). Se ejecuta en cada push y pull request:

1. Instala las dependencias con `uv sync --locked` y Python 3.11.
2. Comprueba que `requirements.txt` coincide con `uv.lock`.
3. Ejecuta los tests.
4. Hace una prueba de humo: arranca el servicio con `uvicorn` y claves ficticias, y comprueba que `/health` responde 200 con `status: ok`, que `/docs` responde 200 y que `vacia.json` devuelve 422. Nada de esto llama al LLM.

**Prueba en vivo (opcional y manual).** En GitHub, ve a _Actions → CI → Run workflow_, marca `live` y ejecútalo. Envía `transcripciones/curso-landing.json` al servicio con una clave real, que el job lee del secret `ANTHROPIC_API_KEY` del repositorio (_Settings → Secrets and variables → Actions_). Cuesta unos 0,01 $ por ejecución y nunca se lanza automáticamente. Conviene usar una clave exclusiva para CI, con un límite de gasto bajo en la consola de Anthropic.

## Desarrollo

El código se desarrolla con [OpenSpec](https://github.com/Fission-AI/OpenSpec): cada paso del ejercicio es un cambio (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`) y se entrega en un commit propio.

## Estado

| Paso | Entrega                                                      | Estado |
| ---- | ------------------------------------------------------------ | ------ |
| 1    | Inicializar el proyecto (uv, dependencias, estructura)       | Hecho  |
| 2    | Configuración con variables de entorno (`config.py`, `.env`) | Hecho  |
| 3    | Contexto estático: ejemplos de estimaciones                  | Hecho  |
| 4    | Servicio de llamada al LLM                                   | Hecho  |
| 5    | Endpoint `POST /api/v1/estimate`                             | Hecho  |
| 6    | Aplicación FastAPI (`GET /health`, Swagger)                  | Hecho  |
| 7    | Verificación                                                 | Hecho  |
| 8    | Pipeline de CI y transcripción de ejemplo                    | Hecho  |
