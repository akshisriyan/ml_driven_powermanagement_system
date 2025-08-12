from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import sqlite3
import pandas as pd
from ..utils.auth import require_admin


router = APIRouter()


def _db_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(backend_dir, 'database.db')


def _ensure_tables():
    conn = sqlite3.connect(_db_path())
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            parent_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS zone_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL,
            tick INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            voltage REAL,
            load REAL,
            FOREIGN KEY(zone_id) REFERENCES zones(id)
        );
        """
    )
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


_DEFAULT_ZONES = [
    ("Faculty of Engineering", "faculty"),
    ("Faculty of Science", "faculty"),
    ("Administration", "admin"),
    ("Hostels", "hostel"),
    ("Canteen", "canteen"),
    ("Library", "library"),
]


class ZoneCreate(BaseModel):
    name: str
    category: str
    parent_id: Optional[int] = None


class ZoneMetric(BaseModel):
    zone_name: str
    load: float
    voltage: float
    tick: Optional[int] = None


@router.get("/zones")
def list_zones():
    """List zones with latest metrics and status."""
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Seed defaults if no zones
        cur.execute("SELECT COUNT(*) as c FROM zones")
        if cur.fetchone()[0] == 0:
            for name, cat in _DEFAULT_ZONES:
                cur.execute("INSERT OR IGNORE INTO zones(name, category) VALUES(?, ?)", (name, cat))
            conn.commit()

        # Latest metrics per zone
        df = pd.read_sql_query(
            """
            SELECT z.id, z.name, z.category, z.is_active,
                   zm.voltage, zm.load, zm.timestamp, zm.tick
            FROM zones z
            LEFT JOIN (
                SELECT zone_id, MAX(id) as max_id FROM zone_metrics GROUP BY zone_id
            ) latest ON latest.zone_id = z.id
            LEFT JOIN zone_metrics zm ON zm.id = latest.max_id
            ORDER BY z.category, z.name
            """,
            conn,
        )
        conn.close()

        zones = []
        for _, r in df.iterrows():
            status = "unknown"
            if pd.notnull(r.get("voltage")) and pd.notnull(r.get("load")):
                if r["voltage"] < 18000 or r["load"] > 500:  # simple threshold
                    status = "warning"
                else:
                    status = "ok"
            zones.append(
                {
                    "id": int(r["id"]),
                    "name": r["name"],
                    "category": r["category"],
                    "is_active": bool(r["is_active"]),
                    "latest": {
                        "voltage": None if pd.isna(r.get("voltage")) else float(r["voltage"]),
                        "load": None if pd.isna(r.get("load")) else float(r["load"]),
                        "timestamp": None if pd.isna(r.get("timestamp")) else str(r["timestamp"]),
                        "tick": None if pd.isna(r.get("tick")) else int(r["tick"]),
                    },
                    "status": status,
                }
            )
        return {"zones": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zones", dependencies=[Depends(require_admin)])
def create_zone(zone: ZoneCreate):
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO zones(name, category, parent_id) VALUES(?, ?, ?)",
            (zone.name, zone.category, zone.parent_id),
        )
        conn.commit()
        zone_id = cur.lastrowid
        conn.close()
        return {"id": zone_id, "name": zone.name, "category": zone.category}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Zone name already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zones/seed-defaults", dependencies=[Depends(require_admin)])
def seed_default_zones():
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        cur = conn.cursor()
        for name, cat in _DEFAULT_ZONES:
            cur.execute("INSERT OR IGNORE INTO zones(name, category) VALUES(?, ?)", (name, cat))
        conn.commit()
        conn.close()
        return {"seeded": True, "count": len(_DEFAULT_ZONES)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MetricsIngest(BaseModel):
    metrics: List[ZoneMetric]


@router.post("/zones/ingest", dependencies=[Depends(require_admin)])
def ingest_zone_metrics(payload: MetricsIngest):
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        cur = conn.cursor()

        inserted = 0
        for m in payload.metrics:
            # ensure zone exists
            cur.execute("SELECT id FROM zones WHERE name = ?", (m.zone_name,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO zones(name, category) VALUES(?, ?)", (m.zone_name, "other"))
                zone_id = cur.lastrowid
            else:
                zone_id = row[0]

            cur.execute(
                "INSERT INTO zone_metrics(zone_id, tick, voltage, load) VALUES(?, ?, ?, ?)",
                (zone_id, m.tick, m.voltage, m.load),
            )
            inserted += 1

        conn.commit()
        conn.close()
        return {"inserted": inserted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zones/summary")
def zones_summary():
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        # Aggregate latest metrics per zone and sum by category
        df = pd.read_sql_query(
            """
            WITH latest AS (
                SELECT z.id as zone_id, z.category, z.name,
                       (SELECT id FROM zone_metrics zm WHERE zm.zone_id = z.id ORDER BY id DESC LIMIT 1) as m_id
                FROM zones z
            )
            SELECT l.category, SUM(zm.load) as total_load, AVG(zm.voltage) as avg_voltage, COUNT(*) as zones
            FROM latest l
            LEFT JOIN zone_metrics zm ON zm.id = l.m_id
            GROUP BY l.category
            """,
            conn,
        )
        conn.close()
        data = []
        for _, r in df.iterrows():
            data.append(
                {
                    "category": r["category"],
                    "total_load": 0.0 if pd.isna(r["total_load"]) else float(r["total_load"]),
                    "avg_voltage": None if pd.isna(r["avg_voltage"]) else float(r["avg_voltage"]),
                    "zones": int(r["zones"]),
                }
            )
        return {"categories": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zones/forecast")
def zones_forecast():
    """Simple heuristic forecast per category based on last N points average load."""
    try:
        _ensure_tables()
        conn = sqlite3.connect(_db_path())
        df = pd.read_sql_query(
            """
            WITH latest AS (
                SELECT z.id as zone_id, z.category
                FROM zones z
            ),
            recent AS (
                SELECT zm.* FROM zone_metrics zm
                WHERE zm.id IN (
                    SELECT id FROM zone_metrics ORDER BY id DESC LIMIT 1000
                )
            )
            SELECT l.category, AVG(r.load) as avg_recent_load
            FROM latest l
            LEFT JOIN recent r ON r.zone_id = l.zone_id
            GROUP BY l.category
            """,
            conn,
        )
        conn.close()
        out = []
        for _, r in df.iterrows():
            base = 0.0 if pd.isna(r["avg_recent_load"]) else float(r["avg_recent_load"])
            out.append({
                "category": r["category"],
                "next_hour_load": round(base * 1.02, 2),
                "next_day_load": round(base * 1.05, 2),
            })
        return {"forecast": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
