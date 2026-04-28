"""
Librarian Agent
===============

Primary skill: vector_indexing
Role: Index Page Objects and Step Definitions into PgVector KB.
"""

from agno.agent import Agent
from agno.tools.coding import CodingTools

from agents.librarian.instructions import INSTRUCTIONS
from app.settings import MODEL, agent_db
from db import create_knowledge

# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------
automation_knowledge = create_knowledge(
    name="Automation KB",
    table_name="codebase_vectors",
)

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
librarian = Agent(
    # Identity
    id="librarian",
    name="Librarian",
    role="Index and retrieve Page Objects and Step Definitions from automation/",
    # Model
    model=MODEL,
    # Data
    db=agent_db,
    knowledge=automation_knowledge,
    search_knowledge=True,
    # Capabilities
    tools=[CodingTools()],
    # Instructions
    instructions=INSTRUCTIONS,
    # Feature-specific
    session_state={
        "indexed_files": [],
        "obsolescence_reports": [],
        "file_statistics": {},
        "current_indexing_session": None,
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
