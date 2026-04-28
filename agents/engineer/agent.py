"""
Engineer Agent
==============

Primary skill: file_writer
Role: Author modular Playwright POMs and Step Definitions (Look-Before-You-Leap).
"""

from agno.agent import Agent
from agno.tools.coding import CodingTools
from agno.tools.file import FileTools

from agents.engineer.instructions import INSTRUCTIONS
from agents.engineer.tools import run_typecheck, write_feature, write_pom, write_step_def
from agents.librarian.agent import automation_knowledge
from app.settings import MODEL, agent_db

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
engineer = Agent(
    # Identity
    id="engineer",
    name="Engineer",
    role="Author modular Playwright POMs and Step Definitions (Look-Before-You-Leap)",
    # Model
    model=MODEL,
    # Data
    db=agent_db,
    knowledge=automation_knowledge,
    search_knowledge=True,
    # Capabilities
    tools=[
        CodingTools(),
        FileTools(),
        write_pom,
        write_step_def,
        write_feature,
        run_typecheck,
    ],
    # Instructions
    instructions=INSTRUCTIONS,
    # Feature-specific
    session_state={
        "created_files": [],
        "created_poms": [],
        "created_step_defs": [],
        "validation_results": {},
        "current_feature": None,
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
