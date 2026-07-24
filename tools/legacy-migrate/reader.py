import sqlite3
from pathlib import Path

LEGACY_TABLES = [
    "profiles",
    "cycles",
    "temperatures",
    "fertility_signs",
    "symptoms",
    "computed_insights",
]


def read_legacy_db(db_path: str | Path) -> dict[str, list[dict]]:
    """Read all data from a legacy bbt.db file.

    Returns dict with keys matching table names.
    Each value is a list of dicts (rows converted from sqlite3.Row).
    Missing tables are returned as empty lists without error.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    data: dict[str, list[dict]] = {}

    for table in LEGACY_TABLES:
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            data[table] = [dict(r) for r in rows]
        except sqlite3.OperationalError:
            data[table] = []

    conn.close()
    return data
