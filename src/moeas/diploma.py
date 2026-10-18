"""Enrollment, module completion, and diploma issuance.

Replaces the original diploma endpoints, which issued a diploma on request. Here a diploma
is issued only when every module has a recorded quiz score at or above PASSING_SCORE.
Each diploma has an id and a SHA-256 digest of its contents so it can be verified later.
This is a completion certificate, not an accredited credential.
"""
from __future__ import annotations

import hashlib
import uuid

from .curriculum import MODULE_IDS, MODULES, PASSING_SCORE
from .store import Store, now


class DiplomaService:
    def __init__(self, store: Store):
        self.s = store

    def enroll(self, name: str) -> int:
        name = (name or "").strip()
        if not name or len(name) > 120:
            raise ValueError("name is required (max 120 characters)")
        return self.s.x("INSERT INTO learners (name, created_utc) VALUES (?, ?)", (name, now())).lastrowid

    def _learner(self, learner_id: int):
        row = self.s.x("SELECT * FROM learners WHERE id=?", (learner_id,)).fetchone()
        if row is None:
            raise KeyError(f"no learner {learner_id}")
        return row

    def complete_module(self, learner_id: int, module_id: int, quiz_score: int) -> dict:
        self._learner(learner_id)
        if module_id not in MODULE_IDS:
            raise ValueError(f"unknown module {module_id}")
        if not isinstance(quiz_score, int) or not 0 <= quiz_score <= 100:
            raise ValueError("quiz_score must be an integer 0-100")
        self.s.x("INSERT OR REPLACE INTO progress VALUES (?,?,?,?)", (learner_id, module_id, quiz_score, now()))
        return self.progress(learner_id)

    def progress(self, learner_id: int) -> dict:
        self._learner(learner_id)
        rows = {r["module_id"]: r["score"] for r in
                self.s.x("SELECT module_id, score FROM progress WHERE learner_id=?", (learner_id,)).fetchall()}
        passed = [m for m in MODULE_IDS if rows.get(m, -1) >= PASSING_SCORE]
        return {"learner_id": learner_id, "scores": rows, "passed": passed,
                "remaining": [m["title"] for m in MODULES if m["id"] not in passed],
                "eligible": len(passed) == len(MODULE_IDS)}

    @staticmethod
    def _digest(diploma_id: str, name: str, issued: str, scores: dict) -> str:
        body = f"{diploma_id}|{name}|{issued}|" + ",".join(f"{k}:{scores[k]}" for k in sorted(scores))
        return hashlib.sha256(body.encode()).hexdigest()

    def issue(self, learner_id: int) -> dict:
        p = self.progress(learner_id)
        if not p["eligible"]:
            raise PermissionError(f"not eligible yet; remaining: {p['remaining']}")
        name = self._learner(learner_id)["name"]
        did, issued = str(uuid.uuid4()), now()
        digest = self._digest(did, name, issued, p["scores"])
        self.s.x("INSERT INTO diplomas VALUES (?,?,?,?)", (did, learner_id, issued, digest))
        return {"diploma_id": did, "name": name, "issued_utc": issued, "digest": digest,
                "title": "Certificate of Completion: AI Literacy and Workforce Productivity",
                "note": "Completion certificate from Mindful Oracle; not an accredited degree."}

    def verify(self, diploma_id: str) -> bool:
        row = self.s.x("SELECT * FROM diplomas WHERE id=?", (diploma_id,)).fetchone()
        if row is None:
            return False
        name = self._learner(row["learner_id"])["name"]
        scores = self.progress(row["learner_id"])["scores"]
        return row["digest"] == self._digest(diploma_id, name, row["issued_utc"], scores)
