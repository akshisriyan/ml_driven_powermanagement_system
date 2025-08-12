from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
import os
from ..utils.auth import require_admin


router = APIRouter()


def _db_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(backend_dir, 'database.db')


def _ensure_settings():
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


class GeneratorToggle(BaseModel):
    enabled: bool


@router.get("/control/generator")
def get_generator_status():
    try:
        _ensure_settings()
        conn = sqlite3.connect(_db_path())
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = 'generator_enabled'")
        row = cur.fetchone()
        conn.close()
        enabled = (row and str(row[0]) == '1')
        return {"enabled": enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control/generator", dependencies=[Depends(require_admin)])
def set_generator_status(toggle: GeneratorToggle):
    try:
        _ensure_settings()
        conn = sqlite3.connect(_db_path())
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO settings(key, value) VALUES('generator_enabled', ?)\n"
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
            ('1' if toggle.enabled else '0',),
        )
        conn.commit()
        conn.close()
        return {"enabled": toggle.enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
