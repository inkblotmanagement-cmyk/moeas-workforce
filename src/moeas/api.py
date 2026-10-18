"""Optional HTTP API: pip install "moeas-workforce-app[server]"; uvicorn moeas.api:app

Set MOEAS_API_KEY. If it is not set, every endpoint except /health returns 503 (fail closed).
Data is stored in MOEAS_DB (default: moeas.db in the working directory).
"""
from __future__ import annotations

import hmac
import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .diploma import DiplomaService
from .fleet import FleetGovernor
from .oracle import MindfulOracle
from .store import Store
from .wealth import debt_payoff, savings_projection

app = FastAPI(title="MOEAS workforce app (JMGL-governed)", version="0.1.0")
_state: dict = {}


def state() -> dict:
    if not _state:
        store = Store(os.environ.get("MOEAS_DB", "moeas.db"))
        oracle = MindfulOracle(store=store)
        _state.update(store=store, oracle=oracle, diplomas=DiplomaService(store),
                      fleet=FleetGovernor(guard=oracle.guard, store=store))
    return _state


def require_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get("MOEAS_API_KEY")
    if not expected:
        raise HTTPException(503, "MOEAS_API_KEY is not configured; refusing requests")
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(401, "invalid API key")


class Demand(BaseModel):
    text: str = Field(..., max_length=8000)


class Enroll(BaseModel):
    name: str = Field(..., max_length=120)


class Complete(BaseModel):
    learner_id: int
    module_id: int
    quiz_score: int = Field(..., ge=0, le=100)


class Debt(BaseModel):
    balance: float
    apr_percent: float
    monthly_payment: float


class Savings(BaseModel):
    monthly_deposit: float
    years: float
    annual_return_percent: float
    start_balance: float = 0.0


class Task(BaseModel):
    robot: str
    task: str


@app.get("/health")
def health() -> dict:
    st = state()["oracle"].guard.status()
    return {"status": "ok" if st.get("engine_loaded") else "failing-closed", **st}


@app.post("/oracle", dependencies=[Depends(require_key)])
def oracle(d: Demand) -> dict:
    return state()["oracle"].answer_call(d.text)


@app.post("/literacy/enroll", dependencies=[Depends(require_key)])
def enroll(e: Enroll) -> dict:
    try:
        return {"learner_id": state()["diplomas"].enroll(e.name)}
    except ValueError as ex:
        raise HTTPException(422, str(ex)) from ex


@app.post("/literacy/complete", dependencies=[Depends(require_key)])
def complete(c: Complete) -> dict:
    try:
        return state()["diplomas"].complete_module(c.learner_id, c.module_id, c.quiz_score)
    except (KeyError, ValueError) as ex:
        raise HTTPException(422, str(ex)) from ex


@app.get("/literacy/progress/{learner_id}", dependencies=[Depends(require_key)])
def progress(learner_id: int) -> dict:
    try:
        return state()["diplomas"].progress(learner_id)
    except KeyError as ex:
        raise HTTPException(404, str(ex)) from ex


@app.post("/literacy/diploma/{learner_id}", dependencies=[Depends(require_key)])
def diploma(learner_id: int) -> dict:
    try:
        return state()["diplomas"].issue(learner_id)
    except PermissionError as ex:
        raise HTTPException(403, str(ex)) from ex
    except KeyError as ex:
        raise HTTPException(404, str(ex)) from ex


@app.get("/literacy/verify/{diploma_id}", dependencies=[Depends(require_key)])
def verify(diploma_id: str) -> dict:
    return {"valid": state()["diplomas"].verify(diploma_id)}


@app.post("/wealth/debt_payoff", dependencies=[Depends(require_key)])
def debt(d: Debt) -> dict:
    try:
        return debt_payoff(d.balance, d.apr_percent, d.monthly_payment)
    except ValueError as ex:
        raise HTTPException(422, str(ex)) from ex


@app.post("/wealth/savings", dependencies=[Depends(require_key)])
def savings(s: Savings) -> dict:
    try:
        return savings_projection(s.monthly_deposit, s.years, s.annual_return_percent, s.start_balance)
    except ValueError as ex:
        raise HTTPException(422, str(ex)) from ex


@app.post("/fleet/review", dependencies=[Depends(require_key)])
def fleet(tasks: list[Task]) -> dict:
    return state()["fleet"].review([t.model_dump() for t in tasks])
