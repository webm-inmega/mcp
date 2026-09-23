# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

practMCP is a practice/learning project: a single-file MCP (Model Context Protocol) server that
exposes a remote MySQL database (on a dedicated server) as tools Claude can call. It lives inside
a larger multi-project workspace — see the parent `/data/proyectos/claude/CLAUDE.md` for how it
relates to sibling projects (short answer: it doesn't, they're unrelated).

## Commands

- Install deps: `uv sync`
- Test the server without a host, via the MCP Inspector (opens a browser UI): `uv run mcp dev server.py`
- Run directly (what a host launches over stdio): `uv run server.py`
- Register with Claude Code as an MCP server: `claude mcp add practmcp -- uv --directory /data/proyectos/claude/practMCP run server.py`
- Quick connectivity smoke test without the Inspector: `uv run python -c "from server import list_tables; print(list_tables())"`

## Setup

- Copy `.env.example` to `.env` and fill in `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
  `MYSQL_PASSWORD`, `MYSQL_DATABASE` for the target dedicated server. `.env` is gitignored —
  never commit it or paste its contents into chat, docs, or commit messages.
- Use a MySQL user with `SELECT`-only grants for this project. There is no admin/write path
  here by design (see Architecture below).

## Architecture

- Single file, `server.py`. Built with `mcp[cli]` v2's `MCPServer`, imported from
  `mcp.server.mcpserver` — **not** `mcp.server.fastmcp.FastMCP`. That class was renamed/moved
  in `mcp` 2.x; any example or older docs written against the v1 API (`FastMCP`) will fail to
  import as-is against the version pinned in `pyproject.toml`.
- Three tools, each opening and closing its own `mysql.connector` connection per call
  (`get_connection()`): `list_tables()`, `describe_table(table_name)`, `run_query(sql)`.
- `run_query` is the only tool that takes arbitrary input, and read-only access is enforced at
  the application layer, not just via MySQL grants: it rejects any statement not starting with
  `select` and rejects embedded `;` (no stacked/multi-statement queries). This is a deliberate
  security boundary — don't loosen it without replacing it with something equally strict.
- MySQL driver values that aren't JSON-serializable (`Decimal`, `datetime`/`date`/`time`,
  and `bytes`/`bytearray` — the latter shows up for geometry/spatial columns returned as WKB)
  will make the MCP protocol layer fail to serialize the tool's response, even though the query
  itself succeeds. `_json_safe()` in `server.py` converts these before returning rows; any new
  tool that returns raw DB rows needs to go through it too.
- Transport is `stdio` (`mcp.run(transport="stdio")`). The server is meant to be launched as a
  subprocess by a local host (Claude Code, Claude Desktop, the MCP Inspector) — it is not a
  standalone network service.
