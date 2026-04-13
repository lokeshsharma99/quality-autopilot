"""
Medic Agent
===========

Performs surgical edits to fix broken locators.
"""

from pathlib import Path

from agno.agent import Agent
from agno.tools.coding import CodingTools
from agno.tools.file import FileTools

from agents.medic.instructions import INSTRUCTIONS
from app.settings import MODEL

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
medic_tools = [
    CodingTools(),
    FileTools(Path("automation")),
]

medic = Agent(
    id="medic",
    name="Medic",
    role="Perform surgical edits to fix broken locators (selector changes only, no logic changes)",
    model=MODEL,
    db=None,
    knowledge=None,
    search_knowledge=False,
    tools=medic_tools,
    instructions=INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
