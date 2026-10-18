"""Mindful Oracle request handling (replaces the MOEAS simulator in MOEA. futuristic device.txt).

The original scored demands with a fixed "mercy constant" and keyword curvature. Here each
demand is judged by JMGL (fail closed). If cleared, the oracle points to the app features
that fit; it does not generate advice itself. Every decision is written to the audit table.
"""
from __future__ import annotations

from typing import Optional

from .jmgl_guard import JMGLGuard, default_guard
from .store import Store

FEATURES = {
    "debt": "Debt payoff calculator (moeas.wealth.debt_payoff) and Module 4: Financial Discipline",
    "budget": "Module 4: Financial Discipline and Debt Reduction",
    "save": "Savings projection (moeas.wealth.savings_projection)",
    "job": "Module 3: AI Tools for Workforce Productivity (resume and job search)",
    "resume": "Module 3: AI Tools for Workforce Productivity (resume and job search)",
    "ai": "Module 1: Introduction to Ethical AI Literacy",
    "mindset": "Module 2: Productive Mindset",
    "stress": "Module 2: Productive Mindset",
    "sales": "Module 5: Deal-Closing and Cross-Industry Application",
}


class MindfulOracle:
    def __init__(self, guard: Optional[JMGLGuard] = None, store: Optional[Store] = None):
        self.guard = guard or default_guard()
        self.store = store or Store()

    def answer_call(self, demand: str) -> dict:
        v = self.guard.evaluate(demand)
        self.store.audit("demand", v.decision, v.rule_id, v.grace_force, {"guard": v.guard, "error": v.error})
        out = {"decision": v.decision, "grace_force": v.grace_force, "reason": v.reason, "resources": v.resources}
        if not v.allowed:
            out["message"] = (v.suggested_modification and f"A safer version: {v.suggested_modification}") or (
                "This needs a person to review before anything happens." if v.decision == "ESCALATE"
                else "MOEAS will not help with this request.")
            return out
        low = demand.lower()
        out["suggested_features"] = sorted({f for k, f in FEATURES.items() if k in low.split() or k in low}) or [
            "Start with Module 1: Introduction to Ethical AI Literacy"]
        out["message"] = "Cleared by JMGL. These parts of the app fit your request."
        return out
