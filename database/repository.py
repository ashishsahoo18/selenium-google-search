"""SQLite persistence for searches, bookmarks, settings and schedules."""
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


class Repository:
    """Thread-safe-per-operation SQLite repository."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.initialize()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
                    browser TEXT, engine TEXT, original_query TEXT, improved_query TEXT,
                    screenshot TEXT, current_url TEXT, status TEXT
                );
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                    query TEXT NOT NULL, engine TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT NOT NULL, engine TEXT NOT NULL,
                    browser TEXT NOT NULL, run_at TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1
                );
            """)

    def add_history(self, **record: str) -> int:
        fields = ["created_at", "browser", "engine", "original_query", "improved_query", "screenshot", "current_url", "status"]
        record.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
        with self._connection() as conn:
            cursor = conn.execute(
                f"INSERT INTO history ({','.join(fields)}) VALUES ({','.join('?' * len(fields))})",
                [record.get(field, "") for field in fields],
            )
            return int(cursor.lastrowid)

    def history(self, search: str = "", limit: int = 500) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute("""SELECT * FROM history WHERE original_query LIKE ? OR improved_query LIKE ?
                ORDER BY id DESC LIMIT ?""", (f"%{search}%", f"%{search}%", limit)).fetchall()
        return [dict(row) for row in rows]

    def delete_history(self, record_id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM history WHERE id = ?", (record_id,))

    def add_bookmark(self, name: str, query: str, engine: str) -> None:
        with self._connection() as conn:
            conn.execute("INSERT INTO bookmarks (name, query, engine, created_at) VALUES (?, ?, ?, ?)",
                         (name, query, engine, datetime.now().isoformat(timespec="seconds")))

    def bookmarks(self) -> list[dict[str, Any]]:
        with self._connection() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM bookmarks ORDER BY id DESC")]

    def set_setting(self, key: str, value: Any) -> None:
        with self._connection() as conn:
            conn.execute("INSERT INTO settings VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def analytics(self) -> dict[str, Any]:
        rows = self.history(limit=10000)
        key = lambda field: Counter(r[field] for r in rows if r[field]).most_common(1)
        daily = Counter(r["created_at"][:10] for r in rows)
        return {"total": len(rows), "browser": key("browser"), "engine": key("engine"),
                "keyword": key("original_query"), "daily": dict(sorted(daily.items()))}
