import time

import pytest

from moeas.jmgl_guard import JMGLGuard


class FakeBackend:
    """Returns a fixed JMGL-shaped answer. Used only for fail-closed and plumbing tests."""
    loaded = True

    def __init__(self, **over):
        self.r = {"decision": "ALLOW", "grace_force": 0.8, "gate_score": 0.8, "rule_id": "GF-PASS",
                  "reason": "fake", "components": {"harm_avoided": 0.9, "human_benefit": 0.8,
                                                   "long_term_flourishing": 0.7}, **over}

    def __call__(self, text, history=None):
        return dict(self.r)


class Broken:
    loaded = True

    def __call__(self, text, history=None):
        raise RuntimeError("boom")


class Slow:
    loaded = True

    def __call__(self, text, history=None):
        time.sleep(2)
        return {}


class Missing:
    loaded = False
    load_error = "not installed"


@pytest.fixture(scope="session")
def real_guard():
    g = JMGLGuard()
    assert g.loaded, f"JMGL must be installed for these tests: {g.status()}"
    yield g
    g.close()
