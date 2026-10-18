"""Humanoid fleet task governance (MOEAS Workforce Productivity Program for Humanoids.txt).

The original promised "20-30% less downtime" from a simulated 85% accurate harm predictor.
This module does one real thing: every task description for a robot is judged by JMGL
before dispatch. Cleared tasks are dispatched; ESCALATE tasks wait for a person; BLOCK
tasks are refused. No efficiency numbers are claimed.
"""
from __future__ import annotations

from typing import Iterable, Optional

from .jmgl_guard import JMGLGuard, default_guard
from .store import Store


class FleetGovernor:
    def __init__(self, guard: Optional[JMGLGuard] = None, store: Optional[Store] = None):
        self.guard = guard or default_guard()
        self.store = store or Store()

    def review(self, tasks: Iterable[dict]) -> dict:
        out = {"dispatch": [], "hold_for_human": [], "refused": []}
        for t in tasks:
            robot, desc = str(t.get("robot", "?")), t.get("task")
            v = self.guard.evaluate(desc)
            self.store.audit("fleet_task", v.decision, v.rule_id, v.grace_force, {"robot": robot})
            item = {"robot": robot, "task": desc, "decision": v.decision, "reason": v.reason}
            key = "dispatch" if v.allowed else "hold_for_human" if v.decision in ("ESCALATE", "MODIFY") else "refused"
            out[key].append(item)
        return out
