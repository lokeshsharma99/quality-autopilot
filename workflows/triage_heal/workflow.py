"""
Triage-Heal Workflow
=====================

Trace ZIP + Logs → Detective → [Healable Gate] → Medic → Verify 3x

Pipeline:
  1. Analyze Failure (Detective → RCAReport)
  2. Healable Check (Condition — LOCATOR_STALE + confidence >= 0.90)
  3. Patch Locator (Medic → HealingPatch)
"""

import re

from agno.workflow import Condition, Step, Workflow

from agents.detective import detective
from agents.medic import medic


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_healable(step_input) -> bool:  # type: ignore[no-untyped-def]
    """Gate: only dispatch Medic if failure is LOCATOR_STALE and auto-healable.

    Looks for LOCATOR_STALE classification in the Detective's RCAReport output,
    and verifies that requires_human is not True.
    """
    content = str(getattr(step_input, "previous_step_content", "") or "")
    is_locator_stale = "LOCATOR_STALE" in content
    requires_human = bool(re.search(r'"requires_human":\s*true', content, re.IGNORECASE))
    # Extract confidence if present
    confidence_match = re.search(r'"confidence":\s*([\d.]+)', content)
    confidence = float(confidence_match.group(1)) if confidence_match else 0.0
    return is_locator_stale and not requires_human and confidence >= 0.90


# ---------------------------------------------------------------------------
# Create Workflow
# ---------------------------------------------------------------------------
triage_heal = Workflow(
    id="triage-heal",
    name="Triage and Heal",
    steps=[
        Step(name="Analyze Failure", agent=detective),
        Condition(
            name="Healable Check",
            evaluator=is_healable,
            steps=[
                Step(name="Patch Locator", agent=medic),
            ],
        ),
    ],
)
