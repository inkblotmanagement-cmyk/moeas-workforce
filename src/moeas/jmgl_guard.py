"""Fail-closed adapter around the Jackson Moral Governance Layer (JMGL).

Every harm/grace decision in this package comes from here. Rules:

* The decision is computed by JMGL Grace Force on the actual request text.
* Fail closed: JMGL not installed, classifier missing, engine error, timeout,
  unusable output, empty or oversized input -> BLOCK.
* Self-harm is never ALLOWed (at least ESCALATE, with 988 crisis resources).
  Stalking is never ALLOWed (BLOCK). These guards can only tighten JMGL.
* Simple digit-for-letter spelling ("k1ll mys3lf") is also judged; the stricter
  result wins.

JMGL is an optional dependency: ``pip install "jmgl[model] @ git+https://github.com/inkblotmanagement-cmyk/JacksonMoralGovernanceLayer@main"``.
Set ``JMGL_SRC=/path/to/JacksonMoralGovernanceLayer/src`` to use a local checkout instead.

This file is shared (identical copy) by grace-physics-framework, moeas-workforce-app
and heart-code-writings. jaxon-prime-concepts has the fuller JAXON PRIME version.
"""
from __future__ import annotations

import concurrent.futures as cf
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

GUARD_VERSION = "jmgl-guard-1.0.0"
DECISIONS = ("ALLOW", "MODIFY", "ESCALATE", "BLOCK")
SEVERITY = {"ALLOW": 0, "MODIFY": 1, "ESCALATE": 2, "BLOCK": 3}
DEFAULT_TIMEOUT_S = float(os.environ.get("JMGL_TIMEOUT_S", "15"))
MAX_CHARS = int(os.environ.get("JMGL_MAX_CHARS", "8000"))
SELFHARM_PROB = 0.30
STALKING_PROB = 0.30
CRISIS_RESOURCES = [
    "US: call or text 988 (988 Suicide & Crisis Lifeline), or chat at 988lifeline.org",
    "If you are in immediate danger, call 911 (US) or your local emergency number",
    "Outside the US: find a local helpline at findahelpline.com",
]
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def deobfuscate(text: str) -> str:
    """Read digits as letters inside words that mix both ("k1ll" -> "kill"). Pure numbers stay."""
    out = []
    for tok in text.split(" "):
        if any(c.isalpha() for c in tok) and any(c in "013457@$" for c in tok):
            tok = tok.translate(_LEET)
        out.append(tok)
    return " ".join(out)


@dataclass
class Verdict:
    decision: str                      # ALLOW / MODIFY / ESCALATE / BLOCK (final)
    grace_force: float                 # JMGL Grace Force, 0..1 (0.0 when failed closed)
    gate_score: float                  # JMGL pass/no-pass gate score, 0..1
    rule_id: str
    reason: str
    jmgl_decision: Optional[str] = None  # JMGL's answer before the guards
    category: Optional[str] = None
    components: dict = field(default_factory=dict)
    resources: list = field(default_factory=list)
    suggested_modification: Optional[str] = None
    guard: Optional[str] = None
    error: Optional[str] = None
    latency_ms: float = 0.0

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["allowed"] = self.allowed
        return d


def blocked(why: str, rule: str = "GUARD-FAILCLOSED", t0: Optional[float] = None) -> Verdict:
    ms = round((time.perf_counter() - t0) * 1000, 1) if t0 else 0.0
    return Verdict("BLOCK", 0.0, 0.0, rule, f"Failed closed: {why}", error=why, latency_ms=ms)


class JMGLBackend:
    """Loads JMGL (installed package, or JMGL_SRC / src checkout) and returns raw signals."""

    def __init__(self, src: Optional[str] = None, require_classifier: bool = True):
        self.src = src or os.environ.get("JMGL_SRC")
        self.require_classifier = require_classifier
        self.loaded = False
        self.load_error: Optional[str] = None
        self.engine_version: Optional[str] = None
        self.grace_version: Optional[str] = None
        self.classifier_loaded = False
        self._m: dict[str, Any] = {}
        try:
            self._load()
        except Exception as e:  # noqa: BLE001 - any load problem means BLOCK everything
            self.loaded, self.load_error = False, f"{type(e).__name__}: {e}"[:300]

    def _load(self) -> None:
        if self.src:
            p = Path(self.src)
            if not (p / "jmgl" / "__init__.py").exists():
                raise ImportError(f"JMGL source not found at {p}")
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
        import jmgl  # noqa: F401
        from jmgl import classifier, crisis, engine, grace
        if self.src and not Path(jmgl.__file__).resolve().is_relative_to(Path(self.src).resolve()):
            raise ImportError(f"a different jmgl is already imported ({jmgl.__file__})")
        self.engine_version, self.grace_version = engine.ENGINE_VERSION, grace.GRACE_VERSION
        self.classifier_loaded = bool(classifier.is_available())
        if self.classifier_loaded:
            classifier.classify("warm-up")
        elif self.require_classifier:
            raise ImportError("JMGL learned classifier unavailable (pip install 'jmgl[model]'); "
                              "rules-only mode refused")
        self._m = {"grace": grace, "crisis": crisis, "clf": classifier}
        self.loaded = True

    def __call__(self, text: str, history: Optional[list] = None) -> dict:
        if not self.loaded:
            raise RuntimeError(self.load_error or "JMGL not loaded")
        ctx = {"history": history} if history else None
        v = self._m["grace"].evaluate_grace_force(text, ctx)
        g = v.grace or {}
        probs = (self._m["clf"].classify(text, ctx).get("probs") or {}) if self.classifier_loaded else {}
        return {
            "decision": v.decision, "grace_force": v.grace_force, "gate_score": g.get("gate_score", 0.0),
            "rule_id": v.rule_id, "reason": v.reason, "category": g.get("category"),
            "components": dict(g.get("components") or {}), "resources": list(v.resources or []),
            "suggested_modification": v.suggested_modification,
            "p_selfharm": float(probs.get("selfharm", 0.0)), "p_stalking": float(probs.get("stalking", 0.0)),
            "crisis_level": self._m["crisis"].assess(" ".join((history or []) + [text])).get("level", "none"),
        }

    def status(self) -> dict:
        return {"engine_loaded": self.loaded, "engine_version": self.engine_version,
                "grace_version": self.grace_version, "classifier_loaded": self.classifier_loaded,
                "load_error": self.load_error, "guard_version": GUARD_VERSION}


class JMGLGuard:
    """Judge text with JMGL, fail closed. ``backend`` may be any callable returning JMGL-style
    signals (used by tests); by default the real JMGL is loaded."""

    def __init__(self, backend: Optional[Callable[..., dict]] = None, timeout_s: float = DEFAULT_TIMEOUT_S,
                 src: Optional[str] = None, require_classifier: bool = True):
        self.backend = backend if backend is not None else JMGLBackend(src, require_classifier)
        self.timeout_s = timeout_s
        self._pool = cf.ThreadPoolExecutor(max_workers=2, thread_name_prefix="jmgl")

    @property
    def loaded(self) -> bool:
        return bool(getattr(self.backend, "loaded", True))

    def status(self) -> dict:
        st = self.backend.status() if hasattr(self.backend, "status") else {"engine_loaded": self.loaded}
        return {**st, "fail_closed": True, "timeout_s": self.timeout_s}

    def evaluate(self, text: Any, history: Optional[list] = None) -> Verdict:
        t0 = time.perf_counter()
        if not isinstance(text, str) or not text.strip():
            return blocked("empty or non-text request", "GUARD-INPUT", t0)
        if len(text) > MAX_CHARS:
            return blocked(f"request longer than {MAX_CHARS} characters", "GUARD-INPUT", t0)
        if not self.loaded:
            return blocked(f"JMGL engine not available ({getattr(self.backend, 'load_error', None)})",
                           "GUARD-NOENGINE", t0)
        hist = [str(h) for h in history] if isinstance(history, list) else None
        variants = [text]
        if deobfuscate(text) != text:
            variants.append(deobfuscate(text))
        best: Optional[Verdict] = None
        deadline = time.perf_counter() + self.timeout_s
        for i, t in enumerate(variants):
            try:
                raw = self._pool.submit(self.backend, t, hist).result(
                    timeout=max(0.01, deadline - time.perf_counter()))
                v = self._verdict(raw)
            except cf.TimeoutError:
                return blocked(f"JMGL did not answer within {self.timeout_s}s", "GUARD-TIMEOUT", t0)
            except Exception as e:  # noqa: BLE001
                return blocked(f"JMGL error or unusable output: {type(e).__name__}: {e}"[:200],
                               "GUARD-ENGINE-ERROR", t0)
            stricter = best is not None and (SEVERITY[v.decision] > SEVERITY[best.decision] or (
                SEVERITY[v.decision] == SEVERITY[best.decision] and v.rule_id == "JL-08" != best.rule_id))
            if i and stricter:
                v.resources = list(dict.fromkeys(best.resources + v.resources))
                v.guard = v.guard or "deobfuscation"
                v.reason = "Judged on the de-obfuscated spelling. " + v.reason
                best = v
            elif best is None:
                best = v
        assert best is not None
        best.latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        return best

    @staticmethod
    def _verdict(r: dict) -> Verdict:
        if r.get("decision") not in DECISIONS:
            raise ValueError(f"unknown decision {r.get('decision')!r}")
        gf = float(r["grace_force"])
        if not 0.0 <= gf <= 1.0:
            raise ValueError(f"grace_force out of range: {gf}")
        v = Verdict(decision=r["decision"], grace_force=round(gf, 4), gate_score=round(float(r["gate_score"]), 4),
                    rule_id=str(r["rule_id"]), reason=str(r["reason"]), jmgl_decision=r["decision"],
                    category=r.get("category"), components=dict(r.get("components") or {}),
                    resources=list(r.get("resources") or []),
                    suggested_modification=r.get("suggested_modification"))
        selfharm = (r.get("crisis_level") in ("self", "third_party") or v.category == "selfharm"
                    or float(r.get("p_selfharm", 0)) >= SELFHARM_PROB)
        stalking = v.category == "stalking" or float(r.get("p_stalking", 0)) >= STALKING_PROB
        if v.decision == "ALLOW" and selfharm:
            v.decision, v.rule_id, v.guard = "ESCALATE", "GUARD-SELFHARM", "selfharm"
            v.reason = "JMGL passed this, but its self-harm/crisis signals are present; routed to support."
        elif v.decision == "ALLOW" and stalking:
            v.decision, v.rule_id, v.guard = "BLOCK", "GUARD-STALKING", "stalking"
            v.reason = "JMGL passed this, but its stalking signal is present; blocked."
        if selfharm or v.rule_id == "JL-08":
            for res in CRISIS_RESOURCES:
                if res not in v.resources:
                    v.resources.append(res)
        return v

    def close(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)


_default: Optional[JMGLGuard] = None


def default_guard() -> JMGLGuard:
    """Process-wide guard (loads JMGL once)."""
    global _default
    if _default is None:
        _default = JMGLGuard()
    return _default
