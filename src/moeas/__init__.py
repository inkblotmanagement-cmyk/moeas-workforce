"""MOEAS workforce app: AI literacy diploma tracking, money calculators, and JMGL-governed requests.

Every free-text request is judged by the real JMGL engine through a fail-closed guard
(``moeas.jmgl_guard``). Without JMGL installed, every request is BLOCKed.
"""
from .curriculum import MODULES, PASSING_SCORE
from .store import Store
from .diploma import DiplomaService
from .wealth import debt_payoff, savings_projection
from .oracle import MindfulOracle
from .fleet import FleetGovernor

__version__ = "0.1.0"
__all__ = ["MODULES", "PASSING_SCORE", "Store", "DiplomaService", "debt_payoff", "savings_projection",
           "MindfulOracle", "FleetGovernor", "__version__"]
