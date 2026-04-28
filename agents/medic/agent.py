"""
Medic Agent
===========

Primary skill: surgical_editor
Role: Patch only the specific locator line in the Page Object.
"""

from agno.agent import Agent
from agno.tools.coding import CodingTools
from agno.tools.file import FileTools

from agents.medic.instructions import INSTRUCTIONS
from app.settings import MODEL, agent_db

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
medic = Agent(
    # Identity
    id="medic",
    name="Medic",
    role="Patch only the specific stale locator in the Page Object — surgical edits only",
    # Model
    model=MODEL,
    # Data
    db=agent_db,
    # Capabilities
    tools=[CodingTools(), FileTools()],
    # Instructions
    instructions=INSTRUCTIONS,
    # Feature-specific
    session_state={
        "applied_edits": [],
        "generated_patches": [],
        "verification_results": {},
        "current_file": None,
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
