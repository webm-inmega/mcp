import datetime
import decimal
import os

import mysql.connector
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

load_dotenv()

mcp = MCPServer("MySQLPractica", log_level="ERROR")

MAX_ROWS = 200


def _json_safe(value):
    """Convierte tipos de MySQL Connector que no son serializables a JSON."""
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return value


def get_connection():
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        connection_timeout=10,
    )


@mcp.tool()
def list_tables() -> list[str]:
    """Lista todas las tablas de la base de datos configurada."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def describe_table(table_name: str) -> list[dict]:
    """Muestra las columnas, tipos y llaves de una tabla."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DESCRIBE `%s`" % table_name.replace("`", ""))
        return cursor.fetchall()
    finally:
        conn.close()


@mcp.tool()
def run_query(sql: str) -> list[dict]:
    """Ejecuta una consulta SELECT de solo lectura y devuelve hasta 200 filas."""
    normalized = sql.strip().rstrip(";")
    if not normalized.lower().startswith("select"):
        raise ValueError("Solo se permiten consultas SELECT en este servidor de práctica.")
    if ";" in normalized:
        raise ValueError("No se permiten múltiples sentencias en una sola consulta.")

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(normalized)
        rows = cursor.fetchmany(MAX_ROWS)
        return [{k: _json_safe(v) for k, v in row.items()} for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")
