# backend-bot-finanzas

API REST para un bot de finanzas personales en Telegram. Registra ingresos y egresos por usuario, los guarda en PostgreSQL y calcula indicadores (saldo, tasa de ahorro, días de supervivencia, gasto por categoría).

La conversación con el usuario (Telegram, transcripción de audio, clasificación con LLM) vive en **n8n**. Este backend es la fuente de verdad de los datos: n8n solo lo llama por HTTP.

```
Telegram ──► n8n (trigger, Whisper, LLM, respuestas) ──HTTP + X-API-Key──► FastAPI ──► PostgreSQL
```

## Arquitectura

Arquitectura en capas con patrón Repository e inyección de dependencias (`Depends` de FastAPI).

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Router | `app/router/` | Endpoints HTTP y fábricas que arman cada servicio con su repositorio |
| Service | `app/service/` | Reglas de negocio, excepciones de dominio y `commit` de la transacción |
| Repository | `app/repository/` | `base_*`: interfaz (`ABC`). `sqlalchemy_*`: implementación Postgres. Nunca hace `commit` |
| Model | `app/model/` | Tablas SQLAlchemy y enums |
| DTO | `app/dto/` | Modelos Pydantic de entrada (`Create`, `Update`) y salida (`Response`) |
| Core | `app/core/` | Configuración, excepciones y seguridad (API key) |
| Database | `app/database/` | Engine, `SessionLocal` y `get_db()` (una sesión por petición) |

## Puesta en marcha

1. Crea un `.env` en la raíz (está en `.gitignore`):

   ```env
   DATABASE_URL=postgresql+psycopg://usuario:clave@localhost:5432/finanzas
   API_KEY=una-clave-larga-y-aleatoria
   ```

   Para generar la clave: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

2. Instala dependencias y arranca:

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Documentación interactiva en `http://localhost:8000/docs` (botón **Authorize** para poner la API key).

Al arrancar, `main.py` crea las tablas que falten y llena `categories_back` con las 9 categorías del enum si aún no existen.

> `create_all` solo crea tablas nuevas, no modifica columnas existentes. La columna `telefono` de `users_back` sigue en la base aunque el modelo ya no la use; es nullable, así que no molesta.
>
> Antes, los ingresos se guardaban con `tipo_gasto = NECESIDAD`. Para limpiar los que ya existen:
>
> ```sql
> UPDATE transactions_back SET tipo_gasto = NULL WHERE tipo_movimiento = 'INGRESO';
> ```

`SQL_ECHO=true` en el `.env` imprime cada consulta SQL (útil en desarrollo). Por defecto está apagado.

## Despliegue en la Raspberry Pi

El backend corre como un servicio más del `compose.yml` de n8n (`/home/josue/n8n/compose.yml`). Así queda en la misma red Docker que `n8n` y `postgres`, y no publica ningún puerto. Lo único que llega desde internet es n8n, a través del túnel.

```
Telegram ─► Cloudflare Tunnel ─► n8n ─► http://backend:8000 ─► postgres:5432
                                 (los tres en la red interna del compose)
```

1. Clona el repo junto a la carpeta de n8n:

   ```bash
   cd /home/josue && git clone <url-del-repo> backend-bot-finanzas
   ```

2. Agrega el servicio al `compose.yml`:

   ```yaml
     backend:
       build: ../backend-bot-finanzas
       restart: always
       depends_on:
         postgres:
           condition: service_healthy
       environment:
         DATABASE_URL: ${BACKEND_DATABASE_URL}
         API_KEY: ${BACKEND_API_KEY}
   ```

3. Agrega las variables al `.env` de n8n:

   ```env
   BACKEND_DATABASE_URL=postgresql+psycopg://admin_bot_finanzas:<clave-url-encoded>@postgres:5432/<base>
   BACKEND_API_KEY=<la misma clave de la credencial de n8n>
   ```

   - El host es `postgres`, el nombre del servicio, no `localhost`.
   - Si el schema del usuario no se llama igual que el usuario, agrega `?options=-csearch_path%3D<schema>` al final de la URL. Con el mismo nombre, Postgres lo usa solo (`search_path = "$user", public`).

4. Construye y levanta solo el backend:

   ```bash
   cd /home/josue/n8n
   docker compose up -d --build backend
   docker compose logs -f backend
   ```

5. Prueba la API por la red interna (usa la `API_KEY` del contenedor, así la clave no queda en el historial de la shell):

   ```bash
   docker compose exec backend python -c "
   import os, urllib.request as u, urllib.error as e
   try:
       u.urlopen(u.Request('http://backend:8000/users/telegram/0', headers={'X-API-Key': os.environ['API_KEY']}))
   except e.HTTPError as x:
       print(x.code, x.read().decode())"
   ```

   Si está todo bien, imprime `404 {"status":"error","message":"No hay un usuario con telegram_id 0",...}`. Eso confirma la conexión a Postgres y la API key. Un `401` significa que la clave no coincide.

Para actualizar: `git pull` en la carpeta del repo y `docker compose up -d --build backend`.

La imagen usa `python:3.13-slim`, que es multi-arquitectura, y todas las dependencias tienen wheels para arm64. No hace falta compilar nada en la Pi.

## Autenticación

Todas las rutas exigen el header `X-API-Key` con el valor de `API_KEY`.

| Situación | Respuesta |
|---|---|
| Header ausente o incorrecto | `401 {"status": "error", "message": "API key inválida o ausente"}` |
| `API_KEY` no definida en el servidor | `500` |

## Endpoints

| Método | Ruta | Uso desde el bot |
|---|---|---|
| `GET` | `/users/telegram/{telegram_id}` | ¿Existe el usuario? Devuelve `id` y `tiene_saldo_inicial`. `404` si no existe |
| `POST` | `/users/` | Registrar usuario nuevo |
| `POST` | `/transactions` | Saldo inicial y registro de ingresos/egresos |
| `POST` | `/transactions/bulk` | Carga de varias transacciones (migraciones) |
| `GET` | `/transactions?user_id=&limit=&offset=` | Listado paginado `{data, total}` |
| `GET` | `/kpis?user_id=&fecha_inicio=&fecha_fin=` | Saldo, egresos del periodo, tasa de ahorro, días de supervivencia, gasto por categoría |
| `GET` | `/transactions/summary?user_id=&fecha_desde=&fecha_hasta=&tipo_movimiento=` | Resumen de un rango de días para el bot: total, por categoría, necesidad/deseo, el más alto y los 20 últimos |
| `GET` | `/transactions/export?user_id=&fecha_desde=&fecha_hasta=` | Excel (`.xlsx`) del rango con ingresos y egresos: hoja *Movimientos* y hoja *Dashboard* con indicadores y gráficos |

### Cuerpos de ejemplo

```jsonc
// POST /users/
{ "nombre": "Josue", "telegram_id": "7381103128" }   // telegram_id también se acepta como número

// POST /transactions  (saldo inicial)
{ "user_id": 1, "tipo_movimiento": "INGRESO", "monto": 100, "descripcion": "Saldo inicial" }

// POST /transactions  (egreso desde el LLM)
{
  "user_id": 1,
  "tipo_movimiento": "EGRESO",
  "monto": 2.5,
  "descripcion": "empanadas",
  "categoria": "PIQUEOS Y COMIDA FUERA",
  "tipo_gasto": "DESEO"
}
```

- `categoria` es una alternativa a `category_id` pensada para el LLM. Ignora mayúsculas, tildes y guiones bajos.
- `tipo_gasto` (`NECESIDAD` | `DESEO`) solo aplica a egresos.
  - Si un egreso llega sin `tipo_gasto`, queda como `NECESIDAD`.
  - En los ingresos siempre se guarda `null`, aunque se envíe un valor.
  - Solo las necesidades cuentan para los días de supervivencia.
- `is_recurrente` es opcional (por defecto `false`).
- `monto` usa **punto decimal** (`10.30`). Con coma (`"10,3"`) responde `422`.

Categorías válidas: `ALIMENTACION HOGAR`, `PIQUEOS Y COMIDA FUERA`, `TRANSPORTE Y MOVILIDAD`, `SERVICIOS Y SUSCRIPCIONES`, `CUIDADO PERSONAL`, `SALUD`, `ENTRETENIMIENTO Y SOCIAL`, `EDUCACION Y TRABAJO`, `VARIOS E IMPREVISTOS`.

### Respuesta de `/kpis`

```json
{
  "ingresos_totales": 100.0,
  "egresos_totales": 3.4,
  "saldo_actual": 96.6,
  "tasa_ahorro": 0.966,
  "dias_supervivencia": 2557,
  "desglose_por_categoria": [
    { "categoria": "PIQUEOS Y COMIDA FUERA", "monto": 2.5, "porcentaje_sobre_ingreso": 2.5 }
  ]
}
```

Sin fechas, el periodo va desde el día 1 del mes (hora de Guayaquil) hasta ahora. `saldo_actual` es histórico, no solo del periodo. Envía las fechas en ISO **con zona horaria** (`2026-10-29T00:00:00-05:00`).

### Respuesta de `/transactions/summary`

```json
{
  "fecha_desde": "2026-11-01",
  "fecha_hasta": "2026-11-15",
  "tipo_movimiento": "EGRESO",
  "total": 63.7,
  "cantidad": 3,
  "por_categoria": [
    { "categoria": "ALIMENTACION HOGAR", "total": 48.2, "cantidad": 1 },
    { "categoria": "PIQUEOS Y COMIDA FUERA", "total": 12.5, "cantidad": 1 }
  ],
  "por_tipo_gasto": { "NECESIDAD": 51.2, "DESEO": 12.5 },
  "mayor": { "fecha": "2026-11-12", "descripcion": "Supermercado", "monto": 48.2, "categoria": "ALIMENTACION HOGAR" },
  "movimientos": [ { "fecha": "2026-11-12", "descripcion": "Supermercado", "monto": 48.2, "categoria": "ALIMENTACION HOGAR" } ]
}
```

- **Fechas:** son días (`YYYY-MM-DD`) en hora de Ecuador y ambos extremos se incluyen. Sin fechas, va del día 1 del mes hasta hoy. Si `fecha_desde` es posterior a `fecha_hasta`, responde `400`.
- **`tipo_movimiento`:** por defecto `EGRESO`. Con `INGRESO`, `por_tipo_gasto` viene en `null` y la categoría suele ser `null`.
- **`movimientos`:** trae como máximo los 20 más recientes. El bot solo los muestra cuando `cantidad` es 20 o menos.

### Excel de `/transactions/export`

Mismas reglas de fechas que el resumen. Lo genera `app/report/excel_report.py` con `openpyxl`.

- **Hoja *Movimientos*:** una tabla de Excel con filtros y filas alternadas, montos en verde (ingreso) o rojo (egreso), y los totales de ingresos, egresos y balance.
- **Hoja *Dashboard*:** cinco tarjetas (ingresos, egresos, balance, movimientos y gasto diario promedio), gasto por categoría con barras, necesidad vs deseo en dona y la evolución en línea (por día hasta 62 días, por mes si el rango es mayor).
- **Totales:** se escriben como valores y no como fórmulas, para que también se vean en los visores del teléfono.

## Integración con n8n

Los nodos `Data Table` (`sesion_usuario`, `registro`, `bot_finanzas`) se reemplazan por nodos **HTTP Request**.

| Carpeta | Contenido |
|---|---|
| `json_n8n/` | Exports originales y CSV de las Data Tables |
| `json_n8n/backend/` | Workflows ya modificados para usar este backend |

`consultar_egresos_hoy` ya no se usa: esa consulta ahora es un solo nodo dentro de `bot-finanzas`.

### Cómo importar los workflows modificados

Pega cada JSON **dentro del workflow existente**, no como uno nuevo. Así `bot-finanzas` sigue apuntando al ID de `bot_registrador` (`tidigNdqK6XtwMxJ`) y el webhook de Telegram no cambia.

1. Crea la credencial del paso 1.
2. Abre `bot_registrador` en n8n, selecciona todo (Ctrl+A), bórralo y pega el contenido de `json_n8n/backend/bot_registrador.json` (Ctrl+V). Guarda.
3. Haz lo mismo con `bot-finanzas` y `json_n8n/backend/bot-finanzas.json`.
4. En cada workflow, abre el nodo **Config** y ajusta `backend_url` (ver paso 2).
5. Abre uno de los nodos HTTP Request y elige la credencial `Backend Finanzas API Key` si n8n no la asignó sola.

Las credenciales de Telegram y Groq se conservan del export original.

### 1. Credencial

En n8n: **Credentials → New → Header Auth**, con nombre de credencial `Backend Finanzas API Key`:

- Name: `X-API-Key`
- Value: el mismo valor de `API_KEY`

Usa una credencial nueva. La `Header Auth account` que ya existe es la de Groq.

### 2. URL base

| Dónde corre el backend | URL del backend |
|---|---|
| En el mismo compose que n8n (la Pi) | `http://backend:8000` |
| En el host, con n8n en Docker | `http://host.docker.internal:8000` |
| En la misma máquina, sin Docker | `http://localhost:8000` |

La URL se define una sola vez por workflow, en el nodo **Config** (`backend_url`, por defecto `http://backend:8000`). Los HTTP Request la leen con `{{ $('Config').item.json.backend_url }}`.

### 3. Equivalencias nodo por nodo (`bot-finanzas`)

Esto es lo que ya hace `json_n8n/backend/bot-finanzas.json`. Las rutas son relativas a `backend_url`.

| Nodo actual | Nuevo nodo HTTP Request |
|---|---|
| Nodo original | Nodo nuevo |
|---|---|
| — | **Config** (Set): `backend_url` |
| `consultar session_usuario` | **Buscar usuario**: GET `/users/telegram/{chat.id}` con *Include Response Headers and Status* y *Never Error*, para que el 404 no corte el flujo |
| `usuario existe?` | Compara `{{ $json.statusCode }}` con `200`. Los datos del usuario quedan en `$('Buscar usuario').item.json.body` |
| `Insert row` (sesion_usuario) | **Crear usuario**: POST `/users/` con `nombre` y `telegram_id` del mensaje |
| IF `has_initial_amount` | Evalúa `{{ $('Buscar usuario').item.json.body.tiene_saldo_inicial }}` |
| `Insert row2` + `Update row(s)1` | **Registrar saldo inicial**: POST `/transactions` con un `INGRESO` y descripción "Saldo inicial" |
| `traer ultimo saldo` (rama *saldo*) | **Consultar saldo**: GET `/kpis?user_id=…`. El mensaje usa `saldo_actual` |
| `Call 'consultar_egresos_hoy'` | **Egresos de hoy**: GET `/kpis?user_id=…&fecha_inicio={{ $today.toISO() }}`. El mensaje usa `egresos_totales` |
| `Registrar` (subflujo) | Recibe `usuario` = `id` interno, ya no el `telegram_id` |
| Regla `initial_amount` del Switch (sin conectar) | Eliminada. La salida *fallback* (`otro`) va a **Responder otro**, que explica qué puede hacer el bot |
| — (nueva intención `reporte`) | **Extraer rango** (LLM con la fecha de hoy en el prompt; devuelve fechas, tipo y `formato`) → **Parsear rango** (Code, mes en curso y texto si el JSON falla) → **pide archivo?** |
| — rama texto | **Resumen periodo**: GET `/transactions/summary` → **Formatear resumen** (Code, HTML con `<pre>`) → **Enviar resumen** (Telegram, `parse_mode=HTML`) |
| — rama archivo | **Descargar Excel**: GET `/transactions/export` con respuesta *File* → **Enviar Excel** (Telegram *Send Document*) |

El LLM nunca escribe SQL: solo extrae el rango de fechas, y el backend filtra siempre por el `user_id` de quien escribe. Por defecto la respuesta es un mensaje de texto, porque los usuarios leen desde el teléfono. El Excel se envía solo si lo piden ("mándame el Excel de octubre").

Arreglos que se aprovecharon de paso:

- El saldo inicial por audio ahora sí usa la transcripción; antes solo leía `message.text`.
- El prompt del saldo inicial pedía `10,3` para "10 dólares con 3 centavos". Ahora pide `10.03`.
- `user_message` usa `||` para no evaluar el nodo de transcripción cuando el mensaje es de texto.

### 4. Subflujo `bot_registrador`

`traer ultimo saldo`, `Merge`, `Code in JavaScript` e `Insert row` desaparecen. También se eliminan los nodos `AI Agent` y `Ollama Chat Model`, que estaban desconectados. El flujo queda así:

```
Start ─► Config ─► Basic LLM Chain ─► Registrar transacción ─► Consultar saldo ─► Resultado
                    (Groq + parser)      POST /transactions       GET /kpis          {tipo_movimiento, descripcion, monto, saldo_actual}
```

- **Basic LLM Chain:** el prompt devuelve `tipo_movimiento`, `monto`, `descripcion`, `categoria` (una de las 9) y `tipo_gasto` (`NECESIDAD`/`DESEO`). Para ingresos, `categoria` y `tipo_gasto` van en `null`.
- **Structured Output Parser:** usa un JSON Schema manual en lugar de un ejemplo. Con un ejemplo, n8n infiere `categoria` como `string` y rechazaría el `null` de los ingresos.
- **Registrar transacción:** el cuerpo es `JSON.stringify({ user_id: Number($('Start').item.json.usuario), ...$json.output })`.
- **Resultado:** es lo que recibe el flujo principal. El IF `es ingreso?` mira `tipo_movimiento`, y los mensajes usan `descripcion` y `saldo_actual`.

Si el LLM devuelve algo que el backend rechaza (por ejemplo, una categoría inventada), el nodo HTTP falla con 422 y el bot no responde. La ejecución queda en el historial de n8n con el detalle.

### 5. Zona horaria

Configura la zona horaria del workflow `bot-finanzas` (*Settings → Timezone*) como `America/Guayaquil`. Así `$today` es la medianoche local y "¿cuánto gasté hoy?" cuenta desde las 00:00 de Ecuador.

## Errores

Las excepciones de dominio se devuelven como:

```json
{ "status": "error", "message": "…", "type": "NotFoundException" }
```

| Código | Causa |
|---|---|
| `400` | Usuario ya registrado |
| `401` | API key inválida |
| `404` | Usuario o categoría inexistente |
| `422` | Validación de Pydantic (formato `{"detail": [...]}`) |
| `500` | Error no controlado |
