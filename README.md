# practMCP

Servidor MCP (Model Context Protocol) de práctica que expone una base de datos MySQL
remota (un servidor dedicado) como herramientas que un host compatible con MCP —como
Claude Code o Claude Desktop— puede invocar directamente:

- **`list_tables()`** — lista todas las tablas de la base configurada.
- **`describe_table(table_name)`** — muestra columnas, tipos y llaves de una tabla.
- **`run_query(sql)`** — ejecuta una consulta de solo lectura (`SELECT`, sin sentencias
  encadenadas) y devuelve hasta 200 filas.

El servidor corre localmente y habla con el host por `stdio`; no expone ningún puerto de
red ni es un servicio standalone. El acceso de solo lectura se aplica en dos capas: los
permisos del usuario MySQL (recomendado `SELECT`-only) y una validación en `run_query`
que rechaza cualquier sentencia que no empiece con `select` o que contenga `;`.

## Requisitos

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** — gestor de paquetes/entornos usado por el proyecto
  (equivalente a `pip` + `venv`, pero más rápido y con lockfile).
- Acceso a un servidor MySQL, y un usuario con permisos de **solo lectura**:
  ```sql
  CREATE USER 'lector'@'%' IDENTIFIED BY 'contraseña-segura';
  GRANT SELECT ON nombre_de_tu_bd.* TO 'lector'@'%';
  ```

## Instalación

### macOS / Linux

```bash
# 1. Instalar uv (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar el repo
git clone git@github.com:webm-inmega/mcp.git practMCP
cd practMCP

# 3. Configurar credenciales
cp .env.example .env
# edita .env con los datos reales de tu servidor MySQL (host, puerto, usuario, password, bd)

# 4. Instalar dependencias (crea .venv automáticamente)
uv sync
```

### Windows (PowerShell)

```powershell
# 1. Instalar uv (si no lo tienes)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clonar el repo
git clone git@github.com:webm-inmega/mcp.git practMCP
cd practMCP

# 3. Configurar credenciales
copy .env.example .env
# edita .env con los datos reales de tu servidor MySQL (host, puerto, usuario, password, bd)

# 4. Instalar dependencias (crea .venv automáticamente)
uv sync
```

> Si prefieres no usar `uv`, también puedes crear un entorno virtual manualmente
> (`python -m venv .venv`, activarlo, y `pip install -e .`), pero los comandos de este
> README asumen `uv` porque es lo que fija el `uv.lock` del repo.

## Variables de entorno (`.env`)

| Variable         | Descripción                                   |
|------------------|------------------------------------------------|
| `MYSQL_HOST`     | Host del servidor MySQL dedicado                |
| `MYSQL_PORT`     | Puerto (por defecto `3306`)                     |
| `MYSQL_USER`     | Usuario MySQL (idealmente solo-lectura)         |
| `MYSQL_PASSWORD` | Contraseña del usuario                          |
| `MYSQL_DATABASE` | Base de datos a exponer                         |

`.env` está en `.gitignore` — nunca se sube al repo. No compartas su contenido en chats,
commits ni documentación.

## Probar el servidor manualmente (sin un host MCP)

El **MCP Inspector** abre una UI en el navegador para invocar las tools directamente:

```bash
uv run mcp dev server.py
```

Esto imprime una URL local (por defecto `http://127.0.0.1:6274`) — ábrela en tu navegador,
conéctate al servidor y prueba `list_tables`, `describe_table` y `run_query` desde ahí.

Smoke test rápido sin abrir el Inspector:

```bash
uv run python -c "from server import list_tables; print(list_tables())"
```

## Ejecutar directamente

Así es como un host MCP lo lanza internamente (normalmente no necesitas correr esto a mano):

```bash
uv run server.py
```

## Registrar el servidor en un host MCP

### Claude Code

```bash
claude mcp add practmcp -- uv --directory /ruta/a/practMCP run server.py
```

En Windows, usa la ruta con el formato que corresponda a tu shell, por ejemplo:

```powershell
claude mcp add practmcp -- uv --directory C:\ruta\a\practMCP run server.py
```

Después, en cualquier sesión de Claude Code, las tools `list_tables`, `describe_table` y
`run_query` estarán disponibles automáticamente.

### Claude Desktop

Edita el archivo de configuración de Claude Desktop y agrega una entrada `practmcp` en
`mcpServers`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "practmcp": {
      "command": "uv",
      "args": ["--directory", "/ruta/absoluta/a/practMCP", "run", "server.py"]
    }
  }
}
```

Usa la ruta absoluta real a tu copia del repo (en Windows, con `\\` o `/`, ambos funcionan
en JSON si se escapan correctamente, ej. `"C:\\ruta\\a\\practMCP"`). Reinicia Claude
Desktop después de guardar el archivo.

### Este repo ya incluye `.mcp.json`

El archivo `.mcp.json` en la raíz del proyecto ya declara el servidor `practmcp` para
hosts que leen configuración de proyecto (como Claude Code al abrir este directorio), así
que en muchos casos no necesitas el paso de `claude mcp add` — el host lo detecta solo.

## Arquitectura

Ver [`CLAUDE.md`](./CLAUDE.md) para detalles de implementación: por qué se usa
`mcp.server.mcpserver.MCPServer` (API v2, no `FastMCP` de v1), cómo se maneja la
serialización de tipos MySQL no nativos de JSON (`Decimal`, fechas, `bytes`/WKB), y el
límite de seguridad en `run_query`.
