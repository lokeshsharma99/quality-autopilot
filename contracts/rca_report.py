"""
RCAReport Contract
===================

Detective agent output — failure classification and root cause analysis.
"""

from pydantic import BaseModel


class RCAReport(BaseModel):
    test_name: str
    trace_id: str
    classification: str         # LOCATOR_STALE | DATA_MISMATCH | TIMING_FLAKE | ENV_FAILURE | LOGIC_CHANGE
    confidence: float           # 0.0 – 1.0
    root_cause: str             # Human-readable explanation
    affected_file: str          # Path to failing test/POM
    affected_locator: str | None
    suggested_fix: str          # What the Medic should do
    requires_human: bool        # True if LOGIC_CHANGE
