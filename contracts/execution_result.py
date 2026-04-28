"""
ExecutionResult Contract
=========================

Test execution output — pass/fail summary from the Playwright runner.
"""

from pydantic import BaseModel


class ScenarioResult(BaseModel):
    scenario_name: str
    feature_file: str
    status: str                     # "passed" | "failed" | "skipped" | "pending"
    duration_ms: int
    error_message: str | None       # None if passed
    screenshot_path: str | None     # Path to failure screenshot
    trace_path: str | None          # Path to trace.zip for failed scenarios


class ExecutionResult(BaseModel):
    ticket_id: str
    run_id: str                     # Unique execution run identifier
    total_scenarios: int
    passed: int
    failed: int
    skipped: int
    pass_rate: float                # 0.0 – 1.0
    duration_ms: int
    scenarios: list[ScenarioResult]
    executed_at: str                # ISO timestamp
    environment: str                # "local" | "ci" | "staging"
