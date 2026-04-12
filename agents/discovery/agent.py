"""
Discovery Agent
===============

Crawls the AUT, extracts UI structure, and produces a Site Manifesto.
Primary Skill: ui_crawler
"""

from agno.agent import Agent
from agno.tools.knowledge import KnowledgeTools
from agno.tools.reasoning import ReasoningTools

from agents.discovery.instructions import INSTRUCTIONS
from agents.discovery.tools import crawl_page, crawl_site
from app.settings import MODEL, agent_db, AUT_ID, CURRENT_AUT_CONFIG, AUTS_CONFIG
from db.session import get_site_manifesto_knowledge

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
discovery = Agent(
    # Identity
    id="discovery",
    name="Discovery",
    role="Crawl AUT and produce Site Manifesto with pages, components, and locators",

    # Model
    model=MODEL,

    # Data
    db=agent_db,
    knowledge=get_site_manifesto_knowledge(),
    search_knowledge=True,

    # Capabilities
    tools=[
        crawl_site,
        crawl_page,
        ReasoningTools(add_instructions=True),
        KnowledgeTools(knowledge=get_site_manifesto_knowledge()),
    ],

    # Instructions
    instructions=INSTRUCTIONS,

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
