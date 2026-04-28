"""
Judge Agent
===========

Primary skill: adversarial_review
Role: Run DoD checklist, auto-approve at >= 90% confidence.
"""

from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from agents.judge.instructions import INSTRUCTIONS
from agents.judge.tools import check_code_quality, lint_gherkin, score_confidence
from app.settings import MODEL, agent_db

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
judge = Agent(
    # Identity
    id="judge",
    name="Judge",
    # Model
    model=MODEL,
    # Data
    db=agent_db,
    # Capabilities
    tools=[
        ReasoningTools(add_instructions=True),
        lint_gherkin,
        check_code_quality,
        score_confidence,
    ],
    # Instructions
    instructions=INSTRUCTIONS,
    # Feature-specific
    session_state={
        "reviewed_artifacts": [],
        "review_findings": [],
        "approval_decisions": [],
        "current_artifact": None,
    },
    enable_agentic_state=True,
    add_session_state_to_context=True,
    # Memory
    enable_agentic_memory=True,
    # Context
    add_datetime_to_context=True,
    # Output
    markdown=True,
)
