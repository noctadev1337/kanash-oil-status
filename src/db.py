import sqlite3
from pathlib import Path
from datetime import datetime

from src import paths


# схема таблиц
schema = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    stations_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS run_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    ext_id TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    UNIQUE(run_id, ext_id)
);

CREATE TABLE IF NOT EXISTS fuel_statuses (
    run_station_id INTEGER NOT NULL REFERENCES run_stations(id) ON DELETE CASCADE,
    fuel TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('yes', 'no', 'maybe', 'unknown')),
    PRIMARY KEY (run_station_id, fuel)
);
"""


def connect():
    path = paths.writable_dir() / "src" / "data" / "oil_status.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def ensure():
    connection = connect()
    try:
        connection.executescript(schema)
        columns = [c[1] for c in connection.execute("PRAGMA table_info(run_stations)")]
        if "status" not in columns:
            connection.execute("ALTER TABLE run_stations ADD COLUMN status TEXT")
        connection.commit()
    finally:
        connection.close()


def save_run(source, rows):
    ensure()
    connection = connect()
    try:
        created_at = datetime.now().isoformat()
        cursor = connection.execute(
            "INSERT INTO runs (source, created_at, stations_count) VALUES (?, ?, ?)",
            (source, created_at, len(rows)))
        run_id = cursor.lastrowid

        for row in rows:
            cursor = connection.execute(
                "INSERT INTO run_stations (run_id, ext_id, name, address, status) VALUES (?, ?, ?, ?, ?)",
                (run_id, row["id"], row["name"], row["address"], row.get("status")))
            station_id = cursor.lastrowid

            fuels = row["fuels"]
            for fuel in fuels:
                connection.execute(
                    "INSERT INTO fuel_statuses (run_station_id, fuel, status) VALUES (?, ?, ?)",
                    (station_id, fuel, fuels[fuel]))

        connection.commit()
    finally:
        connection.close()


def list_runs():
    ensure()
    connection = connect()
    try:
        cursor = connection.execute(
            "SELECT id, created_at, source, stations_count FROM runs ORDER BY created_at DESC")
        runs = []
        for item in cursor.fetchall():
            runs.append({
                "id": item[0],
                "created_at": item[1],
                "source": item[2],
                "stations_count": item[3],
            })
        return runs
    finally:
        connection.close()


def load_rows(run_id):
    ensure()
    connection = connect()
    try:
        cursor = connection.execute(
            "SELECT id, ext_id, name, address, status FROM run_stations WHERE run_id = ?", (run_id,))
        rows = []
        for station in cursor.fetchall():
            station_id = station[0]
            ext_id = station[1]
            name = station[2]
            address = station[3]
            station_status = station[4]

            fuels = {}
            cursor2 = connection.execute(
                "SELECT fuel, status FROM fuel_statuses WHERE run_station_id = ?", (station_id,))
            for status_row in cursor2.fetchall():
                fuels[status_row[0]] = status_row[1]

            rows.append({
                "id": ext_id,
                "name": name,
                "address": address,
                "lat": None,
                "lon": None,
                "fuels": fuels,
                "status": station_status,
            })
        return rows
    finally:
        connection.close()


def delete_run(run_id):
    ensure()
    connection = connect()
    try:
        connection.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        connection.commit()
    finally:
        connection.close()