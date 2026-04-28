"""
Detective Agent
===============

Primary skill: trace_analyzer
Role: Parse Playwright traces to classify failure root cause.
"""

from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from agents.detective.instructions import INSTRUCTIONS
from agents.detective.tools import classify_failure, parse_ci_log, parse_trace_zip
from app.settings import MODEL, agent_db

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
detective = Agent(
    # Identity
    id="detective",
    name="Detective",
    role="Parse Playwright traces, classify failure root cause, produce RCAReport",
    # Model
    model=MODEL,
    # Data
    db=agent_db,
    # Capabilities
    tools=[
        ReasoningTools(add_instructions=True),
        parse_trace_zip,
        parse_ci_log,
        classify_failure,
    ],
    # Instructions
    instructions=INSTRUCTIONS,
    # Feature-specific
    session_state={
        "analyzed_failures": [],
        "root_causes": [],
        "healability_assessments": [],
        "current_failure_id": None,
    },
    enable_agentic_state=True,
    add_session_state_to_context=True,
    # Memory
    enable_agentic_memory=True,
    # Context
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    # Output
    markdown=True,
)
