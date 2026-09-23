# practMCP

Servidor MCP de práctica que expone una base de datos MySQL remota (servidor dedicado)
como herramientas que Claude puede usar: `list_tables`, `describe_table`, `run_query`
(solo `SELECT`, máximo 200 filas).

## Setup

```bash
cp .env.example .env
# edita .env con los datos reales de tu servidor MySQL
uv sync
```

Recomendado: usa un usuario MySQL de **solo lectura** (`GRANT SELECT ON basedatos.* TO 'usuario'@'%';`)
para este servidor de práctica.

## Probar el servidor manualmente

```bash
uv run mcp dev server.py
```

Esto abre el MCP Inspector en el navegador para probar las tools sin necesitar un host como Claude.

## Registrar en Claude Code

```bash
claude mcp add practmcp -- uv --directory /data/proyectos/claude/practMCP run server.py
```

Después, en cualquier sesión de Claude Code, las tools `list_tables`, `describe_table`
y `run_query` estarán disponibles.
