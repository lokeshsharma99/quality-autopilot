"""
JudgeVerdict Contract
======================

Agentic Judge output — quality gate decision.
Confidence >= 0.90 → auto-approve.
Confidence < 0.90 → human review required.
Confidence < 0.50 → auto-reject.
"""

from pydantic import BaseModel


class JudgeVerdict(BaseModel):
    artifact_type: str                  # "gherkin" | "code" | "data" | "healing"
    agent_id: str                       # ID of the agent that produced the artifact
    confidence: float                   # 0.0 – 1.0
    passed: bool                        # True if confidence >= 0.90
    checklist_results: dict[str, bool]  # Each DoD item → pass/fail
    rejection_reasons: list[str]        # Empty if passed
    requires_human: bool                # True if confidence < 0.90
