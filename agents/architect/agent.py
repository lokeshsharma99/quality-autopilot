"""
Architect Agent
===============

Analyzes requirements, queries KB for impact, produces Execution Plans.
Primary Skill: semantic_search
"""

from agno.agent import Agent
from agno.tools.knowledge import KnowledgeTools
from agno.tools.reasoning import ReasoningTools

from agents.architect.instructions import INSTRUCTIONS
from app.settings import MODEL, agent_db
from db.session import get_automation_scaffold_knowledge

# ---------------------------------------------------------------------------
# Knowledge Base
# ---------------------------------------------------------------------------
automation_knowledge = get_automation_scaffold_knowledge()

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
architect = Agent(
    id="architect",
    name="Architect",
    role="Analyze requirements, query KB for impact, produce Execution Plan",
    model=MODEL,
    db=agent_db,
    knowledge=automation_knowledge,
    search_knowledge=True,
    tools=[ReasoningTools(add_instructions=True), KnowledgeTools(knowledge=automation_knowledge)],
    instructions=INSTRUCTIONS,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
