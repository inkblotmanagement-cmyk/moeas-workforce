"""SQLite persistence (standard library only). Replaces the SQLAlchemy sketches."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS learners (id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_utc TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS progress (learner_id INTEGER, module_id INTEGER, score INTEGER, completed_utc TEXT,
  PRIMARY KEY (learner_id, module_id));
CREATE TABLE IF NOT EXISTS diplomas (id TEXT PRIMARY KEY, learner_id INTEGER, issued_utc TEXT, digest TEXT);
CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, ts_utc TEXT, kind TEXT, decision TEXT,
  rule_id TEXT, grace_force REAL, detail TEXT);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self._lock = threading.Lock()

    def x(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.db.execute(sql, args)
            self.db.commit()
            return cur

    def audit(self, kind: str, decision: str, rule_id: str, grace_force: float, detail: Optional[dict] = None):
        self.x("INSERT INTO audit (ts_utc, kind, decision, rule_id, grace_force, detail) VALUES (?,?,?,?,?,?)",
               (now(), kind, decision, rule_id, grace_force, json.dumps(detail or {})))

    def audit_rows(self) -> list[dict]:
        return [dict(r) for r in self.x("SELECT * FROM audit ORDER BY id").fetchall()]
