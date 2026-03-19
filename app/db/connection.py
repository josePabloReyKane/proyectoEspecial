from __future__ import annotations

import pyodbc
from app.db.config import SERVER, DATABASE, DRIVER

def connect_sql_auth(db_user: str, db_pass: str) -> pyodbc.Connection:
    """Conecta a SQL Server usando autenticación SQL.

    Importante:
    - Aquí se valida la contraseña (SQL Auth).
    - Si el usuario/contra son incorrectos, pyodbc lanzará una excepción.
    """
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={db_user};"
        f"PWD={db_pass};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str, timeout=5)
